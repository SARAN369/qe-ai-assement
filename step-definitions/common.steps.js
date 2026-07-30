const { Given } = require('@cucumber/cucumber');
const { getPage } = require('../src/support/pageFactory');

Given('the user launches MakeMyTrip and dismisses any popups', async function () {
  const homePage = getPage(this, 'homePage');
  await homePage.goto();
  await homePage.dismissPopups();
});
