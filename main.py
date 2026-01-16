"""
Main CLI Application
Interactive RAG-based document QA system
"""
import os
import sys
import click
from pathlib import Path
from pdf_loader import PDFLoader
from chunker import TextChunker
from embedder import Embedder
from retriever import Retriever
from rag_system import RAGSystem


class DocumentQASystem:
    """End-to-end document QA system."""

    def __init__(self, pdf_path: str, use_cached: bool = True):
        """
        Initialize the QA system.

        Args:
            pdf_path: Path to PDF file
            use_cached: Use cached embeddings if available
        """
        self.pdf_path = pdf_path
        self.use_cached = use_cached
        self.documents = {}  # Store multiple documents

        # Validate PDF exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        print(f"\n{'='*80}")
        print("RAG DOCUMENT QA SYSTEM INITIALIZATION")
        print(f"{'='*80}\n")

        # Initialize components
        self.loader = PDFLoader(pdf_path)
        self.chunker = TextChunker(chunk_size=512, overlap=100)
        self.embedder = Embedder(model_name="all-MiniLM-L6-v2")
        self.retriever = Retriever(persist_dir="./chroma_db")

        # Load and index
        self._setup()

        # Initialize RAG
        try:
            self.rag = RAGSystem(self.retriever, self.embedder)
        except ValueError as e:
            print(f"\n[ERROR] {e}")
            print("Please set OPENAI_API_KEY environment variable")
            sys.exit(1)

        self.conversation_history = []
        self.documents[pdf_path] = {"pages": self.loader.pages}

    def add_document(self, pdf_path: str) -> None:
        """Add another document to the index."""
        if not os.path.exists(pdf_path):
            print(f"[WARNING] PDF not found: {pdf_path}")
            return

        print(f"\n[ADDING] Document: {pdf_path}")
        loader = PDFLoader(pdf_path)
        pages = loader.load()
        chunks = self.chunker.chunk_pages(pages)
        embeddings = self.embedder.embed_chunks(chunks)
        self.retriever.index_chunks(chunks, embeddings)
        self.documents[pdf_path] = {"pages": pages}
        print(f"[ADDED] {len(chunks)} chunks from {pdf_path}")

    def _setup(self) -> None:
        """Load PDF, chunk, embed, and index."""
        # Check if cached index exists
        if self.use_cached and self.retriever.load_from_existing():
            print("[SETUP] Using cached index from ./chroma_db")
            return

        print("[SETUP] Building index from PDF...")

        # Load PDF
        pages = self.loader.load()

        # Chunk
        chunks = self.chunker.chunk_pages(pages)

        # Embed
        embeddings = self.embedder.embed_chunks(chunks)

        # Index
        self.retriever.index_chunks(chunks, embeddings)
        self.retriever.save()

        print("\n[SETUP] Index built successfully!\n")

    def answer_question(self, query: str, debug: bool = True) -> str:
        """
        Answer a question with citations.

        Args:
            query: User question
            debug: Print retrieval info

        Returns:
            Answer with citations
        """
        # Get answer from RAG
        answer, retrieved_chunks = self.rag.answer_question(
            query=query,
            conversation_history=self.conversation_history,
            top_k=5,
            debug=debug
        )

        # Update conversation history
        self.conversation_history.append({
            "role": "user",
            "content": query
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    def run_interactive(self) -> None:
        """Run interactive chat loop."""
        print(f"\n{'='*80}")
        print("DOCUMENT QA SYSTEM READY")
        print(f"{'='*80}")
        print("\nAsk questions about the document.")
        print("Commands: 'exit' to quit, 'clear' to reset conversation\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "exit":
                    print("\nGoodbye!")
                    break

                if user_input.lower() == "clear":
                    self.conversation_history = []
                    print("[INFO] Conversation history cleared.\n")
                    continue

                # Answer question
                answer = self.answer_question(user_input, debug=True)
                print(f"\nAssistant: {answer}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}\n")


@click.command()
@click.argument("pdf_path", type=click.Path(exists=False))
@click.option("--no-cache", is_flag=True, help="Rebuild index from scratch")
@click.option("--test", is_flag=True, help="Run acceptance tests")
@click.option("--multiple", is_flag=True, help="Index multiple PDFs (SAMPLE1.pdf, SAMPLE2.pdf, ADANI.pdf)")
def main(pdf_path: str, no_cache: bool, test: bool, multiple: bool):
    """
    RAG-based Document QA System

    PDF_PATH: Path to PDF file to analyze
    """
    try:
        # Handle multiple PDFs
        if multiple:
            pdf_paths = ["./SAMPLE1.pdf", "./SAMPLE2.pdf", "./ADANI.pdf"]
            qa_system = DocumentQASystem(pdf_paths[0], use_cached=not no_cache)
            for pdf_path in pdf_paths[1:]:
                if os.path.exists(pdf_path):
                    qa_system.add_document(pdf_path)
        else:
            # Initialize system with single PDF
            qa_system = DocumentQASystem(pdf_path, use_cached=not no_cache)

        if test:
            # Run acceptance tests
            run_acceptance_tests(qa_system)
        else:
            # Run interactive mode
            qa_system.run_interactive()

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)


def run_acceptance_tests(qa_system: DocumentQASystem) -> None:
    """Run the 5 acceptance tests."""
    print(f"\n{'='*80}")
    print("RUNNING ACCEPTANCE TESTS")
    print(f"{'='*80}\n")

    tests = [
        {
            "name": "Test 1: Business Segments",
            "query": "What are the major business segments discussed in the document?"
        },
        {
            "name": "Test 2: Consolidated Total Income",
            "query": "What is the consolidated total income in H1-26?"
        },
        {
            "name": "Test 3: EBITDA Drivers",
            "query": "What drivers are mentioned for EBITDA changes in H1-26?"
        },
        {
            "name": "Test 4: Negative Control",
            "query": "What is the CEO's email address?"
        },
        {
            "name": "Test 5: Multi-turn (Part 1)",
            "query": "Summarize airport performance in H1-26."
        }
    ]

    results = []

    for i, test in enumerate(tests, 1):
        print(f"\n{test['name']}")
        print("-" * 80)
        print(f"Q: {test['query']}\n")

        answer = qa_system.answer_question(test['query'], debug=False)
        print(f"A: {answer}\n")

        results.append({
            "test": test['name'],
            "query": test['query'],
            "answer": answer
        })

    # Test 5 Part 2: Follow-up
    print("\nTest 5: Multi-turn (Part 2)")
    print("-" * 80)
    follow_up = "Break that down into passenger and cargo changes."
    print(f"Q: {follow_up}\n")
    answer = qa_system.answer_question(follow_up, debug=False)
    print(f"A: {answer}\n")

    print(f"\n{'='*80}")
    print("TESTS COMPLETED")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
