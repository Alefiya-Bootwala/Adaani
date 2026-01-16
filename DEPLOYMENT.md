# Deployment & Production Guide

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] OpenAI API account with valid key
- [ ] PDF document ready (any format supported by pdfplumber)
- [ ] 2GB free disk space (for embeddings + index)
- [ ] Internet connection (for first LLM call)

## Installation Steps

### Step 1: Install Dependencies

```bash
cd c:\Users\Dell\Desktop\Int
pip install -r requirements.txt
```

**Verification:**
```bash
python validate_setup.py
```

Expected output:
```
✓ Checking dependencies...
  ✓ OpenAI API (openai)
  ✓ PDF Processing (pdfplumber)
  ✓ Vector Database (chromadb)
  ✓ Embeddings (sentence_transformers)
  ✓ Numerical Computing (numpy)
  ✓ CLI Framework (click)

✓ API Configuration
  ✓ OPENAI_API_KEY is set (sk-...abc)

✓ Source Files
  ✓ main.py
  ✓ pdf_loader.py
  ✓ chunker.py
  ✓ embedder.py
  ✓ retriever.py
  ✓ rag_system.py
  ✓ requirements.txt
  ✓ README.md

✓ ALL CHECKS PASSED - System ready!
```

### Step 2: Configure OpenAI API Key

**Option A: Temporary (for current session)**
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
```

**Option B: Permanent (Windows system-wide)**
1. Press `Win + X` → "System"
2. Click "Advanced system settings"
3. Click "Environment variables" button
4. Click "New" under System variables
5. Variable name: `OPENAI_API_KEY`
6. Variable value: `sk-...`
7. Click OK and restart terminal

**Option C: .env file (development)**
Create `.env` file in project directory:
```
OPENAI_API_KEY=sk-your-key-here
```

Then load it:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Step 3: Prepare PDF

Place your PDF in the project directory or use full path:
```bash
# Option 1: Copy PDF to project
Copy-Item "C:\Downloads\earnings_report.pdf" -Destination "c:\Users\Dell\Desktop\Int\doc.pdf"

# Option 2: Use full path
python main.py "C:\Full\Path\To\document.pdf"

# Option 3: Download sample (Adani Enterprises)
python download_sample_pdf.py doc.pdf
```

## Running the System

### Basic Interactive Mode

```bash
python main.py doc.pdf
```

**First run:**
- Loads PDF (~1-5 sec, depends on size)
- Chunks text
- Generates embeddings (~5 min for ~500 chunks)
- Creates index
- Ready for questions

**Subsequent runs:**
- Uses cached index
- Ready in ~10 seconds

### Run Acceptance Tests

```bash
python main.py doc.pdf --test
```

Runs all 5 mandatory tests:
1. Business segments extraction
2. Numeric value retrieval
3. Multi-factor analysis
4. Negative control (missing data)
5. Multi-turn conversation

### Rebuild Index (Clear Cache)

```bash
python main.py doc.pdf --no-cache
```

Use when:
- PDF was updated
- Want fresh embeddings
- Troubleshooting retrieval

## Docker Deployment

**Dockerfile** (optional):
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV OPENAI_API_KEY=sk-your-key
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "main.py"]
```

Build and run:
```bash
docker build -t rag-qa-system .
docker run -e OPENAI_API_KEY="sk-..." -v $(pwd):/app rag-qa-system doc.pdf
```

## Cloud Deployment (AWS Lambda / GCP Cloud Functions)

### Serverless Setup (AWS Lambda)

Requirements:
- Lambda layer with dependencies (since 250MB limit)
- S3 bucket for PDF storage
- Chroma database in EFS

```bash
# Create Lambda layer
mkdir python
cd python
pip install -r ../requirements.txt -t .
cd ..
zip -r layer.zip python/
aws lambda publish-layer-version --layer-name rag-layer --zip-file fileb://layer.zip
```

### Environment Variables on Cloud

Set in your cloud platform's environment configuration:
```
OPENAI_API_KEY = sk-your-key
CHROMA_DB_PATH = /mnt/efs/chroma_db  # For EFS
```

## Monitoring & Logging

### Add Logging to main.py

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
```

### Monitor Performance

Track metrics:
- PDF load time
- Embedding generation time (per chunk)
- Query retrieval time
- LLM API latency
- Total E2E latency

### Error Logging

```python
try:
    answer = qa_system.answer_question(query)
except Exception as e:
    logger.error(f"Query failed: {query}", exc_info=True)
    raise
```

## Scaling Considerations

### For Multiple PDFs

```python
# Modify Retriever to support multiple documents
class MultiDocumentRetriever(Retriever):
    def index_documents(self, documents: List[Dict]):
        for doc_id, chunks in documents.items():
            self.index_chunks(chunks, embeddings, doc_id=doc_id)
```

### For Large Documents (1000+ pages)

1. Increase chunk size: `chunk_size=1024`
2. Decrease overlap: `overlap=50`
3. Use hybrid retrieval (BM25 + vector)
4. Consider batch indexing

### Memory Optimization

```python
# Stream embeddings instead of loading all at once
def embed_chunks_streaming(self, chunks, batch_size=32):
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        embeddings = self.model.encode([c["text"] for c in batch])
        yield embeddings
```

## Security Best Practices

1. **Never commit API keys**
   ```bash
   echo "OPENAI_API_KEY=*" >> .gitignore
   ```

2. **Use environment variables**
   ```bash
   $env:OPENAI_API_KEY = "sk-..."
   ```

3. **Limit API key scope**
   - Use API keys with minimal permissions
   - Rotate keys regularly

4. **Secure PDF storage**
   - Use encrypted storage for sensitive PDFs
   - Implement access control

5. **Content filtering**
   - Add PII detection before indexing
   - Filter sensitive information

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"
**Solution:**
```powershell
$env:OPENAI_API_KEY = "sk-..."
python main.py doc.pdf
```

### Issue: PDF not found
**Solution:**
```bash
# Use absolute path
python main.py "C:\Users\Dell\Downloads\doc.pdf"

# Or copy to project
Copy-Item "C:\...\doc.pdf" -Destination ".\doc.pdf"
```

### Issue: Slow embedding generation
**Solution:**
- First run is slow (generates embeddings once)
- Subsequent runs use cache
- Use `--no-cache` only when needed

### Issue: "Not enough memory"
**Solution:**
- Reduce chunk size: `TextChunker(chunk_size=256)`
- Process PDFs in batches
- Increase virtual memory

### Issue: Low retrieval scores
**Solution:**
- Verify PDF loaded correctly
- Check retrieval debug output
- Try rephrasing query
- Use hybrid retrieval (BM25 + vector)

## Performance Optimization

### Caching Strategy

```python
# Skip re-embedding on reload
if retriever.load_from_existing():
    print("Using cached index")
else:
    embeddings = embedder.embed_chunks(chunks)
    retriever.index_chunks(chunks, embeddings)
```

### Batch Processing

```python
# Process multiple queries efficiently
queries = [
    "What is revenue?",
    "What are segments?",
    "What is profit?"
]

for query in queries:
    answer = qa_system.answer_question(query, debug=False)
    print(f"{query} → {answer}")
```

### API Rate Limiting

```python
import time
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=3, period=60)
def answer_question_limited(query):
    return qa_system.answer_question(query)
```

## Maintenance

### Regular Tasks

1. **Monitor API costs**
   - Track OpenAI usage in dashboard
   - Set billing alerts

2. **Update dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Clean up old indexes**
   ```bash
   rm -r ./chroma_db  # To rebuild
   ```

4. **Review logs**
   ```bash
   tail -f rag_system.log
   ```

### Update Strategy

1. Test changes locally
2. Use `--test` flag to validate
3. Deploy to production
4. Monitor for issues

## Compliance & Compliance

- **GDPR:** Ensure PDF content doesn't contain unencrypted PII
- **HIPAA:** If handling medical data, add encryption
- **SOC 2:** Implement audit logging
- **Data Retention:** Set automatic index cleanup policies

## Success Criteria

✓ System initializes without errors  
✓ PDF loads successfully  
✓ Embeddings generated and indexed  
✓ Acceptance tests pass (5/5)  
✓ Query latency < 5 seconds  
✓ Answers include citations  
✓ "Not found" responses for missing data  
✓ Multi-turn conversations work correctly  

## Getting Help

**Common Resources:**
- OpenAI Docs: https://platform.openai.com/docs
- Chroma Docs: https://docs.trychroma.com
- Sentence-Transformers: https://www.sbert.net
- pdfplumber: https://github.com/jsvine/pdfplumber
