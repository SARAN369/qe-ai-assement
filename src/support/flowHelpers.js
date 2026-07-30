const { getPage } = require('./pageFactory');
const { getRoutes, getTravellers, getTravellerDetails } = require('../utils/testDataHelper');

/**
 * Reusable multi-step navigation chains shared by step definitions whose
 * scenarios start mid-flow (e.g. "Given the user is on the seat selection
 * page"). Each Cucumber scenario gets a fresh browser context (see
 * support/hooks.js), so these helpers replay the minimum prior steps
 * needed to reach that page rather than relying on state from another
 * scenario.
 */

async function reachSearchResults(world, routesId = 'MULTI_CITY_VALID', travellersId = 'TRAVELLER_VALID') {
  const homePage = getPage(world, 'homePage');
  await homePage.goto();
  await homePage.dismissPopups();
  await homePage.selectMultiCityTab();
  const routes = await getRoutes(routesId);
  await homePage.buildMultiCityRoutes(routes);
  const travellers = await getTravellers(travellersId);
  await homePage.setTravellers(travellers);
  await homePage.selectCabinClass(travellers.cabinClass);
  await homePage.clickSearch();
  const resultsPage = getPage(world, 'searchResultsPage');
  await resultsPage.waitForResults(10000);
  return resultsPage;
}

async function reachTravellerDetails(world) {
  const resultsPage = await reachSearchResults(world);
  await resultsPage.selectFlightCombination(0);
  return getPage(world, 'travellerDetailsPage');
}

async function reachSeatSelection(world, travellerScenarioId = 'TRAVELLER_DETAILS_VALID') {
  const travellerPage = await reachTravellerDetails(world);
  const details = await getTravellerDetails(travellerScenarioId);
  await travellerPage.fillTraveller(details);
  await travellerPage.fillContactInfo(details);
  await travellerPage.submit();
  return getPage(world, 'seatSelectionPage');
}

async function reachAddOns(world) {
  const seatPage = await reachSeatSelection(world);
  await seatPage.continueToAddOns();
  return getPage(world, 'addOnsPage');
}

async function reachInsurance(world) {
  await reachAddOns(world);
  return getPage(world, 'insurancePage');
}

async function reachBookingSummary(world) {
  await reachInsurance(world);
  return getPage(world, 'bookingSummaryPage');
}

module.exports = {
  reachSearchResults,
  reachTravellerDetails,
  reachSeatSelection,
  reachAddOns,
  reachInsurance,
  reachBookingSummary,
};
