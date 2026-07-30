"""Phase 6: Agentic AI Automation — browser-use powered bot.

Uses the `browser-use` library with a local Ollama LLM (via ChatOllama)
to perform end-to-end browser tasks autonomously. The agent receives a
natural-language task, drives a real Chromium browser, and reports results.

Usage:
    python agentic_bot.py                          # default: login task on practice site
    python agentic_bot.py --task "Search for flights on makemytrip.com"
    python agentic_bot.py --task "Add items to cart" --url "https://www.saucedemo.com"
    python agentic_bot.py --model llama3.2:3b      # specify Ollama model
    python agentic_bot.py --headless               # run without visible browser

Requires:
    pip install -r requirements.txt
    ollama pull llama3.2:3b   (or whichever model you specify)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

DEFAULT_URL = "https://the-internet.herokuapp.com/login"
DEFAULT_TASK = (
    "Go to {url}. Log in with username 'tomsmith' and password 'SuperSecretPassword!'. "
    "After logging in, verify that the page shows a success message or a secure area. "
    "Then log out and confirm you are back on the login page."
)
DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_BASE_URL = "http://localhost:11434"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phase 6: Agentic AI browser automation")
    p.add_argument("--task", type=str, default=None, help="Natural-language task for the agent")
    p.add_argument("--url", type=str, default=DEFAULT_URL, help="Starting URL")
    p.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Ollama model name")
    p.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL, help="Ollama API base URL")
    p.add_argument("--max-steps", type=int, default=30, help="Max agent steps")
    p.add_argument("--headless", action="store_true", help="Run browser headless")
    return p


async def run_agent(task: str, model: str, base_url: str, max_steps: int, headless: bool) -> dict:
    from browser_use import Agent, BrowserConfig, BrowserProfile
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model=model, base_url=base_url, temperature=0)

    browser_profile = BrowserProfile(
        headless=headless,
        disable_security=True,
    )

    agent = Agent(
        task=task,
        llm=llm,
        browser_profile=browser_profile,
    )

    print(f"Running agent with model={model}, max_steps={max_steps}...")
    print(f"Task: {task}\n")

    history = await agent.run(max_steps=max_steps)

    result = {
        "task": task,
        "model": model,
        "max_steps": max_steps,
        "timestamp": datetime.now().isoformat(),
        "steps_taken": len(history.history) if history else 0,
        "final_result": history.final_result() if history else None,
        "errors": [str(e) for e in (history.errors() if history else [])],
    }
    return result


def save_result(result: dict) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"agent_run_{ts}.json"
    out_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    return out_path


def main():
    args = build_parser().parse_args()
    task = args.task or DEFAULT_TASK.format(url=args.url)

    print("=" * 60)
    print("Phase 6: Agentic AI Browser Automation")
    print("=" * 60)

    result = asyncio.run(run_agent(
        task=task,
        model=args.model,
        base_url=args.base_url,
        max_steps=args.max_steps,
        headless=args.headless,
    ))

    out_path = save_result(result)

    print("\n" + "=" * 60)
    print("Agent completed.")
    print(f"  Steps taken: {result['steps_taken']}")
    print(f"  Final result: {result['final_result']}")
    if result["errors"]:
        print(f"  Errors: {len(result['errors'])}")
        for e in result["errors"][:3]:
            print(f"    - {e[:120]}")
    print(f"  Output saved to: {out_path}")


if __name__ == "__main__":
    main()
