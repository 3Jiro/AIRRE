# Command-line interface - Lets you test searches interactively. 
# Runs the embedding process and query loop.
from embeddings_manager import EmbeddingsManager
import logging
from app.storage import Storage

logging.basicConfig(level=logging.INFO)

def main():
    manager = EmbeddingsManager()
    storage = Storage()
    
    # First, embed all chunks
    print("Embedding chunks...")
    manager.embed_chunks()
    
    # Interactive search
    print("\n🔍 Contextual Search Ready (type 'quit' to exit)")
    while True:
        query = input("\nAsk: ")
        if query.lower() == 'quit':
            break
        
        results = manager.search(query, k=3)

        chunk_ids = [r['chunk_id'] for r in results]  # You'll need to modify search() to return chunk_ids
        storage.log_query(query, str(results), chunk_ids)

        
        print(f"\nTop {len(results)} results:")
        for i, r in enumerate(results, 1):
            print(f"\n--- Result {i} (Score: {r['score']:.4f}) ---")
            print(r['text'][:300] + "...")

if __name__ == "__main__":
    main()