# Phase 3: Test Design

## `generate_test_design.py`

Produces:

- **`output/manual_test_cases.xlsx`** — one manual test case per real
  automated scenario (27 total): TC ID, Title, AI-written one-sentence
  Objective, Preconditions, Steps, Expected Result, Priority, Type
  (positive/negative), and Linked Requirement (cross-referenced to Phase
  1's `REQ-UC-*` IDs).
- **`output/manual_to_automated_mapping.md`** — traceability from each
  manual test case to its automated Playwright/Cucumber scenario. See
  "Design notes" for why this is a mapping rather than a re-derivation.
- **`output/boundary_negative_suggestions.md`** — AI-proposed boundary-value
  and negative test ideas per input field (dates, ages, GSTIN, email,
  phone, baggage weight, seat selection, ...), each checked against the
  7 existing `@negative` scenarios to separate genuinely new suggestions
  from ones already covered.

```bash
pip install -r requirements.txt
python generate_test_design.py
```

## `ai_update_test_data.py`

Dynamically updates the JS framework's real test data workbook
(`test-data/TestData.xlsx`) from a natural-language instruction — the "use
AI to manage and update it dynamically" deliverable.

```bash
python ai_update_test_data.py --sheet TravellerDetails \
  --instruction "add a negative case with an empty passport number for an international booking" \
  --scenario-id TRAVELLER_DETAILS_MISSING_PASSPORT
# add --dry-run to preview without writing
```

It shows the LLM the sheet's *actual* headers and a few real sample rows so
the proposed row matches the existing schema, then appends it via
`openpyxl`. Already used for real: `TRAVELLER_DETAILS_MISSING_PASSPORT` is
now a genuine row in `test-data/TestData.xlsx`, immediately usable from a
`.feature` file the same way as any other `scenarioId`.

**Caveat:** the JS framework's `pretest` npm script
(`src/utils/generateTestData.js`) regenerates `TestData.xlsx` from scratch
on every `npm test` run. A row added by this tool will be silently
overwritten by the next `npm test` unless you also add it to
`generateTestData.js`, or run `npx cucumber-js` directly (skipping
`pretest`) when you want a dynamically-added row to persist for that run.

## Design notes

- **Manual test cases are derived structurally, not generated freely.**
  Given/When steps (and their `And` continuations) become "Steps"; Then
  steps become "Expected Result" — parsed directly from the real Gherkin
  in `common/feature_reader.py`. The LLM's only contribution per case is a
  single one-sentence "Objective" summarizing a scenario it's *given*,
  which is much lower-risk than asking it to invent test cases from
  requirements text (the fabrication failure mode documented in Phase
  7's README).
- **"Convert to automated scripts" is satisfied in reverse.** Automation
  already exists (Phase 4, built before this phase). Re-deriving scripts
  from these manual cases would just reproduce what's already
  built-and-verified, so `manual_to_automated_mapping.md` proves the link
  instead.
- **Boundary/negative suggestion parsing needed a second fix.** The model
  sometimes prepended a "Here are 18 ideas:" line or appended a "Note:
  ..." summary, both of which parsed as fake ideas until filtered by
  prefix — same class of issue as Phase 1's coverage-check parsing, worth
  watching for generally when parsing free-text LLM output as a list.
