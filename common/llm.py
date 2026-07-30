"""Shared local-LLM client (Ollama) used by the STLC-phase scripts
(phase1, phase2, phase3, phase5, phase6). Mirrors ai-testing-assistant's
OllamaClient but lives here so those phases don't each vendor a copy.
"""
from __future__ import annotations

import requests


class OllamaConnectionError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b", timeout: int = 180):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(self, messages: list[dict], temperature: float = 0.2) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": temperature},
                },
                timeout=self.timeout,
            )
        except requests.exceptions.ConnectionError as exc:
            raise OllamaConnectionError(
                f"Could not reach Ollama at {self.base_url}. Is it running? Start the Ollama "
                f"app/service, then retry."
            ) from exc

        if response.status_code == 404:
            raise OllamaConnectionError(
                f'Model "{self.model}" is not available. Pull it first: `ollama pull {self.model}`.'
            )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def ask(self, system: str, user: str, temperature: float = 0.2) -> str:
        return self.chat(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=temperature,
        )
