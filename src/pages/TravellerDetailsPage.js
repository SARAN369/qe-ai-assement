const BasePage = require('./BasePage');

/**
 * Traveller-details / contact-info step of checkout. This step's markup
 * sits behind an authenticated / live-search-dependent flow, so locators
 * follow MakeMyTrip's documented field-naming convention (name/age/gender/
 * passport, email, phone) and are intentionally resilient (label-based)
 * rather than pinned to volatile generated class names.
 */
class TravellerDetailsPage extends BasePage {
  constructor(page) {
    super(page);
    this.nameInput = page.locator('input[name*="name" i], input[placeholder*="Name" i]').first();
    this.ageInput = page.locator('input[name*="age" i], select[name*="age" i]').first();
    this.genderMale = page.locator('input[value="Male" i], label:has-text("Male")').first();
    this.genderFemale = page.locator('input[value="Female" i], label:has-text("Female")').first();
    this.passportInput = page.locator('input[name*="passport" i]').first();
    this.emailInput = page.locator('input[type="email"], input[name*="email" i]').first();
    this.phoneInput = page.locator('input[name*="mobile" i], input[name*="phone" i]').first();
    this.frequentFlyerInput = page.locator('input[name*="frequentFlyer" i], input[placeholder*="Frequent Flyer" i]').first();
    this.continueButton = page.locator('button:has-text("Continue"), a:has-text("Continue")').first();
    this.fieldError = (fieldLocator) => fieldLocator.locator('xpath=following::*[contains(@class,"error") or contains(@class,"Error")][1]');
  }

  async fillTraveller({ name, age, gender, passport }) {
    if (name) await this.nameInput.fill(name);
    if (age) await this.ageInput.fill(String(age));
    if (gender === 'Male') await this.genderMale.click();
    if (gender === 'Female') await this.genderFemale.click();
    if (passport) await this.passportInput.fill(passport);
  }

  async fillContactInfo({ email, phone }) {
    if (email !== undefined) await this.emailInput.fill(email);
    if (phone !== undefined) await this.phoneInput.fill(phone);
  }

  async setFrequentFlyerNumber(number) {
    await this.frequentFlyerInput.fill(number);
  }

  async submit() {
    await this.continueButton.click();
  }

  async getEmailValidationError() {
    return this.isVisible(this.fieldError(this.emailInput));
  }

  async getPhoneValidationError() {
    return this.isVisible(this.fieldError(this.phoneInput));
  }

  async getRequiredFieldError(fieldLocator) {
    return this.isVisible(this.fieldError(fieldLocator));
  }
}

module.exports = TravellerDetailsPage;
