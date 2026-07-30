const BasePage = require('./BasePage');

/**
 * Flight listing page for a multi-city search. Selectors target the
 * result-card structure MakeMyTrip renders per leg (`.tupleWrapper` /
 * `.flightsListing` family of classes observed on the live listing page).
 */
class SearchResultsPage extends BasePage {
  constructor(page) {
    super(page);
    this.routeSummaryHeader = page.locator('.tripSummary, [class*="routeSummary" i], [class*="searchHeader" i]').first();
    this.flightCards = page.locator('.listingCard, [class*="flightTupleWrapper" i], [class*="tupleWrapper" i]');
    this.sortByPrice = page.locator('[class*="sort" i]:has-text("Cheapest"), [class*="sort" i]:has-text("Price")').first();
    this.sortByDuration = page.locator('[class*="sort" i]:has-text("Duration")').first();
    this.filterFlightType = page.locator('[class*="filter" i]:has-text("Stops"), [class*="filter" i]:has-text("Non Stop")').first();
    this.filterAirlines = page.locator('[class*="filter" i]:has-text("Airlines")').first();
    this.filterDepartureTime = page.locator('[class*="filter" i]:has-text("Departure")').first();
    this.activeFilterChips = page.locator('[class*="filterChip" i], [class*="appliedFilter" i]');
  }

  async waitForResults(timeoutMs = 10000) {
    const start = Date.now();
    await this.flightCards.first().waitFor({ state: 'visible', timeout: timeoutMs });
    return Date.now() - start;
  }

  async applyFilter(locator) {
    await locator.click();
  }

  async getActiveFilterCount() {
    return this.activeFilterChips.count();
  }

  async sortResultsByPrice() {
    await this.sortByPrice.click();
    await this.waitForNavigationSettled();
  }

  async sortResultsByDuration() {
    await this.sortByDuration.click();
    await this.waitForNavigationSettled();
  }

  /**
   * Extracts the first N flight cards into a structured object keyed
   * leg1..legN, matching the shape requested in the use-case brief.
   */
  async extractFlightDetails(count = 3) {
    const cards = this.flightCards;
    const total = Math.min(await cards.count(), count);
    const result = {};
    for (let i = 0; i < total; i++) {
      const card = cards.nth(i);
      const airline = await card.locator('[class*="airlineName" i], [class*="airline" i]').first().innerText().catch(() => '');
      const flightNumber = await card.locator('[class*="flightNumber" i], [class*="flightNo" i]').first().innerText().catch(() => '');
      const departTime = await card.locator('[class*="depart" i][class*="time" i], [class*="departureTime" i]').first().innerText().catch(() => '');
      const arriveTime = await card.locator('[class*="arriv" i][class*="time" i], [class*="arrivalTime" i]').first().innerText().catch(() => '');
      const duration = await card.locator('[class*="duration" i]').first().innerText().catch(() => '');
      const price = await card.locator('[class*="price" i]').first().innerText().catch(() => '');
      result[`leg${i + 1}`] = {
        airline: airline.trim(),
        flightNumber: flightNumber.trim(),
        departureTime: departTime.trim(),
        arrivalTime: arriveTime.trim(),
        duration: duration.trim(),
        price: price.trim(),
      };
    }
    return result;
  }

  async selectFlightCombination(index = 0) {
    await this.flightCards.nth(index).locator('[class*="book" i], button, a').first().click();
  }
}

module.exports = SearchResultsPage;
