# FAISS wrapper - Handles saving/loading vectors, adding embeddings, searching. 
# Maps vector positions to chunk IDs.
import faiss
import numpy as np
import pickle
import os
from pathlib import Path

class VectorStore:
    def __init__(self, dimension=384, index_path="faiss.index"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index = None
        self.chunk_ids = []  # Maps FAISS position to chunk ID
        self.load_or_create_index()
    
    def load_or_create_index(self):
        """Load existing index or create new one"""
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            # Load chunk IDs if they exist
            ids_path = self.index_path.with_suffix('.pkl')
            if ids_path.exists():
                with open(ids_path, 'rb') as f:
                    self.chunk_ids = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def add_embeddings(self, embeddings, chunk_ids):
        """Add embeddings to index"""
        if not embeddings:
            return
        
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
        self.chunk_ids.extend(chunk_ids)
        
        # Save
        faiss.write_index(self.index, str(self.index_path))
        with open(self.index_path.with_suffix('.pkl'), 'wb') as f:
            pickle.dump(self.chunk_ids, f)
    
    def search(self, query_embedding, k=5):
        """Search for similar chunks"""
        if self.index.ntotal == 0:
            return []
        
        query_array = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_array, min(k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunk_ids):
                results.append({
                    'chunk_id': self.chunk_ids[idx],
                    'score': float(distances[0][i])
                })
        return results