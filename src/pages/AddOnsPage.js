const BasePage = require('./BasePage');

class AddOnsPage extends BasePage {
  constructor(page) {
    super(page);
    this.baggageOptionForLeg = (legIndex) => page.locator('[class*="baggage" i][class*="option" i]').nth(legIndex);
    this.baggageChargeForLeg = (legIndex) => page.locator('[class*="baggage" i][class*="charge" i], [class*="baggage" i][class*="price" i]').nth(legIndex);
    this.mealOptions = page.locator('[class*="meal" i][class*="option" i]');
    this.addOnSummary = page.locator('[class*="addOnSummary" i], [class*="ancillarySummary" i]');
  }

  async addBaggage(legIndex, weightLabel) {
    const option = this.baggageOptionForLeg(legIndex).filter({ hasText: new RegExp(weightLabel, 'i') }).first();
    await option.click();
  }

  async getBaggageCharge(legIndex) {
    return this.textOf(this.baggageChargeForLeg(legIndex));
  }

  async selectMealPreference(preference) {
    // preference: 'veg' | 'non-veg' | 'special'
    await this.mealOptions.filter({ hasText: new RegExp(preference, 'i') }).first().click();
  }

  async getAddOnSummaryText() {
    return this.textOf(this.addOnSummary);
  }
}

module.exports = AddOnsPage;
