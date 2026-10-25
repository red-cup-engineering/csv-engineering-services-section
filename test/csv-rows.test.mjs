import test from "node:test";
import assert from "node:assert/strict";
import { decodeCsvRows, encodeCsv, encodeCsvField, encodeCsvRows } from "../scripts/csv-codec.mjs";

test("encodeCsvRows quotes only where RFC 4180 needs it, LF by default", () => {
  const rows = [["a,b", "n"], ['say "hi", ok', 1], ["a|b", 2.5], ["two\nlines", null]];
  const text = encodeCsvRows(rows);
  assert.equal(text, '"a,b",n\n"say ""hi"", ok",1\na|b,2.5\n"two\nlines",\n');
  assert.deepEqual(decodeCsvRows(text), [["a,b", "n"], ['say "hi", ok', "1"], ["a|b", "2.5"], ["two\nlines", ""]]);
});

test("encodeCsvRows takes CRLF, all-quoted output, and writes no rows as the empty text", () => {
  assert.equal(encodeCsvRows([["a", "b"]], { lineEnding: "\r\n" }), "a,b\r\n");
  assert.equal(encodeCsvRows([["a", "b"]], { quoting: "all" }), '"a","b"\n');
  assert.equal(encodeCsvRows([]), "");
  assert.throws(() => encodeCsvRows([["a"]], { lineEnding: "\r" }), TypeError);
  assert.throws(() => encodeCsvRows([["a"]], { quoting: "some" }), TypeError);
});

test("encodeCsv keeps quoting every field unless asked for minimal", () => {
  const records = [{ a: "x", b: "y,z" }];
  assert.equal(encodeCsv(records), '"a","b"\n"x","y,z"\n');
  assert.equal(encodeCsv(records, { quoting: "minimal" }), 'a,b\nx,"y,z"\n');
  assert.equal(encodeCsvField("plain", { quoting: "minimal" }), "plain");
  assert.equal(encodeCsvField("plain"), '"plain"');
});
