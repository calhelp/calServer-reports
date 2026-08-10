#!/usr/bin/env python3
"""Manifest-Werkzeug für Prüfplan-Bundles (calserver.procedure-package).

Zwei Modi:

  --write BUNDLE_DIR [...]
      Berechnet die files[]-Liste (sha256 + size_bytes) über README.md,
      procedure.json, images/** und docs/** neu und schreibt das Manifest.
      `name` und `document.version` kommen aus procedure.json; bestehende
      Felder (created_at, plan, description, locale) bleiben erhalten.
      sha256-Werte werden NIE von Hand gepflegt — immer über diesen Modus.

  --check [BUNDLE_DIR ...]   (Default; ohne Argumente: alle PRUEFPLAN-*)
      Validiert jedes Manifest gegen schema/procedure-package.schema.json
      (Paket `jsonschema`, falls installiert; sonst strukturelle
      Minimalprüfung), rechnet alle sha256 nach, prüft die Vollständigkeit
      in beide Richtungen (jede Datei gelistet, jeder Listeneintrag
      vorhanden), die Eintrags-Allowlist (kein JRXML, keine Fremdformate,
      Tiefe höchstens 1) und den Kopf von procedure.json
      (format calserver.procedure, version <= 2). Exit 1 bei Abweichung.

Die verbindliche Lese-Semantik gehört calServer V2
(laravel/app/Services/Procedure/ProcedurePackageService.php in
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
SCHEMA_PATH = REPO_ROOT / "schema" / "procedure-package.schema.json"

PACKAGE_FORMAT = "calserver.procedure-package"
PACKAGE_VERSION = 1
DOCUMENT_FORMAT = "calserver.procedure"
MAX_DOCUMENT_VERSION = 2

SCHEMA_URL = "https://calhelp.github.io/calServer-reports/schema/procedure-package.schema.json"

# Muss der Allowlist des Lesers entsprechen (ProcedurePackageService::ENTRY_PATTERNS).
ENTRY_PATTERNS = [
    re.compile(r"^README\.md$"),
    re.compile(r"^procedure\.json$"),
    re.compile(r"^images/[A-Za-z0-9][A-Za-z0-9._-]{0,127}\.(png|jpe?g|gif|svg|webp)$", re.IGNORECASE),
    re.compile(r"^docs/[A-Za-z0-9][A-Za-z0-9._-]{0,127}\.(pdf|md|txt|csv|xlsx|docx)$", re.IGNORECASE),
]

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def is_allowed_entry(rel: str) -> bool:
    return any(pattern.match(rel) for pattern in ENTRY_PATTERNS)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bundle_files(bundle: Path) -> list[Path]:
    """Alle Paket-Dateien eines Bundles (ohne manifest.json), sortiert."""
    files = [bundle / "procedure.json", bundle / "README.md"]
    for sub in ("images", "docs"):
        folder = bundle / sub
        if folder.is_dir():
            files.extend(sorted(p for p in folder.iterdir() if p.is_file()))
    return [f for f in files if f.exists()]


def find_bundles(args: list[str]) -> list[Path]:
    if args:
        bundles = [Path(a).resolve() for a in args]
    else:
        bundles = sorted(p for p in REPO_ROOT.iterdir() if p.is_dir() and p.name.startswith("PRUEFPLAN-"))
    for bundle in bundles:
        if not bundle.is_dir():
            fail(f"{bundle}: kein Verzeichnis")
    return [b for b in bundles if b.is_dir()]


def read_document(bundle: Path) -> dict | None:
    doc_path = bundle / "procedure.json"
    if not doc_path.exists():
        fail(f"{bundle.name}: procedure.json fehlt")
        return None
    try:
        document = json.loads(doc_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{bundle.name}/procedure.json: {exc}")
        return None
    if not isinstance(document, dict):
        fail(f"{bundle.name}/procedure.json: kein JSON-Objekt")
        return None
    if document.get("format") != DOCUMENT_FORMAT:
        fail(f"{bundle.name}/procedure.json: format muss {DOCUMENT_FORMAT} sein")
    version = document.get("version")
    if not isinstance(version, int) or version < 1 or version > MAX_DOCUMENT_VERSION:
        fail(
            f"{bundle.name}/procedure.json: version {version!r} — "
            f"erlaubt sind 1 bis {MAX_DOCUMENT_VERSION}"
        )
    return document


def write_manifest(bundle: Path) -> None:
    document = read_document(bundle)
    if document is None:
        return
    if not (bundle / "README.md").exists():
        fail(f"{bundle.name}: README.md fehlt")
        return

    manifest_path = bundle / "manifest.json"
    existing: dict = {}
    if manifest_path.exists():
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                existing = loaded
        except (OSError, json.JSONDecodeError):
            pass

    files = []
    for path in bundle_files(bundle):
        rel = path.relative_to(bundle).as_posix()
        if not is_allowed_entry(rel):
            fail(f"{bundle.name}/{rel}: unzulässiger Paket-Eintrag (Allowlist)")
            continue
        files.append({
            "path": rel,
            "sha256": sha256_of(path),
            "size_bytes": path.stat().st_size,
        })

    name = document.get("name")
    manifest = {
        "$schema": SCHEMA_URL,
        "format": PACKAGE_FORMAT,
        "format_version": PACKAGE_VERSION,
        "name": name if isinstance(name, str) and name.strip() else bundle.name,
        "document": {
            "format": DOCUMENT_FORMAT,
            "version": document.get("version", MAX_DOCUMENT_VERSION),
        },
        "plan": existing.get("plan", {"major_version": 0, "minor_version": 1, "released": None}),
        "created_at": existing.get("created_at", "2026-08-10T12:00:00+00:00"),
        "generator": existing.get("generator", "calserver-reports"),
        "locale": existing.get("locale", "de"),
        "files": files,
    }
    if isinstance(existing.get("description"), str):
        manifest["description"] = existing["description"]

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OK  {bundle.name}: manifest.json geschrieben ({len(files)} Dateien)")


def validate_against_schema(bundle: Path, manifest: dict) -> None:
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"schema/procedure-package.schema.json: {exc}")
        return

    try:
        import jsonschema  # type: ignore[import-untyped]
    except ImportError:
        # Strukturelle Minimalprüfung ohne jsonschema-Paket.
        for key in ("format", "format_version", "name", "document", "files"):
            if key not in manifest:
                fail(f"{bundle.name}/manifest.json: Pflichtfeld {key} fehlt")
        return

    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path)):
        location = "/".join(str(part) for part in error.path) or "<root>"
        fail(f"{bundle.name}/manifest.json ({location}): {error.message}")


def check_bundle(bundle: Path) -> None:
    manifest_path = bundle / "manifest.json"
    if not manifest_path.exists():
        fail(f"{bundle.name}: manifest.json fehlt — scripts/build_pruefplan_manifest.py --write {bundle.name}")
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{bundle.name}/manifest.json: {exc}")
        return
    if not isinstance(manifest, dict):
        fail(f"{bundle.name}/manifest.json: kein JSON-Objekt")
        return

    validate_against_schema(bundle, manifest)

    if manifest.get("format") != PACKAGE_FORMAT:
        fail(f"{bundle.name}/manifest.json: format muss {PACKAGE_FORMAT} sein")
    if manifest.get("format_version") != PACKAGE_VERSION:
        fail(f"{bundle.name}/manifest.json: format_version muss {PACKAGE_VERSION} sein")

    read_document(bundle)

    listed = manifest.get("files")
    if not isinstance(listed, list):
        return

    listed_by_path: dict[str, dict] = {}
    for entry in listed:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            fail(f"{bundle.name}/manifest.json: ungültiger files-Eintrag {entry!r}")
            continue
        rel = entry["path"]
        if rel in listed_by_path:
            fail(f"{bundle.name}/manifest.json: {rel} doppelt gelistet")
        listed_by_path[rel] = entry

    for required in ("procedure.json", "README.md"):
        if required not in listed_by_path:
            fail(f"{bundle.name}/manifest.json: {required} muss gelistet sein")

    on_disk = {path.relative_to(bundle).as_posix(): path for path in bundle_files(bundle)}

    for rel, path in on_disk.items():
        if not is_allowed_entry(rel):
            fail(f"{bundle.name}/{rel}: unzulässiger Paket-Eintrag (Allowlist)")
        if rel not in listed_by_path:
            fail(f"{bundle.name}/{rel}: liegt im Bundle, fehlt aber im Manifest — --write ausführen")

    for rel, entry in listed_by_path.items():
        path = on_disk.get(rel)
        if path is None:
            fail(f"{bundle.name}/manifest.json: {rel} gelistet, aber nicht im Bundle")
            continue
        actual_sha = sha256_of(path)
        if entry.get("sha256") != actual_sha:
            fail(
                f"{bundle.name}/{rel}: sha256 weicht vom Manifest ab — "
                f"niemals von Hand pflegen, --write ausführen"
            )
        if entry.get("size_bytes") != path.stat().st_size:
            fail(f"{bundle.name}/{rel}: size_bytes weicht vom Manifest ab — --write ausführen")

    if not errors:
        print(f"OK  {bundle.name}: {len(on_disk)} Dateien, Manifest konsistent")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Manifeste (neu) schreiben statt prüfen")
    parser.add_argument("bundles", nargs="*", help="Bundle-Verzeichnisse (Default: alle PRUEFPLAN-*)")
    args = parser.parse_args()

    bundles = find_bundles(args.bundles)
    if not bundles and not errors:
        print("Keine PRUEFPLAN-*-Bundles gefunden — nichts zu tun.")
        return 0

    for bundle in bundles:
        if args.write:
            write_manifest(bundle)
        else:
            check_bundle(bundle)

    if errors:
        print("\nFEHLER:", file=sys.stderr)
        for message in errors:
            print(f"  - {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
