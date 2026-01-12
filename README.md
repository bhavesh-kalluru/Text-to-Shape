# ShapeSketch + Web-RAG Geometry Tutor 📐🌐
Draw clean shape outlines (triangle, square, circle, polygons) and ask geometry questions backed by **live web retrieval** (Perplexity) + **synthesis** (OpenAI).

## What this app does
- **ShapeSketch (Drawing):** Select or type a shape and render its outline instantly.
- **Web-RAG Tutor:** Ask geometry questions (area/perimeter/relationships/examples) and get answers grounded in live web sources.

## Why this is “Web-RAG” (not local-file RAG)
This app does NOT use a static local `data/` folder.
Instead:
1) The user asks a question.
2) The app calls **Perplexity** to retrieve web-grounded evidence and sources (no URLs required from the user).
3) The app chunks/organizes that evidence and calls **OpenAI** to synthesize a final answer with citations.

Perplexity endpoint: `https://api.perplexity.ai/chat/completions`  
OpenAI synthesis uses the Python SDK Responses API.

## Tech stack
- Python
- Streamlit
- Matplotlib (shape outlines)
- OpenAI (final synthesis)
- Perplexity (live web retrieval)

---

## Local Setup & Run (macOS + PyCharm)

### 1) Create & activate a virtual environment
```bash
cd streamlit-genai-shape-sketch
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Create `.env` from `.env.example`
```bash
cp .env.example .env
```
Edit `.env` and set:
- `OPENAI_API_KEY=...`
- `PERPLEXITY_API_KEY=...`

### 4) Run Streamlit
```bash
streamlit run app.py
```

### Troubleshooting
- If API calls fail, confirm `.env` is present and keys are valid.
- If Streamlit shows blank plots, ensure `matplotlib` installed and try restarting the app.

---

## Docker Setup (SETUP-2)

### Build
```bash
docker build -t streamlit-genai-rag .
```

### Run
```bash
docker run -p 8501:8501 --env-file .env streamlit-genai-rag
```

---

## Render Deployment Instructions

### 1) Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Streamlit ShapeSketch + Web-RAG Tutor"
git remote add origin <REPO_URL>
git push -u origin main
```

### 2) Create a Render Web Service
- In Render: New → Web Service → connect your GitHub repo
- **Build Command:**
```bash
pip install -r requirements.txt
```
- **Start Command:**
```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```
- Add Environment Variables in Render:
  - `OPENAI_API_KEY`
  - `PERPLEXITY_API_KEY`

---

## Git & .gitignore behavior (don’t commit secrets)
- `.gitignore` **should be committed**
- `.env` must **never** be committed (already ignored by `.gitignore`)

---

## About the Author
I have **5 years of experience** and I’m actively looking for **full-time GenAI / AI Engineer roles** (US).

- GitHub: https://github.com/bhavesh-kalluru
- LinkedIn: https://www.linkedin.com/in/bhaveshkalluru/
- Portfolio: https://kbhavesh.com
- Project repo: REPO_URL_HERE
