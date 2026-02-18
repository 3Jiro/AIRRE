# FastAPI
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import router
from app.embeddings_manager import EmbeddingsManager
from app.storage import Storage

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Loading embeddings...")
    embed_manager = EmbeddingsManager()
    storage = Storage()
    
    # Check if chunks exist and generate embeddings
    chunk_count = storage.get_chunk_count()
    if chunk_count > 0:
        embed_manager.embed_chunks()
        print(f"Generated embeddings for {chunk_count} chunks")
    
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(title="AIRRE API", lifespan=lifespan)
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "AIRRE API is running", "status": "healthy"}