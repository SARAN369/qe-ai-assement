# Boundary Value & Negative Test Case Suggestions

AI-proposed boundary/negative ideas from the Use Case Scenario text, each checked against the existing 7 `@negative`-tagged automated scenarios (keyword-overlap match, min score 3):

- ✅ Already covered — 1. `Departure date`: Test that booking fails when departure date is in the past. (*Attempt to select a past date for a route*)
- ✅ Already covered — 2. `Return date`: Test that booking fails when return date is not provided or is in the past. (*Attempt to select a past date for a route*)
- ✅ Already covered — 3. `Age validation`: Test that booking fails when traveller age is invalid (e.g., negative number, non-numeric input). (*Enter invalid child age while setting traveller count*)
- 🆕 New suggestion — 4. `Email validation`: Test that booking fails when email address is invalid or missing.
- 🆕 New suggestion — 5. `Phone number validation`: Test that booking fails when phone number is invalid or missing.
- 🆕 New suggestion — 6. `Seat selection boundary`: Test that seat selection works correctly for all available seats (e.g., 10 rows, 20 columns).
- 🆕 New suggestion — 7. `Baggage weight limit`: Test that booking fails when baggage weight exceeds the maximum allowed weight.
- ✅ Already covered — 8. `GSTIN validation`: Test that booking fails when GSTIN is invalid or missing. (*Enter an invalid GSTIN pattern*)
- 🆕 New suggestion — 9. `Travel class boundary`: Test that booking fails when travel class is not selected (e.g., economy, business).
- 🆕 New suggestion — 10. `Flight type filter`: Test that filtering by flight type works correctly for different airlines.
- 🆕 New suggestion — 11. `Departure time slot filter`: Test that filtering by departure time slot works correctly for different time ranges.
- ✅ Already covered — 12. `Traveller count boundary`: Test that booking fails when traveller count is not selected (e.g., 1, 2). (*Enter invalid child age while setting traveller count*)
- 🆕 New suggestion — 13. `Flight number validation`: Test that booking fails when flight number is invalid or missing.
- 🆕 New suggestion — 14. `Airline name filter`: Test that filtering by airline name works correctly for different airlines.
- 🆕 New suggestion — 15. `Duration filter`: Test that filtering by duration works correctly for different time ranges.
- 🆕 New suggestion — 16. `Price filter`: Test that filtering by price works correctly for different price ranges.
- 🆕 New suggestion — 17. `Meal preference validation`: Test that booking fails when meal preference is invalid or missing (e.g., "special" meal).
- ✅ Already covered — 18. `Convenience fee calculation`: Test that convenience fee is calculated correctly and falls within a ±2% tolerance of the expected total. (*Detect a total mismatch beyond the allowed tolerance*)
