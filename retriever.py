"""
Retriever Module
Vector DB and retrieval logic using Chroma
"""
import chromadb
from typing import List, Dict, Tuple
import os


class Retriever:
    """Retrieve relevant chunks using vector similarity."""

    def __init__(self, persist_dir: str = "./chroma_db"):
        """
        Initialize retriever with Chroma.

        Args:
            persist_dir: Directory to persist Chroma database
        """
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = None
        self.chunks_by_id = {}

    def index_chunks(self, chunks: List[Dict], embeddings: List) -> None:
        """
        Index chunks in Chroma.

        Args:
            chunks: List of chunk dicts
            embeddings: List of embedding vectors
        """
        # Create/get collection
        self.collection = self.client.get_or_create_collection(
            name="pdf_chunks",
            metadata={"hnsw:space": "cosine"}
        )

        # Prepare data for insertion
        ids = []
        documents = []
        metadatas = []
        embeddings_list = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = chunk["chunk_id"]
            ids.append(chunk_id)
            documents.append(chunk["text"])
            metadatas.append(chunk["metadata"])
            embeddings_list.append(embedding.tolist() if hasattr(
                embedding, 'tolist') else embedding)

            # Store chunk data for reference
            self.chunks_by_id[chunk_id] = chunk

        # Clear and add to collection
        try:
            self.collection.delete(where={"chunk_id": {"$exists": True}})
        except:
            pass

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings_list
        )

        print(f"[RETRIEVER] Indexed {len(chunks)} chunks in Chroma")

    def retrieve(self, query_embedding: List, top_k: int = 5) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of chunks to retrieve

        Returns:
            List of (chunk_dict, score) tuples
        """
        if self.collection is None:
            raise RuntimeError("No chunks indexed. Call index_chunks() first.")

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist() if hasattr(
                query_embedding, 'tolist') else query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []

        if results and results["ids"] and len(results["ids"]) > 0:
            for chunk_id, doc_text, metadata, distance in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                # Convert distance to similarity score (cosine distance -> similarity)
                similarity_score = 1 - distance

                chunk = self.chunks_by_id.get(chunk_id, {})
                retrieved.append({
                    "chunk_id": chunk_id,
                    "text": doc_text,
                    "page": metadata.get("page", -1),
                    "metadata": metadata,
                    "similarity_score": float(similarity_score)
                })

        return retrieved

    def save(self) -> None:
        """Save Chroma database."""
        print(f"[RETRIEVER] Database persisted at {self.persist_dir}")

    def load_from_existing(self) -> bool:
        """Check if existing database exists."""
        return os.path.exists(os.path.join(self.persist_dir, "chroma.sqlite3"))
