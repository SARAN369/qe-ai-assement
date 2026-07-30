# Identified Test Scenarios vs. Actual Coverage

AI-proposed scenario titles (from the extracted requirements), each checked against whether a matching scenario already exists in `features/multiCityFlightBooking.feature` (keyword-overlap match, threshold >= 3 — same technique as the RTM above):

- ❌ **Launch MakeMyTrip** — no matching automated scenario found (potential gap)
- ❌ **Dismiss popups** — no matching automated scenario found (potential gap)
- ✅ **Select "Multi-city" tab and add 3 routes with valid cities and future dates** — covered by: *Add 3 valid multi-city routes and verify fields populate correctly*
- ✅ **Verify all route fields populate correctly after adding new routes** — covered by: *Add 3 valid multi-city routes and verify fields populate correctly*
- ✅ **Select traveller count and choose travel class** — covered by: *Search for multi-city flights with valid traveller count and cabin class*
- ❌ **Click Search and verify search results load within 10 seconds with route summary header** — no matching automated scenario found (potential gap)
- ✅ **Apply filters: Flight type, Preferred airlines, Departure time slots and verify filter chips display active count** — covered by: *Apply flight type filter and verify the active filter chip count increases*
- ✅ **Sort results by price/duration and validate flight list refreshes asynchronously** — covered by: *Sort flight results by price*
- ✅ **Extract the first 3 flight details: Airline name, Flight number, Departure/arrival times, Duration, Price** — covered by: *Extract first 3 flight details in structured format*
- ❌ **Store in structured format** — no matching automated scenario found (potential gap)
- ✅ **Select any flight combination and click Book** — covered by: *Select a flight combination and proceed to traveller details*
- ✅ **Fill mandatory traveller details: Name, Age, Gender, Passport (for international) and verify Email validation, Phone validation, and Add frequent flyer number if available** — covered by: *Fill mandatory traveller details with valid data*
- ✅ **On the Seat Selection page, verify seat map renders for all legs and select available seats (window/aisle/middle)** — covered by: *Verify seat map renders for all legs*
- ✅ **Verify seats highlight upon selection and add extra baggage for any/all legs** — covered by: *Select available seats and verify highlight on selection*
- ✅ **Add meal preferences (veg/non-veg/special) if available and capture add-on summary** — covered by: *Add a meal preference and capture the add-on summary*
- ✅ **Add optional travel insurance and enter GST details if business booking option exists** — covered by: *Enter valid GST details for a business booking*
- ✅ **Verify GST fields validate format (company name, GSTIN pattern) and review booking summary** — covered by: *Review booking summary and verify all fare line items are displayed*
- ✅ **Review booking summary and verify line items: Base fare, Seat charges, Baggage fees, Meal charges, Insurance, Convenience fee, Taxes** — covered by: *Review booking summary and verify all fare line items are displayed*
- ✅ **Calculate expected total by summing all individual charges and compare with the displayed grand total within ±2% tolerance for rounding/dynamic pricing** — covered by: *Computed total matches the displayed grand total within tolerance*
- ✅ **Proceed to the payment gateway and verify payment options load successfully** — covered by: *Proceed to the payment gateway and verify payment options load*
