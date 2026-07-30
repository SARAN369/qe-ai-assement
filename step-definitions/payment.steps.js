const { Given, When, Then } = require('@cucumber/cucumber');
const assert = require('assert');
const { getPage } = require('../src/support/pageFactory');
const { reachInsurance, reachBookingSummary } = require('../src/support/flowHelpers');
const { getGstData } = require('../src/utils/testDataHelper');
const InsurancePage = require('../src/pages/InsurancePage');
const BookingSummaryPage = require('../src/pages/BookingSummaryPage');

Given('the user is on the insurance page', async function () {
  await reachInsurance(this);
});

When('the user selects the first available insurance plan', async function () {
  const insurancePage = getPage(this, 'insurancePage');
  await insurancePage.selectInsurancePlan(0);
});

Then('the insurance plan should be marked as selected', async function () {
  const insurancePage = getPage(this, 'insurancePage');
  const selected = insurancePage.insurancePlanOptions.first();
  const cls = (await selected.getAttribute('class')) || '';
  assert.ok(/selected|active|checked/i.test(cls), 'Expected the first insurance plan to carry a selected/active class');
});

When('the user enables business booking', async function () {
  const insurancePage = getPage(this, 'insurancePage');
  await insurancePage.enableBusinessBooking();
});

When('the user fills GST details from {string}', async function (scenarioId) {
  const insurancePage = getPage(this, 'insurancePage');
  const gstData = await getGstData(scenarioId);
  this.scenarioState.gstData = gstData;
  await insurancePage.fillGstDetails(gstData);
});

Then('the GSTIN should be accepted without a validation error', async function () {
  const insurancePage = getPage(this, 'insurancePage');
  assert.ok(InsurancePage.isValidGstinFormat(this.scenarioState.gstData.gstin), 'GSTIN should match the expected format');
  assert.strictEqual(await insurancePage.isGstinErrorShown(), false, 'Expected no GSTIN validation error');
});

Then('a GSTIN format validation error should be displayed', async function () {
  const insurancePage = getPage(this, 'insurancePage');
  assert.strictEqual(
    InsurancePage.isValidGstinFormat(this.scenarioState.gstData.gstin),
    false,
    'Test data GSTIN was expected to be invalid'
  );
  assert.ok(await insurancePage.isGstinErrorShown(), 'Expected a GSTIN validation error to be shown');
});

Given('the user is on the booking summary page', async function () {
  await reachBookingSummary(this);
});

Then(
  'the fare summary should display base fare, seat charges, baggage fees, meal charges, insurance, convenience fee and taxes',
  async function () {
    const summaryPage = getPage(this, 'bookingSummaryPage');
    const items = await summaryPage.getAllLineItems();
    for (const key of ['baseFare', 'seatCharges', 'baggageFees', 'mealCharges', 'insurance', 'convenienceFee', 'taxes']) {
      assert.ok(key in items, `Expected fare summary to include "${key}"`);
    }
  }
);

When('the user sums all individual fare line items', async function () {
  const summaryPage = getPage(this, 'bookingSummaryPage');
  const items = await summaryPage.getAllLineItems();
  this.scenarioState.computedTotal = Object.values(items).reduce((sum, v) => sum + v, 0);
  this.scenarioState.displayedGrandTotal = await summaryPage.getDisplayedGrandTotal();
});

Then('the computed total should match the displayed grand total within {int} percent tolerance', async function (tolerance) {
  const { computedTotal, displayedGrandTotal } = this.scenarioState;
  assert.ok(
    BookingSummaryPage.isWithinTolerance(computedTotal, displayedGrandTotal, tolerance),
    `Computed total ${computedTotal} should be within ${tolerance}% of displayed total ${displayedGrandTotal}`
  );
});

Given('the following fare breakup is displayed:', async function (dataTable) {
  const row = dataTable.hashes()[0];
  const numericKeys = ['baseFare', 'seatCharges', 'baggageFees', 'mealCharges', 'insurance', 'convenienceFee', 'taxes'];
  const computedTotal = numericKeys.reduce((sum, k) => sum + Number(row[k]), 0);
  this.scenarioState.computedTotal = computedTotal;
  this.scenarioState.displayedGrandTotal = Number(row.displayedGrandTotal);
});

Then('the computed total should not match the displayed grand total within {int} percent tolerance', async function (tolerance) {
  const { computedTotal, displayedGrandTotal } = this.scenarioState;
  assert.strictEqual(
    BookingSummaryPage.isWithinTolerance(computedTotal, displayedGrandTotal, tolerance),
    false,
    `Expected computed total ${computedTotal} to fall outside ${tolerance}% of displayed total ${displayedGrandTotal}`
  );
});

When('the user proceeds to payment', async function () {
  const summaryPage = getPage(this, 'bookingSummaryPage');
  await summaryPage.proceedToPayment();
});

Then('the payment options should load successfully', async function () {
  const paymentPage = getPage(this, 'paymentPage');
  const optionCount = await paymentPage.waitForPaymentOptionsToLoad(15000);
  assert.ok(optionCount > 0, 'Expected at least one payment option to load');
});
