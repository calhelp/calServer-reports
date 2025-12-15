#!/usr/bin/env python3
"""Utility to emit a DCC XML next to the JasperReports PDF output.

The script expects the same data that powers the `dcc-sample.jrxml` report:
- calibration metadata (from the main SQL query)
- measurement rows (from `results`)

It writes a schema-aware XML (see `DCC/main_reports/schema/dcc-certificate.xsd`) and
can optionally validate using the `xmlschema` package when available.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
import uuid
import xml.etree.ElementTree as ET
from typing import Any, Dict, Iterable

SCHEMA_PATH = pathlib.Path(__file__).parent.parent / "DCC" / "main_reports" / "schema" / "dcc-certificate.xsd"
NAMESPACE = "https://calhelp.de/dcc"


def _text(parent: ET.Element, name: str, value: Any | None) -> ET.Element:
    child = ET.SubElement(parent, name)
    if value is not None:
        child.text = str(value)
    return child


def _strip(value: Any | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _load_payload(path: pathlib.Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"❌ Input file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"❌ Invalid JSON in {path}: {exc}")


def build_xml(data: Dict[str, Any], measurement_option: str, report_id: str) -> ET.ElementTree:
    root = ET.Element("CalibrationCertificate", attrib={
        "measurementOption": measurement_option,
        "schemaVersion": "1.0",
        "xmlns": NAMESPACE,
    })

    report = data.get("report", {})
    calibration = data.get("calibration", {})
    results = data.get("results", [])

    report_meta = ET.SubElement(root, "ReportMeta")
    _text(report_meta, "ReportName", _strip(report.get("name", "dcc-sample")))
    _text(report_meta, "ReportId", report_id)
    _text(report_meta, "ReportPath", _strip(report.get("reportpath")))
    _text(report_meta, "Language", _strip(report.get("language", "Deutsch")))
    _text(report_meta, "GeneratedAt", dt.datetime.now(dt.timezone.utc).isoformat())

    cal_el = ET.SubElement(root, "Calibration")
    _text(cal_el, "CTag", _strip(calibration.get("ctag")))
    _text(cal_el, "CertField", _strip(calibration.get("cert_field")))
    _text(cal_el, "CalDate", _strip(calibration.get("cal_date")))
    _text(cal_el, "Customer", _strip(calibration.get("customer")))

    device = calibration.get("asset", {})
    if device:
        device_el = ET.SubElement(cal_el, "Device")
        _text(device_el, "Name", _strip(device.get("name")))
        _text(device_el, "Type", _strip(device.get("type")))
        _text(device_el, "Manufacturer", _strip(device.get("manufacturer")))
        _text(device_el, "SerialNumber", _strip(device.get("serial_number")))
        _text(device_el, "InventoryNumber", _strip(device.get("inventory_number")))
        _text(device_el, "AdditionalId", _strip(device.get("additional_id")))
        _text(device_el, "Description", _strip(device.get("description")))

    procedures = calibration.get("procedures", {})
    if procedures:
        proc_el = ET.SubElement(cal_el, "Procedures")
        _text(proc_el, "ProcedureName", _strip(procedures.get("procedure_name")))
        _text(proc_el, "ProcedureDescription", _strip(procedures.get("procedure_description")))
        _text(proc_el, "CalibrationMethod", _strip(procedures.get("calibration_method")))
        _text(proc_el, "CalibrationItem", _strip(procedures.get("calibration_item")))
        _text(proc_el, "Standards", _strip(procedures.get("standards")))
        _text(proc_el, "Scope", _strip(procedures.get("scope")))

    env_el = ET.SubElement(cal_el, "Environment")
    _text(env_el, "IncomingDate", _strip(calibration.get("incoming_date")))
    _text(env_el, "Condition", _strip(calibration.get("condition")))
    _text(env_el, "CalibrationPlace", _strip(calibration.get("calibration_place")))
    _text(env_el, "WorkingHours", _strip(calibration.get("working_hours")))
    _text(env_el, "EnvironmentalConditions", _strip(calibration.get("environmental_conditions")))

    results_el = ET.SubElement(root, "Results")
    for row in results if isinstance(results, Iterable) else []:
        res_el = ET.SubElement(results_el, "Result")
        _text(res_el, "Row", row.get("row_num"))
        _text(res_el, "Remark", _strip(row.get("remark")))
        _text(res_el, "TestDescription", _strip(row.get("test_desc")))
        _text(res_el, "MeasurementStep", _strip(row.get("test_step2")))
        _text(res_el, "NominalValue", _strip(row.get("fixq")))
        _text(res_el, "SystemActual", _strip(row.get("sys_actual")))
        _text(res_el, "VariationValue", _strip(row.get("varq")))
        _text(res_el, "UpperLimit", _strip(row.get("upper_limit")))
        _text(res_el, "LowerLimit", _strip(row.get("lower_limit")))
        _text(res_el, "ExpandedUncertainty", _strip(row.get("exp_uncert")))
        _text(res_el, "ExpandedUncertaintyIsoE", _strip(row.get("exp_uncert_iso_e")))
        _text(res_el, "ExpandedUncertaintyIsoP", _strip(row.get("exp_uncert_iso_p")))
        _text(res_el, "ToleranceError", _strip(row.get("tol_err")))
        _text(res_el, "RelativeError", _strip(row.get("rel_err")))
        _text(res_el, "PassFail", _strip(row.get("pass_fail")))
        _text(res_el, "Fsc", _strip(row.get("fsc")))
        _text(res_el, "Accredited", _strip(row.get("accred")))

    return ET.ElementTree(root)


def _maybe_validate(xml_path: pathlib.Path) -> None:
    try:
        import xmlschema  # type: ignore
    except ModuleNotFoundError:
        print("⚠️  xmlschema not installed; skipping validation.")
        return

    schema = xmlschema.XMLSchema(SCHEMA_PATH)
    schema.validate(str(xml_path))
    print(f"✅ XML validated against {SCHEMA_PATH}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit a DCC XML next to the JasperReports output")
    parser.add_argument("--input", required=True, help="JSON payload with calibration + results data")
    parser.add_argument("--output", required=False, default="dcc-output.xml", help="Target XML path")
    parser.add_argument("--measurement-option", default="22", help="MeasurementDetails value to embed (default: 22)")
    parser.add_argument("--report-id", default=str(uuid.uuid4()), help="Report identifier to store in the XML header")
    parser.add_argument("--validate", action="store_true", help="Validate the XML with the bundled XSD (requires xmlschema)")

    args = parser.parse_args(argv)

    payload = _load_payload(pathlib.Path(args.input))
    tree = build_xml(payload, measurement_option=str(args.measurement_option), report_id=str(args.report_id))

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Pretty print
    ET.register_namespace("", NAMESPACE)
    xml_bytes = ET.tostring(tree.getroot(), encoding="utf-8")
    try:
        import xml.dom.minidom as minidom

        pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ")
        output_path.write_text(pretty, encoding="utf-8")
    except Exception:
        output_path.write_bytes(xml_bytes)

    print(f"XML written to {output_path}")

    if args.validate:
        _maybe_validate(output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
