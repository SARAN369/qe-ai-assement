# AI Test Execution Summary Report

Source: `reports/cucumber-report.json` (real `cucumber-js` run — see README for scope/why).

## Pass/Fail Trends (computed, not AI-generated)

```
Total scenarios: 9
  failed: 9 (100.0%)

By tag:
  @booking: {'failed': 4}
  @flightBooking: {'failed': 9}
  @negative: {'failed': 8}
  @payment: {'failed': 2}
  @positive: {'failed': 1}
  @search: {'failed': 3}
  @smoke: {'failed': 1}

Failure clusters (by canonicalized error signature):
  [9x] Network error: ERR_HTTP2_PROTOCOL_ERROR
      - Add 3 valid multi-city routes and verify fields populate correctly
      - Attempt search with an incomplete itinerary
      - Attempt to select a past date for a route
      - Enter invalid child age while setting traveller count
      - Submit traveller details with invalid contact information
      - Submit traveller details with invalid contact information
      - Leave mandatory traveller name field blank
      - Enter an invalid GSTIN pattern
      - Detect a total mismatch beyond the allowed tolerance
```

## AI Narrative Summary

Here is a short executive summary:

Our test execution results indicate that all 9 scenarios failed, with no passing results. The dominant failure cluster has a canonicalized error signature of "Network error: ERR_HTTP2_PROTOCOL_ERROR", indicating an issue related to HTTP/2 protocol errors in our system. This root cause falls under the category of environment/network issues. To address this, we recommend adding additional validation and error handling for HTTP/2 protocol errors in our application, particularly for scenarios involving multi-city routes, incomplete itineraries, and traveller details submission.
