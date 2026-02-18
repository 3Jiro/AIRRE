# router
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import shutil
from pathlib import Path

from app.sink import KnowledgeSink
from app.embeddings_manager import EmbeddingsManager
from app.storage import Storage

router = APIRouter()

# Initialize components # Endpoints
sink = KnowledgeSink()
embed_manager = EmbeddingsManager()
storage = Storage()

class QueryRequest(BaseModel):
    query: str
    k: int = 3

class SearchResult(BaseModel):
    text: str
    score: float
    file_hash: str

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = Path("watch_folder") / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    sink.process_file(file_path)
    return {"filename": file.filename, "status": "processing"}

@router.post("/search")
async def search(request: QueryRequest):
    # This line actually does the search
    results = embed_manager.search(request.query, request.k)
    
    # Log it
    chunk_ids = [r['chunk_id'] for r in results]
    storage.log_query(request.query, str(results), chunk_ids)
    
    return {
        "query": request.query,
        "results": [
            {
                "text": r['text'][:500], 
                "score": r['score'], 
                "file_hash": r['file_hash']
            } for r in results
        ]
    }

@router.get("/health")
async def health():
    return {"status": "healthy"}