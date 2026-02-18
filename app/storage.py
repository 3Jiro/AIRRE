# Database layer - Handles all SQLite operations. Saves documents, chunks, and processing logs. 
# Abstracts away the database so other files don't need to know SQL.
import sqlite3
from datetime import datetime
from typing import List, Optional
from app.models import Document, DocumentChunk
import app.config as config

class Storage:
    def __init__(self, db_path=config.DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_hash TEXT UNIQUE NOT NULL,
                    file_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    upload_date TIMESTAMP NOT NULL,
                    extracted_text TEXT,
                    processed INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Chunks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    start_char INTEGER NOT NULL,
                    end_char INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_hash) REFERENCES documents(file_hash),
                    UNIQUE(file_hash, chunk_index)
                )
            ''')
            
            # Processing log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_hash) REFERENCES documents(file_hash)
                )
            ''')
            
            conn.commit()
    
    def save_document(self, doc: Document) -> int:
        """Save document metadata"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO documents 
                (filename, file_hash, file_type, file_path, upload_date, extracted_text, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc.filename, doc.file_hash, doc.file_type, 
                doc.file_path, doc.upload_date, doc.extracted_text, 
                1 if doc.processed else 0
            ))
            conn.commit()
            return cursor.lastrowid
    
    def document_exists(self, file_hash: str) -> bool:
        """Check if document already exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM documents WHERE file_hash = ?", (file_hash,))
            return cursor.fetchone() is not None
    
    def save_chunks(self, chunks: List[DocumentChunk]):
        """Save document chunks"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for chunk in chunks:
                cursor.execute('''
                    INSERT OR IGNORE INTO chunks 
                    (file_hash, chunk_index, text, start_char, end_char)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    chunk.file_hash, chunk.chunk_index, 
                    chunk.text, chunk.start_char, chunk.end_char
                ))
            conn.commit()
    
    def log_processing(self, file_hash: str, status: str, message: str = ""):
        """Log processing events"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO processing_log (file_hash, status, message)
                VALUES (?, ?, ?)
            ''', (file_hash, status, message))
            conn.commit()
    
    def get_unprocessed_documents(self) -> List[Document]:
        """Get documents that haven't been chunked"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT filename, file_hash, file_type, file_path, upload_date, extracted_text, processed, id
                FROM documents 
                WHERE processed = 0 AND extracted_text IS NOT NULL
            ''')
            rows = cursor.fetchall()
            
            documents = []
            for row in rows:
                doc = Document(
                    filename=row[0],
                    file_hash=row[1],
                    file_type=row[2],
                    file_path=row[3],
                    upload_date=datetime.fromisoformat(row[4]) if isinstance(row[4], str) else row[4],
                    extracted_text=row[5],
                    processed=bool(row[6]),
                    id=row[7]
                )
                documents.append(doc)
            
            return documents
        
    def get_all_chunks(self):
        """Get all chunks for embedding"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, file_hash, text FROM chunks ORDER BY id")
            rows = cursor.fetchall()
            return [{'id': row[0], 'file_hash': row[1], 'text': row[2]} for row in rows]
        
    def log_query(self, query, response, chunk_ids_used):
        """Log query and response to audit trail"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    response TEXT,
                    chunks_used TEXT,  -- comma-separated chunk IDs
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                INSERT INTO audit_log (query, response, chunks_used)
                VALUES (?, ?, ?)
            ''', (query, response, ','.join(map(str, chunk_ids_used))))
            conn.commit()

    def get_chunk_count(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM chunks")
            return cursor.fetchone()[0]