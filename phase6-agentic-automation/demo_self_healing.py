"""Demo: self-healing locator in action.

Launches a Playwright browser, navigates to a practice site, and
demonstrates the heal_selector() workflow:

1. Try a *correct* selector — passes through unchanged.
2. Try a deliberately *wrong* selector — the LLM inspects the DOM and
   proposes a corrected one.

Usage:
    python demo_self_healing.py
    python demo_self_healing.py --model llama3.2:3b --base-url http://localhost:11434
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.llm import OllamaClient, OllamaConnectionError
from self_healing_locator import heal_selector


def main():
    parser = argparse.ArgumentParser(description="Self-healing locator demo")
    parser.add_argument("--model", default="llama3.2:3b")
    parser.add_argument("--base-url", default="http://localhost:11434")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    client = OllamaClient(model=args.model, base_url=args.base_url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://the-internet.herokuapp.com/login")
        page.wait_for_load_state("domcontentloaded")

        print("=" * 60)
        print("Self-Healing Locator Demo")
        print("=" * 60)

        # Case 1: correct selector — should pass through
        print("\n[1] Trying correct selector: #username")
        try:
            result = heal_selector(page, "#username", client)
            print(f"    Result: '{result}' (no healing needed)")
        except Exception as e:
            print(f"    Error: {e}")

        # Case 2: broken selector — should heal
        print("\n[2] Trying broken selector: #login-username-field")
        try:
            result = heal_selector(
                page, "#login-username-field", client, area_hint="form"
            )
            print(f"    Healed to: '{result}'")
        except ValueError as e:
            print(f"    Healing failed: {e}")
        except OllamaConnectionError:
            print("    Ollama not running — skipping LLM healing demo.")

        # Case 3: broken button selector
        print("\n[3] Trying broken selector: button.signin-btn")
        try:
            result = heal_selector(
                page, "button.signin-btn", client, area_hint="form"
            )
            print(f"    Healed to: '{result}'")
        except ValueError as e:
            print(f"    Healing failed: {e}")
        except OllamaConnectionError:
            print("    Ollama not running — skipping LLM healing demo.")

        browser.close()

    print("\n" + "=" * 60)
    print("Demo complete. Check output/healed_selectors.json for healing log.")


if __name__ == "__main__":
    main()
