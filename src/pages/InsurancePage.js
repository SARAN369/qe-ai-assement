const BasePage = require('./BasePage');

const GSTIN_PATTERN = /^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$/;

class InsurancePage extends BasePage {
  constructor(page) {
    super(page);
    this.insurancePlanOptions = page.locator('[class*="insurance" i][class*="plan" i]');
    this.businessBookingToggle = page.locator('[class*="gst" i][class*="toggle" i], label:has-text("Business Booking")').first();
    this.companyNameInput = page.locator('input[name*="companyName" i]').first();
    this.gstinInput = page.locator('input[name*="gstin" i]').first();
    this.gstinError = page.locator('[class*="gst" i] [class*="error" i]').first();
  }

  async selectInsurancePlan(index = 0) {
    await this.insurancePlanOptions.nth(index).click();
  }

  async enableBusinessBooking() {
    await this.businessBookingToggle.click();
  }

  async fillGstDetails({ companyName, gstin }) {
    await this.companyNameInput.fill(companyName);
    await this.gstinInput.fill(gstin);
    await this.gstinInput.blur();
  }

  static isValidGstinFormat(gstin) {
    return GSTIN_PATTERN.test(gstin);
  }

  async isGstinErrorShown() {
    return this.isVisible(this.gstinError);
  }
}

module.exports = InsurancePage;
