"""Structured parser for the project's .feature file — turns raw Gherkin
into a list of scenario dicts, so Phase 1/3/5 scripts can cross-reference
requirements/manual test cases against the *actual* automated scenarios
instead of re-describing them from scratch.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Scenario:
    name: str
    tags: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    is_outline: bool = False
    examples: list[dict] = field(default_factory=list)

    @property
    def phase_tags(self) -> list[str]:
        return [t for t in self.tags if t not in ("@positive", "@negative", "@smoke", "@flightBooking")]

    @property
    def polarity(self) -> str:
        if "@positive" in self.tags:
            return "positive"
        if "@negative" in self.tags:
            return "negative"
        return "unspecified"


_SCENARIO_START = re.compile(r"^\s*Scenario(?: Outline)?:\s*(.+)$")
_TAG_LINE = re.compile(r"^\s*(@\S.*)$")
_STEP_LINE = re.compile(r"^\s*(Given|When|Then|And|But)\s+(.+)$")


def parse_feature(path: Path) -> list[Scenario]:
    lines = path.read_text(encoding="utf-8").splitlines()
    scenarios: list[Scenario] = []
    pending_tags: list[str] = []
    current: Scenario | None = None
    in_examples = False
    examples_header: list[str] = []

    def flush():
        if current is not None:
            scenarios.append(current)

    for raw_line in lines:
        line = raw_line.rstrip()
        tag_match = _TAG_LINE.match(line)
        scenario_match = _SCENARIO_START.match(line)
        step_match = _STEP_LINE.match(line)

        if tag_match and not step_match:
            pending_tags.extend(tag_match.group(1).split())
            continue

        if scenario_match:
            flush()
            current = Scenario(
                name=scenario_match.group(1).strip(),
                tags=pending_tags,
                is_outline="Outline" in line,
            )
            pending_tags = []
            in_examples = False
            continue

        if current is None:
            continue

        if line.strip().lower() == "examples:":
            in_examples = True
            examples_header = []
            continue

        if in_examples and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not examples_header:
                examples_header = cells
            else:
                current.examples.append(dict(zip(examples_header, cells)))
            continue

        if step_match:
            current.steps.append(f"{step_match.group(1)} {step_match.group(2)}")
            continue

    flush()
    return scenarios
