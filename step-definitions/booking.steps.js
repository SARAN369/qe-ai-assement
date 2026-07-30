const { Given, When, Then } = require('@cucumber/cucumber');
const assert = require('assert');
const { getPage } = require('../src/support/pageFactory');
const { getTravellerDetails } = require('../src/utils/testDataHelper');
const { reachTravellerDetails } = require('../src/support/flowHelpers');

When('the user selects the first flight combination', async function () {
  const resultsPage = getPage(this, 'searchResultsPage');
  await resultsPage.selectFlightCombination(0);
});

Then('the traveller details page should be displayed', async function () {
  const travellerPage = getPage(this, 'travellerDetailsPage');
  assert.ok(await travellerPage.isVisible(travellerPage.nameInput), 'Traveller name field should be visible');
});

Given('the user is on the traveller details page', async function () {
  await reachTravellerDetails(this);
});

When('the user fills traveller details from {string}', async function (scenarioId) {
  const travellerPage = getPage(this, 'travellerDetailsPage');
  const details = await getTravellerDetails(scenarioId);
  this.scenarioState.travellerDetails = details;
  await travellerPage.fillTraveller(details);
});

When('the user fills contact information from {string}', async function (scenarioId) {
  const travellerPage = getPage(this, 'travellerDetailsPage');
  const details = this.scenarioState.travellerDetails || (await getTravellerDetails(scenarioId));
  await travellerPage.fillContactInfo(details);
});

When('the user submits the traveller details form', async function () {
  const travellerPage = getPage(this, 'travellerDetailsPage');
  await travellerPage.submit();
});

Then('the traveller details should be accepted without validation errors', async function () {
  const travellerPage = getPage(this, 'travellerDetailsPage');
  assert.strictEqual(await travellerPage.getEmailValidationError(), false, 'Expected no email validation error');
  assert.strictEqual(await travellerPage.getPhoneValidationError(), false, 'Expected no phone validation error');
});

When('the user adds frequent flyer number {string}', async function (ffNumber) {
  const travellerPage = getPage(this, 'travellerDetailsPage');
  this.scenarioState.frequentFlyerNumber = ffNumber;
  await travellerPage.setFrequentFlyerNumber(ffNumber);
});

Then('the frequent flyer number field should retain the entered value', async function () {
  const travellerPage = getPage(this, 'travellerDetailsPage');
  const value = await travellerPage.frequentFlyerInput.inputValue();
  assert.strictEqual(value, this.scenarioState.frequentFlyerNumber);
});

Then('a child age validation error should be displayed', async function () {
  const homePage = getPage(this, 'homePage');
  const error = homePage.page.locator('[class*="childAge" i] [class*="error" i], [class*="pax" i] [class*="error" i]').first();
  assert.ok(await homePage.isVisible(error, 5000), 'Expected a child age validation error to be shown');
});

Then('a {string} validation error should be displayed', async function (field) {
  const travellerPage = getPage(this, 'travellerDetailsPage');
  const hasError =
    field === 'email' ? await travellerPage.getEmailValidationError() : await travellerPage.getPhoneValidationError();
  assert.ok(hasError, `Expected a "${field}" validation error to be shown`);
});

Then('a required field validation error should be displayed for the name field', async function () {
  const travellerPage = getPage(this, 'travellerDetailsPage');
  const hasError = await travellerPage.getRequiredFieldError(travellerPage.nameInput);
  assert.ok(hasError, 'Expected a required-field validation error for the name field');
});
