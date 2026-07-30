# Phase 2: Test Planning and Estimation

Produces:

- **`output/effort_estimation.md`** — person-day effort estimate broken
  down by activity (requirement analysis, test design, framework setup,
  execution & stabilization, reporting).
- **`output/Test_Plan.docx`** — a test plan document (scope, objectives,
  approach, resources, entry/exit criteria, risks, timeline).

## Setup & run

```bash
pip install -r requirements.txt
python generate_test_plan.py
```

## Design notes

**The LLM writes rationale, not arithmetic.** An earlier version asked the
model to compute person-day numbers itself from the scope metrics. It
produced answers like:

> "27 automated scenarios / 6 ... = 4.5 person-days per scenario" → used
> to justify **120 person-days just to execute** a suite that actually
> runs in minutes.

This is the same failure mode noted in Phase 1 and Phase 7: small local
models are unreliable at multi-step numeric reasoning, not just at
judging their own retrieval relevance. The fix follows the same pattern —
move the arithmetic into code, keep the LLM for what it's actually good
at:

- `compute_effort_days()` computes every number from fixed, transparent
  ratios applied to **real, programmatically-counted** project metrics
  (actual scenario count from the feature file, actual page object count
  from `src/pages/`, actual requirement count from Phase 1's use-case
  items) — never estimates of estimates.
- The LLM is only asked, per activity, to write one sentence of rationale
  for a number it's *given*, explicitly instructed not to propose a
  different one.

Current run: 48 person-days total (~9.6 weeks for one engineer) — a
credible number for this scope, unlike the arithmetic-hallucinated
version.
