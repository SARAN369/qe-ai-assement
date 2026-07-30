"""Loads the project's requirement document(s) and Gherkin feature files into
a flat list of retrievable text chunks. Chunking is heuristic (paragraph
grouping for docx, scenario blocks for .feature) rather than ML-based, since
the whole assistant is meant to run against nothing but a local Ollama model
and stdlib-adjacent dependencies.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from docx import Document


@dataclass
class Chunk:
    source: str
    title: str
    text: str


_HEADING_PATTERN = re.compile(
    r"^(Phase \d.*|Project (Overview|Objectives|Deliverables)|Tools & Technologies|"
    r"Expected Outcome|Optional Enhancements.*|Use Case Scenario|Languages|Frameworks|"
    r"AI Tools|Libraries|[a-j]\))",
    re.IGNORECASE,
)


def load_docx_chunks(path: Path) -> list[Chunk]:
    """Groups consecutive paragraphs under the most recent heading-like line
    into one chunk per section, so a query about "Phase 7" retrieves that
    whole phase's paragraphs together rather than one line at a time.
    """
    document = Document(str(path))
    chunks: list[Chunk] = []
    current_title = "Overview"
    current_lines: list[str] = []

    def flush():
        text = "\n".join(current_lines).strip()
        if text:
            chunks.append(Chunk(source=path.name, title=current_title, text=text))

    for para in document.paragraphs:
        line = para.text.strip()
        if not line:
            continue
        is_heading = bool(_HEADING_PATTERN.match(line)) or (
            len(line) < 60 and not line.endswith((".", ":", ",")) and line[0:1].isupper()
        )
        if is_heading and current_lines:
            flush()
            current_lines = []
            current_title = line
        elif is_heading and not current_lines:
            current_title = line
        else:
            current_lines.append(line)
    flush()
    return chunks


_SCENARIO_PATTERN = re.compile(
    r"(?=^\s*(?:@\S.*\n)?\s*Scenario(?: Outline)?:.*$)", re.MULTILINE
)


def load_feature_chunks(path: Path) -> list[Chunk]:
    """Splits a .feature file into one chunk per Scenario/Scenario Outline
    block (including its leading @tags line), plus one chunk for the
    Feature-level description/Background.
    """
    text = path.read_text(encoding="utf-8")
    parts = _SCENARIO_PATTERN.split(text)
    chunks: list[Chunk] = []

    header = parts[0].strip()
    if header:
        chunks.append(Chunk(source=path.name, title="Feature description & Background", text=header))

    for block in parts[1:]:
        block = block.rstrip()
        if not block.strip():
            continue
        title_match = re.search(r"Scenario(?: Outline)?:\s*(.+)", block)
        title = title_match.group(1).strip() if title_match else "Scenario"
        chunks.append(Chunk(source=path.name, title=title, text=block.strip()))

    return chunks


def build_corpus(doc_paths: list[Path]) -> list[Chunk]:
    corpus: list[Chunk] = []
    for path in doc_paths:
        if not path.exists():
            continue
        if path.suffix.lower() == ".docx":
            corpus.extend(load_docx_chunks(path))
        elif path.suffix.lower() == ".feature":
            corpus.extend(load_feature_chunks(path))
    return corpus
