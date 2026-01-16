"""
Text Chunking Module
Intelligently chunks text with overlap and metadata preservation
"""
from typing import List, Dict
import re


class TextChunker:
    """Chunk text with overlap for better retrieval."""

    def __init__(self, chunk_size: int = 512, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_pages(self, pages: List[Dict]) -> List[Dict]:
        """
        Chunk all pages into smaller chunks with overlap.

        Args:
            pages: List of page dicts from PDFLoader

        Returns:
            List of chunk dicts with text, metadata (page:chunk_id)
        """
        chunks = []

        for page_data in pages:
            page_num = page_data["page_num"]
            text = page_data["text"]
            source = page_data.get("metadata", {}).get("source", "unknown")

            page_chunks = self._chunk_text(text, page_num, source)
            chunks.extend(page_chunks)

        print(
            f"[CHUNKING] Created {len(chunks)} chunks from {len(pages)} pages")
        return chunks

    def _chunk_text(self, text: str, page_num: int, source: str = "unknown") -> List[Dict]:
        """Chunk a single page's text."""
        chunks = []

        # Extract filename from source path
        import os
        source_name = os.path.basename(source).replace(
            ".pdf", "").replace(".PDF", "")

        # Split by sentences first for better semantics
        sentences = self._split_sentences(text)

        current_chunk = []
        current_length = 0
        chunk_idx = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunk_id = f"{source_name}:p{page_num}:c{chunk_idx}"

                chunks.append({
                    "text": chunk_text,
                    "chunk_id": chunk_id,
                    "page_num": page_num,
                    "chunk_index": chunk_idx,
                    "metadata": {
                        "page": page_num,
                        "chunk_id": chunk_id,
                        "source": source,
                        "source_name": source_name
                    }
                })

                chunk_idx += 1

                # Start new chunk with overlap
                # Keep last few sentences for overlap
                overlap_sentences = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sentences + [sentence]
                current_length = len(" ".join(current_chunk))
            else:
                current_chunk.append(sentence)
                current_length += sentence_length + 1  # +1 for space

        # Save final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_id = f"{source_name}:p{page_num}:c{chunk_idx}"
            chunks.append({
                "text": chunk_text,
                "chunk_id": chunk_id,
                "page_num": page_num,
                "chunk_index": chunk_idx,
                "metadata": {
                    "page": page_num,
                    "chunk_id": chunk_id,
                    "source": source,
                    "source_name": source_name
                }
            })

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter
        text = text.replace("\n", " ").strip()
        # Split on period, exclamation, question mark
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get sentences for overlap."""
        total_length = 0
        overlap_sentences = []

        # Work backwards to get overlap
        for sentence in reversed(sentences):
            if total_length + len(sentence) > self.overlap:
                break
            overlap_sentences.insert(0, sentence)
            total_length += len(sentence) + 1

        return overlap_sentences
