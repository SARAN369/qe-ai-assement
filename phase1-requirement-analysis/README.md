# Phase 1: Requirement Analysis with Gen AI

Reads `docs/AI Usecase.docx`'s Use Case Scenario section (items a–j) and
`features/multiCityFlightBooking.feature`, then produces:

- **`output/requirements_analysis.md`** — functional and non-functional
  requirements extracted via a local LLM (two separate prompts — see
  "Design notes" below).
- **`output/RTM.xlsx`** — Requirement Traceability Matrix: each use-case
  item (a–j) mapped to the actual automated scenario(s) that cover it,
  cross-referenced by keyword overlap against the real feature file (not
  asked of the LLM directly — see Phase 7's README for why that's
  unreliable at this model size).
- **`output/identified_test_scenarios.md`** — the LLM independently
  proposes scenario titles from the extracted requirements, then each is
  checked against whether a matching automated scenario already exists —
  a genuine gap-check against the fixed 32-scenario suite, not busywork.

## Setup & run

```bash
pip install -r requirements.txt
python generate_requirements.py
```

Requires Ollama running locally with `llama3.2:3b` pulled (same as Phase 7).

## Design notes

- **Two prompts, not one.** The first version asked one prompt for both
  functional and non-functional requirements; the model reliably produced
  the functional list and silently dropped the non-functional section.
  Splitting into two single-purpose calls fixed it — same lesson as
  Phase 7.
- **RTM relevance is code, not LLM.** `common/matcher.py` (keyword
  overlap, min score 3) decides which scenarios cover which requirement.
  This surfaced and fixed a real bug: `common/docx_reader.py`'s heading
  heuristic was initially over-eager (any short, capitalized, unpunctuated
  line counted as a heading), which fragmented item `c)` ("Apply filters:
  Flight type / Preferred airlines / Departure time slots / ...") into
  several tiny sections and truncated its real content down to just
  "Apply filters:" — that produced a false RTM gap on filters despite
  three real filter scenarios existing. Fixed by requiring the explicit
  heading pattern only; current run produces 0 gaps across all 10
  use-case items. The same fix was ported to Phase 7's `doc_loader.py`,
  which had the identical heuristic.
