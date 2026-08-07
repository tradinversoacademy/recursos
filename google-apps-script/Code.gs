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
    String(body.nombre || "").trim(),
    String(body.email || "").trim().toLowerCase(),
    body.recurso || "",
    body.origen || "",
    body.campana || body.campaña || "",
    body.consentimiento || "",
    body.estado || "nuevo",
    body.notas || ""
  ]);

  // Asegura el formato de fecha en la fila recién añadida,
  // independientemente de la configuración regional.
  sheet.getRange(sheet.getLastRow(), 1).setNumberFormat("yyyy-mm-dd hh:mm");

  // Mantiene el Resumen al día con cada lead.
  try {
    setupSummarySheet(SpreadsheetApp.openById(SPREADSHEET_ID));
  } catch (error) {
    // El Resumen nunca debe impedir que el lead se guarde.
  }
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
  // Calcula todo en el script y escribe valores: inmune a la configuración
  // regional del documento y siempre al día (se ejecuta con cada lead).
  const sheet = spreadsheet.getSheetByName(SUMMARY_SHEET_NAME) || spreadsheet.insertSheet(SUMMARY_SHEET_NAME);
  const leadSheet = spreadsheet.getSheetByName(SHEET_NAME);
  const lastRow = leadSheet ? leadSheet.getLastRow() : 1;
  const rows = lastRow > 1 ? leadSheet.getRange(2, 1, lastRow - 1, HEADERS.length).getValues() : [];
  const leads = rows.filter(function (row) { return String(row[2] || "").trim() !== ""; });

  const uniqueEmails = {};
  const byResource = {};
  const byStatus = {};
  let lastDate = null;
  let lastSevenDays = 0;
  const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

  leads.forEach(function (row) {
    const date = row[0] instanceof Date ? row[0] : new Date(row[0]);
    const email = String(row[2]).trim().toLowerCase();
    const resource = String(row[3] || "(sin recurso)");
    const status = String(row[7] || "nuevo");

    uniqueEmails[email] = true;
    byResource[resource] = (byResource[resource] || 0) + 1;
    byStatus[status] = (byStatus[status] || 0) + 1;
    if (!Number.isNaN(date.getTime())) {
      if (!lastDate || date > lastDate) lastDate = date;
      if (date > weekAgo) lastSevenDays += 1;
    }
  });

  const sorted = function (counts) {
    return Object.keys(counts)
      .map(function (key) { return [key, counts[key]]; })
      .sort(function (a, b) { return b[1] - a[1]; });
  };

  sheet.clear();
  sheet.getRange("A1").setValue("Resumen leads TRADINVERSO");
  sheet.getRange("A2").setValue("Actualizado automáticamente con cada lead");
  sheet.getRange("A3").setValue("Total leads");
  sheet.getRange("B3").setValue(leads.length);
  sheet.getRange("A4").setValue("Personas únicas");
  sheet.getRange("B4").setValue(Object.keys(uniqueEmails).length);
  sheet.getRange("A5").setValue("Últimos 7 días");
  sheet.getRange("B5").setValue(lastSevenDays);
  sheet.getRange("A6").setValue("Último lead");
  if (lastDate) {
    sheet.getRange("B6").setValue(lastDate).setNumberFormat("yyyy-mm-dd hh:mm");
  }

  sheet.getRange("A8").setValue("Leads por recurso");
  const resourceRows = sorted(byResource);
  if (resourceRows.length) {
    sheet.getRange(9, 1, resourceRows.length, 2).setValues(resourceRows);
  }

  sheet.getRange("D8").setValue("Leads por estado");
  const statusRows = sorted(byStatus);
  if (statusRows.length) {
    sheet.getRange(9, 4, statusRows.length, 2).setValues(statusRows);
  }

  sheet.getRange("A1:B1")
    .setFontWeight("bold")
    .setFontColor("#ffffff")
    .setBackground("#06245c");
  sheet.getRange("A2").setFontColor("#566578");
  sheet.getRange("A8").setFontWeight("bold");
  sheet.getRange("D8").setFontWeight("bold");
  sheet.getRange("A3:B6").setBorder(true, true, true, true, true, true, "#d9e6fb", SpreadsheetApp.BorderStyle.SOLID);
  sheet.setColumnWidth(1, 260);
  sheet.setColumnWidth(2, 140);
  sheet.setColumnWidth(4, 180);
  sheet.setColumnWidth(5, 100);
}
