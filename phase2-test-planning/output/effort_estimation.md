# Effort Estimation

## Scope metrics (actual, not estimated)

- Automated Gherkin scenarios: 27 (20 positive, 7 negative)
- Use-case requirements (from requirement doc, items a-j): 10
- Page Objects implemented: 8 (AddOnsPage, BookingSummaryPage, HomePage, InsurancePage, PaymentPage, SearchResultsPage, SeatSelectionPage, TravellerDetailsPage)
- STLC phases covered by this project: 7 of 7
- Application under test: multi-city flight booking with seats, baggage, meals, insurance/GST, fare review, and payment (MakeMyTrip)

## Estimate

Person-day figures are computed from the scope metrics above via fixed, transparent ratios (see `generate_test_plan.py::compute_effort_days`) — the LLM contributes the rationale text per activity, not the arithmetic (see Design notes in README.md for why).

- **Requirement analysis: 5.0 person-days** — The requirement analysis activity is estimated to require approximately 5.0 person-days, calculated by multiplying the effort per use-case requirement (0.5 person-day) by the total number of use-case requirements (10), indicating a moderate level of complexity in this phase of the testing process.
- **Test design (manual cases + automation scripts): 20.2 person-days** — The estimated effort of 20.2 person-days allocated to test design is based on the assumption that each scenario requires approximately 0.75 person-day of work, which accounts for both manual case authoring and automation script development.
- **Framework setup: 13.0 person-days** — The estimated effort of 13.0 person-days for setting up the framework is justified by the need to establish a solid foundation with a base of 5 person-days and expand upon it with an additional 8 page objects, totaling a comprehensive setup process.
- **Test execution & stabilization: 6.8 person-days** — The estimated effort of 6.8 person-days allocated to "Test execution & stabilization" is based on the assumption that each of the 27 scenarios requires approximately 0.25 person-day of testing time, reflecting our thorough approach to ensuring stability and quality in our test execution process.
- **Reporting & documentation: 3 person-days** — The estimated effort of 3 person-days for this activity is sufficient to ensure that all necessary reporting and documentation requirements are thoroughly addressed, without overextending resources or compromising quality.

**Total: 48.0 person-days** (~9.6 working weeks for a single engineer)
