import os
from openai import OpenAI

class LLMRouter:
    """Routes tasks to a local Ollama model through its OpenAI-compatible API."""
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        self.fast_model = os.getenv("OLLAMA_FAST_MODEL", "qwen2.5:3b")
        self.strong_model = os.getenv("OLLAMA_STRONG_MODEL", "qwen2.5:3b")
        # Ollama does not require a real API key; its OpenAI-compatible endpoint expects a placeholder.
        self.client = OpenAI(base_url=self.base_url, api_key="ollama", timeout=180.0)
        self.trace = []

    def complete(self, task: str, system: str, user: str, *, force_model: str | None = None) -> str:
        if force_model:
            model, reason = force_model, "Model selected explicitly for evaluation"
        elif task in {"question", "simple"}:
            model, reason = self.fast_model, "Local model selected for question generation"
        else:
            model, reason = self.strong_model, "Local model selected for scoring or synthesis"
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.2,
        )
        self.trace.append({"task": task, "model": model, "reason": reason})
        return response.choices[0].message.content or ""
