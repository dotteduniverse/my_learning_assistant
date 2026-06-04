import chromadb
from chromadb.utils import embedding_functions
from core.utils import get_embedding

# Use local embeddings with Chroma
class MemoryStore:
    def __init__(self, persist_dir="./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        # We'll use two collections: chat_history and topics_progress
        self.chat_collection = self.client.get_or_create_collection(
            name="chat_history",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        )
        self.topic_collection = self.client.get_or_create_collection(
            name="topic_notes",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        )
    
    def add_chat_message(self, user_msg, assistant_msg, topic=None):
        self.chat_collection.add(
            documents=[user_msg + "\n" + assistant_msg],
            metadatas=[{"topic": topic or "general", "timestamp": "now"}],
            ids=[f"chat_{len(self.chat_collection.get()['ids'])}"]
        )
    
    def retrieve_similar(self, query, n_results=3, collection="chat"):
        col = self.chat_collection if collection == "chat" else self.topic_collection
        results = col.query(query_texts=[query], n_results=n_results)
        return results['documents'][0] if results['documents'] else []