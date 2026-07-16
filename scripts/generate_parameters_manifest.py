#!/usr/bin/env python3
"""Erzeugt ein parameters.json-Manifest-Gerüst aus dem Haupt-JRXML eines Bundles.

Nur für V2-JSON-Bundles (kein eingebettetes SQL, ADR-009): das Manifest
beschreibt die konfigurierbaren Parameter des Haupt-JRXML für den
calServer-Parameter-Katalog. Der Berichtsentwickler ergänzt anschließend
Labels (de/en), Beschreibungen, Rollen und Scope-Empfehlungen — das Skript
liefert nur das Gerüst:

  Name          aus dem name-Attribut der <parameter>-Deklaration
  Typ (input)   aus dem class-Attribut (Date → date, Integer → number, ...)
  Default       aus literalem <defaultValueExpression> ("...", Zahl)
  Beschreibung  aus <parameterDescription>
  role/scope/…  aus optionalen calserver.*-Properties, sonst Heuristik

Aufruf:
  python3 scripts/generate_parameters_manifest.py DAKKS-JSON-SAMPLE
  python3 scripts/generate_parameters_manifest.py pfad/zu/main.jrxml -o parameters.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SCHEMA_URL = "https://calhelp.github.io/calServer-reports/schema/report-parameters.schema.json"

# Implizite JasperReports-Standardparameter — nie ins Manifest aufnehmen.
BUILTIN_PARAMETERS = {
    "REPORT_LOCALE", "REPORT_CONNECTION", "REPORT_MAX_COUNT", "REPORT_DATA_SOURCE",
    "REPORT_VIRTUALIZER", "REPORT_TIME_ZONE", "REPORT_FORMAT_FACTORY",
    "REPORT_RESOURCE_BUNDLE", "REPORT_CLASS_LOADER", "REPORT_URL_HANDLER_FACTORY",
    "REPORT_FILE_RESOLVER", "REPORT_SCRIPTLET", "REPORT_PARAMETERS_MAP",
    "REPORT_CONTEXT", "IS_IGNORE_PAGINATION", "FILTER", "JASPER_REPORT", "SORT_FIELDS",
}

# Von calServer automatisch versorgte Parameter — immer role=system.
SYSTEM_PARAMETERS = {"Reportpath", "PrefixTable", "data_contract"}

# Java-Klasse (letztes Segment) → Manifest-input.
CLASS_TO_INPUT = {
    "Date": "date", "Timestamp": "date", "LocalDate": "date", "LocalDateTime": "date",
    "Integer": "number", "Long": "number", "Short": "number", "Double": "number",
    "Float": "number", "BigDecimal": "number", "BigInteger": "number", "Number": "number",
    "Boolean": "boolean",
}

VALID_ROLES = {"variable", "prompt", "system"}
VALID_SCOPES = {"report", "type", "global"}
VALID_INPUTS = {"text", "textarea", "select", "boolean", "number", "date", "color", "image"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def find_main_jrxml(target: Path) -> Path:
    if target.is_file():
        return target
    candidates = sorted((target / "main_reports").glob("*.jrxml"))
    if not candidates:
        sys.exit(f"FEHLER: kein Haupt-JRXML unter {target}/main_reports/ gefunden")
    if len(candidates) > 1:
        print(
            f"WARNUNG: mehrere JRXML unter {target}/main_reports/, verwende {candidates[0].name}",
            file=sys.stderr,
        )
    return candidates[0]


def has_embedded_query(root: ET.Element) -> bool:
    for element in root.iter():
        if local_name(element.tag) == "queryString":
            return bool((element.text or "").strip())
    return False


def literal_default(expression: str) -> str | None:
    expression = expression.strip()
    match = re.search(r'"([^"]*)"', expression)
    if match:
        return match.group(1)
    if re.fullmatch(r"-?\d+(\.\d+)?", expression):
        return expression
    return None


def build_entry(parameter: ET.Element) -> dict | None:
    name = parameter.get("name", "")
    if not name or name in BUILTIN_PARAMETERS:
        return None

    properties: dict[str, str] = {}
    description = ""
    default: str | None = None

    for child in parameter:
        tag = local_name(child.tag)
        if tag == "property" and (child.get("name") or "").startswith("calserver."):
            properties[(child.get("name") or "")[len("calserver."):]] = child.get("value") or ""
        elif tag == "parameterDescription":
            description = (child.text or "").strip()
        elif tag == "defaultValueExpression":
            default = literal_default(child.text or "")

    java_class = parameter.get("class", "java.lang.String").rsplit(".", 1)[-1]

    if properties.get("role") in VALID_ROLES:
        role = properties["role"]
    elif name in SYSTEM_PARAMETERS:
        role = "system"
    elif parameter.get("isForPrompting") == "true":
        role = "prompt"
    else:
        role = "variable"

    entry: dict = {
        "name": name,
        # Gerüst: Label = Parametername; der Autor ersetzt ihn durch de/en-Texte.
        "label": properties.get("label") or {"de": name.replace("_", " "), "en": name.replace("_", " ")},
    }
    if description:
        entry["description"] = {"de": description}
    entry["role"] = role
    if role == "variable":
        entry["scope"] = properties.get("scope") if properties.get("scope") in VALID_SCOPES else "report"
        entry["input"] = (
            properties.get("input")
            if properties.get("input") in VALID_INPUTS
            else CLASS_TO_INPUT.get(java_class, "text")
        )
        if default is not None:
            entry["default"] = default
        entry["required"] = False
    return entry


def main() -> None:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument("target", help="Bundle-Verzeichnis oder Pfad zu einem Haupt-JRXML")
    argument_parser.add_argument("-o", "--output", help="Zieldatei (Default: stdout)")
    argument_parser.add_argument("--force", action="store_true", help="vorhandene Zieldatei überschreiben")
    arguments = argument_parser.parse_args()

    jrxml_path = find_main_jrxml(Path(arguments.target))
    root = ET.parse(jrxml_path).getroot()

    if has_embedded_query(root):
        sys.exit(
            f"FEHLER: {jrxml_path} enthält eingebettetes SQL (<queryString>) — "
            "parameters.json ist nur für V2-JSON-Bundles vorgesehen."
        )

    entries = []
    for parameter in root:
        if local_name(parameter.tag) != "parameter":
            continue
        entry = build_entry(parameter)
        if entry is not None:
            entries.append(entry)
            if entry["role"] == "variable" and entry["name"][0].islower():
                print(
                    f"WARNUNG: Parameter „{entry['name']}“ (role=variable) beginnt kleingeschrieben — "
                    "von der calServer-Variablenauflösung (ucfirst) nicht erreichbar.",
                    file=sys.stderr,
                )

    manifest = {"$schema": SCHEMA_URL, "version": 1, "parameters": entries}
    rendered = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    if arguments.output:
        output_path = Path(arguments.output)
        if output_path.exists() and not arguments.force:
            sys.exit(f"FEHLER: {output_path} existiert bereits (mit --force überschreiben)")
        output_path.write_text(rendered, encoding="utf-8")
        print(f"{output_path} geschrieben ({len(entries)} Parameter)", file=sys.stderr)
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
