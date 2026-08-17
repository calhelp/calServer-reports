#!/usr/bin/env python3
"""Manifest-Werkzeug für Konfigurationspakete.

Deckt alle drei Klassen ab, weil sie dieselbe Bauart haben — ein JSON-Dokument,
ein optionales README, kein Binärinhalt:

  calserver.category-package      CATEGORY-*/categories.json
  calserver.status-package        STATUS-*/statuses.json
  calserver.ticket-config-package TICKET-CONFIG-*/ticket-config.json

Zwei Modi:

  --write BUNDLE_DIR [...]
      Berechnet die files[]-Liste (sha256 + size_bytes) neu und schreibt das
      Manifest. `content` wird aus dem Dokument abgeleitet; bestehende Felder
      (name, description, created_at, generator, locale) bleiben erhalten.
      sha256-Werte werden NIE von Hand gepflegt — immer über diesen Modus.

  --check [BUNDLE_DIR ...]   (Default; ohne Argumente: alle Konfigurationspakete)
      Validiert jedes Manifest gegen das zugehörige Schema (Paket `jsonschema`,
      falls installiert; sonst strukturelle Minimalprüfung), rechnet alle
      sha256 nach, prüft Vollständigkeit in beide Richtungen (jede Datei
      gelistet, jeder Listeneintrag vorhanden), die Eintrags-Allowlist und den
      Kopf des Dokuments. Zusätzlich inhaltlich:

        Kategorien — Schlüssel eindeutig, parent_key existiert und zeigt nicht
        auf sich selbst, Eltern stehen vor ihren Kindern, Typ bekannt,
        Feldfunktion nennt ein Feld.

        Status — Schlüssel eindeutig, (Typ, Titel) eindeutig, Typ bekannt,
        Folgeaktionen und Zeitvariablen verweisen auf Status des Pakets,
        Feldfunktion nennt ein Feld.

        Ticketmanagement — Titel je Liste eindeutig, jede Bewertungsstufe mit
        ganzzahligem Gewicht, Formel arithmetisch und mit mindestens einer
        Ebene, dritte Ebene und Formel stimmen überein, Matrixbänder eindeutig
        und lückenlos über den erreichbaren Wertebereich, jede Matrixzeile
        verweist auf eine Priorität desselben Pakets.

      Exit 1 bei Abweichung.

Die verbindliche Lese-Semantik gehört calServer V2
(laravel/app/Services/Category/CategoryPackageService.php,
laravel/app/Services/Status/StatusPackageService.php bzw.
laravel/app/Services/Ticket/TicketConfigPackageService.php in
calhelp/calServer-yii); dieses Skript hält die Bundles dazu kompatibel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SCHEMA_BASE_URL = "https://calhelp.github.io/calServer-reports/schema"

# Bundle-Klassen. `prefix` ist zugleich das Namensmuster der Ordner.
KINDS = {
    "category": {
        "prefix": "CATEGORY-",
        "package_format": "calserver.category-package",
        "document_format": "calserver.categories",
        "document_name": "categories.json",
        "schema": "category-package.schema.json",
        "collection": "categories",
        "types": ("inventory", "calibration", "repair", "booking"),
    },
    "ticket-config": {
        # Vor "status" bewusst nicht noetig (kein gemeinsamer Praefix), aber
        # eigene Klasse: das Dokument traegt keine Sammlung gleichartiger
        # Eintraege, sondern eine ganze Einrichtung.
        "prefix": "TICKET-CONFIG-",
        "package_format": "calserver.ticket-config-package",
        "document_format": "calserver.ticket-config",
        "document_name": "ticket-config.json",
        "schema": "ticket-config-package.schema.json",
        "collection": "types",
        "types": (),
    },
    "status": {
        "prefix": "STATUS-",
        "package_format": "calserver.status-package",
        "document_format": "calserver.statuses",
        "document_name": "statuses.json",
        "schema": "status-package.schema.json",
        "collection": "statuses",
        "types": (
            "inventory",
            "calibration",
            "booking",
            "repair",
            "location",
            "notepad",
            "support_tickets",
        ),
    },
}

PACKAGE_VERSION = 1
MAX_DOCUMENT_VERSION = 1
MANIFEST_NAME = "manifest.json"
README_NAME = "README.md"


def kind_of(bundle: Path) -> str:
    """Bundle-Klasse aus dem Ordnernamen. Der Präfix ist die Regel (robots.md)."""
    name = bundle.name.upper()
    for kind, spec in KINDS.items():
        if name.startswith(spec["prefix"]):
            return kind

    raise SystemExit(
        f"{bundle.name}: unbekannte Bundle-Klasse. Ordner muss mit "
        + " oder ".join(spec["prefix"] for spec in KINDS.values())
        + " beginnen."
    )


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"{path}: kein gültiges JSON ({error})")

    if not isinstance(data, dict):
        raise SystemExit(f"{path}: JSON-Objekt erwartet")

    return data


def file_entries(bundle: Path, spec: dict) -> list[dict]:
    """Die erlaubten Dateien des Bundles mit Prüfsumme, in fester Reihenfolge."""
    entries = []
    for name in (spec["document_name"], README_NAME):
        path = bundle / name
        if path.is_file():
            entries.append(
                {
                    "path": name,
                    "sha256": sha256_of(path),
                    "size_bytes": path.stat().st_size,
                }
            )

    return entries


# Die drei Bewertungsebenen des Ticketmanagements (Reihenfolge = Formel-Token).
RISK_DIMENSIONS = ("risk1", "risk2", "risk3")

# Dieselbe Pruefung, die calServer V2 auf die Formel anwendet.
FORMULA_PATTERN = re.compile(r"^[\s\d+\-*/().]*(\[Risk_[123]\][\s\d+\-*/().]*)+$", re.IGNORECASE)

BAND_PATTERN = re.compile(r"^\d+(-\d+)?$")


def ticket_config_summary(document: dict) -> dict:
    """Kennzahlen fuer das Manifest eines Ticketmanagement-Pakets."""
    formula = document.get("risk", {}).get("formula") if isinstance(document.get("risk"), dict) else None

    def count(key: str) -> int:
        value = document.get(key)
        return len(value) if isinstance(value, list) else 0

    dimensions = 0
    if isinstance(formula, str):
        dimensions = sum(1 for index in (1, 2, 3) if f"[risk_{index}]" in formula.lower())

    return {
        "types": count("types"),
        "categories": count("categories"),
        "priorities": count("priorities"),
        "risk_levels": sum(count(dimension) for dimension in RISK_DIMENSIONS),
        "matrix": count("matrix"),
        "dimensions": dimensions,
        "formula": formula if isinstance(formula, str) else None,
    }


def content_summary(document: dict, spec: dict, kind: str) -> dict:
    if kind == "ticket-config":
        return ticket_config_summary(document)

    items = document.get(spec["collection"], [])
    items = items if isinstance(items, list) else []

    types: list[str] = []
    field_rules = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if isinstance(item_type, str) and item_type not in types:
            types.append(item_type)
        rules = item.get("field_rules")
        if isinstance(rules, list):
            field_rules += len(rules)

    summary: dict = {
        spec["collection"]: len(items),
        "field_rules": field_rules,
        "types": types,
    }

    if kind == "status":
        for key in ("transitions", "processing_times"):
            value = document.get(key)
            summary[key] = len(value) if isinstance(value, list) else 0

    return summary


def write_manifest(bundle: Path) -> None:
    kind = kind_of(bundle)
    spec = KINDS[kind]

    document_path = bundle / spec["document_name"]
    if not document_path.is_file():
        raise SystemExit(f"{bundle.name}: {spec['document_name']} fehlt")

    document = read_json(document_path)
    manifest_path = bundle / MANIFEST_NAME
    existing = read_json(manifest_path) if manifest_path.is_file() else {}

    manifest = {
        "$schema": f"{SCHEMA_BASE_URL}/{spec['schema']}",
        "format": spec["package_format"],
        "format_version": PACKAGE_VERSION,
        "name": existing.get("name") or bundle.name,
        "document": {
            "format": spec["document_format"],
            "version": document.get("version", 1),
        },
        "content": content_summary(document, spec, kind),
        "generator": existing.get("generator") or "calserver-reports",
        "files": file_entries(bundle, spec),
    }

    # Bestehende Provenienz nicht überschreiben: created_at markiert die
    # Entstehung des Pakets, nicht den letzten Manifestlauf.
    for key in ("description", "created_at", "locale"):
        if existing.get(key) is not None:
            manifest[key] = existing[key]

    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"{bundle.name}: Manifest geschrieben ({len(manifest['files'])} Dateien)")


def validate_schema(manifest: dict, spec: dict, bundle: Path, problems: list[str]) -> None:
    schema_path = REPO_ROOT / "schema" / spec["schema"]
    if not schema_path.is_file():
        problems.append(f"{bundle.name}: Schema fehlt ({schema_path})")
        return

    try:
        import jsonschema  # type: ignore
    except ImportError:
        # Ohne die Bibliothek bleibt die strukturelle Prüfung unten; die CI
        # installiert sie (validate-reports.yml).
        return

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path)):
        location = "/".join(str(part) for part in error.path) or "(Wurzel)"
        problems.append(f"{bundle.name}: Schemaverstoß bei {location}: {error.message}")


def check_categories(document: dict, spec: dict, bundle: Path, problems: list[str]) -> None:
    categories = document.get("categories")
    if not isinstance(categories, list) or categories == []:
        problems.append(f"{bundle.name}: categories fehlt oder ist leer")
        return

    seen: set[str] = set()
    for index, category in enumerate(categories, start=1):
        if not isinstance(category, dict):
            problems.append(f"{bundle.name}: Eintrag {index} in categories ist kein Objekt")
            continue

        key = category.get("key")
        name = category.get("name")
        if not isinstance(key, str) or key == "":
            problems.append(f"{bundle.name}: Eintrag {index} hat keinen key")
            continue
        if not isinstance(name, str) or name.strip() == "":
            problems.append(f"{bundle.name}: {key} hat keinen name")
        if key in seen:
            problems.append(f"{bundle.name}: key doppelt vergeben: {key}")
        seen.add(key)

        category_type = category.get("type")
        if category_type not in spec["types"]:
            problems.append(f"{bundle.name}: {key} hat unbekannten type {category_type!r}")

        parent = category.get("parent_key")
        if parent is not None:
            if parent == key:
                problems.append(f"{bundle.name}: {key} ist seine eigene Elternkategorie")
            elif parent not in seen:
                # Eltern vor Kindern: der Leser löst in einem Durchlauf auf.
                problems.append(
                    f"{bundle.name}: {key} verweist auf parent_key {parent!r}, "
                    "der davor nicht steht"
                )

        check_field_rules(category.get("field_rules"), f"{bundle.name}: {key}", problems)


def check_statuses(document: dict, spec: dict, bundle: Path, problems: list[str]) -> None:
    statuses = document.get("statuses")
    if not isinstance(statuses, list) or statuses == []:
        problems.append(f"{bundle.name}: statuses fehlt oder ist leer")
        return

    seen: set[str] = set()
    titles: set[tuple[str, str]] = set()

    for index, status in enumerate(statuses, start=1):
        if not isinstance(status, dict):
            problems.append(f"{bundle.name}: Eintrag {index} in statuses ist kein Objekt")
            continue

        key = status.get("key")
        title = status.get("title")
        status_type = status.get("type")

        if not isinstance(key, str) or key == "":
            problems.append(f"{bundle.name}: Eintrag {index} hat keinen key")
            continue
        if key in seen:
            problems.append(f"{bundle.name}: key doppelt vergeben: {key}")
        seen.add(key)

        if not isinstance(title, str) or title.strip() == "":
            problems.append(f"{bundle.name}: {key} hat keinen title")
        if status_type not in spec["types"]:
            problems.append(f"{bundle.name}: {key} hat unbekannten type {status_type!r}")

        if isinstance(title, str) and isinstance(status_type, str):
            # Der Leser erkennt Status über (Typ, Titel) wieder — zweimal
            # derselbe Titel im selben Typ waere im Ziel eine Kollision.
            pair = (status_type, title.strip().casefold())
            if pair in titles:
                problems.append(f"{bundle.name}: Titel {title!r} doppelt im Typ {status_type}")
            titles.add(pair)

        check_field_rules(status.get("field_rules"), f"{bundle.name}: {key}", problems)

    for transition in document.get("transitions", []) or []:
        if not isinstance(transition, dict):
            problems.append(f"{bundle.name}: Eintrag in transitions ist kein Objekt")
            continue
        for side in ("from_key", "to_key"):
            reference = transition.get(side)
            if reference not in seen:
                problems.append(
                    f"{bundle.name}: Folgeaktion verweist auf unbekannten {side} {reference!r}"
                )
        if not isinstance(transition.get("type"), str) or transition.get("type") == "":
            problems.append(f"{bundle.name}: Folgeaktion ohne type")

    for entry in document.get("processing_times", []) or []:
        if not isinstance(entry, dict):
            problems.append(f"{bundle.name}: Eintrag in processing_times ist kein Objekt")
            continue
        if not isinstance(entry.get("variable_name"), str) or entry.get("variable_name") == "":
            problems.append(f"{bundle.name}: Zeitvariable ohne variable_name")
        references = [entry.get("start_key"), entry.get("stop_key")]
        if not any(reference in seen for reference in references):
            problems.append(
                f"{bundle.name}: Zeitvariable {entry.get('variable_name')!r} verweist auf "
                "keinen Status des Pakets"
            )


def check_ticket_config(document: dict, bundle: Path, problems: list[str]) -> None:
    """Die Einrichtung eines Ticketmoduls — ein Dokument, mehrere Listen.

    Anders als Kategorie- und Statuspaket traegt dieses Dokument Teile, die
    aufeinander zeigen: die Matrix auf die Prioritaeten, die Formel auf die
    Bewertungsebenen. Genau dort entstehen die Fehler, die beim Import nicht
    auffallen — ein Paket mit dritter Ebene und Baendern bis 25 laesst jedes
    Ticket oberhalb von 25 ohne Farbe und ohne Prioritaet.
    """
    priorities = check_ticket_lists(document, bundle, problems)
    max_weights = check_ticket_dimensions(document, bundle, problems)
    formula = check_ticket_formula(document, bundle, problems)

    reachable = 1
    used_dimensions = []
    for index, dimension in enumerate(RISK_DIMENSIONS, start=1):
        if formula is not None and f"[risk_{index}]" not in formula.lower():
            continue
        used_dimensions.append(dimension)
        reachable *= max_weights.get(dimension, 0)

    check_ticket_matrix(document, bundle, problems, priorities, reachable if used_dimensions else 0)


def check_ticket_lists(document: dict, bundle: Path, problems: list[str]) -> set[str]:
    """Titel je Liste eindeutig; liefert die Prioritaetstitel zurueck."""
    priorities: set[str] = set()

    for key in ("types", "categories", "priorities", *RISK_DIMENSIONS):
        entries = document.get(key)
        if entries is None:
            continue

        if not isinstance(entries, list):
            problems.append(f"{bundle.name}: {key} ist keine Liste")
            continue

        seen: set[str] = set()
        for index, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                problems.append(f"{bundle.name}: Eintrag {index} in {key} ist kein Objekt")
                continue

            title = entry.get("title")
            if not isinstance(title, str) or title.strip() == "":
                problems.append(f"{bundle.name}: Eintrag {index} in {key} hat keinen title")
                continue

            # calServer erkennt einen Eintrag am Titel wieder, ohne Ruecksicht
            # auf Gross- und Kleinschreibung — zweimal derselbe Titel waere im
            # Ziel eine Kollision.
            folded = title.strip().casefold()
            if folded in seen:
                problems.append(f"{bundle.name}: Titel doppelt in {key}: {title!r}")
            seen.add(folded)

            if len(title) > 125:
                problems.append(f"{bundle.name}: Titel laenger als 125 Zeichen in {key}: {title!r}")

            if key == "priorities":
                priorities.add(folded)

    for key in ("types", "categories", "priorities"):
        if not isinstance(document.get(key), list) or document.get(key) == []:
            problems.append(f"{bundle.name}: {key} fehlt oder ist leer")

    return priorities


def check_ticket_dimensions(document: dict, bundle: Path, problems: list[str]) -> dict[str, int]:
    """Jede Stufe braucht ein ganzzahliges Gewicht; liefert das je Ebene groesste."""
    max_weights: dict[str, int] = {}

    for dimension in RISK_DIMENSIONS:
        entries = document.get(dimension)
        if not isinstance(entries, list):
            continue

        highest = 0
        for entry in entries:
            if not isinstance(entry, dict):
                continue

            weight = entry.get("weight")
            title = entry.get("title")

            # Ohne Gewicht rechnet die Stufe als 0 und zieht jedes Ticket, das
            # sie traegt, auf den Risikowert 0 — das ist keine Bewertung mehr.
            if not isinstance(weight, int) or isinstance(weight, bool) or weight < 1:
                problems.append(
                    f"{bundle.name}: {dimension}-Stufe {title!r} hat kein ganzzahliges Gewicht >= 1"
                )
                continue

            highest = max(highest, weight)

        max_weights[dimension] = highest

    return max_weights


def check_ticket_formula(document: dict, bundle: Path, problems: list[str]) -> str | None:
    risk = document.get("risk")
    if not isinstance(risk, dict):
        problems.append(f"{bundle.name}: risk fehlt oder ist kein Objekt")
        return None

    formula = risk.get("formula")
    if not isinstance(formula, str) or formula.strip() == "":
        problems.append(f"{bundle.name}: risk.formula fehlt")
        return None

    formula = formula.strip()
    if not FORMULA_PATTERN.match(formula):
        problems.append(
            f"{bundle.name}: risk.formula {formula!r} ist unbrauchbar — erlaubt sind [Risk_1], "
            "[Risk_2], [Risk_3], Zahlen, + - * / und Klammern, und mindestens eine Ebene"
        )
        return None

    # Die dritte Ebene und die Formel muessen dasselbe sagen: eine Liste, die
    # die Formel nicht nutzt, wird am Ticket nie abgefragt, und eine Formel
    # ohne Liste laesst jede Bewertung unvollstaendig.
    uses_third = "[risk_3]" in formula.lower()
    has_third = isinstance(document.get("risk3"), list) and document.get("risk3") != []

    if uses_third and not has_third:
        problems.append(f"{bundle.name}: Die Formel nutzt [Risk_3], aber risk3 ist leer")
    if has_third and not uses_third:
        problems.append(f"{bundle.name}: risk3 traegt Stufen, die Formel nutzt [Risk_3] aber nicht")

    labels = risk.get("dimension_labels")
    if labels is not None and not isinstance(labels, dict):
        problems.append(f"{bundle.name}: risk.dimension_labels ist kein Objekt")
    elif isinstance(labels, dict):
        for key in labels:
            if key not in RISK_DIMENSIONS:
                problems.append(f"{bundle.name}: unbekannte Bewertungsebene in dimension_labels: {key!r}")

    return formula


def check_ticket_matrix(
    document: dict,
    bundle: Path,
    problems: list[str],
    priorities: set[str],
    reachable: int,
) -> None:
    matrix = document.get("matrix")
    if not isinstance(matrix, list) or matrix == []:
        problems.append(f"{bundle.name}: matrix fehlt oder ist leer")
        return

    covered: set[int] = set()
    seen: set[str] = set()

    for index, row in enumerate(matrix, start=1):
        if not isinstance(row, dict):
            problems.append(f"{bundle.name}: Eintrag {index} in matrix ist kein Objekt")
            continue

        band = row.get("risk")
        if isinstance(band, int):
            band = str(band)

        if not isinstance(band, str) or not BAND_PATTERN.match(band.strip()):
            problems.append(
                f"{bundle.name}: Eintrag {index} in matrix hat kein Band (Einzelwert wie \"5\" "
                f"oder Bereich wie \"10-29\"): {row.get('risk')!r}"
            )
            continue

        band = band.strip()
        # `support_risks.risk` fasst zehn Zeichen; ein laengeres Band kaeme
        # gekappt in der Datenbank an und traefe dann ein anderes Intervall.
        if len(band) > 10:
            problems.append(f"{bundle.name}: Band laenger als 10 Zeichen: {band!r}")

        if band in seen:
            problems.append(f"{bundle.name}: Band doppelt in matrix: {band!r}")
        seen.add(band)

        low, _, high = band.partition("-")
        low_value = int(low)
        high_value = int(high) if high else low_value

        if high_value < low_value:
            problems.append(f"{bundle.name}: Band {band!r} laeuft rueckwaerts")
            continue

        covered.update(range(low_value, high_value + 1))

        priority = row.get("priority")
        if priority is None:
            continue

        if not isinstance(priority, str) or priority.strip() == "":
            problems.append(f"{bundle.name}: Band {band!r} hat eine leere Prioritaet")
        elif priority.strip().casefold() not in priorities:
            # Beim Import waere das nur eine Warnung; in einem gepflegten Paket
            # ist es ein Tippfehler, denn die Prioritaeten stehen daneben.
            problems.append(
                f"{bundle.name}: Band {band!r} verweist auf die Prioritaet {priority!r}, "
                "die das Paket nicht mitbringt"
            )

    if reachable <= 0:
        return

    missing = [value for value in range(1, reachable + 1) if value not in covered]
    if missing:
        problems.append(
            f"{bundle.name}: die Matrix deckt den erreichbaren Wertebereich 1 bis {reachable} "
            f"nicht ab — es fehlen {len(missing)} Werte, erster: {missing[0]}"
        )


def check_field_rules(rules: object, label: str, problems: list[str]) -> None:
    if rules is None:
        return

    if not isinstance(rules, list):
        problems.append(f"{label}: field_rules ist keine Liste")
        return

    for rule in rules:
        if not isinstance(rule, dict):
            problems.append(f"{label}: Feldfunktion ist kein Objekt")
            continue
        field = rule.get("field")
        if not isinstance(field, str) or field.strip() == "":
            problems.append(f"{label}: Feldfunktion ohne field")


def check_bundle(bundle: Path) -> list[str]:
    problems: list[str] = []
    kind = kind_of(bundle)
    spec = KINDS[kind]

    manifest_path = bundle / MANIFEST_NAME
    document_path = bundle / spec["document_name"]

    if not manifest_path.is_file():
        return [f"{bundle.name}: {MANIFEST_NAME} fehlt"]
    if not document_path.is_file():
        return [f"{bundle.name}: {spec['document_name']} fehlt"]

    manifest = read_json(manifest_path)
    document = read_json(document_path)

    validate_schema(manifest, spec, bundle, problems)

    if manifest.get("format") != spec["package_format"]:
        problems.append(
            f"{bundle.name}: format ist {manifest.get('format')!r}, "
            f"erwartet {spec['package_format']!r}"
        )

    version = manifest.get("format_version")
    if version != PACKAGE_VERSION:
        problems.append(f"{bundle.name}: format_version ist {version!r}, erwartet {PACKAGE_VERSION}")

    if document.get("format") != spec["document_format"]:
        problems.append(
            f"{bundle.name}: {spec['document_name']} hat format {document.get('format')!r}, "
            f"erwartet {spec['document_format']!r}"
        )

    document_version = document.get("version")
    if not isinstance(document_version, int) or document_version > MAX_DOCUMENT_VERSION:
        problems.append(
            f"{bundle.name}: Dokumentversion {document_version!r} ist unlesbar "
            f"(hoechstens {MAX_DOCUMENT_VERSION})"
        )

    # Dateien: Manifest gegen Platte, in beide Richtungen.
    listed = {}
    for entry in manifest.get("files", []):
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            problems.append(f"{bundle.name}: unvollständiger Dateieintrag im Manifest")
            continue
        listed[entry["path"]] = entry

    allowed = {spec["document_name"], README_NAME}
    on_disk = {
        item.name
        for item in bundle.iterdir()
        if item.is_file() and item.name != MANIFEST_NAME
    }

    for name in sorted(on_disk - allowed):
        problems.append(
            f"{bundle.name}: {name} gehört nicht in ein {spec['package_format']} "
            "(erlaubt sind nur Dokument und README.md)"
        )

    for name in sorted(item.name for item in bundle.iterdir() if item.is_dir()):
        problems.append(f"{bundle.name}: Unterordner {name}/ ist in diesem Format nicht erlaubt")

    for name in sorted(on_disk & allowed):
        if name not in listed:
            problems.append(f"{bundle.name}: {name} fehlt im Manifest")

    for name, entry in sorted(listed.items()):
        path = bundle / name
        if not path.is_file():
            problems.append(f"{bundle.name}: Manifest listet {name}, die Datei fehlt")
            continue

        actual = sha256_of(path)
        if entry.get("sha256") != actual:
            problems.append(f"{bundle.name}: sha256 weicht ab bei {name}")

        size = path.stat().st_size
        if entry.get("size_bytes") != size:
            problems.append(f"{bundle.name}: size_bytes weicht ab bei {name}")

    if kind == "category":
        check_categories(document, spec, bundle, problems)
    elif kind == "ticket-config":
        check_ticket_config(document, bundle, problems)
    else:
        check_statuses(document, spec, bundle, problems)

    return problems


def discover_bundles() -> list[Path]:
    bundles = []
    for spec in KINDS.values():
        bundles.extend(sorted(REPO_ROOT.glob(f"{spec['prefix']}*")))

    return [bundle for bundle in bundles if bundle.is_dir()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="Manifest(e) neu schreiben")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Manifest(e) prüfen (Vorgabe; das Flag gibt es der Deutlichkeit halber)",
    )
    parser.add_argument("bundles", nargs="*", help="Bundle-Verzeichnisse (Default: alle)")
    args = parser.parse_args()

    if args.bundles:
        bundles = [Path(bundle) if Path(bundle).is_absolute() else REPO_ROOT / bundle for bundle in args.bundles]
    else:
        bundles = discover_bundles()

    if not bundles:
        print("Keine Konfigurationspakete gefunden.")
        return 0

    if args.write:
        for bundle in bundles:
            write_manifest(bundle)
        return 0

    problems: list[str] = []
    for bundle in bundles:
        problems.extend(check_bundle(bundle))

    if problems:
        print("Manifest-Prüfung fehlgeschlagen:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(f"{len(bundles)} Konfigurationspaket(e) geprüft: alles konsistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
