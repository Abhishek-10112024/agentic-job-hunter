# 🚀 Agentic Job Hunter

An AI-powered personal job hunting assistant that scrapes live job listings, ranks them against your resume using semantic similarity, and uses Google Gemini to explain why each job matches you and identify your skill gaps.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Resume Parsing** | Upload a PDF — text is extracted and parsed into structured JSON (skills, experience, roles, domains) |
| 🔍 **Live Job Scraping** | Fetches real-time job listings from company Greenhouse job boards |
| 🧠 **Semantic Matching** | Ranks jobs against your resume using cosine similarity via sentence-transformer embeddings |
| 💬 **AI Match Explanation** | Gemini explains in 2 sentences exactly why each job is a good fit |
| 🎯 **Skill Gap Analysis** | Gemini identifies the advanced/production-level skills you're missing for each role |
| 💾 **Persistent Memory** | Your resume is stored in a local ChromaDB vector store — survives server restarts |
| ⚡ **Fast Local Dev** | Vite proxy eliminates CORS issues entirely; backend hot-reloads on file changes |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)             │
│   Upload PDF ──► Find Jobs ──► View Matches + Gaps      │
│   localhost:5173  →  /api/*  →  Vite Proxy              │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP (proxied, no CORS)
┌──────────────────────────▼──────────────────────────────┐
│                  Backend (FastAPI)   :8000               │
│                                                         │
│  POST /upload-resume                                    │
│    ├── resume_parser   → extract raw text from PDF      │
│    ├── resume_agent    → Gemini: parse to JSON          │
│    └── vector_store    → store in ChromaDB (on disk)    │
│                                                         │
│  GET /scrape-jobs                                       │
│    ├── scraper         → Greenhouse API (live jobs)     │
│    ├── matching_agent  → cosine similarity ranking      │
│    ├── explanation_agent → Gemini: why it matches       │
│    └── skill_gap_agent   → Gemini: missing skills       │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │   Google Gemini API     │
              │   (gemini-2.5-flash)    │
              └─────────────────────────┘
```

---

## 📁 Project Structure

```
agentic-job-hunter/
├── .env                          # API key + model config (never commit)
├── .gitignore
├── start.sh                      # One-command backend startup
│
├── backend/
│   ├── requirements.txt          # All Python dependencies
│   │
│   ├── app/
│   │   ├── config.py             # Centralised settings (API key, model, CORS)
│   │   └── main.py               # FastAPI app — all route definitions
│   │
│   ├── agents/
│   │   ├── explanation_agent.py  # Gemini: "why this job fits you"
│   │   ├── matching_agent.py     # Cosine similarity scorer
│   │   ├── resume_agent.py       # Gemini: resume → structured JSON
│   │   └── skill_gap_agent.py    # Gemini: missing skills for each role
│   │
│   ├── config/
│   │   └── companies.json        # ← Edit to add/remove job board sources
│   │
│   ├── memory/
│   │   └── vector_store.py       # ChromaDB persistent client
│   │
│   ├── tools/
│   │   └── scraper.py            # Greenhouse public API scraper
│   │
│   ├── uploads/                  # Uploaded PDFs (gitignored)
│   └── utils/
│       └── resume_parser.py      # PyPDF text extractor
│
└── frontend/
    ├── index.html
    ├── vite.config.js            # Proxy: /api/* → localhost:8000
    ├── package.json
    └── src/
        ├── App.jsx               # Main UI — upload, search, results
        ├── index.css             # Dark-theme design system
        └── main.jsx
```

---

## ⚙️ Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.11+ | Required for type hints used |
| Node.js | 18+ | For the React frontend |
| pip | Latest | Comes with Python |
| A Google Gemini API key | — | Free tier works fine |

---

## 🚀 Setup & Running

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd agentic-job-hunter
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

### 3. Configure environment variables

Edit `.env` in the project root:

```ini
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional — change model if needed (default: gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash
```

Get a free Gemini API key at → https://aistudio.google.com/app/apikey

### 4. Start the backend

```bash
./start.sh
```

This will:
- Activate the virtual environment
- Install all Python dependencies from `backend/requirements.txt`
- Start FastAPI with hot-reload on `http://127.0.0.1:8000`

### 5. Start the frontend

In a **second terminal**:

```bash
cd frontend
npm install       # first time only
npm run dev
```

Frontend runs at → **http://localhost:5173**

---

## 🎮 Usage

1. **Open** http://localhost:5173 in your browser
2. **Click** the file input and select your resume PDF
3. **Click "Upload Resume"** — wait for the success message (Gemini is parsing your resume)
4. **Click "🔍 Find Jobs"** — this will:
   - Scrape live jobs from all companies in `companies.json`
   - Run semantic similarity ranking
   - Call Gemini to explain the top 5 matches and identify skill gaps
   - Display results with match scores, explanations, and missing skills
5. **Click "🔗 Apply"** on any job to open the application page

> ⏱️ The "Find Jobs" step takes **20–40 seconds** — it's making multiple API calls to both the job boards and Gemini.

---

## 🏢 Adding / Removing Job Sources

Edit `backend/config/companies.json` — no code changes needed:

```json
{
  "companies": [
    "openai",
    "anthropic",
    "huggingface",
    "databricks",
    "cohere",
    "mistral",
    "scaleai"
  ]
}
```

These are **Greenhouse job board slugs**. To find a company's slug:
- Go to `https://boards.greenhouse.io/<slug>/jobs` and check if jobs are listed
- Example: `https://boards.greenhouse.io/stripe/jobs`

---

## 🔧 Configuration Reference

All settings live in `.env` at the project root:

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_API_KEY` | *(required)* | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model used by all AI agents |

### Available Gemini Models

| Model | Speed | Quality | Use When |
|---|---|---|---|
| `gemini-2.5-flash` | Fast | High | Default choice |
| `gemini-2.5-pro` | Slow | Best | Want highest-quality explanations |
| `gemini-2.0-flash-lite` | Fastest | Good | Hitting 503 errors on 2.5-flash |

---

## 🛠️ API Endpoints

The FastAPI server exposes these endpoints (also viewable at http://127.0.0.1:8000/docs):

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check — returns `{"status": "ok"}` |
| `POST` | `/upload-resume` | Upload a PDF resume. Parses, stores, returns structured data |
| `GET` | `/scrape-jobs` | Scrape jobs, rank by similarity, enrich with Gemini AI |

### `POST /upload-resume`

**Request:** `multipart/form-data` with a `file` field (PDF only)

**Response:**
```json
{
  "message": "Resume processed & stored successfully",
  "structured_data": {
    "skills": ["Python", "LangChain", "FastAPI", "..."],
    "experience": [{ "company": "...", "title": "...", ... }],
    "roles": ["AI/ML Engineer", "..."],
    "domains": ["LLM Systems", "RAG", "..."]
  }
}
```

### `GET /scrape-jobs`

**Response:**
```json
{
  "jobs": [
    {
      "company": "anthropic",
      "title": "Research Engineer, Interpretability",
      "location": "San Francisco, CA",
      "link": "https://boards.greenhouse.io/anthropic/jobs/...",
      "score": 0.82,
      "match_score": 82.0,
      "why_match": "Your experience with LLM systems and RAG pipelines...",
      "skill_gap": {
        "missing_skills": ["Mechanistic Interpretability", "Circuit Analysis", "SAE Training"]
      }
    }
  ]
}
```

---

## 🐛 Troubleshooting

### ❌ Upload fails — "Check the console"

Check the backend terminal for the exact error. Common causes:

| Error | Fix |
|---|---|
| `404 NOT_FOUND` on model | Change `GEMINI_MODEL` in `.env` to `gemini-2.0-flash-lite` |
| `503 UNAVAILABLE` — high demand | Wait 30s and retry. The app auto-retries 3 times with 5s delay |
| `GOOGLE_API_KEY is not set` | Check your `.env` file exists and has the key |
| File not accepted | Only PDF files are supported |

### ❌ CORS errors in browser console

The Vite proxy should eliminate all CORS issues. If you see them:
- Ensure the **backend** is running on port **8000** (`./start.sh`)
- Ensure the **frontend** is running via `npm run dev` (not a build)
- Do NOT access the backend directly at `localhost:8000` from the browser — always use the frontend at `localhost:5173`

### ❌ No jobs returned

- Some companies periodically change their Greenhouse slug or move to a different ATS
- Try removing companies from `companies.json` one at a time to find the broken one
- The scraper skips companies that fail silently — check backend logs

### ❌ `ModuleNotFoundError` on startup

Ensure you're running `./start.sh` from the **project root**, not from inside `backend/`. The script handles the `cd` automatically.

---

## 🔒 Security Notes

This is a **personal local tool** — it is intentionally not production-hardened:

- The API key is in `.env` (gitignored) — never commit it
- CORS is locked to `localhost:5173` only
- There is no authentication — anyone on your local machine can hit the API
- Uploaded PDFs are stored in `backend/uploads/` (gitignored)
- The ChromaDB vector store lives in `.chroma_db/` at the project root (gitignored)

---

## 📦 Dependencies

### Backend (`backend/requirements.txt`)

| Package | Purpose |
|---|---|
| `fastapi` + `uvicorn` | Web framework and ASGI server |
| `python-dotenv` | Load `.env` config |
| `pypdf` | Extract text from PDF resumes |
| `requests` | HTTP calls to Greenhouse job board APIs |
| `chromadb` | Local persistent vector store |
| `sentence-transformers` | Embedding model for semantic similarity |
| `numpy` | Cosine similarity computation |
| `langchain` + `langchain-core` | LLM orchestration framework |
| `langchain-google-genai` | Gemini integration for LangChain |
| `python-multipart` | Multipart form parsing for file uploads |

### Frontend (`frontend/package.json`)

| Package | Purpose |
|---|---|
| `react` + `react-dom` | UI framework |
| `axios` | HTTP client |
| `vite` | Dev server + bundler with proxy support |

---

## 📝 License

Personal use only — not intended for production deployment.
