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
