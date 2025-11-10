# Parent-Child Chunking Implementation Plan

## 🔍 Analysis Complete! Here's What I Found:

---

## **Current Data Flow Through Pipeline**

```
1. ast_parser.parse_file()
   ├─ extract_nodes() traverses AST recursively
   ├─ Creates node dict: {type, name, content, start_line, end_line, start_byte, end_byte}
   └─ Returns: {file_path, language, content, nodes: [...], tree_info}

2. node_collector.collect_nodes()
   ├─ Receives parsed_file from step 1
   ├─ For each node: hash content (SHA256)
   ├─ Calls build_enriched_content(chunk_metadata, content)
   ├─ Creates chunk: {content, enriched_content, file_path, language, hash, node_type, node_name, start_line, end_line, start_byte, end_byte, locations}
   └─ Deduplicates by hash, tracks duplicate_locations

3. context_builder.build_enriched_content()
   ├─ build_context() creates: "File: X\nLanguage: Y\nType: Z\nSymbol: W\nLines: A-B"
   └─ Returns: "{context}\n\n{content}"

4. chunk_service.chunk_repository()
   ├─ Calls split_chunk() on each chunk
   ├─ Saves to chunks.json with structure: {chunks: [...], statistics, repository, version, total_chunks}
   └─ Each chunk has: content + enriched_content + metadata

5. embedding_service (next step)
   └─ Embeds enriched_content field

6. chroma_store (final step)
   └─ Stores chunks with metadata in ChromaDB
```

---

## **🎯 Key Findings - Where Parent-Child Relationships Are LOST**

### **Problem 1: `extract_nodes()` Flattens Hierarchy**

**Current Code** (`ast_parser.py` lines 248-277):

```python
def traverse(node: Any) -> None:
    """Recursively traverse AST and extract target nodes."""
    if node.type in target_types:
        # Extract node content
        node_content = content_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')

        # Get node name if available
        node_name = get_node_name(node, content_bytes)

        nodes.append({
            'type': node.type,
            'name': node_name,
            'content': node_content,
            'start_line': node.start_point[0] + 1,
            'end_line': node.end_point[0] + 1,
            'start_byte': node.start_byte,
            'end_byte': node.end_byte
        })

    # Continue traversing children
    for child in node.children:
        traverse(child)
```

**❌ Issue:**

- When it finds a `class_definition`, it extracts the ENTIRE class (lines 1-100)
- Then keeps recursing and finds `function_definition` inside the class
- Extracts the function AGAIN (lines 10-20), which is ALREADY inside the class content
- Both get added to `nodes[]` list with NO link between them
- Result: **Duplicate code in embeddings**

---

### **Problem 2: No Parent Tracking During Traversal**

The `traverse()` function has **no context** about nesting:

- It doesn't know if current node is inside a class/module
- No parent reference passed during recursion
- No UUID generation for linking

---

### **Problem 3: `node_collector.py` Preserves Flat Structure**

**Current Code** (lines 42-85):

```python
for node in parsed_file['nodes']:
    # ... creates chunk_metadata ...
    enriched_content = build_enriched_content(chunk_metadata, content)

    chunk = {
        'content': content,
        'enriched_content': enriched_content,
        **chunk_metadata  # Just copies flat metadata
    }
```

**❌ Issue:**

- No `parent_id`, `children_ids`, or `is_parent` fields
- No hierarchy information preserved
- Deduplication by SHA256 alone can't distinguish parent-child from true duplicates

---

## **📐 Exact Changes Needed (Code Level)**

### **Change 1: Modify `ast_parser.extract_nodes()` to Track Hierarchy**

**Add this before the traverse function:**

```python
import uuid

# Define parent node types (containers)
PARENT_NODE_TYPES = {
    'class_definition',      # Python
    'class_declaration',     # Java, JS, TS
    'interface_declaration', # Java, TS
    'impl_item',             # Rust
    'struct_item',           # Rust
    'module',                # Some languages
}
```

**Replace the traverse function (lines 248-277) with:**

```python
def traverse(node: Any, parent_id: Optional[str] = None, parent_info: Optional[Dict] = None) -> None:
    """Recursively traverse AST and extract target nodes with hierarchy tracking."""
    if node.type in target_types:
        # Generate unique ID for this node
        node_id = str(uuid.uuid4())

        # Extract node content
        node_content = content_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')

        # Get node name if available
        node_name = get_node_name(node, content_bytes)

        # Determine if this node is a parent (container)
        is_parent = node.type in PARENT_NODE_TYPES

        # Create node dict with hierarchy
        node_dict = {
            'id': node_id,
            'type': node.type,
            'name': node_name,
            'content': node_content,
            'start_line': node.start_point[0] + 1,
            'end_line': node.end_point[0] + 1,
            'start_byte': node.start_byte,
            'end_byte': node.end_byte,
            'is_parent': is_parent,
            'parent_id': parent_id,
            'children_ids': [],  # Will be populated for parents
        }

        # Add parent information if this is a child
        if parent_id and parent_info:
            node_dict['parent_type'] = parent_info.get('type')
            node_dict['parent_name'] = parent_info.get('name')

        nodes.append(node_dict)

        # If this is a parent node, traverse children with this node as parent
        if is_parent:
            parent_info_for_children = {
                'type': node.type,
                'name': node_name,
                'id': node_id
            }
            for child in node.children:
                traverse(child, parent_id=node_id, parent_info=parent_info_for_children)
        else:
            # Not a parent, continue normal traversal
            for child in node.children:
                traverse(child, parent_id=parent_id, parent_info=parent_info)

        # Populate children_ids for parent nodes (do this after traversing children)
        if is_parent:
            # Find all children added after this node
            for later_node in nodes:
                if later_node.get('parent_id') == node_id:
                    node_dict['children_ids'].append(later_node['id'])
    else:
        # Not a target node, but keep traversing
        for child in node.children:
            traverse(child, parent_id=parent_id, parent_info=parent_info)
```

---

### **Change 2: Update `node_collector.py` to Preserve Hierarchy**

**In `collect_nodes()` method, line 70:**

**Current:**

```python
chunk = {
    'content': content,
    'enriched_content': enriched_content,
    **chunk_metadata
}
```

**New:**

```python
chunk = {
    'content': content,
    'enriched_content': enriched_content,
    **chunk_metadata,
    # Preserve hierarchy fields from node
    'id': node.get('id'),
    'parent_id': node.get('parent_id'),
    'parent_type': node.get('parent_type'),
    'parent_name': node.get('parent_name'),
    'children_ids': node.get('children_ids', []),
    'is_parent': node.get('is_parent', False),
}
```

---

### **Change 3: Enhance `context_builder.build_enriched_content()`**

**Replace the function (lines 60-97) with:**

```python
def build_enriched_content(chunk: Dict[str, Any], content: str) -> str:
    """
    Build enriched content by combining context metadata with code content.

    Now includes parent hierarchy information for better semantic search.
    """
    context_parts: List[str] = []

    # Add parent context if this is a child node
    if chunk.get('parent_id') and chunk.get('parent_name'):
        parent_type = chunk.get('parent_type', 'unknown')
        parent_name = chunk.get('parent_name')
        context_parts.append(f"Parent: {parent_name} ({parent_type})")

    # Add file path
    if 'file_path' in chunk and chunk['file_path']:
        context_parts.append(f"File: {chunk['file_path']}")

    # Add language
    if 'language' in chunk and chunk['language']:
        context_parts.append(f"Language: {chunk['language']}")

    # Add node type (function, class, etc.)
    if 'node_type' in chunk and chunk['node_type']:
        context_parts.append(f"Type: {chunk['node_type']}")

    # Add symbol name if available
    if 'node_name' in chunk and chunk['node_name']:
        context_parts.append(f"Symbol: {chunk['node_name']}")

    # Add line range
    start_line = chunk.get('start_line')
    end_line = chunk.get('end_line')
    if start_line is not None and end_line is not None:
        context_parts.append(f"Lines: {start_line}-{end_line}")

    context = '\n'.join(context_parts) if context_parts else ''

    if not context:
        return content

    return f"{context}\n\n{content}"
```

---

### **Change 4: Filter Parents from Embedding in `embedding_service.py`**

Need to see the embedding service file, but conceptually:

```python
# Before generating embeddings, filter out parents
chunks_to_embed = [
    chunk for chunk in chunks
    if not chunk.get('is_parent', False)
]

logger.info(f"Embedding {len(chunks_to_embed)} child chunks (skipping {len(chunks) - len(chunks_to_embed)} parent chunks)")
```

---

### **Change 5: Update `chunk_service.save_chunks()` to Preserve New Fields**

The current save function already saves everything, but update version:

```python
data = {
    'chunks': chunks,
    'statistics': stats or {},
    'repository': repo_name,
    'version': '2.0',  # Updated for parent-child support
    'total_chunks': len(chunks),
    'schema': {
        'parent_child_enabled': True,
        'hierarchy_fields': ['id', 'parent_id', 'children_ids', 'is_parent']
    }
}
```

---

## **📊 Example: Before vs After**

### **Before (Current Flat Structure)**

```json
{
  "chunks": [
    {
      "content": "class AutoReloadManager:\n    def __init__(self, console):\n        ...\n    def toggle(self):\n        ...",
      "node_type": "class_definition",
      "node_name": "AutoReloadManager",
      "hash": "abc123...",
      "start_line": 3,
      "end_line": 18
    },
    {
      "content": "def __init__(self, console):\n        self.console = console\n        ...",
      "node_type": "function_definition",
      "node_name": "__init__",
      "hash": "def456...",
      "start_line": 6,
      "end_line": 8
    },
    {
      "content": "def toggle(self):\n        self.auto_reload = not self.auto_reload\n        ...",
      "node_type": "function_definition",
      "node_name": "toggle",
      "hash": "ghi789...",
      "start_line": 10,
      "end_line": 14
    }
  ]
}
```

**Problem:** All 3 chunks get embedded → `__init__` and `toggle` code appears in embeddings TWICE

---

### **After (Parent-Child Structure)**

```json
{
  "version": "2.0",
  "chunks": [
    {
      "id": "uuid-parent-123",
      "content": "class AutoReloadManager:\n    def __init__(self, console):\n        ...\n    def toggle(self):\n        ...",
      "enriched_content": "File: auto_reload.py\nLanguage: python\nType: class_definition\nSymbol: AutoReloadManager\nLines: 3-18\n\nclass AutoReloadManager:...",
      "node_type": "class_definition",
      "node_name": "AutoReloadManager",
      "hash": "abc123...",
      "start_line": 3,
      "end_line": 18,
      "is_parent": true,
      "parent_id": null,
      "children_ids": ["uuid-child-456", "uuid-child-789"]
    },
    {
      "id": "uuid-child-456",
      "content": "def __init__(self, console):\n        self.console = console\n        ...",
      "enriched_content": "Parent: AutoReloadManager (class_definition)\nFile: auto_reload.py\nLanguage: python\nType: function_definition\nSymbol: __init__\nLines: 6-8\n\ndef __init__(self, console):...",
      "node_type": "function_definition",
      "node_name": "__init__",
      "hash": "def456...",
      "start_line": 6,
      "end_line": 8,
      "is_parent": false,
      "parent_id": "uuid-parent-123",
      "parent_type": "class_definition",
      "parent_name": "AutoReloadManager",
      "children_ids": []
    },
    {
      "id": "uuid-child-789",
      "content": "def toggle(self):\n        self.auto_reload = not self.auto_reload\n        ...",
      "enriched_content": "Parent: AutoReloadManager (class_definition)\nFile: auto_reload.py\nLanguage: python\nType: function_definition\nSymbol: toggle\nLines: 10-14\n\ndef toggle(self):...",
      "node_type": "function_definition",
      "node_name": "toggle",
      "hash": "ghi789...",
      "start_line": 10,
      "end_line": 14,
      "is_parent": false,
      "parent_id": "uuid-parent-123",
      "parent_type": "class_definition",
      "parent_name": "AutoReloadManager",
      "children_ids": []
    }
  ]
}
```

**Benefits:**

- Only 2 chunks embedded (children only) → saves 33% on embeddings
- Children have "Parent: AutoReloadManager" in enriched_content → better semantic search
- Parent stored with UUID → can be fetched by ID during retrieval
- No duplicate code in embeddings

---

## **🚀 Implementation Roadmap**

### **Module-by-Module Changes**

| **File**                   | **What to Add**                                          | **Why**                                     |
| -------------------------- | -------------------------------------------------------- | ------------------------------------------- |
| `ast_parser.py`            | Parent tracking during AST traversal, UUID generation    | Track hierarchy at extraction time          |
| `node_collector.py`        | `parent_id`, `children_ids`, `is_parent` fields          | Link parents to children post-deduplication |
| `context_builder.py`       | Prepend "Parent: ClassName" to enriched_content if child | Give embeddings hierarchical context        |
| `chunk_service.py`         | Filter logic: embed children only, save all chunks       | Control what gets embedded vs stored        |
| `embedding_service.py`     | Skip `is_parent=True` chunks                             | Reduce API calls by 20-30%                  |
| `chroma_store.py`          | Store parent metadata, enable ID-based parent fetch      | Enable batch retrieval by parent_id         |
| `tools/semantic_search.py` | Post-search parent fetch + attachment                    | Assemble full context after search          |
| `tools/read_file.py`       | Filter out parent chunks, show children only             | Fix duplicate display issue                 |

---

## **💡 Key Design Decisions**

### **1. Parent Definition**

**Rule:** A node is a parent if it can contain other semantic nodes

**Language-Specific Parent Types:**

```python
PARENT_NODE_TYPES = {
    'python': ['module', 'class_definition'],
    'javascript': ['program', 'class_declaration'],
    'typescript': ['program', 'class_declaration', 'interface_declaration'],
    'java': ['class_declaration', 'interface_declaration'],
    'rust': ['impl_item', 'struct_item'],
    # ... etc
}
```

### **2. Storage Strategy**

**Decision:** Store ALL chunks (parents + children) in ChromaDB with:

- Parents: NO embedding (embedding field = None)
- Children: WITH embedding
- Both: Full metadata including parent_id/children_ids

**Why:** Simpler than separate JSON, enables ID-based parent fetch via ChromaDB query

### **3. Retrieval UX**

**Approach:**

1. Semantic search returns top-k **children only** (embedded chunks)
2. Extract unique parent_ids from results
3. Batch-fetch parents from ChromaDB by ID
4. Display: `[Child code] + [▼ Parent: ClassName (click to expand)]`

---

## **🔧 Implementation Phases**

### **Phase 1: Core Hierarchy Tracking (ast_parser.py)**

- [x] Add PARENT_NODE_TYPES mapping
- [ ] Modify extract_nodes() traverse function
- [ ] Add UUID generation
- [ ] Test on sample Python file

### **Phase 2: Metadata Propagation**

- [ ] Update node_collector.py to preserve hierarchy fields
- [ ] Update context_builder.py to add parent context
- [ ] Update chunk_service.py to save v2.0 schema

### **Phase 3: Embedding Optimization**

- [ ] Filter parents in embedding_service.py
- [ ] Update chroma_store.py for parent metadata
- [ ] Measure embedding reduction

### **Phase 4: Retrieval Enhancement**

- [ ] Add parent fetch logic in semantic_search.py
- [ ] Update output_formatter.py for parent display
- [ ] Fix read_file.py duplicate issue

### **Phase 5: Testing & Validation**

- [ ] Test on tkreload repo
- [ ] Verify 20-30% chunk reduction
- [ ] Measure semantic search improvement
- [ ] Update documentation

---

## **📈 Expected Improvements**

### **Quantitative Metrics**

- **Embedding Cost Reduction:** 20-30% fewer API calls
- **Storage Efficiency:** 15-25% smaller vector database
- **Search Quality:** Higher precision@5, recall@10

### **Qualitative Benefits**

- **No Duplicate Results:** Children won't compete with parents
- **Better Context:** "Parent: ClassName" in embeddings improves relevance
- **Hierarchical Understanding:** Can fetch full class context on-demand
- **Cleaner Output:** read_file tool shows each code block once

---

## **🎯 Success Criteria**

✅ **Chunk count reduced by 20-30%** on tkreload repository  
✅ **parent_id/children_ids populated** for all hierarchical nodes  
✅ **No duplicate chunks** in semantic search results  
✅ **Parent context appears** in enriched_content for children  
✅ **Embedding API calls reduced** by measurable percentage  
✅ **Search precision improved** compared to baseline

---

## **📚 References**

- **Current System:** `docs/chunking_system_architecture.md`
- **GitHub Issue:** Parent-child chunking proposal
- **Related Docs:** `docs/cli_run.md` (duplicate chunk examples)
