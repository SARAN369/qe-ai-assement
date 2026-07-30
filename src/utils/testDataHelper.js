const path = require('path');
const ExcelHelper = require('./excelHelper');
const { futureDate } = require('./generateTestData');

const excel = new ExcelHelper(path.join(process.cwd(), 'test-data', 'TestData.xlsx'));

async function getRoutes(scenarioId) {
  const row = await excel.getRowByKey('Routes', 'scenarioId', scenarioId);
  return [1, 2, 3].map((n) => ({
    from: row[`leg${n}From`],
    to: row[`leg${n}To`],
    date: futureDate(Number(row[`leg${n}DaysAhead`])),
  }));
}

async function getTravellers(scenarioId) {
  const row = await excel.getRowByKey('Travellers', 'scenarioId', scenarioId);
  return {
    adults: Number(row.adults),
    children: Number(row.children),
    childAge: Number(row.childAge),
    cabinClass: row.cabinClass,
  };
}

async function getTravellerDetails(scenarioId) {
  const row = await excel.getRowByKey('TravellerDetails', 'scenarioId', scenarioId);
  return {
    name: row.name,
    age: row.age,
    gender: row.gender,
    passport: row.passport,
    email: row.email,
    phone: row.phone,
    expectValid: String(row.expectValid) === 'true',
  };
}

async function getGstData(scenarioId) {
  const row = await excel.getRowByKey('GstData', 'scenarioId', scenarioId);
  return {
    companyName: row.companyName,
    gstin: row.gstin,
    expectValid: String(row.expectValid) === 'true',
  };
}

async function getBaggageData(scenarioId) {
  const row = await excel.getRowByKey('Baggage', 'scenarioId', scenarioId);
  return {
    legIndex: Number(row.legIndex),
    weightOption: row.weightOption,
  };
}

module.exports = {
  getRoutes,
  getTravellers,
  getTravellerDetails,
  getGstData,
  getBaggageData,
};
