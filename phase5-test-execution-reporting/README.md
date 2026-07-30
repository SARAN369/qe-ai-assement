# Phase 5: Test Execution and Reporting

## What this analyzes

A **real** `cucumber-js` run's JSON output (`reports/cucumber-report.json`),
not a mocked/fabricated one. Produced from the repo root with:

```bash
npx cucumber-js --tags "@smoke or @negative" --require-module dotenv/config \
  --require src/support/**/*.js --require step-definitions/**/*.js \
  --format progress-bar --format json:reports/cucumber-report.json
```

A representative 9-scenario tagged subset, not the full 32 — every
scenario's shared `Background` step launches the live MakeMyTrip site, and
this sandbox's network is blocked by MakeMyTrip's WAF (documented in the
root README), so every scenario here fails at the same step regardless of
what it individually tests. Running the full suite would just multiply
identical ~1-second failures 3-4x longer for no new information — this
subset already produces genuine, analyzable pass/fail data.

## Outputs

- **`output/ai_summary_report.md`** — pass/fail trends and failure
  clusters (computed in code), narrated by the LLM.
- **`output/defect_prediction.md`** — see "AI-based defect prediction"
  below for why this is a risk heuristic, not a prediction model.

## Setup & run

```bash
pip install -r requirements.txt
python analyze_results.py
```

Requires `reports/cucumber-report.json` to already exist (run the
`cucumber-js` command above first, from the repo root).

## Actual result (this run)

9/9 scenarios failed, 100% clustering into one signature: `Network error:
ERR_HTTP2_PROTOCOL_ERROR` — i.e., the sandbox's known network block, not
an application defect. This is itself a legitimate, valuable defect-
clustering outcome: a real analyzer correctly recognizing "these 9
failures share one non-application root cause" is exactly what clustering
is for, homogeneous or not.

## Design notes

- **Trends/clusters are computed in code, not by the LLM** — `Counter`s
  and a `re`-based error-signature canonicalizer. Same principle as
  Phase 1/2: numbers and grouping come from code, the LLM only narrates.
- **A real misattribution, caught and fixed.** The first version of the
  narrative prompt produced: *"Given the presence of multiple instances of
  invalid contact information as a root cause category, it's likely that
  we're experiencing problems with data validation..."* — the model saw a
  scenario **named** "Submit traveller details with invalid contact
  information" listed under the failure cluster and concluded that
  contact-info validation was somehow the cause, when the actual cause
  (the cluster's own signature) was 100% network/environment, unrelated
  to what any individual scenario tests. Fixed by explicitly telling the
  prompt that a cluster's scenario list is *which tests were affected*,
  not *evidence of why* — the signature alone determines root cause.
  Worth watching for generally: an LLM summarizing grouped data may
  conflate group *membership* with group *cause* if the members' names
  are topically suggestive.
- **A regex bug, caught by inspecting output.** `net::([A-Z_]+)` doesn't
  match digits, so `ERR_HTTP2_PROTOCOL_ERROR` was truncated to `ERR_HTTP`
  in the cluster signature. Fixed to `[A-Z0-9_]+`.

## AI-based defect prediction (optional deliverable)

A trained defect-prediction model needs historical multi-run failure
data, which doesn't exist for a project with one real execution. Rather
than fabricate a fake model or invented "risk scores", `defect_prediction.md`
is an honestly-labeled heuristic instead: it counts how many scenarios
depend on the live external site vs. are pure computation (from real
per-scenario data), and has the LLM narrate what that dependency-surface
split implies about environmental risk — clearly caveated as heuristic,
not predictive, in the LLM's own output.
