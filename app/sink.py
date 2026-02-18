# Main orchestrator - Glues everything together. 
# Watches the folder, coordinates the processing pipeline, and handles the flow from file detection → extraction → chunking → storage. 
# This is the "brain" that runs the show.
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.models import Document
from app.storage import Storage
from app.extractor import TextExtractor
from app.chunker import DocumentChunker
import app.config as config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeSink(FileSystemEventHandler):
    """Main orchestrator for the knowledge sink"""
    
    def __init__(self, watch_path=config.WATCH_FOLDER):
        self.watch_path = Path(watch_path)
        self.storage = Storage()
        self.extractor = TextExtractor()
        self.chunker = DocumentChunker(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        
        logger.info(f"Knowledge Sink initialized, watching: {self.watch_path}")

# File system monitor - Uses watchdog to detect when files are added to the watch folder. 
# Triggers the processing pipeline when new files appear.

    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            import time
            time.sleep(1)  # Wait for file to finish copying
            file_path = Path(event.src_path)
            logger.info(f"New file detected: {file_path.name}")
            self.process_file(file_path)
    
    def calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def get_file_type(self, file_path: Path) -> Optional[str]:
        """Determine file type from extension"""
        ext = file_path.suffix.lower()
        return config.SUPPORTED_EXTENSIONS.get(ext)
    
    def process_file(self, file_path: Path):
        """Process a single file"""
        try:
            # Calculate hash
            file_hash = self.calculate_hash(file_path)
            
            # Check for duplicates
            if self.storage.document_exists(file_hash):
                logger.info(f"Duplicate file skipped: {file_path.name}")
                self.storage.log_processing(file_hash, "skipped", "Duplicate file")
                return
            
            # Get file type
            file_type = self.get_file_type(file_path)
            if not file_type:
                logger.warning(f"Unsupported file type: {file_path.suffix}")
                self.storage.log_processing(file_hash, "failed", f"Unsupported type: {file_path.suffix}")
                return
            
            # Create document record
            doc = Document(
                filename=file_path.name,
                file_hash=file_hash,
                file_type=file_type,
                file_path=str(file_path),
                upload_date=datetime.now(),
                processed=False
            )
            
            # Save metadata
            self.storage.save_document(doc)
            self.storage.log_processing(file_hash, "metadata_saved")
            
            # Extract text
            logger.info(f"Extracting text from {file_path.name}")
            text = self.extractor.extract(file_path, file_type)
            
            if not text:
                logger.error(f"Failed to extract text from {file_path.name}")
                self.storage.log_processing(file_hash, "failed", "Text extraction failed")
                return
            
            # Update document with extracted text
            doc.extracted_text = text
            self.storage.save_document(doc)
            self.storage.log_processing(file_hash, "text_extracted", f"{len(text)} chars")
            
            # Chunk document
            logger.info(f"Chunking document {file_path.name}")
            chunks = self.chunker.chunk_document(file_hash, text)
            
            if chunks:
                # Save chunks
                self.storage.save_chunks(chunks)
                
                # Mark as processed
                doc.processed = True
                self.storage.save_document(doc)
                self.storage.log_processing(
                    file_hash, 
                    "completed", 
                    f"Created {len(chunks)} chunks"
                )
                
                logger.info(f"Successfully processed {file_path.name}: {len(chunks)} chunks")
            else:
                logger.warning(f"No chunks created for {file_path.name}")
                self.storage.log_processing(file_hash, "warning", "No chunks created")
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            self.storage.log_processing(file_hash, "error", str(e))
    
    def process_existing_files(self):
        """Process any files already in the watch folder"""
        logger.info("Checking for existing files...")
        for file_path in self.watch_path.iterdir():
            if file_path.is_file():
                self.process_file(file_path)
    
    def start(self):
        """Start watching for files"""
        # Process any existing files first
        self.process_existing_files()
        
        # Start watching for new files
        observer = Observer()
        observer.schedule(self, str(self.watch_path), recursive=False)
        observer.start()
        
        logger.info(f"Watching {self.watch_path} for new files...")
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

def main():
    """Main entry point"""
    sink = KnowledgeSink()
    sink.start()

if __name__ == "__main__":
    main()