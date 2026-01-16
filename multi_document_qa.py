"""
Multi-Document RAG System
Index and query across multiple PDFs (SAMPLE1, SAMPLE2, ADANI)
"""
import os
import sys
from main import DocumentQASystem


def run_multi_document_system():
    """Run RAG system with multiple documents."""

    pdfs = [
        "./SAMPLE1.pdf",
        "./SAMPLE2.pdf",
        "./ADANI.pdf"
    ]

    # Filter to existing PDFs
    existing_pdfs = [p for p in pdfs if os.path.exists(p)]

    if not existing_pdfs:
        print("❌ No PDF files found (SAMPLE1.pdf, SAMPLE2.pdf, ADANI.pdf)")
        sys.exit(1)

    print(f"\n{'='*80}")
    print("MULTI-DOCUMENT RAG SYSTEM")
    print(f"{'='*80}\n")

    print(f"📄 Found {len(existing_pdfs)} document(s):")
    for pdf in existing_pdfs:
        print(f"   ✓ {pdf}")

    # Initialize with first PDF
    print(f"\n[INIT] Initializing with {existing_pdfs[0]}...")
    qa_system = DocumentQASystem(existing_pdfs[0], use_cached=False)

    # Add remaining PDFs
    for pdf in existing_pdfs[1:]:
        qa_system.add_document(pdf)

    # Run interactive mode
    print(f"\n{'='*80}")
    print("MULTI-DOCUMENT SYSTEM READY")
    print(f"{'='*80}")
    print(f"\n📚 Indexed {len(existing_pdfs)} documents")
    print("Questions will search across ALL documents")
    print("\nCommands: 'exit' to quit, 'clear' to reset conversation\n")

    qa_system.run_interactive()


if __name__ == "__main__":
    run_multi_document_system()
