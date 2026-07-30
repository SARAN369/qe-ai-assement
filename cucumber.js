const common = [
  'features/**/*.feature',
  '--require-module dotenv/config',
  '--require src/support/**/*.js',
  '--require step-definitions/**/*.js',
  '--format progress-bar',
  '--format json:reports/cucumber-report.json',
  '--format html:reports/cucumber-report.html',
].join(' ');

module.exports = {
  default: common,
  smoke: `${common} --tags @smoke`,
  positive: `${common} --tags @positive`,
  negative: `${common} --tags @negative`,
};
