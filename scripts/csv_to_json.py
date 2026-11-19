#!/usr/bin/env python3
"""Convert headered UTF-8 CSV to a JSON array, preserving field text."""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import sys
import tempfile


def convert_csv_to_json(input_path, output_path, delimiter=None, indent=2,
                        maximum_bytes=1048576):
    if delimiter is not None and (len(delimiter) != 1 or delimiter in '\r\n"'):
        raise ValueError('delimiter must be one character other than CR, LF or quote')
    if not isinstance(indent, int) or not 0 <= indent <= 8:
        raise ValueError('indent must be between 0 and 8')
    if not isinstance(maximum_bytes, int) or maximum_bytes < 1:
        raise ValueError('maximum bytes must be positive')
    with Path(input_path).open('rb') as source:
        encoded = source.read(maximum_bytes + 1)
    if len(encoded) > maximum_bytes:
        raise ValueError('input exceeds maximum bytes')
    text = encoded.decode('utf-8-sig')
    rows = []
    if text:
        if delimiter is None:
            try:
                delimiter = csv.Sniffer().sniff(text[:65536], delimiters=',;\t|').delimiter
            except csv.Error:
                delimiter = ','
        reader = csv.reader(io.StringIO(text, newline=''), delimiter=delimiter, strict=True)
        headers = next(reader)
        if not headers or any(not h for h in headers) or len(set(headers)) != len(headers):
            raise ValueError('headers must be nonempty and unique')
        for fields in reader:
            if len(fields) != len(headers):
                raise ValueError(f'CSV line {reader.line_num}: field count differs from header')
            rows.append(dict(zip(headers, fields)))
    result = (json.dumps(rows, ensure_ascii=False, indent=indent) + '\n').encode('utf-8')
    destination = Path(output_path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as output:
            temporary = Path(output.name)
            output.write(result)
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_csv')
    parser.add_argument('output_json')
    parser.add_argument('--delimiter', help='one literal character; otherwise sniff comma, semicolon, tab or pipe')
    parser.add_argument('--indent', type=int, default=2)
    parser.add_argument('--maximum-bytes', type=int, default=1048576)
    args = parser.parse_args(argv)
    try:
        convert_csv_to_json(args.input_csv, args.output_json, args.delimiter,
                            args.indent, args.maximum_bytes)
    except (OSError, ValueError, csv.Error) as error:
        print(f'csv_to_json: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
