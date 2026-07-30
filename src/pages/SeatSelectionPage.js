const BasePage = require('./BasePage');

class SeatSelectionPage extends BasePage {
  constructor(page) {
    super(page);
    this.seatMapForLeg = (legIndex) => page.locator('[class*="seatMap" i]').nth(legIndex);
    this.availableSeats = page.locator('[class*="seat" i][class*="available" i]:not([class*="unavailable" i])');
    this.selectedSeatBadge = page.locator('[class*="seat" i][class*="selected" i]');
    this.continueButton = page.locator('button:has-text("Continue"), a:has-text("Continue")').first();
  }

  async isSeatMapRendered(legIndex) {
    return this.isVisible(this.seatMapForLeg(legIndex));
  }

  async selectSeatByType(type) {
    // type: 'window' | 'aisle' | 'middle'
    const seat = this.availableSeats.filter({ hasText: new RegExp(type, 'i') }).first();
    const fallback = this.page.locator(`[class*="${type}" i][class*="seat" i]`).first();
    const target = (await seat.count()) ? seat : fallback;
    const label = await target.getAttribute('data-seat-number').catch(() => null);
    const price = await target.locator('[class*="price" i]').innerText().catch(() => '');
    await target.click();
    return { seatNumber: label, price: price.trim() };
  }

  async isSeatHighlighted(seatNumber) {
    return this.isVisible(this.selectedSeatBadge.filter({ hasText: seatNumber }));
  }

  async continueToAddOns() {
    await this.continueButton.click();
  }
}

module.exports = SeatSelectionPage;
