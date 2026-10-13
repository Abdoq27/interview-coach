# Interview Coach — Student Project

A local Streamlit application that helps users practice job interviews, receive structured feedback, and identify areas for improvement.

## 1. Features

- **Two-model LLM router:** Routes simple tasks to a faster local model and evaluation tasks to a stronger local model.
- **Structured outputs:** Uses Pydantic schemas to validate structured interview evaluations and reports.
- **Retrieval-Augmented Generation (RAG):** Uses ChromaDB and local Ollama embeddings to retrieve relevant interview questions, reference answers, and sources.
- **Tool-using agent:** Uses three tools: `next_question`, `score_answer`, and `summarize_weaknesses`.
- **Visible execution trace:** Displays tool execution details in the Streamlit interface.
- **Session state:** Keeps interview progress and answers during the session.
- **Evaluation utilities:** Supports human-score comparison, repeated-score consistency, retrieval metrics, and latency measurement.

## 2. Architecture

```text
                 ┌──────────────────────┐
                 │    Streamlit UI      │
                 │       app.py         │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │   Interview Agent    │
                 │      agent.py        │
                 └──────────┬───────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
      next_question    score_answer   summarize_weaknesses
              │             │             │
              └─────────────┼─────────────┘
                            │
               ┌────────────┴────────────┐
               │                          │
       ┌───────▼────────┐        ┌────────▼────────┐
       │   LLM Router   │        │   RAG / Chroma  │
       │  Two Ollama    │        │ Local question  │
       │  chat models   │        │ bank + sources  │
       └────────────────┘        └─────────────────┘
```

## 3. Requirements

- Windows, macOS, or Linux
- Python 3.10 or newer
- [Ollama](https://ollama.com/)
- The local chat models and embedding model listed below

This project is configured to use local Ollama models. A paid OpenAI API key is not required for the local setup.

## 4. Windows setup

Open PowerShell in the project directory.

Create and activate the virtual environment:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If Python 3.11 is not installed, use an available Python version supported by the project dependencies.

Download the local models:

```powershell
ollama pull qwen2.5:1.5b
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

The first two models are used for chat tasks. `nomic-embed-text` creates embeddings for retrieval.

Make sure Ollama is running. The application uses these default settings:

```text
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_FAST_MODEL=qwen2.5:1.5b
OLLAMA_STRONG_MODEL=qwen2.5:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

If you use a `.env` file, configure the same variable names there. Keep secrets and local environment files out of Git.

If PowerShell blocks virtual-environment activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

## 5. Run the application

With the virtual environment activated, run:

```powershell
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## 6. Try an interview

1. Choose a target role in the sidebar.
2. Optionally enter a job description.
3. Click **Prepare interview**.
4. Read the interview question and enter an answer.
5. Submit the answer to receive a score and feedback.
6. Review retrieved reference sources and the agent trace.
7. View the weakness report and suggested study plan.

## 7. Project structure

| File or directory | Purpose |
|---|---|
| `app.py` | Streamlit interface and session state |
| `llm_router.py` | Routing between local chat models |
| `schemas.py` | Pydantic response schemas |
| `rag.py` | Embeddings, ChromaDB indexing, and retrieval |
| `tools.py` | Three interview-agent tools |
| `agent.py` | Agent orchestration and execution trace |
| `evaluation.py` | Human comparison, consistency, retrieval, and latency metrics |
| `data/interview_bank.json` | Starter interview question bank |
| `.env.example` | Example local configuration |
| `.gitignore` | Excludes environment files and generated artifacts |

## 8. Evaluation

The project includes utilities for measuring:

- **Human-score agreement:** Mean Absolute Error (MAE) and percentage of AI scores within one point of human scores.
- **Consistency:** Mean, standard deviation, and range across repeated scores.
- **Retrieval quality:** Precision@k, Recall@k, and Hit@k when relevant record IDs are known.
- **Latency:** Elapsed time for a function call.

| Metric | Current result | Status |
|---|---|---|
| Human-score MAE | Not yet measured on a real evaluation set | Pending |
| Within-one-point agreement | Not yet measured on a real evaluation set | Pending |
| Repeated-score consistency | Requires actual repeated model runs | Pending |
| Retrieval Precision@k / Recall@k | Requires a labeled retrieval test set | Pending |
| Model latency | Requires recorded timings from actual runs | Pending |

Do not treat sample values displayed in the Evaluation tab or synthetic unit-test examples as measured project results. Record real results before submitting the final report.

## 9. Git branches

The project uses these branch names to organize development stages:

- `v1-llm` — two-model LLM routing
- `v2-rag` — retrieval and source grounding
- `v3-eval` — evaluation metrics
- `v4-agent` — agent tools and trace

Verify the history of each branch before submission. Branch names alone do not prove that each stage has its own implementation history.

## 10. Limitations and responsible use

- The starter question bank is small and should be expanded for a more reliable evaluation.
- Local model responses can vary in quality and consistency.
- Evaluation results depend on the quality of the human reference scores and retrieval labels.
- Use synthetic or public data only. Do not include private interview answers or personal information in the repository.
- The application is intended for practice and learning, not as a definitive hiring decision system.
- The ChromaDB index is stored locally in `.chroma/`. Rebuild it if you change the embedding model.

## 11. Demo video checklist

Prepare a 60–90 second recording that shows:

1. Starting the local application.
2. Preparing an interview for a target role.
3. Submitting an answer and displaying the structured evaluation.
4. Showing retrieved sources and the agent trace.
5. Opening the weakness report and evaluation screen.

Only describe features and evaluation results that you have actually tested.