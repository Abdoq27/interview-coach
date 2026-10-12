# Interview Coach — Student Project

A local Streamlit application for mock interviews. It demonstrates:
- Two LLM choices through a cost-aware router
- Structured JSON validated with Pydantic
- RAG over a local question/answer bank using ChromaDB
- Three explicit agent tools and a visible tool trace
- Session state for the current interview
- Evaluation metrics for human comparison and repeated scoring

## 1. Requirements
- Python 3.10 or newer (Python 3.11 is a good choice)
- Ollama installed and a local chat model (default: `qwen2.5:3b`)
- Internet access while calling the API; the UI itself runs locally

## 2. Windows setup (PowerShell)

Open PowerShell in this folder:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
```

The app uses local Ollama models, so no Ollama local model is required. If `.env` already exists, open it and add/update the `OLLAMA_...` settings from `.env.example`.

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

## 3. Run

```powershell
streamlit run app.py
```

Streamlit will show a local address, usually `http://localhost:8501`.

## 4. First test
1. Paste a job description.
2. Keep the target role as `Machine Learning Engineer` or change it.
3. Click **Prepare interview**.
4. Answer each question and submit it.
5. Review retrieved sources, the agent trace, and the final weakness report.

## 5. Project map
- `app.py`: Streamlit UI
- `llm_router.py`: fast/strong model routing
- `prompts.py`: prompts can be extracted here as the project grows (currently prompts are near the tool logic)
- `schemas.py`: Pydantic response models
- `rag.py`: embeddings, Chroma index, retrieval and source metadata
- `tools.py`: the three agent tools
- `agent.py`: tool orchestration and trace
- `evaluation.py`: evaluation metrics
- `data/interview_bank.json`: starter knowledge bank
- `.env.example`: safe template for environment variables

## 6. Important notes
- API calls can incur charges. Check your account limits and model availability.
- If a model name is unavailable to your account, update `OPENAI_FAST_MODEL` or `OPENAI_STRONG_MODEL` in `.env`.
- The initial question bank is intentionally small so the first run is easy to inspect. Expand it before final evaluation.
- The evaluation screen accepts real scores. The displayed example values are only examples, not project results.
- The RAG collection is stored locally in `.chroma/`. Delete that folder to rebuild the vector index from scratch.
- No deployment is required. The project runs locally.


## Local Ollama setup (no paid API key)

In PowerShell, download the chat model and embedding model:

```powershell
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

Make sure Ollama is running, then activate `.venv`, install dependencies, and run `streamlit run app.py`. The RAG index uses `nomic-embed-text` locally. If you switch embedding models, delete `.chroma/` before rebuilding the index.
