"""
Example usage and test cases for the RAG system
Run this to see the system in action
"""
import os
import sys

# Ensure API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set")
    print("Set it with: $env:OPENAI_API_KEY = 'sk-...'")
    sys.exit(1)

from main import DocumentQASystem


def example_usage():
    """Demonstrate the RAG system with example queries."""

    # Check if ADANI.pdf exists (sample document)
    pdf_path = "./ADANI.pdf"
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        print("Place a PDF in the current directory or provide path as argument")
        sys.exit(1)

    # Initialize system
    print("\nInitializing RAG system with", pdf_path)
    qa_system = DocumentQASystem(pdf_path, use_cached=True)

    # Example queries (non-interactive)
    queries = [
        "What are the main business segments?",
        "What is the total revenue?",
        "Summarize the key financial metrics",
    ]

    print("\n" + "="*80)
    print("EXAMPLE QUERIES")
    print("="*80)

    for i, query in enumerate(queries, 1):
        print(f"\n[Q{i}] {query}")
        answer = qa_system.answer_question(query, debug=False)
        print(f"[A{i}] {answer}\n")


if __name__ == "__main__":
    example_usage()
