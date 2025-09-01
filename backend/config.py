import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
NOTES_DIR = BASE_DIR / "data"
DATA_DIR = BASE_DIR / "backend" / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Supported file types
SUPPORTED_EXTENSIONS = [".md", ".pdf", ".txt"]

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral:latest"

# Vector database settings
VECTOR_DB_PATH = str(DATA_DIR / "vector_db")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chat storage settings
CHAT_HISTORY_PATH = str(DATA_DIR / "chat_history")
ENABLE_CHAT_STORAGE = True
MAX_CHAT_HISTORY = 1000

# Processing settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
BATCH_SIZE = 16

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000