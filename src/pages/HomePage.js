const BasePage = require('./BasePage');

const BASE_URL = 'https://www.makemytrip.com/flights/';

/**
 * Flight search widget on the MakeMyTrip landing page, scoped to the
 * Multi-City flow. Locators below were captured from the live DOM
 * (class/id attributes, e.g. `#fromAnotherCity0`, `.btnAddCity`,
 * `.fltWidgetSearchBtnMultiCity`) rather than guessed, since MakeMyTrip's
 * widget has almost no ARIA roles to rely on.
 */
class HomePage extends BasePage {
  constructor(page) {
    super(page);
    this.multiCityTab = page.locator('li').filter({ hasText: /^Multi City$/ }).first();
    this.addCityButton = page.locator('.btnAddCity');
    this.multiCitySearchButton = page.locator('.fltWidgetSearchBtnMultiCity');
    this.travellersWidget = page.locator('.flightTravellersOnly');
    this.cabinClassWidget = page.locator('.flightCabinClass');
    this.citySuggestionList = page.locator(
      '[class*="suggest" i] li, [class*="dropdown" i] li, [class*="autoComplete" i] li, [class*="cityList" i] li'
    );
    this.mobileNumberOverlayClose = page.locator('.commonModal .cross, .commonModal [class*="close" i]');
  }

  async goto() {
    await this.open(BASE_URL);
  }

  async dismissPopups() {
    await this.dismissPopupIfPresent(this.mobileNumberOverlayClose, 4000);
    await this.dismissPopupIfPresent('.dtSearchWidget__close, [class*="modal" i] [class*="close" i]', 3000);
  }

  async selectMultiCityTab() {
    await this.multiCityTab.click();
  }

  fromCityInput(legIndex) {
    return this.page.locator(`#fromAnotherCity${legIndex}`);
  }

  toCityInput(legIndex) {
    return this.page.locator(`#toAnotherCity${legIndex}`);
  }

  dateInput(legIndex) {
    return this.page.locator(`[id="anotherDeparture ${legIndex}"]`);
  }

  async selectCity(inputLocator, cityName) {
    await inputLocator.click();
    await inputLocator.fill('');
    await this.page.keyboard.type(cityName, { delay: 100 });
    const suggestion = this.citySuggestionList.filter({ hasText: new RegExp(cityName, 'i') }).first();
    try {
      await suggestion.waitFor({ state: 'visible', timeout: 5000 });
      await suggestion.click();
    } catch {
      // Fallback for a self-healing style interaction: if the suggestion
      // list markup changes, pick the first highlighted option via keyboard.
      await this.page.keyboard.press('ArrowDown');
      await this.page.keyboard.press('Enter');
    }
  }

  async setFromCity(legIndex, cityName) {
    await this.selectCity(this.fromCityInput(legIndex), cityName);
  }

  async setToCity(legIndex, cityName) {
    await this.selectCity(this.toCityInput(legIndex), cityName);
  }

  async setDepartureDate(legIndex, date) {
    // date: { day: number, month: 'Aug', year: 2026 }
    await this.dateInput(legIndex).click();
    const dayCell = this.page
      .locator('.datePickerContainer, .DayPicker, [class*="datepicker" i]')
      .locator(`[aria-label*="${date.day} ${date.month} ${date.year}" i], td:has-text("${date.day}"):not(.disabled)`)
      .first();
    await dayCell.click();
  }

  async addAnotherCityLeg() {
    await this.addCityButton.click();
  }

  async buildMultiCityRoutes(routes) {
    // routes: [{ from, to, date: { day, month, year } }, ...] length >= 3
    await this.selectMultiCityTab();
    for (let i = 0; i < routes.length; i++) {
      if (i >= 2) {
        await this.addAnotherCityLeg();
      }
      const leg = routes[i];
      if (i === 0) {
        await this.setFromCity(i, leg.from);
      }
      await this.setToCity(i, leg.to);
      await this.setDepartureDate(i, leg.date);
    }
  }

  async openTravellersWidget() {
    await this.travellersWidget.click();
  }

  async setTravellers({ adults = 1, children = 0, infants = 0, childAge }) {
    await this.openTravellersWidget();
    const panel = this.page.locator('.pax-popup, [class*="traveller" i][class*="popup" i]').first();
    await panel.waitFor({ state: 'visible', timeout: 5000 });
    await this.adjustCounter(panel, 'Adult', adults);
    if (children > 0) {
      await this.adjustCounter(panel, 'Child', children);
      if (childAge !== undefined) await this.setChildAge(0, childAge);
    }
    if (infants > 0) await this.adjustCounter(panel, 'Infant', infants);
  }

  async adjustCounter(panel, label, target) {
    const row = panel.locator(`text=${label}`).locator('xpath=ancestor::div[1]');
    const incrementBtn = row.locator('[class*="increment" i], [class*="plus" i]').first();
    // Adults widget usually starts at 1; children/infants start at 0.
    const startsAt = label === 'Adult' ? 1 : 0;
    for (let i = startsAt; i < target; i++) {
      await incrementBtn.click();
    }
  }

  async setChildAge(childIndex, age) {
    const ageDropdown = this.page.locator(`[class*="childAge" i]`).nth(childIndex);
    await ageDropdown.click();
    await this.page.locator(`li:has-text("${age}")`).first().click();
  }

  async selectCabinClass(cabinClass) {
    await this.cabinClassWidget.click();
    await this.page.locator(`li:has-text("${cabinClass}")`).first().click();
  }

  async clickSearch() {
    await this.multiCitySearchButton.click();
  }
}

module.exports = HomePage;
