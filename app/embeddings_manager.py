# Orchestrator - Connects HuggingFace embeddings to vector store. 
# Converts text → vectors → search results.

from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np
from app.vector_store import VectorStore
from app.storage import Storage
import logging
import sqlite3

logger = logging.getLogger(__name__)

class EmbeddingsManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.embeddings_model = HuggingFaceEmbeddings(model_name=model_name)
        self.vector_store = VectorStore(dimension=384)
        self.storage = Storage()
    
    def embed_chunks(self, chunk_ids=None):
        """Generate and store embeddings for chunks"""
        chunks = self.storage.get_all_chunks()
        
        if not chunks:
            logger.info("No chunks to embed")
            return
        
        texts = [chunk['text'] for chunk in chunks]
        chunk_ids = [chunk['id'] for chunk in chunks]
        
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embeddings_model.embed_documents(texts)
        
        self.vector_store.add_embeddings(embeddings, chunk_ids)
        logger.info(f"Added {len(embeddings)} embeddings to vector store")
    
    def search(self, query, k=5):
        """Search for chunks similar to query"""
        query_embedding = self.embeddings_model.embed_query(query)
        results = self.vector_store.search(query_embedding, k)
        
        # Get full chunk text
        chunks = []
        for r in results:
            chunk = self.get_chunk_by_id(r['chunk_id'])
            if chunk:
                chunks.append({
                    'chunk_id': r['chunk_id'],
                    'text': chunk['text'],
                    'score': r['score'],
                    'file_hash': chunk['file_hash']
                })
        return chunks
    
    def get_chunk_by_id(self, chunk_id):
        """Retrieve chunk text from database"""
        with sqlite3.connect(self.storage.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_hash, text FROM chunks WHERE id = ?", (chunk_id,))
            row = cursor.fetchone()
            if row:
                return {'file_hash': row[0], 'text': row[1]}
        return None