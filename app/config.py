# Configuration settings - Central place for all settings like chunk sizes, folder paths, supported file types. 
# Makes it easy to tweak behavior without changing code.
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
WATCH_FOLDER = BASE_DIR / "watch_folder"
DB_PATH = BASE_DIR / "knowledge_sink.db"

# Processing settings
CHUNK_SIZE = 1000  # characters per chunk
CHUNK_OVERLAP = 200  # overlap between chunks

# Supported file types
SUPPORTED_EXTENSIONS = {
    '.pdf': 'pdf',
    '.txt': 'text',
    '.md': 'text',
    '.html': 'html',
    '.htm': 'html'
}

# Create watch folder if it doesn't exist
os.makedirs(WATCH_FOLDER, exist_ok=True)