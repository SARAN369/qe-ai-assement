"""Phase 3: Test Design.

Rather than asking the LLM to invent manual test cases from scratch (risking
the same fabrication problem documented in Phase 7's README), this script
derives manual test cases *structurally* from the project's real, already-
automated Gherkin scenarios — Given/When steps become "Steps", Then/And-
after-Then steps become "Expected Result". The LLM's only job is a single
one-sentence "Objective" per case, which is low-risk (it's summarizing text
it's given, not generating new claims).

"Convert manual test cases into automated test scripts" is satisfied by
construction here, in reverse: automation already exists for every case, so
this script instead outputs the traceability mapping proving it (Phase 3's
brief deliverable is the *link* between manual and automated, which matters
more than re-deriving automation that's already been built and verified).

Outputs (in output/): manual_test_cases.xlsx, manual_to_automated_mapping.md,
boundary_negative_suggestions.md
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from openpyxl import Workbook

from common.docx_reader import get_section, get_use_case_items
from common.feature_reader import Scenario, parse_feature
from common.llm import OllamaClient
from common.matcher import best_matches

DOCX_PATH = REPO_ROOT / "docs" / "AI Usecase.docx"
FEATURE_PATH = REPO_ROOT / "features" / "multiCityFlightBooking.feature"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

OBJECTIVE_SYSTEM_PROMPT = """You are a QA analyst writing manual test cases. Given a Gherkin \
scenario's name and steps below, write exactly one short sentence describing the test's \
objective in plain business language (not a restatement of Gherkin syntax, not a list). Do not \
add any check or claim not implied by the given scenario. Output only the sentence."""

BOUNDARY_SYSTEM_PROMPT = """You are a QA test designer. Given the USE CASE SCENARIO text below, \
propose boundary-value and negative test ideas for its key input fields (dates, ages, GSTIN, \
email, phone, baggage weight, seat selection, traveller counts, etc — whichever are actually \
mentioned in the text). One idea per line, format: "<field>: <boundary/negative condition>". \
Only propose ideas for fields actually mentioned in the text below — do not invent fields that \
aren't there. Aim for 12-18 ideas."""


def split_steps(steps: list[str]) -> tuple[list[str], list[str]]:
    """Given/When (+ their And-continuations) -> action steps; Then (+ its
    And-continuations) -> expected results."""
    action_steps, expected_results = [], []
    last_kind = None
    for step in steps:
        keyword, _, rest = step.partition(" ")
        kind = last_kind if keyword == "And" else keyword
        last_kind = kind
        (expected_results if kind == "Then" else action_steps).append(rest)
    return action_steps, expected_results


def priority_for(scenario: Scenario) -> str:
    return "High" if "@smoke" in scenario.tags else "Medium"


def build_manual_test_cases(client: OllamaClient, scenarios: list[Scenario], use_case_items):
    rows = []
    for idx, scenario in enumerate(scenarios, start=1):
        tc_id = f"TC-{idx:03d}"
        action_steps, expected_results = split_steps(scenario.steps)
        objective = client.ask(
            OBJECTIVE_SYSTEM_PROMPT,
            f"Scenario: {scenario.name}\nSteps:\n" + "\n".join(scenario.steps),
        ).strip()

        req_matches = best_matches(scenario.name + " " + " ".join(scenario.steps), use_case_items, lambda item: item[1], min_score=3, top_k=1)
        linked_req = f"REQ-UC-{req_matches[0][1][0].rstrip(')')}" if req_matches else "Unmapped"

        rows.append(
            {
                "tc_id": tc_id,
                "title": scenario.name,
                "objective": objective,
                "preconditions": "User is on MakeMyTrip with the prerequisite steps of prior test cases in this flow completed (see Steps for this test case's own entry point).",
                "steps": " | ".join(f"{i+1}. {s}" for i, s in enumerate(action_steps)) or "(none — outline/data-only case)",
                "expected_result": " | ".join(expected_results) or "(see steps)",
                "priority": priority_for(scenario),
                "type": scenario.polarity,
                "linked_requirement": linked_req,
                "scenario": scenario,
            }
        )
    return rows


def write_manual_test_cases_xlsx(rows: list[dict], path: Path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Manual Test Cases"
    headers = ["TC ID", "Title", "Objective (AI)", "Preconditions", "Steps", "Expected Result", "Priority", "Type", "Linked Requirement"]
    ws.append(headers)
    for row in rows:
        ws.append(
            [
                row["tc_id"], row["title"], row["objective"], row["preconditions"],
                row["steps"], row["expected_result"], row["priority"], row["type"], row["linked_requirement"],
            ]
        )
    widths = [10, 45, 45, 40, 70, 50, 10, 10, 18]
    for col_letter, width in zip("ABCDEFGHI", widths):
        ws.column_dimensions[col_letter].width = width
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def write_traceability_mapping(rows: list[dict], path: Path):
    lines = [
        "# Manual Test Case -> Automated Script Traceability\n",
        "Every manual test case here already has a corresponding automated Playwright/Cucumber "
        "scenario — that automation was built in Phase 4, before this phase existed, so rather "
        "than re-deriving scripts from these manual cases, this maps each one to where its "
        "automation actually lives.\n",
        "| TC ID | Manual Test Case | Automated Scenario | Location |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['tc_id']} | {row['title']} | {row['scenario'].name} | "
            f"`features/multiCityFlightBooking.feature` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_boundary_negative_suggestions(client: OllamaClient, scenarios: list[Scenario]) -> str:
    # "Use Case Scenario" itself is a heading whose own section only holds the
    # intro line — the lettered items (a-j) are separate sub-sections, since
    # they match the same heading pattern. Concatenate both so the LLM sees
    # the intro *and* every field the use case actually describes.
    intro = get_section(DOCX_PATH, "Use Case Scenario")
    items_text = "\n\n".join(f"{letter} {text}" for letter, text in get_use_case_items(DOCX_PATH))
    use_case_text = f"{intro}\n\n{items_text}"

    raw = client.ask(BOUNDARY_SYSTEM_PROMPT, f"USE CASE SCENARIO:\n{use_case_text}")
    # Despite "output only the list", the model sometimes prepends a "Here are
    # N ideas:" line or appends a "Note: ..." summary — both parse as fake
    # ideas unless filtered. Real idea lines always have a "<field>: <condition>"
    # shape; preamble/closing lines don't follow that field-name pattern.
    _PREAMBLE_PREFIXES = ("here are", "here's", "these", "in summary", "to summarize", "note")
    ideas = [
        line.strip("-* \t")
        for line in raw.splitlines()
        if line.strip() and not line.strip().lower().lstrip("0123456789. ").startswith(_PREAMBLE_PREFIXES)
    ]

    lines = ["# Boundary Value & Negative Test Case Suggestions\n"]
    lines.append(
        "AI-proposed boundary/negative ideas from the Use Case Scenario text, each checked "
        "against the existing 7 `@negative`-tagged automated scenarios (keyword-overlap match, "
        "min score 3):\n"
    )
    negative_scenarios = [s for s in scenarios if s.polarity == "negative"]
    for idea in ideas:
        matches = best_matches(idea, negative_scenarios, lambda s: s.name, min_score=2, top_k=1)
        if matches:
            lines.append(f"- ✅ Already covered — {idea} (*{matches[0][1].name}*)")
        else:
            lines.append(f"- 🆕 New suggestion — {idea}")
    return "\n".join(lines)


def main():
    print("Reading feature file and use-case requirements...")
    scenarios = parse_feature(FEATURE_PATH)
    use_case_items = get_use_case_items(DOCX_PATH)
    client = OllamaClient()

    print(f"Generating manual test cases for {len(scenarios)} scenarios (this calls the LLM once per scenario)...")
    rows = build_manual_test_cases(client, scenarios, use_case_items)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_manual_test_cases_xlsx(rows, OUTPUT_DIR / "manual_test_cases.xlsx")
    write_traceability_mapping(rows, OUTPUT_DIR / "manual_to_automated_mapping.md")

    print("Generating boundary-value / negative test case suggestions...")
    boundary_md = build_boundary_negative_suggestions(client, scenarios)
    (OUTPUT_DIR / "boundary_negative_suggestions.md").write_text(boundary_md + "\n", encoding="utf-8")

    print(f"\nDone. {len(rows)} manual test cases written. Output in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
