"""Thin client for a local Ollama server's chat API."""
from __future__ import annotations

import requests


class OllamaConnectionError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b", timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(self, messages: list[dict]) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.3},
                },
                timeout=self.timeout,
            )
        except requests.exceptions.ConnectionError as exc:
            raise OllamaConnectionError(
                f"Could not reach Ollama at {self.base_url}. Is the Ollama app/service running? "
                f"Start it, then retry (or run `ollama serve` in a terminal)."
            ) from exc

        if response.status_code == 404:
            raise OllamaConnectionError(
                f'Model "{self.model}" is not available. Pull it first: `ollama pull {self.model}`.'
            )
        response.raise_for_status()
        return response.json()["message"]["content"]
