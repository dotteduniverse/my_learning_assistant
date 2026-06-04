import logging
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

class MemoryStore:
    def __init__(self, persist_dir="./data/chroma_db"):
        logger.info(f"Initializing ChromaDB memory store at {persist_dir}")
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Use the default embedding function (ONNX, downloads on first run, no key)
        embed_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.chat_collection = self.client.get_or_create_collection(
            name="chat_history",
            embedding_function=embed_fn
        )
        self.topic_collection = self.client.get_or_create_collection(
            name="topic_notes",
            embedding_function=embed_fn
        )
        logger.debug("Collections 'chat_history' and 'topic_notes' ready")
    
    def add_chat_message(self, user_msg, assistant_msg, topic=None):
        doc = user_msg + "\n" + assistant_msg
        msg_id = f"chat_{len(self.chat_collection.get()['ids'])}"
        logger.debug(f"Adding chat message ID={msg_id}, topic={topic}, length={len(doc)}")
        self.chat_collection.add(
            documents=[doc],
            metadatas=[{"topic": topic or "general", "timestamp": "now"}],
            ids=[msg_id]
        )
        logger.info(f"Chat message saved (id={msg_id})")
    
    def retrieve_similar(self, query, n_results=3, collection="chat"):
        col = self.chat_collection if collection == "chat" else self.topic_collection
        logger.debug(f"Querying {collection} collection for: '{query[:50]}...' (n={n_results})")
        results = col.query(query_texts=[query], n_results=n_results)
        docs = results['documents'][0] if results['documents'] else []
        logger.info(f"Retrieved {len(docs)} similar documents from {collection}")
        return docs