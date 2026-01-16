# Gemini API Configuration

## Overview

The RAG system has been updated to use **Google Gemini API** instead of OpenAI.

## Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API Key"
3. Create new API key in Google Cloud project
4. Copy your API key

## Setup

### Option 1: Set Environment Variable (Recommended)

**Windows PowerShell:**
```powershell
$env:GOOGLE_API_KEY = "your-gemini-api-key-here"
```

**Permanent (Windows System):**
1. Right-click "This PC" → Properties
2. Advanced system settings → Environment variables
3. New system variable: `GOOGLE_API_KEY` = `your-key`
4. Restart terminal

### Option 2: Create .env File

Create `.env` file in project directory:
```
GOOGLE_API_KEY=your-gemini-api-key-here
```

## Running the System

### Single Document
```bash
python main.py ADANI.pdf
```

### Multiple Documents
```bash
python multi_document_qa.py
```

### With Tests
```bash
python main.py ADANI.pdf --test
```

## What Changed

**Before (OpenAI):**
- Used: `openai==1.3.0`
- Model: `gpt-3.5-turbo`
- API Key: `OPENAI_API_KEY`

**Now (Gemini):**
- Uses: `google-generativeai==0.3.0`
- Model: `gemini-pro`
- API Key: `GOOGLE_API_KEY`

## Key Features (Unchanged)

✅ Document grounding
✅ Citations ([p5:c2])
✅ Multi-turn conversations
✅ Retrieval visibility
✅ "Not found" handling
✅ Temperature = 0 (deterministic)

## Installation

Update dependencies:
```bash
pip install -r requirements.txt
```

This installs:
- google-generativeai (Gemini API)
- pdfplumber (PDF processing)
- chromadb (Vector DB)
- sentence-transformers (Embeddings)
- Other utilities

## Troubleshooting

### "GOOGLE_API_KEY not set"

**Solution:**
```powershell
$env:GOOGLE_API_KEY = "your-key-here"
python multi_document_qa.py
```

### API Rate Limits

Gemini API has free tier limits. If you hit limits:
- Wait a moment before next query
- Use slower query pace
- Check [Google AI pricing](https://ai.google.dev/pricing)

### Connection Issues

Ensure:
1. API key is correct
2. Internet connection is active
3. Google API is not blocked by firewall

## Gemini vs OpenAI

| Feature | Gemini | OpenAI |
|---------|--------|--------|
| Cost | Free tier available | Always costs $ |
| Models | gemini-pro, gemini-vision | gpt-3.5, gpt-4 |
| Speed | Fast | Fast |
| Quality | Good | Excellent |
| Setup | Simpler | Requires billing |

## Switching Back to OpenAI

If you want to switch back:

1. Update `requirements.txt`:
```
openai==1.3.0
```

2. Update `rag_system.py` (replace Gemini code with OpenAI code)

3. Set OpenAI key:
```powershell
$env:OPENAI_API_KEY = "sk-..."
```

## Example Run

```bash
$ python multi_document_qa.py

[RAG] Using Gemini API (gemini-pro) with temperature=0

[PDF] Loaded 31 pages from ADANI.pdf
[CHUNKING] Created 87 chunks
[RETRIEVER] Indexed 87 chunks in Chroma

You: What are the business segments?

[RETRIEVAL] Retrieved 5 chunks
...
Assistant: The company operates through four segments [p5:c1]...
```

## Resources

- [Google AI Studio](https://aistudio.google.com/app/apikey)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Gemini Pricing](https://ai.google.dev/pricing)

## Support

For issues:
1. Check `GOOGLE_API_KEY` is set
2. Verify API key works in [AI Studio](https://aistudio.google.com/)
3. Check internet connection
4. Review error message in terminal
