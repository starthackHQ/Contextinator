"""Shared pytest fixtures for testing."""
import pytest
import tempfile
import shutil
from pathlib import Path
import chromadb
from chromadb.config import Settings


@pytest.fixture
def temp_repo():
    """Create a temporary test repository with sample Python files."""
    temp_dir = tempfile.mkdtemp()
    
    # Create sample Python files with various structures
    (Path(temp_dir) / "src").mkdir()
    
    # Main module with function and class
    (Path(temp_dir) / "src" / "main.py").write_text("""
def authenticate_user(username, password):
    '''Authenticate user with credentials.'''
    if not username or not password:
        return False
    return True

class UserManager:
    '''Manage user operations.'''
    
    def __init__(self):
        self.users = {}
    
    def create_user(self, name, email):
        '''Create a new user.'''
        user_id = len(self.users) + 1
        self.users[user_id] = {"name": name, "email": email}
        return user_id
    
    def get_user(self, user_id):
        '''Get user by ID.'''
        return self.users.get(user_id)
    
    def delete_user(self, user_id):
        '''Delete user by ID.'''
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
""")
    
    # Utils module
    (Path(temp_dir) / "src" / "utils.py").write_text("""
def validate_input(data):
    '''Validate input data.'''
    if not data:
        return False
    if not isinstance(data, (str, dict, list)):
        return False
    return True

def format_response(data, status_code=200):
    '''Format API response.'''
    return {
        "status": status_code,
        "data": data,
        "timestamp": None
    }
""")
    
    # Database module
    (Path(temp_dir) / "src" / "database.py").write_text("""
class DatabaseConnection:
    '''Handle database connections.'''
    
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connected = False
    
    def connect(self):
        '''Establish database connection.'''
        self.connected = True
        return True
    
    def disconnect(self):
        '''Close database connection.'''
        self.connected = False
        return True
    
    def execute_query(self, query):
        '''Execute SQL query.'''
        if not self.connected:
            raise RuntimeError("Not connected to database")
        return []
""")
    
    # Create README
    (Path(temp_dir) / "README.md").write_text("""
# Test Repository

This is a test repository for unit testing.

## Features
- User authentication
- Database operations
- Input validation
""")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_chromadb():
    """Create a temporary ChromaDB instance."""
    temp_dir = tempfile.mkdtemp()
    client = chromadb.PersistentClient(
        path=temp_dir,
        settings=Settings(anonymized_telemetry=False, allow_reset=True)
    )
    
    yield client, temp_dir
    
    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass  # Handle Windows file locking issues


@pytest.fixture
def test_collection(temp_chromadb):
    """Create a test collection with sample embedded data using ChromaVectorStore."""
    from contextinator.vectorstore.chroma_store import ChromaVectorStore
    
    client, temp_dir = temp_chromadb
    store = ChromaVectorStore(db_path=temp_dir)
    
    # Create sample embedded chunks
    # Using 3072 dimensions to match OpenAI text-embedding-3-small model
    embedded_chunks = [
        {
            "id": "chunk1",
            "content": "def authenticate_user(username, password):\n    '''Authenticate user with credentials.'''",
            "embedding": [0.1] * 3072,
            "metadata": {
                "file_path": "src/main.py",
                "node_name": "authenticate_user",
                "language": "python",
                "node_type": "function_definition",
                "start_line": 2,
                "end_line": 6
            }
        },
        {
            "id": "chunk2",
            "content": "class UserManager:\n    '''Manage user operations.'''",
            "embedding": [0.2] * 3072,
            "metadata": {
                "file_path": "src/main.py",
                "node_name": "UserManager",
                "language": "python",
                "node_type": "class_definition",
                "start_line": 8,
                "end_line": 28
            }
        }
    ]
    
    # Store the embeddings
    store.store_embeddings(embedded_chunks, "test_repo", clear_existing=True)
    
    yield store, temp_dir
    
    # Cleanup handled by temp_chromadb fixture


@pytest.fixture
def mock_openai_embeddings(monkeypatch):
    """Mock OpenAI API calls for embeddings to avoid API costs during testing."""
    
    class MockEmbedding:
        def __init__(self):
            self.embedding = [0.1] * 1536
    
    class MockEmbeddingResponse:
        def __init__(self, num_embeddings=1):
            self.data = [MockEmbedding() for _ in range(num_embeddings)]
    
    def mock_create(*args, **kwargs):
        # Determine number of inputs
        input_data = kwargs.get('input', [])
        if isinstance(input_data, str):
            num_embeddings = 1
        else:
            num_embeddings = len(input_data)
        return MockEmbeddingResponse(num_embeddings)
    
    # Mock the OpenAI client
    try:
        import openai
        monkeypatch.setattr("openai.resources.embeddings.Embeddings.create", mock_create)
    except ImportError:
        pass  # OpenAI not installed yet
    
    yield mock_create


@pytest.fixture
def sample_chunks():
    """Provide sample code chunks for testing (matching actual chunk structure)."""
    return [
        {
            "id": "chunk1",
            "content": "def authenticate_user(username, password):\n    return True",
            "metadata": {
                "file_path": "src/main.py",
                "node_name": "authenticate_user",
                "language": "python",
                "node_type": "function_definition"
            }
        },
        {
            "id": "chunk2",
            "content": "class UserManager:\n    def __init__(self):\n        pass",
            "metadata": {
                "file_path": "src/main.py",
                "node_name": "UserManager",
                "language": "python",
                "node_type": "class_definition"
            }
        }
    ]


@pytest.fixture
def sample_embedded_chunks(sample_chunks):
    """Provide sample chunks with embeddings."""
    embedded = []
    for chunk in sample_chunks:
        chunk_copy = chunk.copy()
        # Using 3072 dimensions to match OpenAI text-embedding-3-small model
        chunk_copy["embedding"] = [0.1] * 3072
        embedded.append(chunk_copy)
    return embedded


@pytest.fixture
def test_collection_with_data(temp_chromadb):
    """Create a test collection with sample embedded data for search tests.
    
    This fixture is specifically for testing search tools that require
    a pre-populated ChromaDB collection.
    """
    from contextinator.vectorstore.chroma_store import ChromaVectorStore
    
    client, temp_dir = temp_chromadb
    store = ChromaVectorStore(db_path=temp_dir)
    
    # Create sample embedded chunks with proper structure
    # Using 3072 dimensions to match OpenAI text-embedding-3-small model
    embedded_chunks = [
        {
            "id": "chunk_calculate",
            "content": "def calculate(a, b):\n    '''Calculate sum of two numbers.'''\n    return a + b",
            "embedding": [0.1] * 3072,
            "file_path": "utils.py",
            "node_name": "calculate",
            "language": "python",
            "node_type": "function_definition",
            "start_line": 1,
            "end_line": 3
        },
        {
            "id": "chunk_userauth",
            "content": "class UserAuth:\n    '''Handle user authentication.'''\n    def login(self, user, pwd):\n        return True",
            "embedding": [0.2] * 3072,
            "file_path": "auth.py",
            "node_name": "UserAuth",
            "language": "python",
            "node_type": "class_definition",
            "start_line": 1,
            "end_line": 4
        },
        {
            "id": "chunk_validate",
            "content": "def validate_input(data):\n    '''Validate input data.'''\n    return bool(data)",
            "embedding": [0.15] * 3072,
            "file_path": "utils.py",
            "node_name": "validate_input",
            "language": "python",
            "node_type": "function_definition",
            "start_line": 5,
            "end_line": 7
        }
    ]
    
    # Store the embeddings in the test_collection
    store.store_embeddings(embedded_chunks, "test_collection", clear_existing=True)
    
    yield store, temp_dir
    
    # Cleanup handled by temp_chromadb fixture
