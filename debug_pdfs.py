#!/usr/bin/env python3
"""Debug script to check PDF content"""

import pdfplumber
import os

pdfs = ["SAMPLE1.pdf", "SAMPLE2.pdf", "ADANI.pdf"]

for pdf_name in pdfs:
    if not os.path.exists(pdf_name):
        print(f"❌ {pdf_name} NOT FOUND")
        continue

    print(f"\n{'='*60}")
    print(f"📄 {pdf_name}")
    print(f"{'='*60}")

    try:
        with pdfplumber.open(pdf_name) as pdf:
            print(f"Pages: {len(pdf.pages)}")

            if len(pdf.pages) > 0:
                text = pdf.pages[0].extract_text()
                if text:
                    print(f"First 300 chars:\n{text[:300]}")
                else:
                    print("⚠️ First page has NO TEXT (might be image-based)")
            else:
                print("❌ PDF has no pages")
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n{'='*60}")
print("Summary: Check if PDFs have extractable text content")
print(f"{'='*60}")
