# Getting Started with RAG System

## What You Have

A production-ready **Retrieval-Augmented Generation (RAG)** system for document-grounded Q&A.

**Key Features:**
- ✅ Answers questions from PDF documents
- ✅ Cites every fact ([p5:c2] format)
- ✅ Multi-turn conversation support
- ✅ Shows what it retrieved
- ✅ Refuses external knowledge
- ✅ All 5 acceptance tests implemented

---

## 3-Step Quick Start

### 1️⃣ Install (2 minutes)
```bash
cd c:\Users\Dell\Desktop\Int
pip install -r requirements.txt
```

### 2️⃣ Configure API Key
```powershell
$env:OPENAI_API_KEY = "sk-your-api-key-here"
```

Get key: https://platform.openai.com/api-keys

### 3️⃣ Run
```bash
python main.py ADANI.pdf
```

**First run:** ~5-10 minutes (generates embeddings)
**Subsequent runs:** ~10 seconds (uses cache)

---

## What Happens on First Run

```
1. Load PDF from ADANI.pdf
2. Extract text (page-by-page)
3. Split into chunks (512 chars, 100 char overlap)
4. Generate embeddings (384-dim)
5. Build Chroma index
6. Ready for questions!
```

---

## Using the System

### Ask Questions
```
You: What are the major business segments?

[RETRIEVAL] Retrieved 5 chunks
1. Chunk p5:c1 | Score: 0.852 | Text: "The company operates through..."