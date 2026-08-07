import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const sourcePath = "C:/Users/Administrator/Downloads/competencia 300 traders.xlsx";
const previewDir = "C:/Users/Administrator/Documents/RECURSOS/tmp/competidores-priorizados/previews-original";

await fs.mkdir(previewDir, { recursive: true });
const source = await FileBlob.load(sourcePath);
const workbook = await SpreadsheetFile.importXlsx(source);

const overview = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 12000,
  tableMaxRows: 12,
  tableMaxCols: 20,
  tableMaxCellChars: 160,
});
console.log("OVERVIEW");
console.log(overview.ndjson);

const sheets = await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 4000 });
console.log("SHEETS");
console.log(sheets.ndjson);

for (let index = 0; ; index += 1) {
  let sheet;
  try {
    sheet = workbook.worksheets.getItemAt(index);
  } catch {
    break;
  }
  if (!sheet) break;
  const used = sheet.getUsedRange(true);
  const range = used ? used.address : "A1";
  console.log(`SHEET_RANGE ${index} ${sheet.name} ${range}`);
  const preview = await workbook.render({ sheetName: sheet.name, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${previewDir}/sheet-${String(index + 1).padStart(2, "0")}.png`, new Uint8Array(await preview.arrayBuffer()));
}
