const { setWorldConstructor, World } = require('@cucumber/cucumber');

/**
 * Custom Cucumber World shared across steps within a single scenario.
 * Holds the Playwright page plus scenario-scoped state (flight data,
 * computed totals, etc.) that step definitions read/write across steps.
 */
class CustomWorld extends World {
  constructor(options) {
    super(options);
    this.page = null;
    this.context = null;
    this.browser = null;
    this.pages = {}; // lazily-created page objects, see support/pageFactory.js
    this.testData = {}; // data loaded from Excel for the current scenario
    this.scenarioState = {}; // free-form bag for cross-step values (extracted flights, totals, etc.)
  }
}

setWorldConstructor(CustomWorld);
