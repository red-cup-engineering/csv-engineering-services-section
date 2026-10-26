# CSV services section

<!-- 561-group-standards:badges:start -->
[![Red Cup Engineering](https://img.shields.io/badge/561%20Group-Red%20Cup%20Engineering-c0392b)](https://github.com/red-cup-engineering)
[![License: MIT](https://img.shields.io/badge/license-MIT-c0392b)](LICENSE)
[![Indigenous data: CARE](https://img.shields.io/badge/Indigenous%20data-CARE-4b6f44)](https://github.com/red-cup-engineering/.github/blob/main/GOVERNANCE.md)
[![Tips welcome](https://img.shields.io/badge/tips-welcome-d4a017)](https://github.com/561-group/.github/blob/main/TIPS.md)
<!-- 561-group-standards:badges:end -->

Comma-separated values as RFC 4180 defines them. `decodeCsvRows` reads CSV
text into rows of fields, `decodeCsv` into records keyed by the header row, and
`encodeCsv` writes records back out with every field quoted. Quoted fields may
hold commas, doubled quotes and line breaks, as county report exports do.

```js
import { decodeCsv, encodeCsv } from "@red-cup-engineering/csv-services-section/csv-codec";

const records = decodeCsv(text);
await writeFile("sellers.csv", encodeCsv(records));
```

## Python JSON-to-CSV CLI

Python 3.10 or later; the converter uses only the standard library:

```sh
python3 scripts/json_to_csv.py input.json output.csv
# After installing this package, the same executable is available as json-to-csv.
```

For `[{"name":"Ada"},{"name":"Bo","active":true}]`, the result is:

```csv
"name","active"
"Ada",""
"Bo","true"
```

The input is a UTF-8 JSON array of flat objects. Headers include every key in
first-seen order; missing keys and null become empty cells, and booleans become
`true` or `false`. Numbers must be finite. Empty input arrays produce empty
files. Commas, quotes, Unicode and embedded newlines are preserved. Every field
is quoted with doubled embedded quotes and CRLF record endings, following
[RFC 4180 section 2](https://www.rfc-editor.org/rfc/rfc4180.html#section-2).

Invalid JSON, nested values, non-finite numbers and invalid UTF-8 produce a
nonzero exit code and a diagnostic on stderr. The complete result is validated
and encoded before opening the output, so validation failures leave an existing
output unchanged. A valid conversion replaces the destination. Runtime memory
holds the input and result; this CLI is intended for ordinary file conversion,
not streaming arbitrarily large datasets.

Run the buyer-facing tests with installed pytest:

```sh
python3 -m pytest -q test/test_json_to_csv.py
npm test
```

This file adapter serves the requirements of the public
[OpenTask JSON-to-CSV task](https://opentask.ai/tasks/cmpupoqmm0027kw04351wcfhz)
(source updated October 3, 2026). It adds missing-key/union-header behavior for
that CLI; the existing JavaScript `jsonToCsv({records, columns})` contract still
requires exactly the declared columns. Source preparation establishes no award,
buyer acceptance or payment.

## Python CSV-to-JSON CLI

```sh
python3 scripts/csv_to_json.py input.csv output.json
python3 scripts/csv_to_json.py input-semicolon.csv output.json --delimiter ';' --indent 4
python3 -m unittest discover -s test -p test_csv_to_json.py
```

The converter accepts headered UTF-8 (including a BOM), detects comma, semicolon,
tab and pipe delimiters, and supports a literal single-character override. Use
an actual tab in the delimiter argument. Every value remains a string, including
leading zeros and empty cells. Quoted separators, doubled quotes, embedded
newlines and Unicode are preserved. Empty files and header-only files yield an
empty array. Indentation is configurable from 0 through 8 spaces.

Duplicate or empty headers, inconsistent row widths, invalid quoting or UTF-8,
and inputs over the default 1,048,576-byte ceiling fail with a diagnostic and
nonzero exit code. `--maximum-bytes` selects another positive ceiling. Input is
fully validated before a temporary output in the destination directory is
atomically substituted, preserving the destination on invalid input.

This package serves both directions of the original CSV business. It is prepared
for the two public 100-USDC CSV-to-JSON requests; each buyer must agree the exact
artifact, bounded semantics and machine acceptance before commissioned delivery.
