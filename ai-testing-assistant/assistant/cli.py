from __future__ import annotations

from pathlib import Path

from .doc_loader import build_corpus
from .llm_client import OllamaClient, OllamaConnectionError
from .prompts import SYSTEM_PROMPT, build_user_message
from .retriever import retrieve

BANNER = """AI Testing Assistant (Phase 7)
Reads: {sources}
Model: {model} (via Ollama at {base_url})
Type a question, or :sources / :reload / :exit
"""


class Assistant:
    def __init__(self, doc_paths: list[Path], model: str, base_url: str):
        self.doc_paths = doc_paths
        self.client = OllamaClient(base_url=base_url, model=model)
        self.corpus = build_corpus(doc_paths)
        self.last_sources: list[str] = []

    def reload(self):
        self.corpus = build_corpus(self.doc_paths)

    def ask(self, query: str) -> str:
        top = retrieve(self.corpus, query, top_k=5)
        self.last_sources = [f"{s.chunk.source} :: {s.chunk.title} (score={s.score})" for s in top]

        # The retriever's relevance threshold is a more reliable judge of
        # "is this topic actually covered" than a small local model is when
        # asked to decide that itself (see README caveats) — so handle the
        # no-match case deterministically in code instead of asking the LLM
        # to recognize and announce it.
        if not top:
            return f'No matching test cases/requirements found in the current requirement document or feature file for: "{query}".'

        context_blocks = [f"[{s.chunk.source} — {s.chunk.title}]\n{s.chunk.text}" for s in top]
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(query, context_blocks)},
        ]
        return self.client.chat(messages)


def run_repl(doc_paths: list[Path], model: str, base_url: str):
    assistant = Assistant(doc_paths, model, base_url)
    print(BANNER.format(sources=", ".join(p.name for p in doc_paths), model=model, base_url=base_url))
    print(f"Loaded {len(assistant.corpus)} chunks from {len(doc_paths)} document(s).\n")

    while True:
        try:
            query = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query:
            continue
        if query in (":exit", ":quit"):
            break
        if query == ":reload":
            assistant.reload()
            print(f"Reloaded. {len(assistant.corpus)} chunks.\n")
            continue
        if query == ":sources":
            if assistant.last_sources:
                print("Last answer used:")
                for s in assistant.last_sources:
                    print(f"  - {s}")
            else:
                print("No question asked yet.")
            print()
            continue

        try:
            answer = assistant.ask(query)
        except OllamaConnectionError as exc:
            print(f"\n[error] {exc}\n")
            continue
        print(f"\nassistant> {answer}\n")
