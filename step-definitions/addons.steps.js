const { Given, When, Then } = require('@cucumber/cucumber');
const assert = require('assert');
const { getPage } = require('../src/support/pageFactory');
const { reachAddOns } = require('../src/support/flowHelpers');
const { getBaggageData } = require('../src/utils/testDataHelper');

Given('the user is on the add-ons page', async function () {
  await reachAddOns(this);
});

When('the user adds baggage for leg {int} using data {string}', async function (legNumber, scenarioId) {
  const addOnsPage = getPage(this, 'addOnsPage');
  const data = await getBaggageData(scenarioId);
  await addOnsPage.addBaggage(legNumber - 1, data.weightOption);
});

Then('the baggage charge for leg {int} should be displayed', async function (legNumber) {
  const addOnsPage = getPage(this, 'addOnsPage');
  const charge = await addOnsPage.getBaggageCharge(legNumber - 1);
  assert.ok(charge && charge.length > 0, `Expected a baggage charge to be displayed for leg ${legNumber}`);
});

When('the user selects {string} meal preference', async function (meal) {
  const addOnsPage = getPage(this, 'addOnsPage');
  this.scenarioState.selectedMeal = meal;
  await addOnsPage.selectMealPreference(meal);
});

Then('the add-on summary should include the meal selection', async function () {
  const addOnsPage = getPage(this, 'addOnsPage');
  const summary = await addOnsPage.getAddOnSummaryText();
  assert.ok(
    summary.toLowerCase().includes(this.scenarioState.selectedMeal.toLowerCase()),
    `Expected add-on summary to mention "${this.scenarioState.selectedMeal}"`
  );
});
