const report = require('multiple-cucumber-html-reporter');
const path = require('path');
const fs = require('fs');
const os = require('os');

const jsonDir = path.join(process.cwd(), 'reports');

if (!fs.existsSync(path.join(jsonDir, 'cucumber-report.json'))) {
  console.warn('No cucumber-report.json found — skipping HTML report generation. Run the tests first.');
  process.exit(0);
}

report.generate({
  jsonDir,
  reportPath: path.join(jsonDir, 'html-report'),
  metadata: {
    browser: { name: 'chromium', version: 'latest' },
    device: os.hostname(),
    platform: { name: os.platform(), version: os.release() },
  },
  customData: {
    title: 'Run Info',
    data: [
      { label: 'Project', value: 'AI-Powered Multi-City Flight Booking Automation' },
      { label: 'Execution Start Time', value: new Date().toISOString() },
    ],
  },
});
