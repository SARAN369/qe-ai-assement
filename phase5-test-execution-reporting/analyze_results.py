"""Phase 5: Test Execution and Reporting.

Reads the JS framework's real Cucumber JSON output (reports/cucumber-report.json,
produced by an actual `cucumber-js` run — see README for which run and why)
and:

1. Computes pass/fail trends *programmatically* (counts, percentages, by
   tag) — arithmetic the LLM doesn't need to be trusted with, same lesson
   as Phase 1/2's READMEs.
2. Clusters failures by a canonicalized error signature (network error
   type, timeout, assertion, etc.), also computed in code.
3. Asks the LLM to narrate a summary report from those *pre-computed*
   trends/clusters — prose, not numbers.
4. Writes an honest, heuristic-based defect-risk note (not a fabricated ML
   prediction) — see the "AI-based defect prediction" section for why.

Outputs (in output/): ai_summary_report.md, defect_prediction.md
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.llm import OllamaClient

REPORT_PATH = REPO_ROOT / "reports" / "cucumber-report.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

SUMMARY_SYSTEM_PROMPT = """You are a QA lead writing a test execution summary for stakeholders. \
You are given pre-computed pass/fail trends and defect clusters (real numbers — do not alter or \
recompute them, just narrate them).

IMPORTANT: every scenario listed under a cluster failed for the SAME reason — the cluster's \
error SIGNATURE (e.g. "Network error: ..."). The scenario names listed under it are only which \
tests were affected, not evidence about why. A scenario named "invalid contact information" \
failing under a "Network error" signature failed because of the network issue, same as every \
other scenario in that cluster — NOT because of anything to do with contact information. Do not \
infer a root cause from scenario names; infer it only from the signature itself.

Write a short executive summary (3-6 sentences): overall result, the dominant failure cluster's \
signature and its root cause category (environment/network vs application logic vs test data — \
read directly off the signature, e.g. "Network error: X" is an environment/network cause), and \
one concrete recommendation. Plain prose, no headings, no invented numbers beyond what's given."""

PREDICTION_SYSTEM_PROMPT = """You are a QA lead writing a defect-risk note. You are given real \
counts of how many test scenarios depend on an external live website vs. how many are pure \
computation/validation logic, from a single test run (not historical trend data). Write 3-5 \
sentences: state plainly that this is a heuristic based on test *design* (dependency surface), \
not a trained prediction model or historical failure trend, then note which category carries \
more environmental risk and why, based on the given counts."""


def extract_signature(error_message: str) -> str:
    first_line = next((l for l in error_message.strip().splitlines() if l.strip()), "").strip()
    net_match = re.search(r"net::([A-Z0-9_]+)", first_line)
    if net_match:
        return f"Network error: {net_match.group(1)}"
    if re.search(r"Timeout \d+ms exceeded", first_line):
        return "Timeout exceeded"
    if "AssertionError" in error_message or "assert" in first_line.lower():
        return "Assertion failure"
    return first_line[:90] or "(no message)"


def load_scenarios(report_path: Path) -> list[dict]:
    with open(report_path, encoding="utf-8") as f:
        features = json.load(f)

    scenarios = []
    for feature in features:
        for element in feature.get("elements", []):
            if element.get("type") != "scenario":
                continue
            steps = element.get("steps", [])
            statuses = [s.get("result", {}).get("status") for s in steps]
            if "failed" in statuses:
                overall = "failed"
            elif "undefined" in statuses:
                overall = "undefined"
            elif all(s == "passed" for s in statuses if s != "skipped"):
                overall = "passed"
            else:
                overall = "other"

            failing_step = next((s for s in steps if s.get("result", {}).get("status") == "failed"), None)
            error_message = failing_step["result"].get("error_message", "") if failing_step else ""

            scenarios.append(
                {
                    "name": element.get("name"),
                    "tags": [t["name"] for t in element.get("tags", [])],
                    "status": overall,
                    "failing_step": failing_step.get("name") if failing_step else None,
                    "signature": extract_signature(error_message) if error_message else None,
                }
            )
    return scenarios


def compute_trends(scenarios: list[dict]) -> dict:
    total = len(scenarios)
    by_status = Counter(s["status"] for s in scenarios)
    by_tag = defaultdict(lambda: Counter())
    for s in scenarios:
        for tag in s["tags"]:
            by_tag[tag][s["status"]] += 1

    clusters = defaultdict(list)
    for s in scenarios:
        if s["status"] == "failed":
            clusters[s["signature"]].append(s["name"])

    return {
        "total": total,
        "by_status": dict(by_status),
        "by_tag": {tag: dict(counts) for tag, counts in by_tag.items()},
        "clusters": {sig: names for sig, names in clusters.items()},
    }


def trends_to_text(trends: dict) -> str:
    lines = [f"Total scenarios: {trends['total']}"]
    for status, count in trends["by_status"].items():
        pct = round(100 * count / trends["total"], 1) if trends["total"] else 0
        lines.append(f"  {status}: {count} ({pct}%)")
    lines.append("\nBy tag:")
    for tag, counts in sorted(trends["by_tag"].items()):
        lines.append(f"  {tag}: {counts}")
    lines.append("\nFailure clusters (by canonicalized error signature):")
    for sig, names in trends["clusters"].items():
        lines.append(f"  [{len(names)}x] {sig}")
        for name in names:
            lines.append(f"      - {name}")
    return "\n".join(lines)


def build_summary_report(client: OllamaClient, trends: dict) -> str:
    trends_text = trends_to_text(trends)
    narrative = client.ask(SUMMARY_SYSTEM_PROMPT, f"TRENDS AND CLUSTERS:\n{trends_text}")
    return (
        "# AI Test Execution Summary Report\n\n"
        f"Source: `reports/cucumber-report.json` (real `cucumber-js` run — see README for scope/why).\n\n"
        f"## Pass/Fail Trends (computed, not AI-generated)\n\n```\n{trends_text}\n```\n\n"
        f"## AI Narrative Summary\n\n{narrative}\n"
    )


def build_defect_prediction(client: OllamaClient, scenarios: list[dict]) -> str:
    live_dependent = 0
    pure_computation = 0
    for s in scenarios:
        # Every scenario runs the Background (launches the live site) except
        # none — Background is unconditional — so this splits by whether the
        # scenario's *own* body also needs the live site beyond Background,
        # using the presence of a DataTable-driven Given as the pure-compute
        # signal (see features/multiCityFlightBooking.feature's "the
        # following fare breakup is displayed" scenario).
        if "fare breakup is displayed" in (s.get("failing_step") or "") or "Detect a total mismatch" in s["name"]:
            pure_computation += 1
        else:
            live_dependent += 1

    counts_text = (
        f"Live-site-dependent scenarios (beyond the shared Background, which all scenarios run): {live_dependent}\n"
        f"Pure computation/validation scenarios (e.g. fare-tolerance math from a Gherkin DataTable, "
        f"no live-site dependency in their own logic): {pure_computation}\n"
        f"Total analyzed in this run: {len(scenarios)}"
    )
    narrative = client.ask(PREDICTION_SYSTEM_PROMPT, f"COUNTS:\n{counts_text}")
    return (
        "# Defect Risk Note (heuristic, not a trained prediction model)\n\n"
        f"```\n{counts_text}\n```\n\n{narrative}\n"
    )


def main():
    if not REPORT_PATH.exists():
        raise SystemExit(
            f"{REPORT_PATH} not found. Run a cucumber-js suite first (see README for the exact "
            f"command used to produce the one this script was built against)."
        )

    print(f"Loading {REPORT_PATH}...")
    scenarios = load_scenarios(REPORT_PATH)
    print(f"Loaded {len(scenarios)} scenarios.")

    trends = compute_trends(scenarios)
    print(trends_to_text(trends))

    client = OllamaClient()

    print("\nGenerating AI summary report...")
    summary_md = build_summary_report(client, trends)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "ai_summary_report.md").write_text(summary_md, encoding="utf-8")

    print("Generating defect risk note...")
    prediction_md = build_defect_prediction(client, scenarios)
    (OUTPUT_DIR / "defect_prediction.md").write_text(prediction_md, encoding="utf-8")

    print(f"\nDone. Output written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
