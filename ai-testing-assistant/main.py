"""AI Testing Assistant — Phase 7 deliverable.

Reads the project's requirement document and Gherkin feature file(s) and
answers questions about them (test cases, requirements) or generates
Selenium automation code, via a local Ollama model.

Usage:
    python main.py                          # interactive REPL
    python main.py --query "What are the test cases for the search flow?"
"""
from __future__ import annotations

import argparse
from pathlib import Path

from assistant.cli import Assistant, run_repl

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_DOCS = [
    REPO_ROOT / "docs" / "AI Usecase.docx",
    REPO_ROOT / "features" / "multiCityFlightBooking.feature",
]


def parse_args():
    parser = argparse.ArgumentParser(description="AI Testing Assistant")
    parser.add_argument(
        "--docs",
        nargs="+",
        type=Path,
        default=DEFAULT_DOCS,
        help="Requirement document(s) / feature file(s) to read (.docx, .feature).",
    )
    parser.add_argument("--model", default="llama3.2:3b", help="Ollama model tag to use.")
    parser.add_argument("--base-url", default="http://localhost:11434", help="Ollama server URL.")
    parser.add_argument("--query", help="Ask a single question non-interactively and exit.")
    return parser.parse_args()


def main():
    args = parse_args()

    missing = [str(p) for p in args.docs if not p.exists()]
    if missing:
        print("Warning: these document paths were not found and will be skipped:")
        for m in missing:
            print(f"  - {m}")

    if args.query:
        assistant = Assistant(args.docs, args.model, args.base_url)
        print(assistant.ask(args.query))
        return

    run_repl(args.docs, args.model, args.base_url)


if __name__ == "__main__":
    main()
