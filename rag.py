import json
import os
from pathlib import Path
from typing import List, Dict, Any
import requests
import chromadb

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "interview_bank.json"
CHROMA_DIR = ROOT / ".chroma"
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1").removesuffix("/v1")
EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

class InterviewRAG:
    def __init__(self):
        self.db = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.db.get_or_create_collection(
            name="interview_question_bank_local",
            metadata={"hnsw:space": "cosine"}
        )

    def _embed(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        for text in texts:
            response = requests.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBEDDING_MODEL, "prompt": text},
                timeout=180,
            )
            if response.status_code == 404:
                raise RuntimeError(
                    "Ollama embedding endpoint returned 404. Update Ollama to a recent version, "
                    "then run: ollama pull nomic-embed-text"
                )
            response.raise_for_status()
            vector = response.json().get("embedding")
            if not vector:
                raise RuntimeError("Ollama returned no embedding. Check that nomic-embed-text is installed.")
            vectors.append(vector)
        return vectors

    def index_bank(self, force: bool = False) -> int:
        if force and self.collection.count():
            ids = self.collection.get()["ids"]
            if ids:
                self.collection.delete(ids=ids)
        if self.collection.count() > 0:
            return self.collection.count()
        records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        ids, docs, metas = [], [], []
        for i, item in enumerate(records):
            ids.append(item.get("id", f"item-{i}"))
            docs.append(
                f"Topic: {item['topic']}\nQuestion: {item['question']}\n"
                f"Model answer: {item['model_answer']}\nKey points: {', '.join(item['key_points'])}"
            )
            metas.append({
                "topic": item["topic"], "question": item["question"],
                "model_answer": item["model_answer"],
                "key_points": json.dumps(item["key_points"], ensure_ascii=False),
                "source": item.get("source", "Local interview bank")
            })
        vectors = self._embed(docs)
        self.collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=vectors)
        return self.collection.count()

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        if self.collection.count() == 0:
            self.index_bank()
        vector = self._embed([query])[0]
        result = self.collection.query(
            query_embeddings=[vector], n_results=min(k, max(1, self.collection.count())),
            include=["documents", "metadatas", "distances"]
        )
        found = []
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        for i, doc in enumerate(docs):
            meta = metas[i] or {}
            found.append({
                "id": ids[i], "document": doc, "topic": meta.get("topic", "Unknown"),
                "question": meta.get("question", ""), "model_answer": meta.get("model_answer", ""),
                "key_points": json.loads(meta.get("key_points", "[]")),
                "source": meta.get("source", "Local interview bank"),
                "distance": distances[i] if i < len(distances) else None,
            })
        return found
