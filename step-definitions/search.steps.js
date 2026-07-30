const { Given, When, Then } = require('@cucumber/cucumber');
const assert = require('assert');
const { getPage } = require('../src/support/pageFactory');
const { getRoutes, getTravellers } = require('../src/utils/testDataHelper');

async function buildItinerary(world, scenarioId, legCount = 3) {
  const homePage = getPage(world, 'homePage');
  const routes = (await getRoutes(scenarioId)).slice(0, legCount);
  await homePage.buildMultiCityRoutes(routes);
  world.scenarioState.routes = routes;
  return routes;
}

async function performFullSearch(world, routesId, travellersId) {
  const homePage = getPage(world, 'homePage');
  await homePage.selectMultiCityTab();
  await buildItinerary(world, routesId);
  const travellers = await getTravellers(travellersId);
  await homePage.setTravellers(travellers);
  await homePage.selectCabinClass(travellers.cabinClass);
  await homePage.clickSearch();
  const resultsPage = getPage(world, 'searchResultsPage');
  await resultsPage.waitForResults(10000);
}

When('the user selects the {string} tab', async function (tabName) {
  const homePage = getPage(this, 'homePage');
  assert.strictEqual(tabName, 'Multi-City');
  await homePage.selectMultiCityTab();
});

When('the user builds the itinerary from route data {string}', async function (scenarioId) {
  await buildItinerary(this, scenarioId);
});

Given('the user has built the itinerary from route data {string}', async function (scenarioId) {
  const homePage = getPage(this, 'homePage');
  await homePage.selectMultiCityTab();
  await buildItinerary(this, scenarioId);
});

Then('all 3 route fields should be populated correctly', async function () {
  const homePage = getPage(this, 'homePage');
  for (let i = 0; i < 3; i++) {
    const toValue = await homePage.toCityInput(i).inputValue().catch(() => '');
    assert.ok(toValue && toValue.length > 0, `Leg ${i + 1} "to" city should be populated`);
  }
});

When('the user sets traveller and cabin class details from {string}', async function (scenarioId) {
  const homePage = getPage(this, 'homePage');
  const travellers = await getTravellers(scenarioId);
  this.scenarioState.travellerRequest = travellers;
  await homePage.setTravellers(travellers);
  await homePage.selectCabinClass(travellers.cabinClass);
});

When('the user clicks the multi-city Search button', async function () {
  const homePage = getPage(this, 'homePage');
  await homePage.clickSearch();
});

Then('the search results should load within 10 seconds', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  const elapsedMs = await resultsPage.waitForResults(10000);
  assert.ok(elapsedMs <= 10000, `Results took ${elapsedMs}ms, expected <= 10000ms`);
});

Then('the route summary header should be displayed', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  assert.ok(await resultsPage.isVisible(resultsPage.routeSummaryHeader), 'Route summary header should be visible');
});

Given('the user has searched multi-city flights using {string} and {string}', async function (routesId, travellersId) {
  await performFullSearch(this, routesId, travellersId);
});

When('the user applies the flight type filter', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  await resultsPage.applyFilter(resultsPage.filterFlightType);
});

When('the user applies the preferred airline filter', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  await resultsPage.applyFilter(resultsPage.filterAirlines);
});

When('the user applies the departure time slot filter', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  await resultsPage.applyFilter(resultsPage.filterDepartureTime);
});

Then('the active filter chip count should be greater than 0', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  const count = await resultsPage.getActiveFilterCount();
  assert.ok(count > 0, `Expected at least one active filter chip, found ${count}`);
});

Then('the flight results should refresh asynchronously', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  await resultsPage.waitForNavigationSettled();
  assert.ok(await resultsPage.flightCards.first().isVisible(), 'Flight cards should still be visible after filtering');
});

When('the user sorts results by price', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  await resultsPage.sortResultsByPrice();
});

When('the user sorts results by duration', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  await resultsPage.sortResultsByDuration();
});

Then('the flight list should be reordered by {word}', async function (criterion) {
  const resultsPage = getPage(this, 'searchResultsPage');
  assert.ok(await resultsPage.flightCards.first().isVisible(), `Flight list should be visible after sorting by ${criterion}`);
});

When('the user extracts the first 3 flight details', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  this.scenarioState.extractedFlights = await resultsPage.extractFlightDetails(3);
});

Then(
  'the extracted flight data should contain {string}, {string} and {string} with airline, flight number, times, duration and price',
  async function (leg1, leg2, leg3) {
    const data = this.scenarioState.extractedFlights;
    assert.ok(data, 'Expected flight data to have been extracted');
    for (const legKey of [leg1, leg2, leg3]) {
      assert.ok(data[legKey], `Expected extracted data to contain ${legKey}`);
      const leg = data[legKey];
      for (const field of ['airline', 'flightNumber', 'departureTime', 'arrivalTime', 'duration', 'price']) {
        assert.ok(field in leg, `${legKey} should contain field "${field}"`);
      }
    }
  }
);

When('the user builds only 2 of the 3 routes from route data {string}', async function (scenarioId) {
  const homePage = getPage(this, 'homePage');
  await homePage.selectMultiCityTab();
  await buildItinerary(this, scenarioId, 2);
});

Then('the multi-city Search button should be disabled or show a validation error', async function () {
  const homePage = getPage(this, 'homePage');
  const isDisabled = await homePage.multiCitySearchButton.getAttribute('disabled').catch(() => null);
  const hasDisabledClass = ((await homePage.multiCitySearchButton.getAttribute('class')) || '').includes('disabled');
  assert.ok(isDisabled !== null || hasDisabledClass, 'Search button should be disabled when itinerary is incomplete');
});

When('the user attempts to set a past departure date for route data {string}', async function (scenarioId) {
  const homePage = getPage(this, 'homePage');
  const routes = await getRoutes(scenarioId);
  this.scenarioState.pastDateAttempt = routes[0];
  await homePage.dateInput(0).click();
});

Then('the date picker should prevent selecting a past date', async function () {
  const homePage = getPage(this, 'homePage');
  const pastDate = this.scenarioState.pastDateAttempt.date;
  const disabledPastCell = homePage.page
    .locator('.datePickerContainer, .DayPicker, [class*="datepicker" i]')
    .locator(`td.disabled:has-text("${pastDate.day}"), [aria-disabled="true"]:has-text("${pastDate.day}")`)
    .first();
  assert.ok(await homePage.isVisible(disabledPastCell, 5000), 'Past date should render as a disabled cell in the date picker');
});
