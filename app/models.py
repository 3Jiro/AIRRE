# Data structures - Defines the Document and DocumentChunk classes using dataclasses. 
# These are like blueprints for the data flowing through the system.
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Document:
    """Represents a document in the system"""
    filename: str
    file_hash: str
    file_type: str  # 'pdf', 'text', 'html'
    file_path: str
    upload_date: datetime
    extracted_text: Optional[str] = None
    processed: bool = False
    id: Optional[int] = None

@dataclass
class DocumentChunk:
    """Represents a chunk of a document"""
    file_hash: str
    chunk_index: int
    text: str
    start_char: int
    end_char: int
    id: Optional[int] = None