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
