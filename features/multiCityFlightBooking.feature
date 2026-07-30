@flightBooking
Feature: Multi-City Flight Booking with Ancillary Services
  As a traveller
  I want to book a multi-city flight itinerary with seats, baggage, meals, insurance and GST details
  So that I can complete an end-to-end trip booking on MakeMyTrip

  Background:
    Given the user launches MakeMyTrip and dismisses any popups

  # ---------------------------------------------------------------------
  # Phase a-c: Multi-city search, traveller/class selection, filters, sort
  # ---------------------------------------------------------------------

  @smoke @positive @search
  Scenario: Add 3 valid multi-city routes and verify fields populate correctly
    When the user selects the "Multi-City" tab
    And the user builds the itinerary from route data "MULTI_CITY_VALID"
    Then all 3 route fields should be populated correctly

  @positive @search
  Scenario: Search for multi-city flights with valid traveller count and cabin class
    Given the user has built the itinerary from route data "MULTI_CITY_VALID"
    When the user sets traveller and cabin class details from "TRAVELLER_VALID"
    And the user clicks the multi-city Search button
    Then the search results should load within 10 seconds
    And the route summary header should be displayed

  @positive @search
  Scenario: Apply flight type filter and verify the active filter chip count increases
    Given the user has searched multi-city flights using "MULTI_CITY_VALID" and "TRAVELLER_VALID"
    When the user applies the flight type filter
    Then the active filter chip count should be greater than 0

  @positive @search
  Scenario: Apply preferred airline filter and verify results refresh
    Given the user has searched multi-city flights using "MULTI_CITY_VALID" and "TRAVELLER_VALID"
    When the user applies the preferred airline filter
    Then the flight results should refresh asynchronously

  @positive @search
  Scenario: Apply departure time slot filter and verify results refresh
    Given the user has searched multi-city flights using "MULTI_CITY_VALID" and "TRAVELLER_VALID"
    When the user applies the departure time slot filter
    Then the flight results should refresh asynchronously

  @positive @search
  Scenario: Sort flight results by price
    Given the user has searched multi-city flights using "MULTI_CITY_VALID" and "TRAVELLER_VALID"
    When the user sorts results by price
    Then the flight list should be reordered by price

  @positive @search
  Scenario: Sort flight results by duration
    Given the user has searched multi-city flights using "MULTI_CITY_VALID" and "TRAVELLER_VALID"
    When the user sorts results by duration
    Then the flight list should be reordered by duration

  @positive @search
  Scenario: Extract first 3 flight details in structured format
    Given the user has searched multi-city flights using "MULTI_CITY_VALID" and "TRAVELLER_VALID"
    When the user extracts the first 3 flight details
    Then the extracted flight data should contain "leg1", "leg2" and "leg3" with airline, flight number, times, duration and price

  @negative @search
  Scenario: Attempt search with an incomplete itinerary
    When the user selects the "Multi-City" tab
    And the user builds only 2 of the 3 routes from route data "MULTI_CITY_VALID"
    Then the multi-city Search button should be disabled or show a validation error

  @negative @search
  Scenario: Attempt to select a past date for a route
    When the user selects the "Multi-City" tab
    And the user attempts to set a past departure date for route data "MULTI_CITY_PAST_DATE"
    Then the date picker should prevent selecting a past date

  # ---------------------------------------------------------------------
  # Phase e: Traveller details and contact validation
  # ---------------------------------------------------------------------

  @positive @booking
  Scenario: Select a flight combination and proceed to traveller details
    Given the user has searched multi-city flights using "MULTI_CITY_VALID" and "TRAVELLER_VALID"
    When the user selects the first flight combination
    Then the traveller details page should be displayed

  @positive @booking
  Scenario Outline: Fill mandatory traveller details with valid data
    Given the user is on the traveller details page
    When the user fills traveller details from "<scenarioId>"
    And the user fills contact information from "<scenarioId>"
    And the user submits the traveller details form
    Then the traveller details should be accepted without validation errors

    Examples:
      | scenarioId               |
      | TRAVELLER_DETAILS_VALID  |

  @positive @booking
  Scenario: Add a frequent flyer number
    Given the user is on the traveller details page
    When the user adds frequent flyer number "AI123456789"
    Then the frequent flyer number field should retain the entered value

  @negative @booking
  Scenario: Enter invalid child age while setting traveller count
    Given the user has built the itinerary from route data "MULTI_CITY_VALID"
    When the user sets traveller and cabin class details from "TRAVELLER_INVALID_CHILD_AGE"
    Then a child age validation error should be displayed

  @negative @booking
  Scenario Outline: Submit traveller details with invalid contact information
    Given the user is on the traveller details page
    When the user fills traveller details from "<scenarioId>"
    And the user fills contact information from "<scenarioId>"
    And the user submits the traveller details form
    Then a "<field>" validation error should be displayed

    Examples:
      | scenarioId                        | field |
      | TRAVELLER_DETAILS_INVALID_EMAIL   | email |
      | TRAVELLER_DETAILS_INVALID_PHONE   | phone |

  @negative @booking
  Scenario: Leave mandatory traveller name field blank
    Given the user is on the traveller details page
    When the user fills traveller details from "TRAVELLER_DETAILS_MISSING_NAME"
    And the user submits the traveller details form
    Then a required field validation error should be displayed for the name field

  # ---------------------------------------------------------------------
  # Phase f-g: Seats, baggage, meals
  # ---------------------------------------------------------------------

  @positive @seats
  Scenario: Verify seat map renders for all legs
    Given the user is on the seat selection page
    Then the seat map should render for all 3 legs

  @positive @seats
  Scenario Outline: Select available seats and verify highlight on selection
    Given the user is on the seat selection page
    When the user selects a "<seatType>" seat
    Then the selected seat should be highlighted

    Examples:
      | seatType |
      | window   |
      | aisle    |
      | middle   |

  @positive @addons
  Scenario: Add extra baggage for a leg and verify charges display
    Given the user is on the add-ons page
    When the user adds baggage for leg 1 using data "BAGGAGE_VALID"
    Then the baggage charge for leg 1 should be displayed

  @positive @addons
  Scenario Outline: Add a meal preference and capture the add-on summary
    Given the user is on the add-ons page
    When the user selects "<meal>" meal preference
    Then the add-on summary should include the meal selection

    Examples:
      | meal     |
      | veg      |
      | non-veg  |
      | special  |

  # ---------------------------------------------------------------------
  # Phase h-j: Insurance, GST, fare review, payment
  # ---------------------------------------------------------------------

  @positive @payment
  Scenario: Add optional travel insurance
    Given the user is on the insurance page
    When the user selects the first available insurance plan
    Then the insurance plan should be marked as selected

  @positive @payment
  Scenario: Enter valid GST details for a business booking
    Given the user is on the insurance page
    When the user enables business booking
    And the user fills GST details from "GST_VALID"
    Then the GSTIN should be accepted without a validation error

  @negative @payment
  Scenario: Enter an invalid GSTIN pattern
    Given the user is on the insurance page
    When the user enables business booking
    And the user fills GST details from "GST_INVALID_PATTERN"
    Then a GSTIN format validation error should be displayed

  @positive @payment
  Scenario: Review booking summary and verify all fare line items are displayed
    Given the user is on the booking summary page
    Then the fare summary should display base fare, seat charges, baggage fees, meal charges, insurance, convenience fee and taxes

  @positive @payment
  Scenario: Computed total matches the displayed grand total within tolerance
    Given the user is on the booking summary page
    When the user sums all individual fare line items
    Then the computed total should match the displayed grand total within 2 percent tolerance

  @negative @payment
  Scenario: Detect a total mismatch beyond the allowed tolerance
    Given the following fare breakup is displayed:
      | baseFare | seatCharges | baggageFees | mealCharges | insurance | convenienceFee | taxes | displayedGrandTotal |
      | 4000     | 500         | 300         | 200         | 150       | 100            | 450   | 6500                |
    Then the computed total should not match the displayed grand total within 2 percent tolerance

  @positive @payment
  Scenario: Proceed to the payment gateway and verify payment options load
    Given the user is on the booking summary page
    When the user proceeds to payment
    Then the payment options should load successfully
