/**
 * csv-codec — comma-separated values (RFC 4180): `decodeCsvRows` reads text into rows of fields,
 * `decodeCsv` reads it into records keyed by the header row, `encodeCsv` writes records back out,
 * and `encodeCsvRows` writes plain rows of fields (minimal quoting by default). Quoted fields may hold commas, doubled quotes and line breaks; CRLF and LF line endings and
 * a leading byte-order mark are accepted. Pure string ↔ value functions, no I/O.
 * @packageDocumentation
 */

/** Rows of fields. Blank lines are dropped; an unterminated quoted field is an error. */
export function decodeCsvRows(text) {
  const source = text.charCodeAt(0) === 0xfeff ? text.slice(1) : text;
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  let closedQuote = false;
  let started = false;
  const endRow = () => {
    row.push(field);
    if (row.length > 1 || row[0] !== "" || started) rows.push(row);
    row = [];
    field = "";
    started = false;
    closedQuote = false;
  };
  for (let index = 0; index < source.length; index += 1) {
    const char = source[index];
    if (quoted) {
      if (char === '"' && source[index + 1] === '"') { field += '"'; index += 1; }
      else if (char === '"') { quoted = false; closedQuote = true; }
      else field += char;
    } else if (char === '"' && !started) { quoted = true; started = true; }
    else if (char === ",") { row.push(field); field = ""; started = false; closedQuote = false; }
    else if (char === "\n") endRow();
    else if (char === "\r" && source[index + 1] === "\n") { endRow(); index += 1; }
    else {
      if (closedQuote || char === '"' || char === "\r") throw new SyntaxError("CSV has an invalid quote or line ending");
      field += char; started = true;
    }
  }
  if (quoted) throw new SyntaxError("CSV text ends inside a quoted field");
  if (started || field !== "" || row.length > 0) endRow();
  return rows;
}

/** Records keyed by the header row; a short row's missing fields read as "". */
export function decodeCsv(text) {
  const [columns, ...rows] = decodeCsvRows(text);
  if (!columns) return [];
  return rows.map((row) => Object.fromEntries(columns.map((column, index) => [column, row[index] ?? ""])));
}

const LINE_ENDINGS = ["\n", "\r\n"];
const QUOTINGS = ["all", "minimal"];
function admitFormat(lineEnding, quoting) {
  if (!LINE_ENDINGS.includes(lineEnding)) throw new TypeError("CSV line ending must be LF or CRLF");
  if (!QUOTINGS.includes(quoting)) throw new TypeError('CSV quoting must be "all" or "minimal"');
}

/** One field as RFC 4180 text: always quoted (`quoting: "all"`), or quoted only when it holds a comma,
 *  a double quote, CR or LF (`quoting: "minimal"`). A missing value (null, undefined) is the empty field. */
export function encodeCsvField(value, { quoting = "all" } = {}) {
  admitFormat("\n", quoting);
  const text = String(value ?? "");
  return quoting === "all" || /[",\r\n]/u.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

/** Rows of fields (a header row is just the first row) as CSV text, one line ending after every row,
 *  fields quoted only where RFC 4180 needs it unless `quoting: "all"`. No rows is the empty text. */
export function encodeCsvRows(rows, { lineEnding = "\n", quoting = "minimal" } = {}) {
  admitFormat(lineEnding, quoting);
  return rows.map((row) => `${row.map((field) => encodeCsvField(field, { quoting })).join(",")}${lineEnding}`).join("");
}

/**
 * Records as CSV text with a header row, every field quoted (`quoting: "all"`, the default; "minimal"
 * quotes only where needed), LF line endings and a final newline. Columns default to the first
 * record's keys.
 */
export function encodeCsv(records, { columns = records.length ? Object.keys(records[0]) : [], lineEnding = "\n", quoting = "all" } = {}) {
  admitFormat(lineEnding, quoting);
  if (records.length === 0) return "";
  return encodeCsvRows([columns, ...records.map((record) => columns.map((column) => record[column]))], { lineEnding, quoting });
}

const limit = 65536;
function bounded(text) {
  if (typeof text !== "string" || !text.isWellFormed() || new TextEncoder().encode(text).length > limit) throw new TypeError("CSV conversion requires well-formed Unicode within 65536 UTF-8 bytes");
}
/** Convert a CSV header and rectangular rows, without silently dropping extra cells. */
export function csvToJson(body) {
  if (!body || Object.keys(body).join() !== "text") throw new TypeError("request requires only text");
  bounded(body.text);
  const [columns, ...rows] = decodeCsvRows(body.text);
  if (!columns) return { columns: [], records: [] };
  if (new Set(columns).size !== columns.length) throw new TypeError("CSV headers must be unique");
  if (rows.length > 4096 || columns.length > 256 || rows.some(row => row.length !== columns.length)) throw new TypeError("CSV must have at most 4096 rectangular rows and 256 columns");
  return { columns, records: rows.map(row => Object.fromEntries(columns.map((key, index) => [key, row[index]]))) };
}
/** Emit RFC 4180 quoting and CRLF. Values are scalar; column order is explicit. */
export function jsonToCsv(body) {
  if (!body || !Array.isArray(body.records) || !Array.isArray(body.columns) || Object.keys(body).some(key => !["records", "columns"].includes(key))) throw new TypeError("request requires records and columns");
  const { columns, records } = body;
  if (!columns.length || columns.length > 256 || columns.some(key => typeof key !== "string") || new Set(columns).size !== columns.length || records.length > 4096) throw new TypeError("requires 1–256 unique column names and at most 4096 records");
  for (const record of records) {
    if (!record || typeof record !== "object" || Array.isArray(record) || Object.keys(record).some(key => !columns.includes(key)) || columns.some(key => !Object.hasOwn(record, key))) throw new TypeError("each record must have exactly the declared columns");
    if (Object.values(record).some(value => value !== null && (!["string", "number", "boolean"].includes(typeof value) || (typeof value === "number" && !Number.isFinite(value))))) throw new TypeError("CSV fields must be finite JSON scalars");
  }
  const text = records.length ? encodeCsv(records, { columns, lineEnding: "\r\n" }) : columns.map(key => `"${key.replaceAll('"', '""')}"`).join(",") + "\r\n";
  bounded(text);
  return { text, mediaType: "text/csv", standard: "RFC4180", rowCount: records.length };
}
