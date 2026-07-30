/**
 * Shared helpers for every page object. Keeping raw Playwright calls behind
 * these methods means a site-wide markup change (or an AI-assisted locator
 * repair) only has to be fixed in one place.
 */
class BasePage {
  constructor(page) {
    this.page = page;
  }

  async open(url) {
    await this.page.goto(url, { waitUntil: 'domcontentloaded' });
  }

  async dismissPopupIfPresent(locator, timeout = 5000) {
    try {
      const el = this.page.locator(locator).first();
      await el.waitFor({ state: 'visible', timeout });
      await el.click();
      return true;
    } catch {
      return false;
    }
  }

  async textOf(locator) {
    return (await this.page.locator(locator).innerText()).trim();
  }

  async isVisible(locator, timeout = 5000) {
    try {
      await this.page.locator(locator).first().waitFor({ state: 'visible', timeout });
      return true;
    } catch {
      return false;
    }
  }

  async waitForNavigationSettled(timeout = 15000) {
    await this.page.waitForLoadState('domcontentloaded', { timeout });
  }
}

module.exports = BasePage;
