# PDF Q&A – RAG System

A fully local Retrieval-Augmented Generation (RAG) system built with **Flask**.  
Upload a PDF, ask questions, get answers grounded only in the document's content — no external APIs required.

---

## Architecture

```
PDF upload ──► Text extract (PyMuPDF)
           ──► Chunking (~500 words, 50-word overlap)
           ──► Embedding (sentence-transformers/all-MiniLM-L6-v2)
           ──► FAISS index (in-memory, per session)

User question ──► Embed query (same model)
              ──► FAISS top-4 chunk retrieval
              ──► Prompt + context ──► flan-t5-base (local LLM)
              ──► Answer returned to browser
```

Optional: every Q&A pair is logged to **MySQL** if DB credentials are set.

---

## Requirements

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| pip | latest |
| MySQL | 8.0+ |

---

## Setup

### 1. Clone / copy the project

```bash
git clone <your-repo-url>
cd rag_system
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note on PyTorch:** The default install pulls the CPU build (~800 MB).  
> For GPU support (faster generation):
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu121
> ```

### 4. (Optional) Configure MySQL

Set these environment variables before running:

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=your_user
export DB_PASSWORD=your_password
export DB_NAME=rag_db
```

Create the database first:
```sql
CREATE DATABASE rag_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

The `qa_log` table is created automatically on startup.

### 5. Run the server

```bash
python app.py
```

The server starts at **http://localhost:5000**.

---

## Usage

1. Open **http://localhost:5000** in your browser.
2. **Drag & drop** or click to upload a PDF (max 32 MB).
3. Wait for indexing (~5–15 seconds depending on PDF size and CPU).
4. Type a question and press **Ask** (or Enter).
5. The answer appears below, with expandable source chunks for transparency.
6. Click **Reset** to clear the session and upload a new document.

---

## Project structure

```
rag_system/
├── app.py                  # Flask routes and session management
├── requirements.txt
├── uploads/                # Temporary PDF storage (gitignored)
└── rag/
    ├── __init__.py
    ├── pdf_loader.py       # PyMuPDF text extraction
    ├── chunker.py          # Sliding-window text chunker
    ├── embedder.py         # sentence-transformers wrapper
    ├── retriever.py        # FAISS index builder + query
    ├── generator.py        # flan-t5 answer generation
    └── db.py               # MySQL logging (optional, graceful fallback)
```

---

## Models used

| Role | Model | Size | Hardware |
|------|-------|------|----------|
| Embedding | `all-MiniLM-L6-v2` | ~90 MB | CPU |
| Generation | `google/flan-t5-base` | ~250 MB | CPU / GPU |

Both models download automatically from Hugging Face on first run and are cached locally.

To upgrade to a larger LLM, change `Generator.MODEL_NAME` in `rag/generator.py`:

```python
MODEL_NAME = "google/flan-t5-large"    # ~800 MB – better quality
MODEL_NAME = "google/flan-t5-xl"       # ~3 GB   – even better
```

---

## Evaluation criteria (from task brief)

| Criterion | How it's addressed |
|-----------|-------------------|
| Answer relevance | FAISS cosine-similarity retrieval + grounded prompt ("answer only from context") |
| Approach | Standard RAG pipeline: chunk → embed → retrieve → generate |
| Code quality | Modular package (`rag/`), typed functions, docstrings, graceful error handling |

---

## Limitations

- **Scanned / image-only PDFs** are not supported (no OCR). Use a pre-OCR'd PDF.
- `flan-t5-base` is compact but may give shorter/simpler answers. Upgrade the model name for better output.
- The FAISS index lives in RAM and is lost on server restart; re-upload the PDF to start a new session.

---

## License

MIT
