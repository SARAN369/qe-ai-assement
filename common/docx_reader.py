"""Reads the project's requirement docx into both a flat paragraph list and
section-grouped chunks (heading heuristics shared with
ai-testing-assistant/assistant/doc_loader.py).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from docx import Document


@dataclass
class Section:
    title: str
    text: str


_HEADING_PATTERN = re.compile(
    r"^(Phase \d.*|Project (Overview|Objectives|Deliverables)|Tools & Technologies|"
    r"Expected Outcome|Optional Enhancements.*|Use Case Scenario|Languages|Frameworks|"
    r"AI Tools|Libraries|[a-j]\))",
    re.IGNORECASE,
)


def read_paragraphs(path: Path) -> list[str]:
    document = Document(str(path))
    return [p.text.strip() for p in document.paragraphs if p.text.strip()]


def read_sections(path: Path) -> list[Section]:
    sections: list[Section] = []
    current_title = "Overview"
    current_lines: list[str] = []

    def flush():
        text = "\n".join(current_lines).strip()
        if text:
            sections.append(Section(title=current_title, text=text))

    for line in read_paragraphs(path):
        # Only the explicit pattern counts as a heading. An earlier "short
        # capitalized line" fallback also matched plain body bullets like
        # "Flight type" / "Preferred airlines", which fragmented items like
        # "c) Apply filters: ..." into tiny sections and truncated their
        # real content — that showed up downstream as a false RTM gap.
        is_heading = bool(_HEADING_PATTERN.match(line))
        if is_heading and current_lines:
            flush()
            current_lines = []
            current_title = line
        elif is_heading and not current_lines:
            current_title = line
        else:
            current_lines.append(line)
    flush()
    return sections


def read_full_text(path: Path) -> str:
    return "\n".join(read_paragraphs(path))


def get_section(path: Path, title_prefix: str) -> str:
    for section in read_sections(path):
        if section.title.lower().startswith(title_prefix.lower()):
            return section.text
    return ""


def get_use_case_items(path: Path) -> list[tuple[str, str]]:
    """Returns the Use Case Scenario's lettered items as [("a)", text), ...]."""
    items = []
    for s in read_sections(path):
        if len(s.title) <= 3 and s.title.rstrip(")").isalpha() and s.title.endswith(")"):
            items.append((s.title, s.text))
    return items
