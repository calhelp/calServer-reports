#!/usr/bin/env python3
"""Guardrail for the PTB DCC 3.3.0 export (scripts/dcc330_writer.py).

Runs three checks:
  1. Unit tests for the D-SI helpers (prefix scaling + unit vocabulary).
  2. Regenerates the committed sample from the DAKKS-JSON-SAMPLE contract and
     asserts it is byte-identical (the writer is deterministic — parity guard).
  3. If `xmlschema` is installed AND the DCC schema (with its remote SI/dsig
     imports) can be loaded, validates the sample against dcc-v3.3.0.xsd.
     When xmlschema is missing or the schema is unreachable, that step is
     skipped (not failed), so the guard stays green offline.

Usage: python3 scripts/check_dcc330.py
Exit code 0 = ok, 1 = failure.
"""
from __future__ import annotations

import io
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import dcc330_writer as w  # noqa: E402

CONTRACT = ROOT / "DAKKS-JSON-SAMPLE" / "main_reports" / "sample-data.json"
SAMPLE = ROOT / "DAKKS-JSON-SAMPLE" / "main_reports" / "sample-dcc-3.3.0.xml"


def _fail(msg: str) -> None:
    print(f"❌ {msg}")
    raise SystemExit(1)


def check_helpers() -> None:
    cases = {
        ("35", "µ"): "0.000035",
        ("10.00000", ""): "10.00000",
        ("10.0000", "k"): "10000.0000",
        ("", ""): None,
        ("n/a", ""): None,
    }
    for (val, prefix), expected in cases.items():
        got = w._to_base(val, prefix)
        if got != expected:
            _fail(f"_to_base({val!r},{prefix!r}) = {got!r}, expected {expected!r}")
    units = {"V": r"\volt", "Ω": r"\ohm", "°C": r"\degreecelsius", "": r"\one", "A": r"\ampere"}
    for raw, dsi in units.items():
        got = w._dsi_unit(raw)
        if got != dsi:
            _fail(f"_dsi_unit({raw!r}) = {got!r}, expected {dsi!r}")
    print("✅ D-SI helper unit tests passed")


def _render(data: dict) -> bytes:
    tree = w.build_dcc(data, software_release="1.0", lang="de")
    ET.indent(tree, space="  ")
    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    return buf.getvalue()


def check_parity() -> bytes:
    import json
    if not CONTRACT.exists():
        _fail(f"contract sample missing: {CONTRACT}")
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rendered = _render(data)
    if not SAMPLE.exists():
        _fail(f"committed DCC sample missing — run: python3 scripts/dcc330_writer.py "
              f"--input {CONTRACT.relative_to(ROOT)} --output {SAMPLE.relative_to(ROOT)}")
    committed = SAMPLE.read_bytes()
    if rendered.replace(b"\r\n", b"\n") != committed.replace(b"\r\n", b"\n"):
        _fail(f"{SAMPLE.relative_to(ROOT)} is stale — regenerate it (writer output changed).")
    print(f"✅ {SAMPLE.relative_to(ROOT)} is up to date (deterministic parity)")
    return rendered


def check_structure(xml_bytes: bytes) -> None:
    root = ET.fromstring(xml_bytes)
    if not root.tag.endswith("digitalCalibrationCertificate"):
        _fail(f"unexpected root element: {root.tag}")
    if root.get("schemaVersion") != "3.3.0":
        _fail("schemaVersion attribute is not 3.3.0")
    for required in ("administrativeData", "measurementResults"):
        if root.find(f"{{{w.DCC}}}{required}") is None:
            _fail(f"missing mandatory element dcc:{required}")
    reals = root.findall(f".//{{{w.SI}}}real")
    if not reals:
        _fail("no si:real quantities emitted")
    print(f"✅ structure ok ({len(reals)} D-SI quantities)")


def check_schema() -> None:
    try:
        import xmlschema  # type: ignore
    except ModuleNotFoundError:
        print("⏭️  xmlschema not installed — skipping XSD validation")
        return
    schema_path = ROOT / "DCC" / "main_reports" / "schema" / "dcc-v3.3.0.xsd"
    try:
        schema = xmlschema.XMLSchema(str(schema_path))
    except Exception as exc:  # remote SI/dsig imports unreachable
        print(f"⏭️  DCC schema not loadable (offline?) — skipping XSD validation: {exc}")
        return
    errors = list(schema.iter_errors(str(SAMPLE)))
    if errors:
        for err in errors[:15]:
            print(f"❌ {getattr(err, 'path', '?')}: {getattr(err, 'reason', err)}")
        _fail(f"{SAMPLE.name} failed DCC 3.3.0 schema validation ({len(errors)} error(s))")
    print(f"✅ {SAMPLE.name} valid against dcc-v3.3.0.xsd")


def main() -> int:
    check_helpers()
    xml_bytes = check_parity()
    check_structure(xml_bytes)
    check_schema()
    print("\n🎉 DCC 3.3.0 export checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
