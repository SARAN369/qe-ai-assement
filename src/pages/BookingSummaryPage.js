const BasePage = require('./BasePage');

const LINE_ITEM_LABELS = {
  baseFare: 'Base Fare',
  seatCharges: 'Seat',
  baggageFees: 'Baggage',
  mealCharges: 'Meal',
  insurance: 'Insurance',
  convenienceFee: 'Convenience Fee',
  taxes: 'Taxes',
  grandTotal: 'Total Amount',
};

class BookingSummaryPage extends BasePage {
  constructor(page) {
    super(page);
    this.fareSummaryPanel = page.locator('[class*="fareSummary" i], [class*="priceBreakup" i]').first();
    this.proceedToPayButton = page.locator('button:has-text("Proceed to Pay"), a:has-text("Proceed to Pay")').first();
  }

  lineItemLocator(label) {
    return this.fareSummaryPanel
      .locator(`text=${label}`)
      .locator('xpath=ancestor::div[1]')
      .locator('[class*="amount" i], [class*="price" i]')
      .last();
  }

  async getLineItem(key) {
    const label = LINE_ITEM_LABELS[key];
    if (!label) throw new Error(`Unknown fare line item: ${key}`);
    const text = await this.textOf(this.lineItemLocator(label));
    return this.parseAmount(text);
  }

  async getAllLineItems() {
    const entries = await Promise.all(
      Object.keys(LINE_ITEM_LABELS)
        .filter((k) => k !== 'grandTotal')
        .map(async (k) => [k, await this.getLineItem(k).catch(() => 0)])
    );
    return Object.fromEntries(entries);
  }

  async getDisplayedGrandTotal() {
    return this.getLineItem('grandTotal');
  }

  parseAmount(text) {
    const numeric = text.replace(/[^0-9.]/g, '');
    return numeric ? parseFloat(numeric) : 0;
  }

  /**
   * Sums the individual fare components and compares against the displayed
   * grand total within a tolerance, matching the use case's Β±2% allowance
   * for rounding / dynamic pricing.
   */
  static isWithinTolerance(computedTotal, displayedTotal, tolerancePercent = 2) {
    if (displayedTotal === 0) return computedTotal === 0;
    const diffPercent = (Math.abs(computedTotal - displayedTotal) / displayedTotal) * 100;
    return diffPercent <= tolerancePercent;
  }

  async proceedToPayment() {
    await this.proceedToPayButton.click();
  }
}

module.exports = BookingSummaryPage;
