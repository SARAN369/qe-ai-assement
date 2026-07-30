const ExcelJS = require('exceljs');

/**
 * Thin wrapper around exceljs for reading test data by sheet name, and
 * writing arbitrary rows back (used to persist AI/dynamically-generated
 * data during a run). Rows are returned as plain objects keyed by header.
 */
class ExcelHelper {
  constructor(filePath) {
    this.filePath = filePath;
  }

  async readSheet(sheetName) {
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile(this.filePath);
    const sheet = workbook.getWorksheet(sheetName);
    if (!sheet) throw new Error(`Sheet "${sheetName}" not found in ${this.filePath}`);

    const headerRow = sheet.getRow(1).values.slice(1).map((h) => String(h).trim());
    const rows = [];
    sheet.eachRow((row, rowNumber) => {
      if (rowNumber === 1) return;
      const values = row.values.slice(1);
      const record = {};
      headerRow.forEach((header, idx) => {
        record[header] = values[idx] !== undefined ? values[idx] : '';
      });
      rows.push(record);
    });
    return rows;
  }

  async getRowByKey(sheetName, keyColumn, keyValue) {
    const rows = await this.readSheet(sheetName);
    const match = rows.find((r) => String(r[keyColumn]) === String(keyValue));
    if (!match) throw new Error(`No row found in "${sheetName}" where ${keyColumn}="${keyValue}"`);
    return match;
  }

  async appendRow(sheetName, record) {
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile(this.filePath);
    const sheet = workbook.getWorksheet(sheetName);
    const headerRow = sheet.getRow(1).values.slice(1).map((h) => String(h).trim());
    sheet.addRow(headerRow.map((h) => record[h] ?? ''));
    await workbook.xlsx.writeFile(this.filePath);
  }
}

module.exports = ExcelHelper;
