"""Exercise the shipped Python CLI, including safe failure at its file boundary."""

import csv
import io
import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "json_to_csv.py"


def run_cli(source, target):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(source), str(target)],
        capture_output=True, text=True, timeout=10, check=False,
    )


def test_first_seen_union_missing_keys_and_scalar_values(tmp_path):
    source, target = tmp_path / "input.json", tmp_path / "output.csv"
    source.write_text(json.dumps([
        {"name": "Ada", "active": True},
        {"score": 2.5, "name": "Bo", "active": False, "note": None},
        {},
    ]), encoding="utf-8")
    result = run_cli(source, target)
    assert result.returncode == 0, result.stderr
    assert result.stdout == result.stderr == ""
    assert target.read_bytes() == (
        b'"name","active","score","note"\r\n'
        b'"Ada","true","",""\r\n'
        b'"Bo","false","2.5",""\r\n'
        b'"","","",""\r\n'
    )


def test_unicode_commas_quotes_and_embedded_line_breaks_round_trip(tmp_path):
    source, target = tmp_path / "input.json", tmp_path / "output.csv"
    records = [{"city": "東京 🤖", "a,\"b": 'comma, "quote"\nnext\r\nlast'}]
    source.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    result = run_cli(source, target)
    assert result.returncode == 0, result.stderr
    raw = target.read_bytes()
    assert raw.endswith(b"\r\n")
    assert b'"a,""b"' in raw
    assert list(csv.reader(io.StringIO(raw.decode("utf-8"), newline=""))) == [
        ["city", 'a,"b'], ["東京 🤖", 'comma, "quote"\nnext\r\nlast'],
    ]


def test_empty_array_writes_an_empty_file(tmp_path):
    source, target = tmp_path / "input.json", tmp_path / "output.csv"
    source.write_text("[]", encoding="utf-8")
    assert run_cli(source, target).returncode == 0
    assert target.read_bytes() == b""


@pytest.mark.parametrize("body", [
    b"{broken", b"{}", b"null", b"[1]", b"[null]", b"[[]]",
    b'[{"x": {"nested": 1}}]', b'[{"x": [1]}]',
    b'[{"x": NaN}]', b'[{"x": Infinity}]', b'[{"x": -Infinity}]',
    b'[{"x": 1e400}]', b'[{"x": "\\ud800"}]', b"\xff",
])
def test_invalid_input_does_not_overwrite_existing_output(tmp_path, body):
    source, target = tmp_path / "input.json", tmp_path / "output.csv"
    source.write_bytes(body)
    target.write_bytes(b"existing customer output\r\n")
    result = run_cli(source, target)
    assert result.returncode != 0
    assert result.stderr.startswith("json_to_csv:")
    assert target.read_bytes() == b"existing customer output\r\n"


def test_missing_input_does_not_create_output(tmp_path):
    target = tmp_path / "output.csv"
    assert run_cli(tmp_path / "absent.json", target).returncode != 0
    assert not target.exists()
