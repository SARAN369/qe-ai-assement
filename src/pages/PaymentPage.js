const BasePage = require('./BasePage');

class PaymentPage extends BasePage {
  constructor(page) {
    super(page);
    this.paymentOptionsPanel = page.locator('[class*="paymentOptions" i], [class*="paymentMode" i]').first();
    this.paymentOptionTiles = page.locator('[class*="paymentOptions" i] [class*="option" i], [class*="paymentMode" i] [class*="tile" i]');
  }

  async waitForPaymentOptionsToLoad(timeoutMs = 15000) {
    await this.paymentOptionsPanel.waitFor({ state: 'visible', timeout: timeoutMs });
    return this.paymentOptionTiles.count();
  }
}

module.exports = PaymentPage;
