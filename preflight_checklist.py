#!/usr/bin/env python
"""
Pre-Flight Checklist
Verify all components before running the system
"""
import os
import sys


def check_all():
    """Run all pre-flight checks."""

    print("="*80)
    print("RAG SYSTEM PRE-FLIGHT CHECKLIST")
    print("="*80)

    checks = {
        "Dependencies": check_dependencies,
        "Source Files": check_source_files,
        "Documentation": check_documentation,
        "Configuration": check_configuration,
        "Sample Data": check_sample_data,
    }

    results = {}
    for section, check_func in checks.items():
        print(f"\n{section}:")
        print("-" * 80)
        try:
            result = check_func()
            results[section] = result
        except Exception as e:
            print(f"ERROR: {e}")
            results[section] = False

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for section, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {section}")

    print("\n" + "="*80)
    if passed == total:
        print(f"✓ ALL CHECKS PASSED ({total}/{total})")
        print("\nNext steps:")
        print("  1. Set OPENAI_API_KEY: $env:OPENAI_API_KEY = 'sk-...'")
        print("  2. Run: python main.py ADANI.pdf")
        print("  3. Ask questions about the document")
        print("="*80)
        return 0
    else:
        print(f"✗ SOME CHECKS FAILED ({passed}/{total})")
        print("\nPlease fix the issues above before running the system")
        print("="*80)
        return 1


def check_dependencies():
    """Check if required packages are installed."""
    packages = [
        "openai",
        "pdfplumber",
        "chromadb",
        "sentence_transformers",
        "numpy",
        "click",
    ]

    all_ok = True
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"  ✓ {pkg}")
        except ImportError:
            print(f"  ✗ {pkg} - Install: pip install -r requirements.txt")
            all_ok = False

    return all_ok


def check_source_files():
    """Check if all source files exist."""
    files = [
        "main.py",
        "pdf_loader.py",
        "chunker.py",
        "embedder.py",
        "retriever.py",
        "rag_system.py",
        "requirements.txt",
    ]

    all_ok = True
    for file in files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - NOT FOUND")
            all_ok = False

    return all_ok


def check_documentation():
    """Check if documentation files exist."""
    docs = [
        "README.md",
        "QUICKSTART.md",
        "ARCHITECTURE.md",
        "DEPLOYMENT.md",
        "INDEX.md",
    ]

    all_ok = True
    for doc in docs:
        if os.path.exists(doc):
            print(f"  ✓ {doc}")
        else:
            print(f"  ✗ {doc} - NOT FOUND")
            all_ok = False

    return all_ok


def check_configuration():
    """Check if API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key and api_key.startswith("sk-"):
        masked = api_key[:10] + "..." + api_key[-4:]
        print(f"  ✓ OPENAI_API_KEY configured ({masked})")
        return True
    else:
        print(f"  ✗ OPENAI_API_KEY not set or invalid")
        print(f"     Set with: $env:OPENAI_API_KEY = 'sk-...'")
        return False


def check_sample_data():
    """Check if sample PDF exists."""
    if os.path.exists("ADANI.pdf"):
        size_mb = os.path.getsize("ADANI.pdf") / (1024 * 1024)
        print(f"  ✓ ADANI.pdf ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ✗ ADANI.pdf not found")
        print(f"     Download: python download_sample_pdf.py")
        return False


if __name__ == "__main__":
    sys.exit(check_all())
