# Phase 6: Agentic AI Test Automation

## What this does

Two capabilities, both powered by a local Ollama LLM:

### 1. Agentic browser automation (`agentic_bot.py`)

Uses the [`browser-use`](https://github.com/browser-use/browser-use) library
with `ChatOllama` to perform end-to-end browser tasks from a natural-language
instruction. The agent autonomously navigates, fills forms, clicks buttons,
and reports results — no hardcoded selectors or step sequences.

Default demo task: log in → verify secure area → log out on
[the-internet.herokuapp.com/login](https://the-internet.herokuapp.com/login)
(a publicly available practice site).

### 2. Self-healing locator module (`self_healing_locator.py`)

When a CSS selector breaks (DOM changed, element renamed), the module:
1. Extracts the current page DOM snippet.
2. Sends the broken selector + DOM to the LLM.
3. Validates the LLM's proposed replacement against the live page.
4. Logs the old → new selector mapping to `output/healed_selectors.json`.

This also satisfies Phase 4's "AI-assisted XPath/CSS selector generation"
requirement — the same LLM-powered selector inference, applied reactively
as a self-healing mechanism.

## Setup

```bash
cd phase6-agentic-automation
pip install -r requirements.txt
playwright install chromium
```

Ensure Ollama is running with a model pulled:
```bash
ollama pull llama3.2:3b
ollama serve   # if not already running
```

## Running

### Agentic bot
```bash
python agentic_bot.py                                    # default login task
python agentic_bot.py --task "Navigate to example.com"   # custom task
python agentic_bot.py --headless --max-steps 20          # headless, fewer steps
```

### Self-healing demo
```bash
python demo_self_healing.py
```

Demonstrates correct-selector passthrough and broken-selector healing
against a live practice site.

## Output

- `output/agent_run_<timestamp>.json` — agent execution trace (task,
  steps taken, final result, errors).
- `output/healed_selectors.json` — log of all self-healed selectors
  (original → healed, URL where healing occurred).

## Design notes

- **Practice sites only.** The default target is `the-internet.herokuapp.com`,
  which is reachable from this sandbox (unlike MakeMyTrip). For real project
  use, point `--url` at your target site.
- **Local LLM.** All inference runs through Ollama on localhost — no API
  keys, no cloud calls. The 3B-parameter model is sufficient for selector
  healing; agentic browsing benefits from larger models when available.
- **Deterministic validation.** The LLM proposes selectors, but code
  validates them against the live DOM before accepting — same principle as
  Phases 1–5 (LLM for prose/proposals, code for verification).
