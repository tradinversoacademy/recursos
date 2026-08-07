import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const sourcePath = "C:/Users/Administrator/Downloads/competencia 300 traders.xlsx";
const outputPath = "C:/Users/Administrator/Documents/RECURSOS/COMPETIDORES/app/data/seed.json";

const blob = await FileBlob.load(sourcePath);
const workbook = await SpreadsheetFile.importXlsx(blob);

const cleanUrl = (value) => {
  const raw = String(value ?? "").trim();
  if (!raw) return "";
  const normalized = raw.startsWith("http") ? raw : `https://${raw}`;
  try {
    const url = new URL(normalized);
    url.search = "";
    url.hash = "";
    return url.toString();
  } catch {
    return raw;
  }
};

const slugFromInstagram = (url) => {
  try {
    const path = new URL(cleanUrl(url)).pathname.split("/").filter(Boolean);
    return (path[0] ?? "").toLowerCase();
  } catch {
    return "";
  }
};

const academyRows = workbook.worksheets.getItem("academias").getRange("A1:G7").values;
const academyNotes = new Map();
for (const row of academyRows) {
  const instagramUrl = cleanUrl(row[0]);
  const username = slugFromInstagram(instagramUrl);
  if (!username) continue;
  const notes = row.slice(4).map((v) => String(v ?? "").trim()).filter(Boolean).join(" · ");
  academyNotes.set(username, notes);
}

const priorityOrder = new Map([
  ["fxtrading.lab", 1],
  ["alexruizn7", 2],
  ["tradeando", 3],
  ["enrique-moris", 4],
  ["merytrader212", 5],
  ["fondeapro", 6],
  ["belikethealgo", 7],
  ["traderlabacademy", 8],
  ["sr.machadofx", 9],
  ["elsensei", 10],
  ["senseiprofe", 11],
]);

const knownYoutube = new Map([
  ["fxtrading.lab", "https://www.youtube.com/@InstitucionalTradingLab"],
  ["belikethealgo", "https://www.youtube.com/@BELIKETHEALGO"],
]);

const sourceRows = workbook.worksheets.getItem("competencia ig").getRange("A2:H329").values;
const competitors = [];

for (let index = 0; index < sourceRows.length; index += 1) {
  const row = sourceRows[index];
  const username = String(row[1] ?? "").trim();
  const name = String(row[2] ?? "").trim();
  const instagramUrl = cleanUrl(row[3]);
  if (!username && !instagramUrl) continue;
  const key = username.toLowerCase() || slugFromInstagram(instagramUrl);
  const youtubeUrl = cleanUrl(row[7]) || knownYoutube.get(key) || "";
  const academyNote = academyNotes.get(key) || "";
  const isAcademy = /academy|academia|institucional|traderlab|trading\.lab/i.test(`${username} ${name}`) || academyNotes.has(key);
  const hasSpanishSignal = /aprende|inversor|inversion|mercado|bolsa|fondeo|espa[nñ]ol|capital|trader|trading/i.test(`${username} ${name}`);
  const pinned = priorityOrder.get(key);
  competitors.push({
    id: `ig-${key || index + 1}`,
    name: name || username,
    username,
    instagramUrl,
    youtubeUrl,
    priority: pinned ? "Crítica" : (youtubeUrl || isAcademy ? "Alta" : hasSpanishSignal ? "Media" : "Baja"),
    initialOrder: pinned ?? 1000 + index,
    followers: null,
    followersUpdatedAt: null,
    studied: false,
    notes: academyNote,
    source: "Excel original",
    mailerfind: null,
  });
}

for (const row of academyRows) {
  const instagramUrl = cleanUrl(row[0]);
  const username = slugFromInstagram(instagramUrl);
  if (!username || competitors.some((item) => item.username.toLowerCase() === username)) continue;
  competitors.push({
    id: `academy-${username}`,
    name: username.replace(/[._-]+/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase()),
    username,
    instagramUrl,
    youtubeUrl: "",
    priority: "Alta",
    initialOrder: 900 + competitors.length,
    followers: null,
    followersUpdatedAt: null,
    studied: false,
    notes: academyNotes.get(username) || "Academia incluida en la hoja original",
    source: "Hoja academias",
    mailerfind: null,
  });
}

competitors.push({
  id: "manual-enrique-moris",
  name: "Enrique Moris",
  username: "",
  instagramUrl: "",
  youtubeUrl: "",
  priority: "Crítica",
  initialOrder: 4,
  followers: null,
  followersUpdatedAt: null,
  studied: false,
  notes: "Perfil pendiente de confirmar",
  source: "Prioridad indicada",
  mailerfind: null,
});

competitors.sort((a, b) => a.initialOrder - b.initialOrder || a.name.localeCompare(b.name, "es"));
competitors.forEach((item, index) => { item.manualOrder = index + 1; delete item.initialOrder; });

await fs.mkdir(new URL("./", `file:///${outputPath.replace(/\\/g, "/")}`).pathname, { recursive: true }).catch(() => {});
await fs.mkdir("C:/Users/Administrator/Documents/RECURSOS/COMPETIDORES/app/data", { recursive: true });
await fs.writeFile(outputPath, `${JSON.stringify(competitors, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ total: competitors.length, firstSeven: competitors.slice(0, 7).map((item) => ({ name: item.name, username: item.username })) }, null, 2));
