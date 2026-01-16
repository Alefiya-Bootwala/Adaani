"""
PDF Loader Module
Extracts text from PDF page-by-page with metadata tracking
"""
import pdfplumber
from typing import List, Dict, Tuple


class PDFLoader:
    """Load and extract text from PDF documents."""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pages = []
        self.metadata = {}

    def load(self) -> List[Dict[str, any]]:
        """
        Load PDF and extract text page-by-page.

        Returns:
            List of dicts with 'page_num', 'text', 'metadata'
        """
        pages = []

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"[PDF] Loaded {total_pages} pages from {self.pdf_path}")

                for page_idx, page in enumerate(pdf.pages):
                    page_num = page_idx + 1  # 1-indexed
                    text = page.extract_text() or ""

                    # Try to extract tables
                    tables = page.extract_tables() or []
                    table_text = ""
                    if tables:
                        table_text = "\n".join([
                            "\n".join([
                                " | ".join([str(cell) for cell in row])
                                for row in table
                            ])
                            for table in tables
                        ])
                        text = text + "\n\n" + table_text if text else table_text

                    if text.strip():
                        pages.append({
                            "page_num": page_num,
                            "text": text,
                            "metadata": {
                                "page": page_num,
                                "source": self.pdf_path
                            }
                        })

                    if page_idx % 10 == 0:
                        print(
                            f"  Processed {page_idx + 1}/{total_pages} pages...")

        except Exception as e:
            raise RuntimeError(f"Failed to load PDF: {e}")

        self.pages = pages
        return pages

    def get_page_text(self, page_num: int) -> str:
        """Get text from a specific page."""
        for page in self.pages:
            if page["page_num"] == page_num:
                return page["text"]
        return ""

    def get_total_pages(self) -> int:
        """Get total number of pages."""
        return len(self.pages)
