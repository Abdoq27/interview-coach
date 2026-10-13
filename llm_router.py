
import os
from openai import OpenAI


class LLMRouter:
    """Routes tasks between two local Ollama chat models."""

    def __init__(self):
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434/v1",
        )
        self.fast_model = os.getenv(
            "OLLAMA_FAST_MODEL",
            "qwen2.5:1.5b",
        )
        self.strong_model = os.getenv(
            "OLLAMA_STRONG_MODEL",
            "qwen2.5:3b",
        )

        self.client = OpenAI(
            base_url=self.base_url,
            api_key="ollama",
            timeout=180.0,
        )
        self.trace = []

    def complete(
        self,
        task: str,
        system: str,
        user: str,
        *,
        force_model: str | None = None,
    ) -> str:

        if force_model:
            model = force_model
            reason = "Model selected explicitly for evaluation"

        elif task in {"question", "simple"}:
            model = self.fast_model
            reason = "Fast model selected for a simple task"

        else:
            model = self.strong_model
            reason = "Stronger model selected for analysis or scoring"

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )

        self.trace.append({
            "task": task,
            "model": model,
            "reason": reason,
        })

        return response.choices[0].message.content or ""
