#!/usr/bin/env python3
"""CI-Validator für parameters.json-Manifeste (analog check_jasper_version.sh).

Prüft jedes im Repository gefundene Parameter-Manifest (Bundle-Wurzel oder
main_reports/) gegen das JSON-Schema und das zugehörige Haupt-JRXML:

Fehler (Exit 1):
  - Manifest nicht parsebar oder verletzt schema/report-parameters.schema.json
  - Manifest-Parameter, der im Haupt-JRXML nicht deklariert ist
  - Manifest in einem Bundle MIT eingebettetem SQL (<queryString>) —
    Manifeste sind nur für V2-JSON-Bundles vorgesehen
  - options bei einem input ≠ select bzw. input=select ohne options
  - doppelte Parameternamen

Warnung (kein Exit-Fehler):
  - role=variable mit kleingeschriebenem Anfangsbuchstaben (von der
    calServer-Variablenauflösung per ucfirst nicht erreichbar)

Aufruf: python3 scripts/check_parameters_manifest.py [BUNDLE_DIR ...]
Ohne Argumente wird das gesamte Repository durchsucht.
Nutzt das Paket `jsonschema`, falls installiert (CI); ohne läuft eine
strukturelle Minimalprüfung.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "report-parameters.schema.json"

VALID_ROLES = {"variable", "prompt", "system"}
VALID_SCOPES = {"report", "type", "global"}
VALID_INPUTS = {"text", "textarea", "select", "boolean", "number", "date", "color", "image"}

errors: list[str] = []
warnings: list[str] = []


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def find_manifests(targets: list[Path]) -> list[Path]:
    manifests: list[Path] = []
    for target in targets:
        for path in sorted(target.rglob("parameters.json")):
            if any(part in {".git", "schema", "downloads", "pages", "staging", "zip_output"} for part in path.parts):
                continue
            manifests.append(path)
    return manifests


def bundle_dir_of(manifest: Path) -> Path:
    # Manifest liegt an der Bundle-Wurzel (neben main_reports/) oder in main_reports/.
    return manifest.parent.parent if manifest.parent.name == "main_reports" else manifest.parent


def main_jrxml_of(bundle: Path) -> Path | None:
    candidates = sorted((bundle / "main_reports").glob("*.jrxml"))
    return candidates[0] if candidates else None


def jrxml_facts(jrxml: Path) -> tuple[set[str], bool]:
    root = ET.parse(jrxml).getroot()
    declared = {
        element.get("name", "")
        for element in root
        if local_name(element.tag) == "parameter" and element.get("name")
    }
    has_query = any(
        (element.text or "").strip()
        for element in root.iter()
        if local_name(element.tag) == "queryString"
    )
    return declared, has_query


def validate_against_schema(manifest_path: Path, manifest: object) -> None:
    try:
        import jsonschema
    except ImportError:
        structural_fallback(manifest_path, manifest)
        return

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)
    for violation in sorted(validator.iter_errors(manifest), key=lambda v: list(v.absolute_path)):
        location = "/".join(str(part) for part in violation.absolute_path) or "<Wurzel>"
        errors.append(f"{manifest_path}: Schema-Verstoß bei {location}: {violation.message}")


def structural_fallback(manifest_path: Path, manifest: object) -> None:
    if not isinstance(manifest, dict) or manifest.get("version") != 1 or not isinstance(manifest.get("parameters"), list):
        errors.append(f"{manifest_path}: erwartet Objekt mit version=1 und parameters-Liste")
        return
    for index, entry in enumerate(manifest["parameters"]):
        if not isinstance(entry, dict) or not entry.get("name") or "label" not in entry:
            errors.append(f"{manifest_path}: parameters/{index}: name und label sind Pflicht")
            continue
        for field, allowed in (("role", VALID_ROLES), ("scope", VALID_SCOPES), ("input", VALID_INPUTS)):
            if field in entry and entry[field] not in allowed:
                errors.append(f"{manifest_path}: parameters/{index}: ungültiges {field} „{entry[field]}“")


def check_manifest(manifest_path: Path) -> None:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as parse_error:
        errors.append(f"{manifest_path}: nicht parsebar: {parse_error}")
        return

    validate_against_schema(manifest_path, manifest)

    bundle = bundle_dir_of(manifest_path)
    jrxml = main_jrxml_of(bundle)
    if jrxml is None:
        errors.append(f"{manifest_path}: kein Haupt-JRXML unter {bundle}/main_reports/ gefunden")
        return

    declared, has_query = jrxml_facts(jrxml)

    if has_query:
        errors.append(
            f"{manifest_path}: Bundle {bundle.name} enthält eingebettetes SQL — "
            "parameters.json ist nur für V2-JSON-Bundles erlaubt (calServer ignoriert es sonst)."
        )

    entries = manifest.get("parameters", []) if isinstance(manifest, dict) else []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            continue
        if name in seen:
            errors.append(f"{manifest_path}: Parameter „{name}“ ist doppelt deklariert")
        seen.add(name)

        if name not in declared:
            errors.append(
                f"{manifest_path}: Parameter „{name}“ ist im Haupt-JRXML ({jrxml.name}) nicht deklariert"
            )

        role = entry.get("role", "variable")
        if role == "variable" and name[0].islower():
            warnings.append(
                f"{manifest_path}: Parameter „{name}“ (role=variable) beginnt kleingeschrieben — "
                "von der calServer-Variablenauflösung (ucfirst) nicht erreichbar."
            )

        input_type = entry.get("input", "text")
        if "options" in entry and input_type != "select":
            errors.append(f"{manifest_path}: Parameter „{name}“: options sind nur bei input=select erlaubt")
        if input_type == "select" and "options" not in entry:
            errors.append(f"{manifest_path}: Parameter „{name}“: input=select verlangt options")


def main() -> None:
    targets = [Path(argument) for argument in sys.argv[1:]] or [REPO_ROOT]
    manifests = find_manifests(targets)

    for manifest_path in manifests:
        check_manifest(manifest_path)

    for message in warnings:
        print(f"⚠️  {message}")
    for message in errors:
        print(f"❌ {message}", file=sys.stderr)

    if errors:
        sys.exit(1)
    print(f"✅ {len(manifests)} Parameter-Manifest(e) geprüft, keine Fehler")


if __name__ == "__main__":
    main()
