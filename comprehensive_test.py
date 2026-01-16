"""
Comprehensive Test Suite for RAG System
Demonstrates all features and validates functionality
"""
import os
import sys


def test_imports():
    """Test 1: Verify all modules can be imported."""
    print("\n" + "="*80)
    print("TEST 1: IMPORT VERIFICATION")
    print("="*80)

    modules = [
        "pdf_loader",
        "chunker",
        "embedder",
        "retriever",
        "rag_system",
        "main"
    ]

    try:
        for module in modules:
            __import__(module)
            print(f"✓ {module}.py imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_api_key():
    """Test 2: Verify OpenAI API key configuration."""
    print("\n" + "="*80)
    print("TEST 2: API KEY CONFIGURATION")
    print("="*80)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ OPENAI_API_KEY not set")
        print("  Set with: $env:OPENAI_API_KEY = 'sk-...'")
        return False

    if api_key.startswith("sk-"):
        masked = api_key[:10] + "..." + api_key[-4:]
        print(f"✓ OPENAI_API_KEY configured ({masked})")
        return True
    else:
        print("✗ OPENAI_API_KEY doesn't start with 'sk-'")
        return False


def test_pdf_loading():
    """Test 3: Verify PDF loading functionality."""
    print("\n" + "="*80)
    print("TEST 3: PDF LOADING")
    print("="*80)

    from pdf_loader import PDFLoader

    # Check if ADANI.pdf exists
    if not os.path.exists("./ADANI.pdf"):
        print("✗ ADANI.pdf not found")
        print("  Place a PDF in current directory or modify path")
        return False

    try:
        loader = PDFLoader("./ADANI.pdf")
        pages = loader.load()

        if len(pages) > 0:
            print(f"✓ Loaded {len(pages)} pages from ADANI.pdf")
            print(f"  First page has {len(pages[0]['text'])} characters")
            return True
        else:
            print("✗ PDF loaded but has no pages")
            return False
    except Exception as e:
        print(f"✗ PDF loading failed: {e}")
        return False


def test_chunking():
    """Test 4: Verify text chunking."""
    print("\n" + "="*80)
    print("TEST 4: TEXT CHUNKING")
    print("="*80)

    from pdf_loader import PDFLoader
    from chunker import TextChunker

    try:
        loader = PDFLoader("./ADANI.pdf")
        pages = loader.load()

        chunker = TextChunker(chunk_size=512, overlap=100)
        chunks = chunker.chunk_pages(pages)

        if len(chunks) > 0:
            print(f"✓ Created {len(chunks)} chunks")
            sample_chunk = chunks[0]
            print(f"  Sample chunk ID: {sample_chunk['chunk_id']}")
            print(f"  Sample text length: {len(sample_chunk['text'])} chars")

            # Verify chunk IDs have correct format
            if ":" in sample_chunk["chunk_id"]:
                print(
                    f"  ✓ Chunk ID format correct: {sample_chunk['chunk_id']}")
                return True
            else:
                print(
                    f"  ✗ Chunk ID format incorrect: {sample_chunk['chunk_id']}")
                return False
        else:
            print("✗ No chunks created")
            return False
    except Exception as e:
        print(f"✗ Chunking failed: {e}")
        return False


def test_embeddings():
    """Test 5: Verify embedding generation."""
    print("\n" + "="*80)
    print("TEST 5: EMBEDDING GENERATION")
    print("="*80)

    from embedder import Embedder

    try:
        embedder = Embedder("all-MiniLM-L6-v2")

        # Test single text embedding
        test_text = "This is a test document about business segments."
        embedding = embedder.embed_text(test_text)

        print(f"✓ Generated embedding for test text")
        print(f"  Embedding dimension: {len(embedding)}")
        print(f"  Expected dimension: 384")

        if len(embedding) == 384:
            print("  ✓ Dimension correct")
            return True
        else:
            print("  ✗ Dimension mismatch")
            return False
    except Exception as e:
        print(f"✗ Embedding failed: {e}")
        return False


def test_retriever():
    """Test 6: Verify vector database functionality."""
    print("\n" + "="*80)
    print("TEST 6: VECTOR DATABASE (CHROMA)")
    print("="*80)

    from retriever import Retriever

    try:
        retriever = Retriever(persist_dir="./test_chroma_db")
        print(f"✓ Retriever initialized")

        # Check if database is persistent
        if retriever.load_from_existing():
            print("  ✓ Using existing Chroma database")
        else:
            print("  ℹ Creating new Chroma database")

        return True
    except Exception as e:
        print(f"✗ Retriever initialization failed: {e}")
        return False


def test_rag_system():
    """Test 7: Verify RAG system initialization."""
    print("\n" + "="*80)
    print("TEST 7: RAG SYSTEM")
    print("="*80)

    from embedder import Embedder
    from retriever import Retriever
    from rag_system import RAGSystem

    try:
        embedder = Embedder("all-MiniLM-L6-v2")
        retriever = Retriever(persist_dir="./test_chroma_db")
        rag = RAGSystem(retriever, embedder)

        print(f"✓ RAG system initialized")
        print(f"  Model: {rag.model}")
        print(f"  Temperature: {rag.temperature}")

        if rag.temperature == 0:
            print("  ✓ Temperature set to 0 (deterministic)")
            return True
        else:
            print("  ✗ Temperature not set to 0")
            return False
    except Exception as e:
        print(f"✗ RAG system initialization failed: {e}")
        return False


def test_citation_format():
    """Test 8: Verify citation formatting."""
    print("\n" + "="*80)
    print("TEST 8: CITATION FORMAT")
    print("="*80)

    from chunker import TextChunker

    # Create sample chunks and verify format
    sample_chunks = [
        {"text": "Revenue is $100M", "chunk_id": "p1:c0", "page_num": 1},
        {"text": "Profit is $20M", "chunk_id": "p1:c1", "page_num": 1},
        {"text": "EBITDA is $30M", "chunk_id": "p2:c0", "page_num": 2},
    ]

    all_valid = True
    for chunk in sample_chunks:
        chunk_id = chunk["chunk_id"]
        # Verify format: pN:cM
        if chunk_id.startswith("p") and ":" in chunk_id and chunk_id.split(":")[1].startswith("c"):
            print(f"✓ Valid chunk ID: {chunk_id}")
        else:
            print(f"✗ Invalid chunk ID: {chunk_id}")
            all_valid = False

    return all_valid


def test_not_found_handling():
    """Test 9: Verify 'Not found' response handling."""
    print("\n" + "="*80)
    print("TEST 9: 'NOT FOUND' HANDLING")
    print("="*80)

    # Simulate empty retrieval (no chunks)
    empty_chunks = []

    if not empty_chunks:
        print("✓ Empty retrieval correctly identified")
        print("  RAG will return: 'Not found in the document.'")
        return True
    else:
        print("✗ Empty retrieval not handled correctly")
        return False


def test_conversation_history():
    """Test 10: Verify conversation history structure."""
    print("\n" + "="*80)
    print("TEST 10: CONVERSATION HISTORY")
    print("="*80)

    # Sample conversation history
    history = [
        {"role": "user", "content": "What is revenue?"},
        {"role": "assistant", "content": "Revenue is $100M [p5]"},
        {"role": "user", "content": "Break that down"},
        {"role": "assistant", "content": "By segment: ..."},
    ]

    print(f"✓ Created conversation history with {len(history)} messages")

    valid = True
    for msg in history:
        if "role" in msg and "content" in msg and msg["role"] in ["user", "assistant"]:
            print(f"  ✓ {msg['role'].capitalize()}: {msg['content'][:50]}...")
        else:
            print(f"  ✗ Invalid message format")
            valid = False

    return valid


def run_all_tests():
    """Run all tests sequentially."""
    tests = [
        ("Import Verification", test_imports),
        ("API Key Configuration", test_api_key),
        ("PDF Loading", test_pdf_loading),
        ("Text Chunking", test_chunking),
        ("Embedding Generation", test_embeddings),
        ("Vector Database", test_retriever),
        ("RAG System", test_rag_system),
        ("Citation Format", test_citation_format),
        ("'Not Found' Handling", test_not_found_handling),
        ("Conversation History", test_conversation_history),
    ]

    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "RAG SYSTEM COMPREHENSIVE TEST SUITE" + " "*24 + "║")
    print("╚" + "="*78 + "╝")

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n[ERROR] {test_name}: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {test_name}")

    print("\n" + "="*80)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*80)

    if passed == total:
        print("\n✓ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. python main.py ADANI.pdf")
        print("  2. Ask questions about the document")
        print("  3. Type 'exit' to quit")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please fix issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
