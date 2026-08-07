const SHEET_NAME = "Leads";
const SPREADSHEET_ID = "1n-MnjkvHRd0F1Gu5JehfpRsDf3YsXKmXOnxytgfOTgY";
const SUMMARY_SHEET_NAME = "Resumen";
const UNIQUE_SHEET_NAME = "Únicos";
const UNIQUE_HEADERS = ["nombre", "email", "recursos", "primer contacto", "último contacto", "recursos pedidos"];
const HEADERS = [
  "fecha",
  "nombre",
  "email",
  "recurso",
  "origen",
  "consentimiento",
  "repetido",
  "notas"
];

function doPost(e) {
  const body = JSON.parse((e && e.postData && e.postData.contents) || "{}");
  appendLead(body);

  return ContentService
    .createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
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
  // Dos formularios enviados a la vez pueden escribir en la misma fila y
  // perder un lead. El bloqueo los serializa.
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
  } catch (error) {
    // Si el bloqueo no llega a tiempo, es preferible escribir que perder el lead.
  }

  try {
    writeLead(body);
  } finally {
    try {
      lock.releaseLock();
    } catch (error) {
      // El bloqueo puede haber expirado por su cuenta.
    }
  }
}

function writeLead(body) {
  const sheet = getLeadSheet();

  sheet.appendRow([
    parseLeadDate(body.fecha),
    String(body.nombre || "").trim(),
    String(body.email || "").trim().toLowerCase(),
    body.recurso || "",
    body.origen || "",
    body.consentimiento || "",
    "",
    body.notas || ""
  ]);

  // Asegura el formato de fecha en la fila recién añadida,
  // independientemente de la configuración regional.
  sheet.getRange(sheet.getLastRow(), 1).setNumberFormat("yyyy-mm-dd hh:mm");

  // Señal de repetidos, lista de únicos y Resumen siempre al día.
  try {
    const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
    updateRepeatSignals(sheet);
    setupUniqueSheet(spreadsheet);
    setupSummarySheet(spreadsheet);
  } catch (error) {
    // Nada de esto debe impedir que el lead se guarde.
  }
}

function parseLeadDate(value) {
  if (!value) {
    return new Date();
  }

  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? new Date() : parsed;
}

// Al guardar un lead solo se comprueba que la hoja existe con sus cabeceras:
// el formateo completo (bordes, anchos, filtros) es trabajo caro y no cambia
// entre leads, así que se reserva para setupSpreadsheet().
function getLeadSheet() {
  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);

  const firstRow = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0];
  if (firstRow.join("") === "") {
    migrateLeadSheet(sheet);
    setupLeadSheet(sheet);
  }

  return sheet;
}

function setupSpreadsheet() {
  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);
  migrateLeadSheet(sheet);
  setupLeadSheet(sheet);
  updateRepeatSignals(sheet);
  setupUniqueSheet(spreadsheet);
  setupSummarySheet(spreadsheet);
}

// Lee las filas de Leads y devuelve una entrada por persona (email).
function collectLeads(spreadsheet) {
  const leadSheet = spreadsheet.getSheetByName(SHEET_NAME);
  const lastRow = leadSheet ? leadSheet.getLastRow() : 1;
  if (lastRow < 2) return [];

  return leadSheet.getRange(2, 1, lastRow - 1, HEADERS.length).getValues()
    .filter(function (row) { return String(row[2] || "").trim() !== ""; });
}

function groupByPerson(leads) {
  const people = {};

  leads.forEach(function (row) {
    const email = String(row[2]).trim().toLowerCase();
    const date = row[0] instanceof Date ? row[0] : new Date(row[0]);
    const resource = String(row[3] || "").trim();

    if (!people[email]) {
      people[email] = { email: email, nombre: String(row[1] || "").trim(), first: null, last: null, resources: [] };
    }
    const person = people[email];
    if (!person.nombre) person.nombre = String(row[1] || "").trim();
    if (resource && person.resources.indexOf(resource) === -1) person.resources.push(resource);
    if (!Number.isNaN(date.getTime())) {
      if (!person.first || date < person.first) person.first = date;
      if (!person.last || date > person.last) person.last = date;
    }
  });

  return Object.keys(people).map(function (email) { return people[email]; });
}

// Una fila por persona, sin duplicados: la hoja para exportar a campañas.
function setupUniqueSheet(spreadsheet) {
  const sheet = spreadsheet.getSheetByName(UNIQUE_SHEET_NAME) || spreadsheet.insertSheet(UNIQUE_SHEET_NAME);
  const people = groupByPerson(collectLeads(spreadsheet));

  people.sort(function (a, b) {
    if (b.resources.length !== a.resources.length) return b.resources.length - a.resources.length;
    return (b.last ? b.last.getTime() : 0) - (a.last ? a.last.getTime() : 0);
  });

  sheet.clear();
  sheet.getRange(1, 1, 1, UNIQUE_HEADERS.length).setValues([UNIQUE_HEADERS]);

  if (people.length) {
    const rows = people.map(function (person) {
      return [
        person.nombre,
        person.email,
        person.resources.length,
        person.first,
        person.last,
        person.resources.join(", ")
      ];
    });
    sheet.getRange(2, 1, rows.length, UNIQUE_HEADERS.length).setValues(rows);
    sheet.getRange(2, 4, rows.length, 2).setNumberFormat("yyyy-mm-dd hh:mm");
    sheet.getRange(2, 3, rows.length, 1).setHorizontalAlignment("center");
  }

  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, UNIQUE_HEADERS.length)
    .setFontWeight("bold")
    .setFontColor("#ffffff")
    .setBackground("#06245c")
    .setHorizontalAlignment("center");
  sheet.setColumnWidth(1, 200);
  sheet.setColumnWidth(2, 250);
  sheet.setColumnWidth(3, 90);
  sheet.setColumnWidth(4, 150);
  sheet.setColumnWidth(5, 150);
  sheet.setColumnWidth(6, 420);

  if (!sheet.getFilter()) {
    sheet.getRange(1, 1, Math.max(people.length + 1, 2), UNIQUE_HEADERS.length).createFilter();
  }
}

// Elimina las columnas antiguas "campaña" y "estado" si siguen presentes
// y garantiza la columna "repetido". Es idempotente.
function migrateLeadSheet(sheet) {
  if (sheet.getLastRow() === 0) return;

  const width = sheet.getLastColumn();
  if (!width) return;
  const firstRow = sheet.getRange(1, 1, 1, width).getValues()[0].map(function (value) {
    return String(value).trim().toLowerCase();
  });

  ["campaña", "campana", "estado"].forEach(function (name) {
    const current = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0]
      .map(function (value) { return String(value).trim().toLowerCase(); });
    const index = current.indexOf(name);
    if (index !== -1) {
      sheet.deleteColumn(index + 1);
    }
  });

  const afterDelete = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0]
    .map(function (value) { return String(value).trim().toLowerCase(); });
  if (afterDelete.indexOf("repetido") === -1 && firstRow.join("") !== "") {
    const notasIndex = afterDelete.indexOf("notas");
    if (notasIndex !== -1) {
      sheet.insertColumnBefore(notasIndex + 1);
      sheet.getRange(1, notasIndex + 1).setValue("repetido");
    }
  }
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
  sheet.setColumnWidth(6, 145);
  sheet.setColumnWidth(7, 110);
  sheet.setColumnWidth(8, 260);

  if (!sheet.getFilter()) {
    sheet.getRange(1, 1, sheet.getMaxRows(), HEADERS.length).createFilter();
  }
}

// Marca en la columna "repetido" cuántos recursos ha pedido cada persona:
// "x2", "x3"... en cada una de sus filas. Vacío si solo ha pedido uno.
function updateRepeatSignals(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  const emailColumn = 3;
  const repeatColumn = 7;
  const emails = sheet.getRange(2, emailColumn, lastRow - 1, 1).getValues();
  const counts = {};

  emails.forEach(function (row) {
    const email = String(row[0] || "").trim().toLowerCase();
    if (email) counts[email] = (counts[email] || 0) + 1;
  });

  const signals = emails.map(function (row) {
    const email = String(row[0] || "").trim().toLowerCase();
    return [email && counts[email] > 1 ? "x" + counts[email] : ""];
  });

  const range = sheet.getRange(2, repeatColumn, signals.length, 1);
  range.setValues(signals);
  range.setFontWeight("bold").setFontColor("#2d89ff").setHorizontalAlignment("center");
}

function setupSummarySheet(spreadsheet) {
  // Calcula todo en el script y escribe valores: inmune a la configuración
  // regional del documento y siempre al día (se ejecuta con cada lead).
  const sheet = spreadsheet.getSheetByName(SUMMARY_SHEET_NAME) || spreadsheet.insertSheet(SUMMARY_SHEET_NAME);
  const leadSheet = spreadsheet.getSheetByName(SHEET_NAME);
  const lastRow = leadSheet ? leadSheet.getLastRow() : 1;
  const rows = lastRow > 1 ? leadSheet.getRange(2, 1, lastRow - 1, HEADERS.length).getValues() : [];
  const leads = rows.filter(function (row) { return String(row[2] || "").trim() !== ""; });

  const byEmail = {};
  const byResource = {};
  let lastDate = null;
  let lastSevenDays = 0;
  const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

  leads.forEach(function (row) {
    const date = row[0] instanceof Date ? row[0] : new Date(row[0]);
    const email = String(row[2]).trim().toLowerCase();
    const resource = String(row[3] || "(sin recurso)");

    byEmail[email] = (byEmail[email] || 0) + 1;
    byResource[resource] = (byResource[resource] || 0) + 1;
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
  sheet.getRange("B4").setValue(Object.keys(byEmail).length);
  const repeaters = Object.keys(byEmail).filter(function (email) { return byEmail[email] > 1; }).length;
  sheet.getRange("A5").setValue("Repiten (ver hoja Únicos)");
  sheet.getRange("B5").setValue(repeaters);
  sheet.getRange("A6").setValue("Últimos 7 días");
  sheet.getRange("B6").setValue(lastSevenDays);
  sheet.getRange("A7").setValue("Último lead");
  if (lastDate) {
    sheet.getRange("B7").setValue(lastDate).setNumberFormat("yyyy-mm-dd hh:mm");
  }

  sheet.getRange("A9").setValue("Leads por recurso");
  const resourceRows = sorted(byResource);
  if (resourceRows.length) {
    sheet.getRange(10, 1, resourceRows.length, 2).setValues(resourceRows);
  }

  sheet.getRange("A1:B1")
    .setFontWeight("bold")
    .setFontColor("#ffffff")
    .setBackground("#06245c");
  sheet.getRange("A2").setFontColor("#566578");
  sheet.getRange("A9").setFontWeight("bold");
  sheet.getRange("A3:B7").setBorder(true, true, true, true, true, true, "#d9e6fb", SpreadsheetApp.BorderStyle.SOLID);
  sheet.setColumnWidth(1, 260);
  sheet.setColumnWidth(2, 140);
}
