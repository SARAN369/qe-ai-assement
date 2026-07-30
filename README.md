# AI-Powered Multi-City Flight Booking Automation

Playwright (JavaScript) + Cucumber BDD + Page Object Model test automation
framework built for the capstone use case **"Multi-City Flight Booking with
Ancillary Services"** on [MakeMyTrip](https://www.makemytrip.com).

## STLC Phases

All seven STLC phases from the capstone brief are implemented. Each
AI-powered phase uses a local Ollama LLM (llama3.2:3b) with the same
design principle: deterministic code for numbers/logic/validation,
LLM only for prose and proposals.

| Phase | Directory | What it does |
|-------|-----------|-------------|
| 1 — Requirement Analysis | [`phase1-requirement-analysis/`](phase1-requirement-analysis/) | Extracts functional + non-functional requirements from the docx, builds an RTM (Excel), checks scenario coverage |
| 2 — Test Planning | [`phase2-test-planning/`](phase2-test-planning/) | Generates effort estimation (code-computed, LLM-narrated) and a Test Plan document (docx) |
| 3 — Test Design | [`phase3-test-design/`](phase3-test-design/) | Manual test cases (Excel), manual-to-automated traceability, boundary/negative suggestions, AI-assisted test data generation |
| 4 — Framework Development | Root project (`src/`, `features/`, `step-definitions/`) | Playwright + Cucumber BDD + POM framework (this README's main content below) |
| 5 — Test Execution & Reporting | [`phase5-test-execution-reporting/`](phase5-test-execution-reporting/) | Analyzes real cucumber-js JSON output: pass/fail trends, failure clustering, AI narrative summary, defect risk heuristic |
| 6 — Agentic AI Automation | [`phase6-agentic-automation/`](phase6-agentic-automation/) | browser-use agentic bot (natural-language → browser actions), self-healing locator module (LLM-powered selector repair) |
| 7 — AI Testing Assistant | [`ai-testing-assistant/`](ai-testing-assistant/) | CLI chatbot that answers requirement/test-case questions from the docx and feature file via local Ollama |

**Shared library:** [`common/`](common/) — Ollama client, docx reader,
feature file parser, keyword matcher — used across phases 1, 3, 5, 7.

## Tech stack

| Concern            | Choice                                   |
|---------------------|-------------------------------------------|
| Browser automation | Playwright (`playwright`, JavaScript)      |
| Test structure      | BDD via `@cucumber/cucumber` (Gherkin)     |
| Design pattern       | Page Object Model                          |
| Test data           | Excel (`exceljs`) — `test-data/TestData.xlsx` |
| Reporting            | `multiple-cucumber-html-reporter` (HTML)   |

## Project structure

```
features/                        Gherkin feature files
step-definitions/                Step definitions (Given/When/Then), one file per flow area
src/
  pages/                         Page Objects (one class per app page/section)
  support/
    world.js                    Custom Cucumber World (scenario-scoped state)
    hooks.js                    Browser lifecycle (Before/After), screenshot-on-failure
    pageFactory.js               Lazy, memoized page-object accessor for step defs
    flowHelpers.js               Reusable multi-step navigation chains (e.g. reach seat selection)
  utils/
    excelHelper.js               Generic Excel read/write (exceljs)
    testDataHelper.js            Typed accessors over TestData.xlsx sheets
    generateTestData.js          Regenerates TestData.xlsx (run automatically via `pretest`)
    generateReport.js            Builds the HTML report from the Cucumber JSON output
test-data/TestData.xlsx          Generated test data (Routes, Travellers, TravellerDetails, GstData, Baggage)
reports/                          Cucumber JSON/HTML output + failure screenshots (generated, gitignored)
cucumber.js                       Cucumber CLI profiles
```

## Setup

```bash
npm install
npm run install:browsers
```

## Running tests

```bash
npm test                 # all scenarios
npm run test:positive    # @positive tagged scenarios only
npm run test:negative    # @negative tagged scenarios only
npm run test:search      # @search tagged scenarios only (Phase a-c: itinerary, filters, sort, extract)
```

`npm test` regenerates `test-data/TestData.xlsx` first (`pretest`) and builds
the HTML report afterwards (`posttest`) at `reports/html-report/index.html`.

Set `HEADLESS=false` (see `.env.example`) to watch the browser while
debugging locally.

## Scenario coverage

`features/multiCityFlightBooking.feature` implements the full use case
(steps a-j from the brief) as 32 scenarios (well over the "not less than 20"
requirement), tagged `@search`, `@booking`, `@seats`, `@addons`, `@payment`
and `@positive`/`@negative`:

- **Search (a-c):** multi-city route entry across 3 legs with future dates,
  traveller count/class selection, filters (flight type, airline, departure
  time), sort (price/duration), incomplete-itinerary and past-date negative
  cases.
- **Extraction (d):** first 3 flight cards parsed into the `{leg1, leg2,
  leg3}` structured object from the brief.
- **Traveller details (e):** valid submission, frequent flyer number,
  invalid email/phone/child age, missing required field.
- **Seats (f):** seat map rendering per leg, window/aisle/middle selection,
  highlight verification.
- **Add-ons (g):** baggage charge display per leg, meal preference summary.
- **Insurance/GST (h):** plan selection, valid/invalid GSTIN format
  (regex-validated against the real GSTIN pattern).
- **Fare review (i-j):** all fare line items present, computed-total-vs-
  displayed-total check within the brief's ±2% tolerance (both a passing
  and an intentionally-mismatched case), payment options load.

## Test data

All scenario inputs (routes, traveller counts, traveller PII, GST numbers,
baggage options) live in `test-data/TestData.xlsx`, one sheet per data type,
keyed by `scenarioId`. Step definitions never hardcode data — they look it
up via `src/utils/testDataHelper.js`. The workbook is regenerated by
`src/utils/generateTestData.js` so its schema can't drift from what the
step definitions expect; edit that script (not the checked-in `.xlsx`
directly) to add new data rows.

## Important limitation: live execution in this environment

The page objects' selectors (`#fromAnotherCity0`, `.btnAddCity`,
`.fltWidgetSearchBtnMultiCity`, etc.) were captured from the **live**
makemytrip.com DOM, not guessed. However, this sandbox's outbound network
could not reach makemytrip.com to run the suite end-to-end: direct HTTP
requests from this environment were rejected by MakeMyTrip's WAF (`403`,
then timeouts even with full browser headers), which is common bot/
datacenter-IP protection on production travel sites. `npx cucumber-js
--dry-run` was used instead to verify every one of the 32 scenarios' 200
steps resolves to exactly one step definition (no undefined/ambiguous
steps) — that passed cleanly. **Run `npm test` from your own machine/network
to execute live** and confirm selectors still match (MakeMyTrip's markup
changes periodically, as with most production SPAs — that's the intended
target for the framework's AI-assisted self-healing hooks in
`HomePage.selectCity()`, which already falls back to keyboard navigation if
a suggestion-list selector stops matching).

## Extending the framework

- New scenario: add to `features/multiCityFlightBooking.feature`, add data
  rows to `generateTestData.js` if needed, implement any new steps in the
  relevant `step-definitions/*.steps.js` file.
- New page/section: add a class under `src/pages/` extending `BasePage`,
  register it in `src/support/pageFactory.js`.
- New data sheet: add a worksheet in `generateTestData.js` and a typed
  accessor in `src/utils/testDataHelper.js`.
