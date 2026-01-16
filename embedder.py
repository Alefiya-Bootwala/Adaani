"""
Embedder Module
Generate embeddings using sentence-transformers
"""
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np


class Embedder:
    """Generate embeddings for text chunks."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedder with a pretrained model.

        Args:
            model_name: HuggingFace model name for embeddings
        """
        print(f"[EMBEDDER] Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(
            f"[EMBEDDER] Model loaded. Embedding dimension: {self.embedding_dim}")

    def embed_chunks(self, chunks: List[dict]) -> List[np.ndarray]:
        """
        Generate embeddings for all chunks.

        Args:
            chunks: List of chunk dicts with 'text' field

        Returns:
            List of embedding vectors
        """
        texts = [chunk["text"] for chunk in chunks]
        print(f"[EMBEDDER] Generating embeddings for {len(texts)} chunks...")

        embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"[EMBEDDER] Generated {len(embeddings)} embeddings")

        return embeddings

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        return self.model.encode(text)

    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a query."""
        return self.model.encode(query)
