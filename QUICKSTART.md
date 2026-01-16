# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set OpenAI API Key

Get your API key from: https://platform.openai.com/api-keys

**PowerShell:**
```powershell
$env:OPENAI_API_KEY = "sk-your-api-key-here"
```

## 3. Prepare PDF

Download or prepare any PDF document (earnings report, contract, etc.)

## 4. Run

```bash
python main.py ./doc.pdf
```

### Run Tests
```bash
python main.py ./doc.pdf --test
```

### Rebuild Index
```bash
python main.py ./doc.pdf --no-cache
```

## Commands in Chat

- Ask any question
- `exit` - Quit
- `clear` - Reset conversation

## Example

```
$ python main.py earnings.pdf

[PDF] Loaded 31 pages...
[CHUNKING] Created 87 chunks...
[EMBEDDER] Loading model...
[RETRIEVER] Indexed 87 chunks...

================================================================================
DOCUMENT QA SYSTEM READY
================================================================================

You: What are the revenue segments?

[RETRIEVAL] Query: What are the revenue segments?
[RETRIEVAL] Retrieved 5 chunks
...