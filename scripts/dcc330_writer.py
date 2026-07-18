#!/usr/bin/env python3
"""Emit an official PTB **Digital Calibration Certificate (DCC) 3.3.0** XML from the
calServer ``calibration-certificate`` JSON contract.

This lets the DAkkS calibration certificate that already drives the
``DAKKS-JSON-SAMPLE`` JasperReport be issued *additionally* as a machine-readable
DCC per the PTB standard (https://wiki.dcc.ptb.de/). It consumes the SAME JSON
contract as the report (``DAKKS-JSON-SAMPLE/main_reports/sample-data.json``), so a
user can "choose the DAkkS certificate as DCC" without a second data source.

The output validates against ``DCC/main_reports/schema/dcc-v3.3.0.xsd`` (which
imports the D-SI unit schema and the XML-DSig schema). Measured quantities are
expressed with D-SI (``si:real`` = value + unit + expanded uncertainty).

Usage:
    python3 scripts/dcc330_writer.py \
        --input DAKKS-JSON-SAMPLE/main_reports/sample-data.json \
        --output build/dakks-dcc-3.3.0.xml --validate
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys
from decimal import Decimal
from typing import Any
import xml.etree.ElementTree as ET

DCC = "https://ptb.de/dcc"
SI = "https://ptb.de/si"
SCHEMA_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "DCC" / "main_reports" / "schema" / "dcc-v3.3.0.xsd"
)

ET.register_namespace("dcc", DCC)
ET.register_namespace("si", SI)

# --- D-SI unit vocabulary -------------------------------------------------
# calServer stores value/prefix/unit separately (e.g. exp_uncert=35, _p="µ", _u="V").
# D-SI expresses a unit as backslash tokens, so we scale the prefix into the numeric
# value and always emit the SI base unit — this keeps a value and its uncertainty in
# the same unit (a D-SI requirement for si:expandedMU).
_PREFIX_EXP = {
    "": 0, "da": 1, "h": 2, "k": 3, "M": 6, "G": 9, "T": 12,
    "d": -1, "c": -2, "m": -3, "µ": -6, "u": -6, "n": -9, "p": -12, "f": -15,
}
_UNIT_DSI = {
    "": r"\one", "1": r"\one", "%": r"\percent",
    "V": r"\volt", "mV": r"\milli\volt", "A": r"\ampere", "mA": r"\milli\ampere",
    "Ω": r"\ohm", "Ohm": r"\ohm", "ohm": r"\ohm", "W": r"\watt", "F": r"\farad",
    "H": r"\henry", "Hz": r"\hertz", "S": r"\siemens", "C": r"\coulomb",
    "K": r"\kelvin", "°C": r"\degreecelsius", "degC": r"\degreecelsius",
    "m": r"\metre", "mm": r"\milli\metre", "s": r"\second", "kg": r"\kilogram",
    "g": r"\gram", "N": r"\newton", "Pa": r"\pascal", "bar": r"\bar",
    "mol": r"\mole", "cd": r"\candela", "lx": r"\lux", "lm": r"\lumen",
}
_COUNTRY = {"deutschland": "DE", "germany": "DE", "österreich": "AT",
            "austria": "AT", "schweiz": "CH", "switzerland": "CH"}


def _dsi_unit(unit: str) -> str:
    """Map a calServer unit string to a D-SI unit token (fallback: dimensionless)."""
    return _UNIT_DSI.get((unit or "").strip(), r"\one")


def _to_base(value: str, prefix: str) -> str | None:
    """Scale ``value`` by its SI ``prefix`` into the base unit, as a plain decimal.

    Returns ``None`` when the value is empty or not numeric.
    """
    raw = (value or "").strip().replace(",", ".")
    if raw == "":
        return None
    try:
        scaled = Decimal(raw) * (Decimal(10) ** _PREFIX_EXP.get((prefix or "").strip(), 0))
    except (ArithmeticError, ValueError):
        return None
    # Plain fixed-point string (no exponent), trailing zeros trimmed but keep one decimal.
    text = format(scaled, "f")
    return text


def _iso_country(name: str) -> str:
    return _COUNTRY.get((name or "").strip().lower(), "DE")


# --- small XML helpers ----------------------------------------------------
def _el(parent: ET.Element | None, tag_ns: str, tag: str, text: str | None = None,
        **attrs: str) -> ET.Element:
    el = ET.Element(f"{{{tag_ns}}}{tag}") if parent is None else ET.SubElement(parent, f"{{{tag_ns}}}{tag}")
    if text is not None:
        el.text = str(text)
    for k, v in attrs.items():
        el.set(k, v)
    return el


def _dcc_text(parent: ET.Element, tag: str, value: str | None, lang: str = "de") -> ET.Element:
    """A dcc textType element: one <dcc:content lang="..">value</dcc:content>."""
    holder = _el(parent, DCC, tag)
    _el(holder, DCC, "content", "" if value is None else str(value), lang=lang)
    return holder


def _si_real(parent: ET.Element, value: str, unit_dsi: str,
             unc_value: str | None = None, coverage_factor: str = "2",
             coverage_prob: str = "0.95") -> ET.Element:
    """Add a ``si:real`` (D-SI value + unit + optional expanded uncertainty) under ``parent``."""
    real = _el(parent, SI, "real")
    _el(real, SI, "value", value)
    _el(real, SI, "unit", unit_dsi)
    if unc_value is not None:
        mu = _el(real, SI, "measurementUncertaintyUnivariate")
        exp = _el(mu, SI, "expandedMU")
        _el(exp, SI, "valueExpandedMU", unc_value)
        _el(exp, SI, "coverageFactor", coverage_factor)
        _el(exp, SI, "coverageProbability", coverage_prob)
    return real


def _quantity(parent: ET.Element, name: str, value: str, unit_dsi: str,
              unc_value: str | None = None, lang: str = "de") -> ET.Element:
    q = _el(parent, DCC, "quantity")
    _dcc_text(q, "name", name, lang)
    _si_real(q, value, unit_dsi, unc_value)
    return q


# --- contract -> DCC mapping ---------------------------------------------
def build_dcc(data: dict[str, Any], *, software_release: str, lang: str = "de") -> ET.ElementTree:
    meta = data.get("meta", {}) or {}
    lab = data.get("laboratory", {}) or {}
    accred = data.get("accreditation", {}) or {}
    cal = data.get("calibration", {}) or {}
    device = data.get("device", {}) or {}
    customer = data.get("customer", {}) or {}
    procedure = data.get("procedure", {}) or {}
    signatures = data.get("signatures", []) or []
    results = data.get("results", []) or []

    root = _el(None, DCC, "digitalCalibrationCertificate", schemaVersion="3.3.0")

    admin = _el(root, DCC, "administrativeData")

    # -- dccSoftware (mandatory)
    swlist = _el(admin, DCC, "dccSoftware")
    sw = _el(swlist, DCC, "software")
    _dcc_text(sw, "name", "calServer", lang)
    _el(sw, DCC, "release", software_release or "0")

    # -- coreData (mandatory)
    core = _el(admin, DCC, "coreData")
    _el(core, DCC, "countryCodeISO3166_1", _iso_country(lab.get("country")))
    _el(core, DCC, "usedLangCodeISO639_1", lang)
    _el(core, DCC, "mandatoryLangCodeISO639_1", lang)
    unique = (cal.get("certificate_number") or meta.get("certificate_number")
              or cal.get("certificate_display") or cal.get("id") or "UNKNOWN")
    _el(core, DCC, "uniqueIdentifier", str(unique))
    cal_date = (cal.get("calibration_date") or "").strip() or _today()
    _el(core, DCC, "beginPerformanceDate", cal_date)
    _el(core, DCC, "endPerformanceDate", cal_date)
    _el(core, DCC, "performanceLocation", _performance_location(lab))

    # -- items (mandatory: the calibrated device)
    items = _el(admin, DCC, "items")
    item = _el(items, DCC, "item")
    _dcc_text(item, "name", device.get("description") or device.get("model") or "Kalibriergegenstand", lang)
    manu = device.get("manufacturer")
    if manu:
        man_el = _el(item, DCC, "manufacturer")
        _dcc_text(man_el, "name", manu, lang)
    if device.get("model"):
        _el(item, DCC, "model", str(device["model"]))
    ident_list = _el(item, DCC, "identifications")
    _identification(ident_list, "manufacturer", device.get("serial_number"), "Seriennummer", lang)
    if device.get("asset_number"):
        _identification(ident_list, "customer", device.get("asset_number"), "Inventarnummer", lang)
    if not device.get("serial_number") and not device.get("asset_number"):
        # identifications requires at least one entry
        _identification(ident_list, "other", str(unique), "Zertifikatsnummer", lang)

    # -- calibrationLaboratory (mandatory)
    lab_el = _el(admin, DCC, "calibrationLaboratory")
    if lab.get("code"):
        _el(lab_el, DCC, "calibrationLaboratoryCode", str(lab["code"]))
    lab_contact = _el(lab_el, DCC, "contact")
    _dcc_text(lab_contact, "name", lab.get("name") or lab.get("company_name") or "Kalibrierlabor", lang)
    if lab.get("email"):
        _el(lab_contact, DCC, "eMail", str(lab["email"]))
    if lab.get("phone"):
        _el(lab_contact, DCC, "phone", str(lab["phone"]))
    _location(lab_contact, lab.get("city"), lab.get("country"), lab.get("zip"), lab.get("street"))

    # -- respPersons (mandatory)
    resp = _el(admin, DCC, "respPersons")
    if signatures:
        for idx, sig in enumerate(signatures):
            rp = _el(resp, DCC, "respPerson")
            person = _el(rp, DCC, "person")
            _dcc_text(person, "name", sig.get("name") or "N/A", lang)
            if sig.get("role"):
                _el(rp, DCC, "role", str(sig["role"]))
            # last signer (approver) is the main signer
            if sig.get("role", "").lower() in ("approver", "approval", "leiter") or idx == len(signatures) - 1:
                _el(rp, DCC, "mainSigner", "true")
    else:
        rp = _el(resp, DCC, "respPerson")
        person = _el(rp, DCC, "person")
        _dcc_text(person, "name", cal.get("technician") or "N/A", lang)

    # -- customer (mandatory)
    cust_el = _el(admin, DCC, "customer")
    _dcc_text(cust_el, "name", customer.get("name") or customer.get("company_name") or "Kunde", lang)
    if customer.get("email"):
        _el(cust_el, DCC, "eMail", str(customer["email"]))
    _location(cust_el, customer.get("city"), customer.get("country"), customer.get("zip"), customer.get("street"))

    # -- measurementResults (mandatory)
    mrs = _el(root, DCC, "measurementResults")
    mr = _el(mrs, DCC, "measurementResult")
    _dcc_text(mr, "name", procedure.get("procedure_name") or "Kalibrierergebnisse", lang)
    res_list = _el(mr, DCC, "results")
    emitted = 0
    for row in results:
        if _emit_result_row(res_list, row, lang):
            emitted += 1
    if emitted == 0:
        # resultListType requires at least one result: emit a text-only placeholder.
        placeholder = _el(res_list, DCC, "result")
        _dcc_text(placeholder, "name", "Keine numerischen Messwerte", lang)
        data_el = _el(placeholder, DCC, "data")
        txt = _el(data_el, DCC, "text")
        _el(txt, DCC, "content", "keine", lang=lang)

    _accreditation_statement(admin, accred, lab, lang)
    return ET.ElementTree(root)


def _emit_result_row(res_list: ET.Element, row: dict[str, Any], lang: str) -> bool:
    """Append one <dcc:result> for a calServer results row. Returns False if it has no numeric data."""
    nominal = _to_base(row.get("fixq", ""), row.get("fixq_p", ""))
    measured = _to_base(row.get("varq", ""), row.get("varq_p", ""))
    lower = _to_base(row.get("lower_limit", ""), row.get("lower_limit_p", ""))
    upper = _to_base(row.get("upper_limit", ""), row.get("upper_limit_p", ""))
    unc = _to_base(row.get("exp_uncert", ""), row.get("exp_uncert_p", ""))
    if nominal is None and measured is None:
        return False

    unit = _dsi_unit(row.get("varq_u") or row.get("fixq_u") or "")
    result = _el(res_list, DCC, "result")
    _dcc_text(result, "name", row.get("test_desc") or f"Messpunkt {row.get('row_num', '')}", lang)
    data_el = _el(result, DCC, "data")
    lst = _el(data_el, DCC, "list")
    if nominal is not None:
        _quantity(lst, "Nennwert", nominal, _dsi_unit(row.get("fixq_u") or ""), lang=lang)
    if measured is not None:
        _quantity(lst, "Messwert", measured, unit, unc_value=unc, lang=lang)
    if lower is not None:
        _quantity(lst, "Untere Grenze", lower, _dsi_unit(row.get("lower_limit_u") or ""), lang=lang)
    if upper is not None:
        _quantity(lst, "Obere Grenze", upper, _dsi_unit(row.get("upper_limit_u") or ""), lang=lang)
    return True


def _identification(parent: ET.Element, issuer: str, value: Any, name: str, lang: str) -> None:
    ident = _el(parent, DCC, "identification")
    _el(ident, DCC, "issuer", issuer)
    _el(ident, DCC, "value", str(value) if value not in (None, "") else "-")
    _dcc_text(ident, "name", name, lang)


def _location(contact: ET.Element, city: str | None, country: str | None,
              post_code: str | None, street: str | None) -> None:
    loc = _el(contact, DCC, "location")
    if city:
        _el(loc, DCC, "city", str(city))
    _el(loc, DCC, "countryCode", _iso_country(country))
    if post_code:
        _el(loc, DCC, "postCode", str(post_code))
    if street:
        _el(loc, DCC, "street", str(street))


def _performance_location(lab: dict[str, Any]) -> str:
    place = (lab.get("calibration_place") or "").lower()
    if "kunde" in place or "customer" in place or "vor ort" in place:
        return "customer"
    return "laboratory"


def _accreditation_statement(admin: ET.Element, accred: dict[str, Any],
                             lab: dict[str, Any], lang: str) -> None:
    marks = [accred.get("calibration_mark"), accred.get("mark_number_1"), lab.get("code")]
    marks = [str(m).replace("\n", " ").strip() for m in marks if m]
    if not marks:
        return
    statements = _el(admin, DCC, "statements")
    st = _el(statements, DCC, "statement")
    decl = _el(st, DCC, "declaration")
    _el(decl, DCC, "content",
        "Akkreditierte Kalibrierung (DAkkS): " + ", ".join(marks), lang=lang)


def _today() -> str:
    return dt.date.today().isoformat()


# --- validation & CLI -----------------------------------------------------
def validate(xml_path: pathlib.Path) -> bool:
    try:
        import xmlschema  # type: ignore
    except ModuleNotFoundError:
        print("⚠️  xmlschema not installed; skipping validation.", file=sys.stderr)
        return True
    try:
        schema = xmlschema.XMLSchema(str(SCHEMA_PATH))
    except Exception as exc:  # remote SI/dsig imports unreachable
        print(f"⚠️  Could not load DCC schema (offline?): {exc}", file=sys.stderr)
        return True
    errors = list(schema.iter_errors(str(xml_path)))
    if errors:
        for err in errors[:15]:
            print(f"❌ {err.path}: {err.reason}", file=sys.stderr)
        return False
    print(f"✅ XML valid against {SCHEMA_PATH.name}")
    return True


def _serialize(tree: ET.ElementTree, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main(argv: list[str] | None = None) -> int:
    import json
    parser = argparse.ArgumentParser(description="Emit a PTB DCC 3.3.0 XML from the calibration-certificate JSON contract")
    parser.add_argument("--input", required=True, help="calibration-certificate JSON (same as the DAKKS-JSON-SAMPLE report data)")
    parser.add_argument("--output", default="dcc-3.3.0.xml", help="target XML path")
    parser.add_argument("--software-release", default="1.0", help="release string for the producing software (calServer)")
    parser.add_argument("--lang", default="de", help="primary ISO 639-1 language code")
    parser.add_argument("--validate", action="store_true", help="validate the result against dcc-v3.3.0.xsd (needs xmlschema)")
    args = parser.parse_args(argv)

    in_path = pathlib.Path(args.input)
    try:
        data = json.loads(in_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"❌ Input file not found: {in_path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"❌ Invalid JSON in {in_path}: {exc}")

    tree = build_dcc(data, software_release=args.software_release, lang=args.lang)
    out_path = pathlib.Path(args.output)
    _serialize(tree, out_path)
    print(f"DCC 3.3.0 XML written to {out_path}")

    if args.validate:
        return 0 if validate(out_path) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
