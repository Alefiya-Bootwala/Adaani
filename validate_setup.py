"""
Setup Validation Script
Checks all dependencies and configuration before running the main system
"""
import sys
import os


def check_dependencies():
    """Check if all required packages are installed."""
    dependencies = [
        ("openai", "OpenAI API"),
        ("pdfplumber", "PDF Processing"),
        ("chromadb", "Vector Database"),
        ("sentence_transformers", "Embeddings"),
        ("numpy", "Numerical Computing"),
        ("click", "CLI Framework"),
    ]

    print("Checking dependencies...")
    all_ok = True

    for package, description in dependencies:
        try:
            __import__(package)
            print(f"  ✓ {description} ({package})")
        except ImportError:
            print(f"  ✗ {description} ({package}) - NOT INSTALLED")
            all_ok = False

    return all_ok


def check_api_key():
    """Check if OpenAI API key is set."""
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        # Show first 10 chars and last 4 for verification
        masked = api_key[:10] + "..." + \
            api_key[-4:] if len(api_key) > 14 else "***"
        print(f"  ✓ OPENAI_API_KEY is set ({masked})")
        return True
    else:
        print("  ✗ OPENAI_API_KEY is not set")
        return False


def check_files():
    """Check if all required source files exist."""
    files = [
        "main.py",
        "pdf_loader.py",
        "chunker.py",
        "embedder.py",
        "retriever.py",
        "rag_system.py",
        "requirements.txt",
        "README.md"
    ]

    print("\nChecking source files...")
    all_ok = True

    for filename in files:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} - NOT FOUND")
            all_ok = False

    return all_ok


def main():
    """Run all checks."""
    print("="*60)
    print("RAG SYSTEM SETUP VALIDATION")
    print("="*60)
    print()

    checks = [
        ("Dependencies", check_dependencies),
        ("API Configuration", check_api_key),
        ("Source Files", check_files),
    ]

    results = {}
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        results[check_name] = check_func()

    print("\n" + "="*60)

    if all(results.values()):
        print("✓ ALL CHECKS PASSED - System ready!")
        print("\nNext steps:")
        print("  1. Download a PDF (e.g., earnings report)")
        print("  2. Run: python main.py <pdf_path>")
        print("="*60)
        return 0
    else:
        print("✗ SOME CHECKS FAILED - Please fix the issues above")
        print("\nTo install dependencies:")
        print("  pip install -r requirements.txt")
        print("\nTo set API key (PowerShell):")
        print('  $env:OPENAI_API_KEY = "sk-..."')
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
