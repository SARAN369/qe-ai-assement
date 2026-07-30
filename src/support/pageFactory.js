const HomePage = require('../pages/HomePage');
const SearchResultsPage = require('../pages/SearchResultsPage');
const TravellerDetailsPage = require('../pages/TravellerDetailsPage');
const SeatSelectionPage = require('../pages/SeatSelectionPage');
const AddOnsPage = require('../pages/AddOnsPage');
const InsurancePage = require('../pages/InsurancePage');
const BookingSummaryPage = require('../pages/BookingSummaryPage');
const PaymentPage = require('../pages/PaymentPage');

const REGISTRY = {
  homePage: HomePage,
  searchResultsPage: SearchResultsPage,
  travellerDetailsPage: TravellerDetailsPage,
  seatSelectionPage: SeatSelectionPage,
  addOnsPage: AddOnsPage,
  insurancePage: InsurancePage,
  bookingSummaryPage: BookingSummaryPage,
  paymentPage: PaymentPage,
};

/**
 * Returns a memoized page-object instance bound to the current scenario's
 * Playwright page. Keeps step definitions free of `new XyzPage(this.page)`
 * boilerplate and guarantees one instance per scenario per page object.
 */
function getPage(world, name) {
  const PageClass = REGISTRY[name];
  if (!PageClass) {
    throw new Error(`Unknown page object requested from pageFactory: "${name}"`);
  }
  if (!world.pages[name]) {
    world.pages[name] = new PageClass(world.page);
  }
  return world.pages[name];
}

module.exports = { getPage };
