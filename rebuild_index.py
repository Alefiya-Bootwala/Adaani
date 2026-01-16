#!/usr/bin/env python3
"""Test the RAG system with debugging"""

import os
import sys
from pdf_loader import PDFLoader
from chunker import TextChunker
from embedder import Embedder
from retriever import Retriever
from rag_system import RAGSystem
import google.generativeai as genai

# Set API key
API_KEY = os.getenv(
    "GOOGLE_API_KEY", "AIzaSyD4NED4XQobmNAojPg7wkNHEnA0q1DY98w")
genai.configure(api_key=API_KEY)


def rebuild_index():
    """Rebuild the Chroma index from scratch"""

    print("\n" + "="*70)
    print("REBUILDING RAG INDEX")
    print("="*70)

    pdfs = ["SAMPLE1.pdf", "SAMPLE2.pdf", "ADANI.pdf"]
    existing_pdfs = [p for p in pdfs if os.path.exists(p)]

    if not existing_pdfs:
        print("❌ No PDFs found!")
        return

    print(f"\n📄 Loading {len(existing_pdfs)} PDF(s)...")

    # Load all PDFs
    all_pages = []
    for pdf_path in existing_pdfs:
        print(f"\n   Processing: {pdf_path}")
        loader = PDFLoader(pdf_path)
        pages = loader.load()
        print(f"   ✓ Extracted {len(pages)} pages")
        all_pages.extend(pages)

    print(f"\n📊 Total pages loaded: {len(all_pages)}")

    # Chunk text
    print(f"\n✂️  Chunking text...")
    chunker = TextChunker()
    chunks = chunker.chunk_pages(all_pages)
    print(f"✓ Created {len(chunks)} chunks")

    if len(chunks) == 0:
        print("❌ No chunks created! PDF text extraction may have failed.")
        return

    # Embed chunks
    print(f"\n🧠 Embedding {len(chunks)} chunks...")
    embedder = Embedder()
    embeddings = embedder.embed_chunks(chunks)
    print(f"✓ Generated {len(embeddings)} embeddings (dim: 384)")

    # Index chunks
    print(f"\n💾 Indexing in Chroma...")
    # Delete old index first
    import shutil
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
    retriever = Retriever(persist_dir="./chroma_db")
    retriever.index_chunks(chunks, embeddings)
    print(f"✓ Indexed {len(chunks)} chunks")

    # Test retrieval
    print(f"\n🔍 Testing retrieval...")
    test_query = "What are the business segments?"
    query_embedding = embedder.embed_query(test_query)
    results = retriever.retrieve(query_embedding, top_k=3)

    print(f"\nRetrieval test for: '{test_query}'")
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n  [{i}] Score: {result['similarity_score']:.4f}")
        print(f"      Chunk: {result['chunk_id']}")
        print(f"      Text: {result['text'][:100]}...")

    print("\n" + "="*70)
    print("INDEX REBUILD COMPLETE")
    print("="*70)


if __name__ == "__main__":
    rebuild_index()
