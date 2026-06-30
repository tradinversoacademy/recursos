const SHEET_NAME = "Leads";
const SPREADSHEET_ID = "1n-MnjkvHRd0F1Gu5JehfpRsDf3YsXKmXOnxytgfOTgY";
const SUMMARY_SHEET_NAME = "Resumen";
const HEADERS = [
  "fecha",
  "nombre",
  "email",
  "recurso",
  "origen",
  "campaña",
  "consentimiento",
  "estado",
  "notas"
];
const STATUS_VALUES = ["nuevo", "contactado", "interesado", "descartado", "alumno"];

function doPost(e) {
  const body = JSON.parse((e && e.postData && e.postData.contents) || "{}");
  appendLead(body);

  return ContentService
    .createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

function testLead() {
  const sheet = getLeadSheet();

  sheet.appendRow([
    new Date().toISOString(),
    "Test TRADINVERSO",
    "test@tradinverso.com",
    "checklist-entrada-mercado",
    "test-apps-script",
    "test-manual",
    "si",
    "nuevo",
    "Fila de prueba creada desde Apps Script"
  ]);
}

function doGet(e) {
  const params = (e && e.parameter) || {};

  if (params.email || params.nombre) {
    appendLead(params);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  setupSpreadsheet();

  return ContentService
    .createTextOutput("TRADINVERSO leads activo")
    .setMimeType(ContentService.MimeType.TEXT);
}

function appendLead(body) {
  const sheet = getLeadSheet();

  sheet.appendRow([
    parseLeadDate(body.fecha),
    body.nombre || "",
    body.email || "",
    body.recurso || "",
    body.origen || "",
    body.campana || body.campaña || "",
    body.consentimiento || "",
    body.estado || "nuevo",
    body.notas || ""
  ]);
}

function parseLeadDate(value) {
  if (!value) {
    return new Date();
  }

  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? new Date() : parsed;
}

function getLeadSheet() {
  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);
  setupLeadSheet(sheet);

  return sheet;
}

function setupSpreadsheet() {
  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);
  setupLeadSheet(sheet);
  setupSummarySheet(spreadsheet);
}

function setupLeadSheet(sheet) {
  const firstRow = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0];
  const hasHeaders = firstRow.join("") !== "";

  if (!hasHeaders) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  }

  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, HEADERS.length)
    .setFontWeight("bold")
    .setFontColor("#ffffff")
    .setBackground("#06245c")
    .setHorizontalAlignment("center");
  sheet.getRange(1, 1, sheet.getMaxRows(), HEADERS.length)
    .setBorder(true, true, true, true, true, true, "#d9e6fb", SpreadsheetApp.BorderStyle.SOLID);
  sheet.getRange(2, 1, Math.max(sheet.getMaxRows() - 1, 1), 1).setNumberFormat("yyyy-mm-dd hh:mm");
  sheet.setColumnWidth(1, 165);
  sheet.setColumnWidth(2, 150);
  sheet.setColumnWidth(3, 230);
  sheet.setColumnWidth(4, 210);
  sheet.setColumnWidth(5, 130);
  sheet.setColumnWidth(6, 170);
  sheet.setColumnWidth(7, 145);
  sheet.setColumnWidth(8, 130);
  sheet.setColumnWidth(9, 260);

  if (!sheet.getFilter()) {
    sheet.getRange(1, 1, sheet.getMaxRows(), HEADERS.length).createFilter();
  }

  const statusRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(STATUS_VALUES, true)
    .setAllowInvalid(false)
    .build();
  sheet.getRange(2, 8, Math.max(sheet.getMaxRows() - 1, 1), 1).setDataValidation(statusRule);
}

function setupSummarySheet(spreadsheet) {
  const sheet = spreadsheet.getSheetByName(SUMMARY_SHEET_NAME) || spreadsheet.insertSheet(SUMMARY_SHEET_NAME);
  sheet.clear();
  sheet.getRange("A1").setValue("Resumen leads TRADINVERSO");
  sheet.getRange("A3").setValue("Total leads");
  sheet.getRange("B3").setFormula("=CONTARA(Leads!C2:C)");
  sheet.getRange("A4").setValue("Último lead");
  sheet.getRange("B4").setFormula("=SI(CONTARA(Leads!A2:A)=0;\"\";MAX(Leads!A2:A))");
  sheet.getRange("A6").setValue("Leads por recurso");
  sheet.getRange("A7").setFormula("=SI(CONTARA(Leads!C2:C)=0;\"Sin datos\";QUERY(Leads!A2:I;\"select D, count(C) where C is not null group by D label D 'recurso', count(C) 'leads'\";0))");
  sheet.getRange("A1:B1")
    .setFontWeight("bold")
    .setFontColor("#ffffff")
    .setBackground("#06245c");
  sheet.getRange("A3:B7").setBorder(true, true, true, true, true, true, "#d9e6fb", SpreadsheetApp.BorderStyle.SOLID);
  sheet.setColumnWidth(1, 220);
  sheet.setColumnWidth(2, 140);
}
