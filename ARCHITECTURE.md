# RAG System Architecture & Technical Specification

## Overview

This is a production-grade Retrieval-Augmented Generation (RAG) system designed for document-grounded question answering. It enforces strict grounding in PDF content with zero external knowledge injection.

## Core Components

### 1. PDF Loader (`pdf_loader.py`)
**Responsibility:** Extract text from PDF with page-level metadata

```
PDF File → pdfplumber → Text Extraction (per page)
           + Table Detection
           + Metadata Tagging
           
Output: List[Dict] with:
  - page_num: int (1-indexed)
  - text: str (full page text + tables)
  - metadata: {page, source}
```

**Key Features:**
- Page-by-page extraction (preserves document structure)
- Table-aware extraction (tables converted to delimited text)
- Progress tracking
- Error handling

**API:**
```python
loader = PDFLoader("doc.pdf")
pages = loader.load()  # Returns list of page dicts
text = loader.get_page_text(3)  # Get text from page 3
```

---

### 2. Text Chunker (`chunker.py`)
**Responsibility:** Intelligently chunk text with overlap and metadata

```
Pages → Sentence Splitting → Chunk Grouping (512 chars default)
        ↓
        Overlap Management (100 chars default)
        ↓
        Metadata Tagging (p{page}:c{index})
        
Output: List[Dict] with:
  - text: str (chunk text)
  - chunk_id: str (e.g., "p5:c2")
  - page_num: int
  - metadata: {page, chunk_id, source}
```

**Key Features:**
- Sentence-level chunking (semantically meaningful)
- Configurable chunk size & overlap
- Unique chunk IDs for citation tracking
- No random window splitting

**Chunking Strategy:**
```
Page: "Sentence 1. Sentence 2. Sentence 3. Sentence 4."
Chunk 1: [Sentence 1. Sentence 2.]
Chunk 2: [Sentence 2. Sentence 3. Sentence 4.]  ← Overlap
```

**API:**
```python
chunker = TextChunker(chunk_size=512, overlap=100)
chunks = chunker.chunk_pages(pages)
# chunks[0] = {
#   "text": "...",
#   "chunk_id": "p1:c0",
#   "page_num": 1,
#   "metadata": {...}
# }
```

---

### 3. Embedder (`embedder.py`)
**Responsibility:** Generate semantic embeddings for chunks

```
Chunks → Sentence-Transformers (all-MiniLM-L6-v2)
         ↓
         Vector Embeddings (384-dimensional)
         
Output: List[np.ndarray] (shape: [n_chunks, 384])
```

**Key Features:**
- Open-source embeddings (no API calls, fast)
- Efficient batch processing
- Semantic similarity capture
- Progress tracking

**Model Choice:**
- **Model:** `all-MiniLM-L6-v2` (384-dim)
- **Why:** Fast, lightweight, good quality, no API costs
- **Alternatives:** `all-mpnet-base-v2` (more accurate, slower)

**API:**
```python
embedder = Embedder("all-MiniLM-L6-v2")
embeddings = embedder.embed_chunks(chunks)  # List[np.ndarray]
query_embedding = embedder.embed_query("What is revenue?")
```

---

### 4. Retriever (`retriever.py`)
**Responsibility:** Store embeddings and retrieve relevant chunks

```
Embeddings + Chunks → Chroma Vector DB
                      ↓
                      Index with Metadata
                      ↓
                      Persistent Storage (chroma_db/)
                      
Query → Query Embedding → Similarity Search → Top-k Results
```

**Key Features:**
- Persistent vector database (Chroma)
- Cosine similarity search
- Similarity scoring (0-1)
- Metadata preservation
- Cache-aware (skips re-indexing)

**Chroma Benefits:**
- No external server needed
- Built-in similarity scoring
- Metadata filtering
- Local persistence

**API:**
```python
retriever = Retriever(persist_dir="./chroma_db")
retriever.index_chunks(chunks, embeddings)
retrieved = retriever.retrieve(query_embedding, top_k=5)
# Retrieved: List[Dict] with text, page, chunk_id, similarity_score
```

---

### 5. RAG System (`rag_system.py`)
**Responsibility:** Orchestrate retrieval + LLM + grounding

```
Query → Query Embedding → Retrieval (Top-5 chunks)
        ↓
        Build Context String [p5:c1] text... [p5:c2] text...
        ↓
        LLM Prompt (System: "Answer ONLY from context")
        ↓
        OpenAI gpt-3.5-turbo (temperature=0)
        ↓
        Post-Process Answer
        ↓
        Ensure Citations [p5] or [p5:c2]
        ↓
        Return: Answer + Retrieved Chunks
```

**Key Features:**
- Temperature = 0 (deterministic)
- Context-only prompting (no full doc)
- Conversation history support
- Citation enforcement
- "Not found" handling
- Retrieval visibility (debug output)

**System Prompt Design:**
```
CRITICAL: Answer ONLY using provided context.
If answer not in context → "Not found in the document."
ALWAYS include citations [pN:cM]
```

**LLM Flow:**
```
User Query
    ↓
Retrieve Top-5 chunks with similarity scores
    ↓
Build context: [p5:c1]\ntext...\n[p5:c2]\ntext...
    ↓
Messages = [
    {role: "assistant", content: "previous answer + citation"},
    {role: "user", content: "question\n\ncontext"}
]
    ↓
OpenAI.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0,
    max_tokens=1000
)
    ↓
Parse answer, ensure citations
    ↓
Return answer + chunks
```

**API:**
```python
rag = RAGSystem(retriever, embedder, api_key="sk-...")
answer, chunks = rag.answer_question(
    query="What is revenue?",
    conversation_history=[{role: "user", content: "..."}, ...],
    top_k=5,
    debug=True
)
```

---

### 6. Main CLI (`main.py`)
**Responsibility:** User interface and orchestration

```
CLI Input (PDF Path)
    ↓
DocumentQASystem.__init__()
    ├─ PDFLoader.load() → pages
    ├─ TextChunker.chunk_pages() → chunks
    ├─ Embedder.embed_chunks() → embeddings
    └─ Retriever.index_chunks() → indexed
    ↓
Interactive Chat Loop
    ├─ User Input
    ├─ answer_question() → RAGSystem.answer_question()
    ├─ Update conversation_history
    └─ Print Answer + Retrieved Chunks
    ↓
Commands: exit, clear
```

**Key Features:**
- Single-command initialization
- Persistent conversation history
- Fresh retrieval per question
- Cache management (--no-cache flag)
- Acceptance test runner (--test flag)

**CLI Commands:**
```bash
# Interactive mode
python main.py doc.pdf

# With tests
python main.py doc.pdf --test

# Rebuild index
python main.py doc.pdf --no-cache
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ USER QUESTION                                               │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
    ┌─────────────────┐          ┌──────────────────┐
    │ Embedder        │          │ RAGSystem.       │
    │ embed_query()   │          │ format_history() │
    │                 │          │                  │
    │ Query Embedding │          │ Conversation     │
    │ (384-dim)       │          │ History (msgs)   │
    └────────┬────────┘          └────────┬─────────┘
             │                           │
             └───────────────┬───────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │ Retriever.retrieve()│
                    │                     │
                    │ Chroma Index        │
                    │ Top-5 by Similarity │
                    └────────┬────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
         Top-5 Chunks (text, page, score)│
                │                         │
                └────────────┬────────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │ RAGSystem.           │
                    │ _build_context()     │
                    │                      │
                    │ [p5:c1]              │
                    │ text...              │
                    │ [p5:c2]              │
                    │ text...              │
                    └────────┬─────────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
            ▼                                 ▼
    ┌──────────────────┐          ┌──────────────────────┐
    │ System Prompt    │          │ Messages Array       │
    │ "Answer ONLY     │          │ [history + query]    │
    │  from context"   │          │                      │
    └────────┬─────────┘          └────────┬─────────────┘
             │                             │
             └──────────────┬──────────────┘
                            │
                            ▼
                   ┌─────────────────────┐
                   │ OpenAI LLM Call     │
                   │ gpt-3.5-turbo       │
                   │ temperature=0       │
                   │ max_tokens=1000     │
                   └────────┬────────────┘
                            │
                            ▼
                   ┌─────────────────────┐
                   │ LLM Response        │
                   │ Raw Answer Text     │
                   └────────┬────────────┘
                            │
                            ▼
                   ┌─────────────────────┐
                   │ Post-Process        │
                   │ - Add citations     │
                   │ - Check for "Not    │
                   │   found"            │
                   │ - Format output     │
                   └────────┬────────────┘
                            │
                            ▼
    ┌─────────────────────────────────────┐
    │ FINAL OUTPUT                        │
    │ Answer with Citations [p5:c1]       │
    │ + Retrieved Chunks (debug view)     │
    └─────────────────────────────────────┘
```

---

## Data Structures

### Chunk Format
```python
{
    "text": "Full chunk text...",
    "chunk_id": "p5:c2",           # page 5, chunk 2
    "page_num": 5,
    "chunk_index": 2,
    "metadata": {
        "page": 5,
        "chunk_id": "p5:c2",
        "source": "page_5"
    }
}
```

### Retrieved Chunk Format
```python
{
    "chunk_id": "p5:c2",
    "text": "Full chunk text...",
    "page": 5,
    "metadata": {...},
    "similarity_score": 0.8765
}
```

### Conversation History
```python
[
    {"role": "user", "content": "What is revenue?"},
    {"role": "assistant", "content": "Revenue is... [p5:c1]"},
    {"role": "user", "content": "Break that down"},
    {"role": "assistant", "content": "Breakdown: ... [p6:c0]"},
]
```

---

## Key Design Decisions

### 1. Temperature = 0
- Ensures deterministic outputs
- Prevents hallucinated facts
- Suitable for factual Q&A

### 2. Context-Only Prompting
- LLM sees ONLY retrieved chunks (no full document)
- Reduces hallucination
- Efficient token usage
- Makes answers traceable

### 3. Sentence-Level Chunking
- Semantically meaningful units
- Better overlap handling
- Preserves sentence boundaries
- Easier to cite

### 4. Metadata on Every Chunk
- Enables citations
- Supports multi-document scenarios
- Tracking for debugging

### 5. Conversation History in Prompt
- Supports follow-up questions
- No separate context injection
- Limited to recent history (prevent context bloat)

### 6. Two-Step Citation Process
1. LLM includes citations in answer
2. Post-process ensures format: `[pN]` or `[pN:cM]`

---

## Acceptance Test Mapping

| Test | Query | Expected | Implementation |
|------|-------|----------|-----------------|
| 1 - Segments | "Major business segments?" | Segment names + [citations] | Retrieval + RAG |
| 2 - Numeric | "Consolidated income H1-26?" | Number + [page] or "Not found" | Retrieval + citation |
| 3 - Drivers | "EBITDA drivers H1-26?" | Factors + [citations] | RAG grounding |
| 4 - Negative | "CEO's email?" | "Not found in the document." | LLM refusal |
| 5 - Follow-up | Q1: "Summarize airports" + Q2: "Break down" | Uses history, stays grounded | Conversation + retrieval |

---

## Configuration Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `chunk_size` | 512 | Chunk size in characters |
| `overlap` | 100 | Overlap between chunks |
| `top_k` | 5 | Number of chunks to retrieve |
| `temperature` | 0 | LLM determinism |
| `max_tokens` | 1000 | LLM response limit |
| `model` | gpt-3.5-turbo | LLM choice |
| `embedding_dim` | 384 | Embedding dimension |

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| PDF Load (20 pages) | ~1 sec | Depends on file size |
| Chunking (500 chunks) | ~0.5 sec | Sentence splitting |
| Embedding Gen (500 chunks) | ~5 min | Batch inference, one-time |
| Index Creation | ~1 sec | Chroma insertion |
| Query Embedding | ~0.5 sec | Single query |
| Retrieval | ~0.2 sec | Cosine similarity |
| LLM Call | ~2-3 sec | OpenAI API latency |
| **Total Per Question** | **~3 sec** | Cached index |

---

## Error Handling

```
PDF Load Errors → FileNotFoundError, RuntimeError
Chunking Errors → ValueError (empty chunks)
Embedding Errors → OutOfMemory, API errors
Retrieval Errors → RuntimeError (no index)
LLM Errors → OpenAI API errors, timeout
API Key Missing → ValueError at init
```

---

## Future Extensions

1. **Hybrid Retrieval:** BM25 (keyword) + vector (semantic)
2. **Per-Sentence Citations:** Granular citation tracking
3. **Confidence Scoring:** Filter low-relevance results
4. **Query Expansion:** Rephrase queries for better retrieval
5. **Multi-Document:** Index multiple PDFs simultaneously
6. **Streaming LLM:** Real-time token generation
7. **Fine-tuned Embeddings:** Domain-specific models
8. **Long Context:** GPT-4 Turbo for larger documents
