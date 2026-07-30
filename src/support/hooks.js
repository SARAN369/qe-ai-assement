const { Before, After, BeforeAll, AfterAll, Status, setDefaultTimeout } = require('@cucumber/cucumber');
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

setDefaultTimeout(60 * 1000);

const HEADLESS = process.env.HEADLESS !== 'false';
const SCREENSHOT_DIR = path.join(process.cwd(), 'reports', 'screenshots');

let browser;

BeforeAll(async function () {
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }
  browser = await chromium.launch({
    headless: HEADLESS,
    args: ['--start-maximized'],
  });
});

AfterAll(async function () {
  if (browser) {
    await browser.close();
  }
});

Before(async function () {
  this.context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    acceptDownloads: true,
  });
  this.page = await this.context.newPage();
  this.pages = {};
  this.scenarioState = {};
});

After(async function (scenario) {
  if (scenario.result?.status === Status.FAILED && this.page) {
    const safeName = scenario.pickle.name.replace(/[^a-z0-9]/gi, '_').slice(0, 80);
    const screenshotPath = path.join(SCREENSHOT_DIR, `${safeName}_${Date.now()}.png`);
    const image = await this.page.screenshot({ path: screenshotPath, fullPage: true });
    await this.attach(image, 'image/png');
  }
  if (this.page) await this.page.close();
  if (this.context) await this.context.close();
});
