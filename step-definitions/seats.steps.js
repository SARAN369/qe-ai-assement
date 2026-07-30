const { Given, When, Then } = require('@cucumber/cucumber');
const assert = require('assert');
const { getPage } = require('../src/support/pageFactory');
const { reachSeatSelection } = require('../src/support/flowHelpers');

Given('the user is on the seat selection page', async function () {
  await reachSeatSelection(this);
});

Then('the seat map should render for all {int} legs', async function (legCount) {
  const seatPage = getPage(this, 'seatSelectionPage');
  for (let i = 0; i < legCount; i++) {
    assert.ok(await seatPage.isSeatMapRendered(i), `Seat map for leg ${i + 1} should render`);
  }
});

When('the user selects a {string} seat', async function (seatType) {
  const seatPage = getPage(this, 'seatSelectionPage');
  const seat = await seatPage.selectSeatByType(seatType);
  this.scenarioState.selectedSeat = seat;
});

Then('the selected seat should be highlighted', async function () {
  const seatPage = getPage(this, 'seatSelectionPage');
  const seat = this.scenarioState.selectedSeat;
  assert.ok(seat, 'Expected a seat to have been selected first');
  assert.ok(await seatPage.isSeatHighlighted(seat.seatNumber), `Seat ${seat.seatNumber} should be highlighted after selection`);
});
