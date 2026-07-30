/**
 * Generates test-data/TestData.xlsx from scratch. Run automatically via the
 * `pretest` npm script so a fresh, known-good workbook exists before every
 * run (Excel is treated as the source of truth for scenario data, but the
 * sheet layout itself is code-generated so it never drifts from what the
 * step definitions expect).
 */
const ExcelJS = require('exceljs');
const path = require('path');

const OUTPUT_PATH = path.join(process.cwd(), 'test-data', 'TestData.xlsx');

function futureDate(daysAhead) {
  const d = new Date();
  d.setDate(d.getDate() + daysAhead);
  return {
    day: d.getDate(),
    month: d.toLocaleString('en-US', { month: 'short' }),
    year: d.getFullYear(),
  };
}

async function generate() {
  const workbook = new ExcelJS.Workbook();

  const routesSheet = workbook.addWorksheet('Routes');
  routesSheet.columns = [
    { header: 'scenarioId', key: 'scenarioId' },
    { header: 'leg1From', key: 'leg1From' },
    { header: 'leg1To', key: 'leg1To' },
    { header: 'leg1DaysAhead', key: 'leg1DaysAhead' },
    { header: 'leg2From', key: 'leg2From' },
    { header: 'leg2To', key: 'leg2To' },
    { header: 'leg2DaysAhead', key: 'leg2DaysAhead' },
    { header: 'leg3From', key: 'leg3From' },
    { header: 'leg3To', key: 'leg3To' },
    { header: 'leg3DaysAhead', key: 'leg3DaysAhead' },
  ];
  routesSheet.addRow({
    scenarioId: 'MULTI_CITY_VALID',
    leg1From: 'Delhi', leg1To: 'Mumbai', leg1DaysAhead: 15,
    leg2From: 'Mumbai', leg2To: 'Bengaluru', leg2DaysAhead: 20,
    leg3From: 'Bengaluru', leg3To: 'Delhi', leg3DaysAhead: 30,
  });
  routesSheet.addRow({
    scenarioId: 'MULTI_CITY_PAST_DATE',
    leg1From: 'Delhi', leg1To: 'Mumbai', leg1DaysAhead: -1,
    leg2From: 'Mumbai', leg2To: 'Bengaluru', leg2DaysAhead: 20,
    leg3From: 'Bengaluru', leg3To: 'Delhi', leg3DaysAhead: 30,
  });

  const travellersSheet = workbook.addWorksheet('Travellers');
  travellersSheet.columns = [
    { header: 'scenarioId', key: 'scenarioId' },
    { header: 'adults', key: 'adults' },
    { header: 'children', key: 'children' },
    { header: 'childAge', key: 'childAge' },
    { header: 'cabinClass', key: 'cabinClass' },
  ];
  travellersSheet.addRow({ scenarioId: 'TRAVELLER_VALID', adults: 2, children: 1, childAge: 8, cabinClass: 'Economy' });
  travellersSheet.addRow({ scenarioId: 'TRAVELLER_INVALID_CHILD_AGE', adults: 2, children: 1, childAge: 25, cabinClass: 'Economy' });

  const travellerDetailsSheet = workbook.addWorksheet('TravellerDetails');
  travellerDetailsSheet.columns = [
    { header: 'scenarioId', key: 'scenarioId' },
    { header: 'name', key: 'name' },
    { header: 'age', key: 'age' },
    { header: 'gender', key: 'gender' },
    { header: 'passport', key: 'passport' },
    { header: 'email', key: 'email' },
    { header: 'phone', key: 'phone' },
    { header: 'expectValid', key: 'expectValid' },
  ];
  travellerDetailsSheet.addRow({ scenarioId: 'TRAVELLER_DETAILS_VALID', name: 'Rahul Sharma', age: 34, gender: 'Male', passport: 'M1234567', email: 'rahul.sharma@example.com', phone: '9876543210', expectValid: true });
  travellerDetailsSheet.addRow({ scenarioId: 'TRAVELLER_DETAILS_INVALID_EMAIL', name: 'Rahul Sharma', age: 34, gender: 'Male', passport: 'M1234567', email: 'rahul.sharma[at]example.com', phone: '9876543210', expectValid: false });
  travellerDetailsSheet.addRow({ scenarioId: 'TRAVELLER_DETAILS_INVALID_PHONE', name: 'Rahul Sharma', age: 34, gender: 'Male', passport: 'M1234567', email: 'rahul.sharma@example.com', phone: '98765', expectValid: false });
  travellerDetailsSheet.addRow({ scenarioId: 'TRAVELLER_DETAILS_MISSING_NAME', name: '', age: 34, gender: 'Male', passport: 'M1234567', email: 'rahul.sharma@example.com', phone: '9876543210', expectValid: false });

  const gstSheet = workbook.addWorksheet('GstData');
  gstSheet.columns = [
    { header: 'scenarioId', key: 'scenarioId' },
    { header: 'companyName', key: 'companyName' },
    { header: 'gstin', key: 'gstin' },
    { header: 'expectValid', key: 'expectValid' },
  ];
  gstSheet.addRow({ scenarioId: 'GST_VALID', companyName: 'Acme Travels Pvt Ltd', gstin: '29ABCDE1234F1Z5', expectValid: true });
  gstSheet.addRow({ scenarioId: 'GST_INVALID_PATTERN', companyName: 'Acme Travels Pvt Ltd', gstin: 'INVALID_GSTIN_123', expectValid: false });

  const baggageSheet = workbook.addWorksheet('Baggage');
  baggageSheet.columns = [
    { header: 'scenarioId', key: 'scenarioId' },
    { header: 'legIndex', key: 'legIndex' },
    { header: 'weightOption', key: 'weightOption' },
  ];
  baggageSheet.addRow({ scenarioId: 'BAGGAGE_VALID', legIndex: 0, weightOption: '5 Kg' });

  const fs = require('fs');
  fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
  await workbook.xlsx.writeFile(OUTPUT_PATH);
  console.log(`Test data written to ${OUTPUT_PATH}`);
}

if (require.main === module) {
  generate().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}

module.exports = { generate, futureDate, OUTPUT_PATH };
