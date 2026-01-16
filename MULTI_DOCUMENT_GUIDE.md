# Multi-Document RAG System

## Overview

The RAG system now supports indexing and querying across **multiple PDFs simultaneously**.

**You have 3 sample documents:**
- SAMPLE1.pdf
- SAMPLE2.pdf  
- ADANI.pdf

## Running Multi-Document Mode

**Option 1: Use --multiple flag**
```bash
python main.py SAMPLE1.pdf --multiple
```

**Option 2: Use dedicated script (recommended)**
```bash
python multi_document_qa.py
```

## How It Works

**All 3 PDFs are indexed together in one unified Chroma database.**

When you query:
1. Your question is embedded
2. Top-5 chunks retrieved from ANY/ALL documents
3. LLM sees chunks with their source marked
4. Answer includes citations showing which PDF each fact came from

## Features

✅ Unified index across all documents
✅ Cross-document semantic search
✅ Document tracking in citations
✅ Multi-turn conversations
✅ Easy to add more PDFs

## Example

```
You: What are the main business segments?

[RETRIEVAL] Retrieved 5 chunks:
1. [SAMPLE1.pdf p5:c1] Score: 0.87
   Text: "Segments include..."

2. [SAMPLE2.pdf p3:c2] Score: 0.84
   Text: "Categories are..."

3. [ADANI.pdf p8:c0] Score: 0.79
   Text: "Business divisions..."
```

## Adding More Documents

Edit multi_document_qa.py to add more PDFs:

```python
pdfs = [
    "./SAMPLE1.pdf",
    "./SAMPLE2.pdf",
    "./ADANI.pdf",
    "./YOUR_PDF.pdf"  # Add here
]
```

## Rebuilding Index

```bash
python main.py SAMPLE1.pdf --multiple --no-cache
```

This rebuilds the entire index from scratch.
