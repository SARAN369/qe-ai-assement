# Manual Test Case -> Automated Script Traceability

Every manual test case here already has a corresponding automated Playwright/Cucumber scenario — that automation was built in Phase 4, before this phase existed, so rather than re-deriving scripts from these manual cases, this maps each one to where its automation actually lives.

| TC ID | Manual Test Case | Automated Scenario | Location |
|---|---|---|---|
| TC-001 | Add 3 valid multi-city routes and verify fields populate correctly | Add 3 valid multi-city routes and verify fields populate correctly | `features/multiCityFlightBooking.feature` |
| TC-002 | Search for multi-city flights with valid traveller count and cabin class | Search for multi-city flights with valid traveller count and cabin class | `features/multiCityFlightBooking.feature` |
| TC-003 | Apply flight type filter and verify the active filter chip count increases | Apply flight type filter and verify the active filter chip count increases | `features/multiCityFlightBooking.feature` |
| TC-004 | Apply preferred airline filter and verify results refresh | Apply preferred airline filter and verify results refresh | `features/multiCityFlightBooking.feature` |
| TC-005 | Apply departure time slot filter and verify results refresh | Apply departure time slot filter and verify results refresh | `features/multiCityFlightBooking.feature` |
| TC-006 | Sort flight results by price | Sort flight results by price | `features/multiCityFlightBooking.feature` |
| TC-007 | Sort flight results by duration | Sort flight results by duration | `features/multiCityFlightBooking.feature` |
| TC-008 | Extract first 3 flight details in structured format | Extract first 3 flight details in structured format | `features/multiCityFlightBooking.feature` |
| TC-009 | Attempt search with an incomplete itinerary | Attempt search with an incomplete itinerary | `features/multiCityFlightBooking.feature` |
| TC-010 | Attempt to select a past date for a route | Attempt to select a past date for a route | `features/multiCityFlightBooking.feature` |
| TC-011 | Select a flight combination and proceed to traveller details | Select a flight combination and proceed to traveller details | `features/multiCityFlightBooking.feature` |
| TC-012 | Fill mandatory traveller details with valid data | Fill mandatory traveller details with valid data | `features/multiCityFlightBooking.feature` |
| TC-013 | Add a frequent flyer number | Add a frequent flyer number | `features/multiCityFlightBooking.feature` |
| TC-014 | Enter invalid child age while setting traveller count | Enter invalid child age while setting traveller count | `features/multiCityFlightBooking.feature` |
| TC-015 | Submit traveller details with invalid contact information | Submit traveller details with invalid contact information | `features/multiCityFlightBooking.feature` |
| TC-016 | Leave mandatory traveller name field blank | Leave mandatory traveller name field blank | `features/multiCityFlightBooking.feature` |
| TC-017 | Verify seat map renders for all legs | Verify seat map renders for all legs | `features/multiCityFlightBooking.feature` |
| TC-018 | Select available seats and verify highlight on selection | Select available seats and verify highlight on selection | `features/multiCityFlightBooking.feature` |
| TC-019 | Add extra baggage for a leg and verify charges display | Add extra baggage for a leg and verify charges display | `features/multiCityFlightBooking.feature` |
| TC-020 | Add a meal preference and capture the add-on summary | Add a meal preference and capture the add-on summary | `features/multiCityFlightBooking.feature` |
| TC-021 | Add optional travel insurance | Add optional travel insurance | `features/multiCityFlightBooking.feature` |
| TC-022 | Enter valid GST details for a business booking | Enter valid GST details for a business booking | `features/multiCityFlightBooking.feature` |
| TC-023 | Enter an invalid GSTIN pattern | Enter an invalid GSTIN pattern | `features/multiCityFlightBooking.feature` |
| TC-024 | Review booking summary and verify all fare line items are displayed | Review booking summary and verify all fare line items are displayed | `features/multiCityFlightBooking.feature` |
| TC-025 | Computed total matches the displayed grand total within tolerance | Computed total matches the displayed grand total within tolerance | `features/multiCityFlightBooking.feature` |
| TC-026 | Detect a total mismatch beyond the allowed tolerance | Detect a total mismatch beyond the allowed tolerance | `features/multiCityFlightBooking.feature` |
| TC-027 | Proceed to the payment gateway and verify payment options load | Proceed to the payment gateway and verify payment options load | `features/multiCityFlightBooking.feature` |
