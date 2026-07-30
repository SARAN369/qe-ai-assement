# Requirements Analysis (Gen AI-extracted)

Source: `docs/AI Usecase.docx` — Use Case Scenario section (items a-j).

**FUNCTIONAL REQUIREMENTS:**

1. Launch MakeMyTrip.
2. Dismiss popups.
3. Select "Multi-city" tab.
4. Add 3 routes with valid cities and future dates.
5. Verify all route fields populate correctly.
6. Select traveller count.
7. Choose travel class.
8. Click Search.
9. Verify search results load within 10 seconds with route summary header.
10. Apply filters: Flight type, Preferred airlines, Departure time slots.
11. Verify filter chips display active count.
12. Sort results by price/duration and validate flight list refreshes asynchronously.
13. Extract the first 3 flight details: Airline name, Flight number, Departure/arrival times, Duration, Price.
14. Store in structured format.
15. Select any flight combination and click Book.
16. Fill mandatory traveller details: Name, Age, Gender, Passport (for international).
17. Verify Email validation, Phone validation, and Add frequent flyer number if available.
18. On the Seat Selection page, verify seat map renders for all legs.
19. Select available seats (window/aisle/middle) and capture seat numbers and individual prices.
20. Verify seats highlight upon selection.
21. Add extra baggage for any/all legs and verify baggage charges display per leg.
22. Add meal preferences (veg/non-veg/special) if available and capture add-on summary.
23. Add optional travel insurance and enter GST details if business booking option exists.
24. Verify GST fields validate format (company name, GSTIN pattern).
25. Review booking summary and verify line items: Base fare, Seat charges, Baggage fees, Meal charges, Insurance, Convenience fee, Taxes.
26. Calculate expected total by summing all individual charges and compare with the displayed grand total within ±2% tolerance for rounding/dynamic pricing.
27. Proceed to the payment gateway and verify payment options load successfully.

**NON-FUNCTIONAL REQUIREMENTS:**

1. Results load within 10 seconds.
2. GSTIN pattern validation.
3. ±2% tolerance for rounding/dynamic pricing.
4. Email validation.
5. Phone validation.
6. Seat map renders for all legs.
7. Seats highlight upon selection.
8. Baggage charges display per leg.
9. GST fields validate format (company name, GSTIN pattern).
10. All amounts are displayed correctly with ±2% tolerance for rounding/dynamic pricing.
11. Payment options load successfully.
