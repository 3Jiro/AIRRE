# AIRRE - Automated Intelligence-Driven Research & Reporting Engine

A RAG (Retrieval-Augmented Generation) system that automatically ingests documents, makes them searchable, and provides intelligent answers with full audit trails.

## 🚀 Features

- **Knowledge Sink**: Auto-ingests PDFs, text files, and HTML documents
- **Smart Chunking**: Intelligent document splitting with configurable size
- **Vector Search**: Semantic search using HuggingFace embeddings + FAISS
- **Audit Trail**: Complete logging of all queries and responses
- **REST API**: FastAPI endpoints for upload and search
- **Dockerized**: One-command deployment

## 🛠️ Tech Stack

- FastAPI
- HuggingFace Transformers
- FAISS Vector Store
- Sentence-Transformers
- Docker
- SQLite

## 📦 Quick Start

### Local Setup
```bash
pip install -r requirements.txt
python app/sink.py  # Start file watcher
python app/search_cli.py  # Interactive search
```

### DOCKER 
```bash
docker build -t airre .
docker run -p 8001:8001 -v ${PWD}/data:/app/data airre
```

### 📚 API Endpoints

POST /upload - Upload documents

POST /search - Semantic search

GET /health - System status


### 📊 Project Structure

AIRRE/
├── app/               # Core application
├── watch_folder/      # Drop files here
├── Dockerfile
├── requirements.txt
└── README.md


Author - @3Jiro