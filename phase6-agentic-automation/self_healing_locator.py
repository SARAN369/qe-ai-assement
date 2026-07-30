"""Self-healing locator module.

Given a stale CSS/XPath selector that no longer matches, uses the local
Ollama LLM to propose an alternative selector from the current page DOM.

Workflow:
1. Playwright tries the original selector — if it works, done.
2. If it fails, extract a DOM snippet around where the element was
   expected (or the full visible DOM if unknown).
3. Send the original selector + DOM snippet to the LLM and ask for
   a corrected selector.
4. Validate the LLM's proposed selector against the live page.
5. Log the old → new mapping so it can be reviewed / persisted.

This is the Phase 4 "AI-assisted XPath/CSS generation" requirement
surfaced through Phase 6's agentic automation layer.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.llm import OllamaClient, OllamaConnectionError

SELECTOR_SYSTEM_PROMPT = """You are a Playwright selector expert. You are given:
1. A CSS or XPath selector that no longer matches any element on the page.
2. A snippet of the current page DOM (HTML).

Your job: propose ONE corrected CSS selector that targets the same logical
element the original selector was intended to find.

Reply with ONLY the selector string — no explanation, no markdown fences,
no quotes. Example reply:
button.search-btn[data-testid="submit"]"""

HEAL_LOG_PATH = Path(__file__).resolve().parent / "output" / "healed_selectors.json"


def _extract_dom_snippet(page, area_hint: str | None = None, max_chars: int = 8000) -> str:
    if area_hint:
        try:
            outer = page.evaluate(
                """(hint) => {
                    const el = document.querySelector(hint);
                    return el ? el.outerHTML : null;
                }""",
                area_hint,
            )
            if outer and len(outer) < max_chars:
                return outer
        except Exception:
            pass
    return page.evaluate(
        """(maxLen) => {
            const html = document.body.innerHTML;
            return html.length > maxLen ? html.slice(0, maxLen) + '<!-- truncated -->' : html;
        }""",
        max_chars,
    )


def _parse_selector(raw: str) -> str | None:
    cleaned = raw.strip().strip("`").strip('"').strip("'").strip()
    if not cleaned or "\n" in cleaned:
        return None
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rstrip("`").strip()
    return cleaned if cleaned else None


def _log_healing(original: str, healed: str, url: str) -> None:
    HEAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    history: list[dict] = []
    if HEAL_LOG_PATH.exists():
        try:
            history = json.loads(HEAL_LOG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    history.append({"original": original, "healed": healed, "url": url})
    HEAL_LOG_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")


def heal_selector(
    page,
    original_selector: str,
    client: OllamaClient | None = None,
    area_hint: str | None = None,
) -> str:
    """Try *original_selector*; if it fails, ask the LLM for a fix.

    Returns the working selector (original or healed).
    Raises ValueError if healing fails.
    """
    try:
        if page.query_selector(original_selector):
            return original_selector
    except Exception:
        pass

    if client is None:
        client = OllamaClient()

    dom_snippet = _extract_dom_snippet(page, area_hint)
    prompt = (
        f"Original (broken) selector:\n{original_selector}\n\n"
        f"Current DOM snippet:\n{dom_snippet}"
    )

    try:
        raw_reply = client.ask(SELECTOR_SYSTEM_PROMPT, prompt)
    except OllamaConnectionError:
        raise ValueError(
            f"Selector '{original_selector}' is broken and Ollama is unreachable for healing."
        )

    proposed = _parse_selector(raw_reply)
    if not proposed:
        raise ValueError(
            f"LLM returned unusable selector for '{original_selector}': {raw_reply!r}"
        )

    try:
        if page.query_selector(proposed):
            _log_healing(original_selector, proposed, page.url)
            return proposed
    except Exception:
        pass

    raise ValueError(
        f"LLM-proposed selector '{proposed}' also failed on the page. "
        f"Original: '{original_selector}'."
    )
