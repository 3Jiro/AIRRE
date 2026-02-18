# Document splitter - Takes long text and breaks it into smaller, overlapping chunks. 
# This is crucial because LLMs and embeddings work better with smaller pieces of text.
import re
from typing import List, Dict
from app.models import DocumentChunk
import logging

logger = logging.getLogger(__name__)

class DocumentChunker:
    """Split documents into overlapping chunks"""
    
    def __init__(self, chunk_size=300, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def find_split_point(self, text: str, start: int, end: int) -> int:
        """Find a good point to split text"""
        # Look for paragraph break
        paragraph_break = text.rfind('\n\n', start, end)
        if paragraph_break != -1 and paragraph_break > start:
            return paragraph_break
        
        # Look for sentence break
        sentence_breaks = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        for break_char in sentence_breaks:
            pos = text.rfind(break_char, start, end)
            if pos != -1 and pos > start:
                return pos + len(break_char) - 1
        
        # Look for line break
        line_break = text.rfind('\n', start, end)
        if line_break != -1 and line_break > start:
            return line_break
        
        # Look for word break
        word_break = text.rfind(' ', start, end)
        if word_break != -1 and word_break > start:
            return word_break
        
        # If no good break, return end
        return end
    
    def chunk_document(self, file_hash: str, text: str) -> List[DocumentChunk]:
        """Split document into chunks"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = min(start + self.chunk_size, text_length)
            
            # Find good split point if not at end
            if end < text_length:
                end = self.find_split_point(text, start, end)
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunk = DocumentChunk(
                    file_hash=file_hash,
                    chunk_index=len(chunks),
                    text=chunk_text,
                    start_char=start,
                    end_char=end
                )
                chunks.append(chunk)
                logger.debug(f"Created chunk {len(chunks)}: {len(chunk_text)} chars")
            
            # Move start for next chunk with overlap
            start = max(end - self.chunk_overlap, start + 1)
        
        logger.info(f"Created {len(chunks)} chunks for document {file_hash}")
        return chunks