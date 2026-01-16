#!/usr/bin/env python
"""
Download the sample PDF for testing
"""
import os
import urllib.request
import sys


def download_pdf(url, output_path="doc.pdf"):
    """Download PDF from URL."""
    print(f"Downloading PDF from:\n{url}\n")

    try:
        print(f"Saving to: {output_path}")
        urllib.request.urlretrieve(url, output_path)
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✓ Downloaded successfully ({file_size:.1f} MB)")
        return True
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return False


if __name__ == "__main__":
    # Adani Enterprises Earnings Report Q2-FY26
    url = "https://www.adanienterprises.com/-/media/Project/Enterprises/Investors/Investor-Downloads/Results-Presentations/AEL_Earnings_Presentation_Q2-FY26.pdf"

    output = "doc.pdf"
    if len(sys.argv) > 1:
        output = sys.argv[1]

    if download_pdf(url, output):
        print(f"\nNext: python main.py {output}")
        sys.exit(0)
    else:
        print("\nManually download the PDF from the link above")
        sys.exit(1)
