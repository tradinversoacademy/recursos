import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const sourcePath = "C:/Users/Administrator/Downloads/competencia 300 traders.xlsx";
const source = await FileBlob.load(sourcePath);
const workbook = await SpreadsheetFile.importXlsx(source);

const terms = ["tradinglab", "trading.lab", "traderlab", "alexruiz", "alex ruiz", "ashleyruiz", "tradeando", "enrique", "mery", "fondea", "belikethealgo"];

for (let i = 0; i < 3; i += 1) {
  const sheet = workbook.worksheets.getItemAt(i);
  const used = sheet.getUsedRange(true);
  const rows = used.values;
  console.log(`\n### ${sheet.name} (${rows.length} rows)`);
  for (let r = 0; r < rows.length; r += 1) {
    const joined = rows[r].map((v) => v == null ? "" : String(v)).join(" | ");
    const normalized = joined.toLowerCase();
    if (terms.some((term) => normalized.includes(term))) {
      console.log(`${r + 1}: ${joined}`);
    }
  }
}

const igRows = workbook.worksheets.getItem("competencia ig").getRange("A2:H329").values;
const usernames = igRows.map((r) => String(r[1] ?? "").trim().toLowerCase()).filter(Boolean);
const duplicateNames = [...new Set(usernames.filter((u, idx) => usernames.indexOf(u) !== idx))];
const ytRows = workbook.worksheets.getItem("competencia en yt").getRange("A1:A254").values.flat().map((v) => String(v ?? "").trim()).filter(Boolean);
const normalizedYt = ytRows.map((url) => url.toLowerCase().replace(/[?#].*$/, "").replace(/\/$/, ""));
const duplicateYt = [...new Set(normalizedYt.filter((u, idx) => normalizedYt.indexOf(u) !== idx))];
console.log("\nSUMMARY");
console.log(JSON.stringify({
  instagramRows: igRows.filter((r) => r.some((v) => v != null && String(v).trim() !== "")).length,
  instagramDuplicateUsernames: duplicateNames,
  youtubeNonBlankRows: ytRows.length,
  youtubeUniqueNormalized: new Set(normalizedYt).size,
  youtubeDuplicateNormalized: duplicateYt,
}, null, 2));
