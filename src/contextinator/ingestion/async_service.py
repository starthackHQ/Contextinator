"""Async Ingestion Service for concurrent repository processing."""
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
import os
import tempfile
import shutil
from ..utils.repo_utils import extract_repo_name_from_url, clone_repo
from ..chunking import chunk_repository, save_chunks
from ..embedding import EmbeddingService
from ..vectorstore import store_repository_embeddings
from ..utils.logger import logger


class AsyncIngestionService:
    """Async pipeline: clone -> chunk -> embed -> store (concurrent)."""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.embedding_service = None  # Lazy init to avoid sync client in async context
        self.base_dir = base_dir or "./contextinator_data"
        self._temp_dirs = []  # Track temp dirs for cleanup
    
    def _get_embedding_service(self):
        """Lazy init embedding service to avoid sync client in async context."""
        if not self.embedding_service:
            self.embedding_service = EmbeddingService()
        return self.embedding_service
    
    async def clone_repository_async(self, repo_url: str, timeout: int = 300) -> Dict[str, Any]:
        """Async git clone using subprocess with timeout."""
        repo_name = extract_repo_name_from_url(repo_url) or "repo"
        target_dir = os.path.join(tempfile.gettempdir(), f"contextinator_{repo_name}_{os.getpid()}")
        
        target_path = Path(target_dir)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔄 Cloning {repo_url}")
        
        try:
            process = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    "git", "clone", "--depth", "1", repo_url, str(target_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                ),
                timeout=timeout
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"Git clone failed: {error_msg}")
            
            file_count = sum(1 for root, dirs, files in os.walk(target_path) 
                            if '.git' not in root for _ in files)
            
            logger.info(f"✅ Cloned {file_count} files")
            self._temp_dirs.append(str(target_path))
            
            return {"repo_path": str(target_path), "file_count": file_count}
            
        except asyncio.TimeoutError:
            if target_path.exists():
                shutil.rmtree(target_path, ignore_errors=True)
            raise Exception(f"Git clone timeout after {timeout}s")
    
    async def chunk_repository_async(self, repo_path: str, repo_name: str) -> List[Dict[str, Any]]:
        """Async chunking (runs in thread pool)."""
        logger.info(f"📦 Chunking {repo_name}")
        
        loop = asyncio.get_event_loop()
        chunks = await loop.run_in_executor(
            None, 
            lambda: chunk_repository(repo_path, repo_name, save=False, output_dir=None)
        )
        
        logger.info(f"✅ Created {len(chunks)} chunks")
        return chunks
    
    async def embed_chunks_async(
        self,
        chunks: List[Dict[str, Any]],
        use_async: bool = True,
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """Async embedding - calls async method directly to avoid nested event loop."""
        logger.info(f"🔮 Embedding {len(chunks)} chunks")
        
        service = self._get_embedding_service()
        # Call async method directly instead of generate_embeddings to avoid nested loop
        embeddings = await service._generate_embeddings_async(chunks, 250, max_concurrent)
        
        logger.info(f"✅ Embedded {len(embeddings)} chunks")
        return embeddings
    
    async def store_embeddings_async(
        self,
        repo_name: str,
        embedded_chunks: List[Dict[str, Any]],
        collection_name: str
    ) -> Dict[str, Any]:
        """Async vector store."""
        logger.info(f"💾 Storing {len(embedded_chunks)} embeddings")
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: store_repository_embeddings(
                self.base_dir,
                repo_name,
                embedded_chunks,
                collection_name,
                None  # chromadb_dir
            )
        )
        
        logger.info(f"✅ Stored embeddings")
        return {"stored": len(embedded_chunks)}
    
    def cleanup_temp_dirs(self):
        """Clean up temporary cloned directories."""
        for temp_dir in self._temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    logger.debug(f"Cleaned up: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {temp_dir}: {e}")
        self._temp_dirs.clear()
    
    async def process_repository_async(
        self,
        repo_url: str,
        collection_name: str,
        use_async: bool = True,
        max_concurrent: int = 5,
        cleanup: bool = True
    ) -> Dict[str, Any]:
        """Complete async pipeline for single repository."""
        repo_path = None
        try:
            clone_result = await self.clone_repository_async(repo_url)
            repo_path = clone_result["repo_path"]
            repo_name = extract_repo_name_from_url(repo_url) or Path(repo_path).name
            
            chunks = await self.chunk_repository_async(repo_path, repo_name)
            embeddings = await self.embed_chunks_async(chunks, use_async, max_concurrent)
            stats = await self.store_embeddings_async(repo_name, embeddings, collection_name)
            
            return {
                "status": "success",
                "repo_path": repo_path,
                "repo_name": repo_name,
                "collection_name": collection_name,
                "total_chunks": len(chunks),
                "total_embeddings": len(embeddings),
                "storage_stats": stats
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process {repo_url}: {e}")
            return {
                "status": "failed",
                "repo_url": repo_url,
                "collection_name": collection_name,
                "error": str(e)
            }
        finally:
            if cleanup and repo_path:
                try:
                    shutil.rmtree(repo_path, ignore_errors=True)
                except Exception as e:
                    logger.warning(f"Failed to cleanup {repo_path}: {e}")
    
    async def process_batch_async(
        self,
        repos: List[Dict[str, str]],
        max_concurrent: int = 5,
        cleanup: bool = True
    ) -> List[Dict[str, Any]]:
        """Process multiple repositories concurrently."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(repo_info):
            async with semaphore:
                return await self.process_repository_async(
                    repo_url=repo_info["repo_url"],
                    collection_name=repo_info["collection_name"],
                    use_async=True,
                    max_concurrent=3,
                    cleanup=cleanup
                )
        
        logger.info(f"🚀 Processing {len(repos)} repositories concurrently (max={max_concurrent})")
        
        try:
            results = await asyncio.gather(
                *[process_with_semaphore(repo) for repo in repos],
                return_exceptions=True
            )
            
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Repo {i} failed: {result}")
                    processed_results.append({
                        "status": "failed",
                        "repo_url": repos[i]["repo_url"],
                        "error": str(result)
                    })
                else:
                    processed_results.append(result)
            
            success_count = sum(1 for r in processed_results if r.get("status") == "success")
            logger.info(f"✅ Batch complete: {success_count}/{len(repos)} successful")
            
            return processed_results
        finally:
            if cleanup:
                self.cleanup_temp_dirs()
