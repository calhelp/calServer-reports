#!/usr/bin/env python3
"""Derive the DAKKS-JSON-SAMPLE JRXMLs from the V1 DAKKS-SAMPLE originals.

The V2 bundle is an EXACT copy of the accredited V1 certificate — same bands,
same elements, same parameters, same expressions — with only the data source
swapped from embedded SQL/JDBC to the calServer report-data-contract
`calibration-certificate` (JSON). To keep that guarantee verifiable, the clone
is not hand-edited: this script derives it mechanically from the V1 sources.

Allowed transformations (nothing else changes, byte for byte):
  1. remove the <queryString> block (exactly one per file),
  2. give every <field> a <fieldDescription> with its JSON path
     (field NAME and CLASS stay untouched, so all $F{...} expressions and
     the guardrail "V1 layout parity" hold),
  3. swap the two subreport <connectionExpression> for a
     <dataSourceExpression> reading subDataSource("standards"/"results"),
  4. main report only: rename the report + point the Studio default adapter
     at the bundled sample-data.json,
  5. Results only: field row_num java.lang.Number -> java.lang.Integer —
     JsonDataSource cannot instantiate the abstract Number the way the JDBC
     source could; no template expression reads $F{row_num}, so the change
     is invisible to the layout.

Usage:
  python3 scripts/build_dakks_json_clone.py --write   # (re)generate the clone
  python3 scripts/build_dakks_json_clone.py --check   # verify committed files
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Source (V1, SQL/JDBC) → target (V2, JSON) files.
FILES = [
    (
        "DAKKS-SAMPLE/main_reports/dakks-sample.jrxml",
        "DAKKS-JSON-SAMPLE/main_reports/dakks-json-sample.jrxml",
        "main",
    ),
    (
        "DAKKS-SAMPLE/subreports/Standard.jrxml",
        "DAKKS-JSON-SAMPLE/subreports/Standard.jrxml",
        "standard",
    ),
    (
        "DAKKS-SAMPLE/subreports/Results.jrxml",
        "DAKKS-JSON-SAMPLE/subreports/Results.jrxml",
        "results",
    ),
]

# field name → JSON path (contract calibration-certificate v1.2).
# Main report paths are absolute from the dataset root; subreport paths are
# relative to their subDataSource element.
FIELD_MAP = {
    "main": {
        "cert_field": "calibration.certificate_display",
        "C2307": "calibration.technician",
        "C2308": "calibration.condition",
        "C2311": "calibration.custom_fields.C2311",
        "C2312": "calibration.custom_fields.C2312",
        "C2313": "calibration.place",
        "C2314": "calibration.custom_fields.C2314",
        "C2320": "calibration.custom_fields.C2320",
        "C2327": "calibration.custom_fields.C2327",
        "C2301": "calibration.calibration_date",
        "cal_date": "calibration.calibration_month",
        "customer": "customer.address_block",
        "I4201": "device.asset_number",
        "I4202": "device.manufacturer",
        "I4203": "device.model",
        "I4204": "device.description",
        "I4206": "device.serial_number",
        "I4224": "device.accuracy_class",
        "procedure_name": "procedure.procedure_name",
        "calibration_item": "procedure.calibration_item",
        "calibration_method": "procedure.calibration_method",
        "procedure_description": "procedure.description",
        "measurement_conditions": "procedure.measurement_conditions",
        "standards": "procedure.standards",
        "scope": "procedure.scope",
        "resource_working_hours": "environment.working_hours",
        "report_variant_template": "report_variant.template",
    },
    "standard": {
        "I4201": "asset_number",
        "I4202": "manufacturer",
        "I4203": "model",
        "I4204": "description",
        "C2303": "due_date",
        "CalibrationMark": "calibration_mark",
    },
    "results": {
        # identity mapping except the capitalised SQL alias
        "Fsc": "fsc",
    },
}

# Which contract array feeds each subreport call (matched via the
# subreportExpression that follows the connectionExpression).
SUBREPORT_SOURCES = {
    "Standard.jasper": "standards",
    "Results.jasper": "results",
}

FIELD_RE = re.compile(r'^(\s*)<field name="([^"]+)" class="([^"]+)"/>\s*$')


def json_path(kind: str, name: str) -> str:
    mapping = FIELD_MAP[kind]
    if name in mapping:
        return mapping[name]
    if kind == "results":
        return name  # identity: contract results[] keys equal the V1 aliases
    raise SystemExit(f"ERROR: no JSON path mapped for field '{name}' ({kind})")


def strip_query_string(text: str, source: str) -> str:
    blocks = re.findall(r"[ \t]*<queryString[^>]*>.*?</queryString>\n", text, flags=re.S)
    if len(blocks) != 1:
        raise SystemExit(f"ERROR: expected exactly 1 <queryString> in {source}, found {len(blocks)}")
    return text.replace(blocks[0], "")


def bind_fields(text: str, kind: str, source: str) -> str:
    out = []
    bound = 0
    for line in text.split("\n"):
        match = FIELD_RE.match(line)
        if match:
            indent, name, cls = match.groups()
            if kind == "results" and name == "row_num":
                cls = "java.lang.Integer"
            path = json_path(kind, name)
            out.append(
                f'{indent}<field name="{name}" class="{cls}">\n'
                f"{indent}\t<fieldDescription><![CDATA[{path}]]></fieldDescription>\n"
                f"{indent}</field>"
            )
            bound += 1
        else:
            out.append(line)
    expected = {"main": 27, "standard": 6, "results": 32}[kind]
    if bound != expected:
        raise SystemExit(f"ERROR: bound {bound} fields in {source}, expected {expected}")
    return "\n".join(out)


def swap_subreport_sources(text: str, source: str) -> str:
    connection = "<connectionExpression><![CDATA[$P{REPORT_CONNECTION}]]></connectionExpression>"
    parts = text.split(connection)
    if len(parts) != 3:
        raise SystemExit(
            f"ERROR: expected exactly 2 subreport connectionExpressions in {source}, found {len(parts) - 1}"
        )

    rebuilt = parts[0]
    for tail in parts[1:]:
        jasper = re.search(r'\$P\{Reportpath\} \+ "/subreports/([A-Za-z]+\.jasper)"', tail)
        if jasper is None or jasper.group(1) not in SUBREPORT_SOURCES:
            raise SystemExit(f"ERROR: could not resolve the subreport following a connectionExpression in {source}")
        array = SUBREPORT_SOURCES[jasper.group(1)]
        rebuilt += (
            "<dataSourceExpression><![CDATA[((net.sf.jasperreports.engine.data.JsonDataSource)"
            f'$P{{REPORT_DATA_SOURCE}}).subDataSource("{array}")]]></dataSourceExpression>'
        ) + tail
    return rebuilt


def retarget_main(text: str) -> str:
    text = text.replace('name="dakks-sample"', 'name="dakks-json-sample"', 1)
    adapter = (
        '<property name="com.jaspersoft.studio.data.defadapter" '
        'value="dakks-json-sample_adapter.xml"/>'
    )
    old = '<property name="com.jaspersoft.studio.data.defaultdataadapter" value="CalHelp Data Adapter "/>'
    if old not in text:
        raise SystemExit("ERROR: Studio default-adapter property not found in main report")
    return text.replace(old, adapter, 1)


def build() -> dict[str, str]:
    generated = {}
    for source, target, kind in FILES:
        text = (ROOT / source).read_text(encoding="utf-8")
        text = strip_query_string(text, source)
        text = bind_fields(text, kind, source)
        if kind == "main":
            text = swap_subreport_sources(text, source)
            text = retarget_main(text)
        generated[target] = text
    return generated


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    generated = build()

    if mode == "--write":
        for target, text in generated.items():
            path = ROOT / target
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"wrote {target}")
        return 0

    if mode == "--check":
        failed = False
        for target, text in generated.items():
            path = ROOT / target
            if not path.exists():
                print(f"MISSING {target}")
                failed = True
            elif path.read_text(encoding="utf-8") != text:
                print(f"DIVERGES {target} (re-run with --write)")
                failed = True
            else:
                print(f"ok {target}")
        return 1 if failed else 0

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
