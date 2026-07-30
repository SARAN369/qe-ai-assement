"""Phase 1: Requirement Analysis with Gen AI.

Reads docs/AI Usecase.docx and features/multiCityFlightBooking.feature, then:

1. Extracts functional & non-functional requirements via a local LLM,
   grounded in the Use Case Scenario section (see REQUIREMENT_SYSTEM_PROMPT).
2. Builds a Requirement Traceability Matrix (RTM) linking each use-case
   requirement (a-j) to the actual automated scenarios that cover it,
   cross-referenced by keyword overlap rather than asked of the LLM
   directly — Phase 7's README documents why small local models are
   unreliable at self-judging relevance; the same fix applies here.
3. Asks the LLM to independently propose test scenarios from the
   requirements, then checks which proposals are already covered by the
   real feature file and which aren't — a genuine gap-check against a
   fixed 32-scenario suite, not busywork.

Outputs (in output/): requirements_analysis.md, RTM.xlsx,
identified_test_scenarios.md
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from openpyxl import Workbook

from common.docx_reader import get_use_case_items
from common.feature_reader import parse_feature
from common.llm import OllamaClient
from common.matcher import best_matches, overlap_score

DOCX_PATH = REPO_ROOT / "docs" / "AI Usecase.docx"
FEATURE_PATH = REPO_ROOT / "features" / "multiCityFlightBooking.feature"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

# Split into two single-purpose prompts rather than one combined "extract both
# sections" prompt: the local model reliably produced a FUNCTIONAL list but
# silently dropped the NON-FUNCTIONAL section when asked for both at once —
# the same small-model unreliability documented in Phase 7's README. Two
# separate calls, each demanding just one thing, fixed it.
FUNCTIONAL_SYSTEM_PROMPT = """You are a QA business analyst. Given the USE CASE SCENARIO text \
below (from a real project's requirement document), extract the FUNCTIONAL REQUIREMENTS: what \
the system must let the user do. Numbered list, one line each. Only extract what's actually \
stated or directly implied — do not invent requirements about features the text doesn't \
mention. No preamble, just the numbered list."""

NON_FUNCTIONAL_SYSTEM_PROMPT = """You are a QA business analyst. Given the USE CASE SCENARIO \
text below (from a real project's requirement document), extract the NON-FUNCTIONAL \
REQUIREMENTS: performance limits, validation/format rules, tolerances, and usability constraints \
mentioned or implied (e.g. "results load within 10 seconds", "±2% tolerance", "GSTIN pattern", \
"email/phone validation"). Numbered list, one line each, each citing the specific constraint. \
Only extract what's actually stated or directly implied — do not invent constraints the text \
doesn't mention. No preamble, just the numbered list."""

SCENARIO_PROPOSAL_SYSTEM_PROMPT = """You are a QA test analyst. Given the numbered requirements \
below, propose a short list of distinct test scenario titles that should exist to verify them \
(one per line, no numbering, no explanations, just the scenario title as you'd write it in a \
Gherkin "Scenario:" line). Aim for 10-15 titles covering the main positive and negative cases."""


def build_requirements_markdown(client: OllamaClient, use_case_text: str) -> str:
    functional = client.ask(FUNCTIONAL_SYSTEM_PROMPT, f"USE CASE SCENARIO:\n{use_case_text}")
    non_functional = client.ask(NON_FUNCTIONAL_SYSTEM_PROMPT, f"USE CASE SCENARIO:\n{use_case_text}")
    return f"**FUNCTIONAL REQUIREMENTS:**\n\n{functional}\n\n**NON-FUNCTIONAL REQUIREMENTS:**\n\n{non_functional}"


def build_rtm(use_case_items: list[tuple[str, str]], scenarios) -> list[dict]:
    rows = []
    for idx, (letter, text) in enumerate(use_case_items, start=1):
        req_id = f"REQ-UC-{letter.rstrip(')')}"
        matches = best_matches(text, scenarios, lambda sc: f"{sc.name} {' '.join(sc.steps)}", min_score=3, top_k=6)
        rows.append(
            {
                "req_id": req_id,
                "requirement": text.replace("\n", " ")[:300],
                "matched_scenarios": [sc.name for _, sc in matches],
                "status": "Covered" if matches else "GAP — no automated scenario found",
            }
        )
    return rows


def write_rtm_xlsx(rows: list[dict], path: Path):
    wb = Workbook()
    ws = wb.active
    ws.title = "RTM"
    ws.append(["Requirement ID", "Requirement (from Use Case Scenario)", "Covered By Scenario(s)", "Status"])
    for row in rows:
        ws.append(
            [
                row["req_id"],
                row["requirement"],
                "; ".join(row["matched_scenarios"]) or "(none)",
                row["status"],
            ]
        )
    for col_letter, width in zip("ABCD", (16, 60, 60, 28)):
        ws.column_dimensions[col_letter].width = width
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def check_scenario_coverage(client: OllamaClient, requirements_md: str, scenarios) -> str:
    proposal_text = client.ask(SCENARIO_PROPOSAL_SYSTEM_PROMPT, f"REQUIREMENTS:\n{requirements_md}")
    proposed_titles = [line.strip("-* \t") for line in proposal_text.splitlines() if line.strip()]

    lines = ["# Identified Test Scenarios vs. Actual Coverage\n"]
    lines.append(
        "AI-proposed scenario titles (from the extracted requirements), each checked against "
        "whether a matching scenario already exists in `features/multiCityFlightBooking.feature` "
        "(keyword-overlap match, threshold >= 3 — same technique as the RTM above):\n"
    )
    for title in proposed_titles:
        matches = best_matches(title, scenarios, lambda sc: sc.name, min_score=3, top_k=1)
        if matches:
            lines.append(f"- ✅ **{title}** — covered by: *{matches[0][1].name}*")
        else:
            lines.append(f"- ❌ **{title}** — no matching automated scenario found (potential gap)")
    return "\n".join(lines)


def main():
    print("Reading requirement document and feature file...")
    scenarios = parse_feature(FEATURE_PATH)
    use_case_items = get_use_case_items(DOCX_PATH)
    use_case_text = "\n\n".join(f"{letter} {text}" for letter, text in use_case_items)

    print(f"Found {len(use_case_items)} use-case items (a-j) and {len(scenarios)} automated scenarios.")
    client = OllamaClient()

    print("Extracting functional & non-functional requirements via local LLM...")
    requirements_md = build_requirements_markdown(client, use_case_text)

    print("Building Requirement Traceability Matrix (RTM)...")
    rtm_rows = build_rtm(use_case_items, scenarios)
    write_rtm_xlsx(rtm_rows, OUTPUT_DIR / "RTM.xlsx")

    print("Checking AI-proposed scenarios against actual coverage...")
    coverage_md = check_scenario_coverage(client, requirements_md, scenarios)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "requirements_analysis.md").write_text(
        "# Requirements Analysis (Gen AI-extracted)\n\n"
        "Source: `docs/AI Usecase.docx` — Use Case Scenario section (items a-j).\n\n"
        f"{requirements_md}\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "identified_test_scenarios.md").write_text(coverage_md + "\n", encoding="utf-8")

    gaps = [r for r in rtm_rows if r["status"].startswith("GAP")]
    print(f"\nDone. RTM: {len(rtm_rows)} requirements, {len(gaps)} gap(s).")
    print(f"Output written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
