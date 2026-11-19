#!/usr/bin/env python3
"""Convert a JSON array of flat objects to UTF-8, quoted RFC 4180 CSV."""

import argparse
import csv
import io
import json
import math
from pathlib import Path
import sys


def _reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")


def _cell(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def convert_json_to_csv(input_path, output_path):
    """Validate the complete input before opening or replacing the output."""
    with Path(input_path).open(encoding="utf-8") as source:
        records = json.load(source, parse_constant=_reject_constant)
    if not isinstance(records, list):
        raise ValueError("input must be a JSON array of flat objects")
    columns = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"record {index + 1} must be a flat object")
        for key, value in record.items():
            if isinstance(value, (dict, list)):
                raise ValueError(f"record {index + 1} contains a nested value")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f"record {index + 1} contains a non-finite number")
            columns.setdefault(key, None)

    text = io.StringIO(newline="")
    if records:
        writer = csv.writer(text, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
        writer.writerow(columns)
        for record in records:
            writer.writerow(_cell(record.get(key)) for key in columns)
    # Encoding can reject malformed Unicode accepted by JSON's escape syntax.
    # Complete it before write_bytes can truncate an existing destination.
    encoded = text.getvalue().encode("utf-8")
    Path(output_path).write_bytes(encoded)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", help="UTF-8 JSON file containing an array of flat objects")
    parser.add_argument("output_csv", help="destination CSV file (replaced only after input validation)")
    args = parser.parse_args(argv)
    try:
        convert_json_to_csv(args.input_json, args.output_csv)
    except (OSError, ValueError, RecursionError) as error:
        print(f"json_to_csv: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
