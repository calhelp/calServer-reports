#!/usr/bin/env python3
"""Manifest-Werkzeug für Wiki-Bundles (calserver.wiki-package).

Zwei Modi:

  --write BUNDLE_DIR [...]
      Berechnet die files[]-Liste (sha256 + size_bytes) über README.md,
      wiki.json und media/** neu und schreibt das Manifest. `content`
      (Kategorien, Artikel, Seiten, Sprachen) wird aus wiki.json abgeleitet;
      bestehende Felder (name, description, created_at, generator, locale)
      bleiben erhalten. sha256-Werte werden NIE von Hand gepflegt — immer
      über diesen Modus.

  --check [BUNDLE_DIR ...]   (Default; ohne Argumente: alle WIKI-*)
      Validiert jedes Manifest gegen schema/wiki-package.schema.json (Paket
      `jsonschema`, falls installiert; sonst strukturelle Minimalprüfung),
      rechnet alle sha256 nach, prüft die Vollständigkeit in beide Richtungen
      (jede Datei gelistet, jeder Listeneintrag vorhanden), die
      Eintrags-Allowlist (Tiefe höchstens 1) und den Kopf von wiki.json
      (format calserver.wiki, version <= 1). Zusätzlich inhaltlich: jede
      Seite verweist auf eine Kategorie, die das Bundle mitbringt, jeder
      Artikel hat eine general_page_id, keine Sprache doppelt je Artikel,
      und jedes im Blockdokument referenzierte Bild liegt unter media/.
      Exit 1 bei Abweichung.

Die verbindliche Lese-Semantik gehört calServer V2
(laravel/app/Services/Wiki/WikiPackageService.php in calhelp/calServer-yii);
dieses Skript hält die Bundles dazu kompatibel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "wiki-package.schema.json"

PACKAGE_FORMAT = "calserver.wiki-package"
PACKAGE_VERSION = 1
DOCUMENT_FORMAT = "calserver.wiki"
MAX_DOCUMENT_VERSION = 1

SCHEMA_URL = "https://calhelp.github.io/calServer-reports/schema/wiki-package.schema.json"

# Muss der Allowlist des Lesers entsprechen (WikiPackageService::ENTRY_PATTERNS).
ENTRY_PATTERNS = [
    re.compile(r"^README\.md$"),
    re.compile(r"^wiki\.json$"),
    re.compile(r"^media/[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"),
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
    files = [bundle / "wiki.json", bundle / "README.md"]
    media = bundle / "media"
    if media.is_dir():
        files.extend(sorted(p for p in media.iterdir() if p.is_file()))
    return [f for f in files if f.exists()]


def find_bundles(args: list[str]) -> list[Path]:
    if args:
        bundles = [Path(a).resolve() for a in args]
    else:
        bundles = sorted(p for p in REPO_ROOT.iterdir() if p.is_dir() and p.name.startswith("WIKI-"))
    for bundle in bundles:
        if not bundle.is_dir():
            fail(f"{bundle}: kein Verzeichnis")
    return [b for b in bundles if b.is_dir()]


def collect_media_ids(node: object, found: set[str]) -> None:
    """Jede mediaId aus einem Blockdokument einsammeln (beliebig geschachtelt)."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "mediaId" and isinstance(value, str):
                found.add(value)
            else:
                collect_media_ids(value, found)
    elif isinstance(node, list):
        for item in node:
            collect_media_ids(item, found)


def read_document(bundle: Path) -> dict | None:
    doc_path = bundle / "wiki.json"
    if not doc_path.exists():
        fail(f"{bundle.name}: wiki.json fehlt")
        return None
    try:
        document = json.loads(doc_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{bundle.name}/wiki.json: {exc}")
        return None
    if not isinstance(document, dict):
        fail(f"{bundle.name}/wiki.json: kein JSON-Objekt")
        return None
    if document.get("format") != DOCUMENT_FORMAT:
        fail(f"{bundle.name}/wiki.json: format muss {DOCUMENT_FORMAT} sein")
    version = document.get("version")
    if not isinstance(version, int) or version < 1 or version > MAX_DOCUMENT_VERSION:
        fail(
            f"{bundle.name}/wiki.json: version {version!r} — "
            f"erlaubt sind 1 bis {MAX_DOCUMENT_VERSION}"
        )

    categories = document.get("categories")
    category_keys: set[str] = set()
    if isinstance(categories, list):
        for category in categories:
            if not isinstance(category, dict):
                fail(f"{bundle.name}/wiki.json: categories-Eintrag ist kein Objekt")
                continue
            key = category.get("key")
            if not isinstance(key, str) or not key:
                fail(f"{bundle.name}/wiki.json: Kategorie ohne key: {category.get('title')!r}")
                continue
            if key in category_keys:
                fail(f"{bundle.name}/wiki.json: Kategorie-key {key!r} doppelt vergeben")
            category_keys.add(key)
            if not isinstance(category.get("title"), str) or not category["title"].strip():
                fail(f"{bundle.name}/wiki.json: Kategorie {key!r} ohne Titel")
    else:
        fail(f"{bundle.name}/wiki.json: categories fehlt oder ist keine Liste")

    # Medien-Verweise im Blockdokument müssen als Datei existieren; die
    # Zuordnung läuft über die Medien-ID, nicht über den Dateinamen.
    declared_media = document.get("media")
    media_by_id: dict[str, str] = {}
    if isinstance(declared_media, list):
        for entry in declared_media:
            if not isinstance(entry, dict):
                continue
            media_id, rel = entry.get("id"), entry.get("file")
            if not isinstance(media_id, str) or not isinstance(rel, str):
                fail(f"{bundle.name}/wiki.json: media-Eintrag ohne id/file")
                continue
            if not (bundle / rel).is_file():
                fail(f"{bundle.name}/wiki.json: media {media_id!r} verweist auf fehlende Datei {rel!r}")
            media_by_id[media_id] = rel

    articles = document.get("articles")
    if not isinstance(articles, list) or not articles:
        fail(f"{bundle.name}/wiki.json: articles fehlt, ist keine Liste oder leer")
        return document

    seen_article_ids: set[str] = set()
    referenced_media: set[str] = set()

    for article in articles:
        if not isinstance(article, dict):
            fail(f"{bundle.name}/wiki.json: articles-Eintrag ist kein Objekt")
            continue

        article_id = article.get("general_page_id")
        if not isinstance(article_id, str) or not article_id:
            fail(f"{bundle.name}/wiki.json: Artikel ohne general_page_id")
            continue
        if article_id in seen_article_ids:
            fail(f"{bundle.name}/wiki.json: general_page_id {article_id!r} doppelt vergeben")
        seen_article_ids.add(article_id)

        pages = article.get("pages")
        if not isinstance(pages, list) or not pages:
            fail(f"{bundle.name}/wiki.json: Artikel {article_id} ohne Seiten")
            continue

        languages: set[str] = set()
        for page in pages:
            if not isinstance(page, dict):
                fail(f"{bundle.name}/wiki.json: Seite in {article_id} ist kein Objekt")
                continue

            language = page.get("language_code")
            if not isinstance(language, str) or not language:
                fail(f"{bundle.name}/wiki.json: Seite in {article_id} ohne language_code")
            elif language in languages:
                fail(f"{bundle.name}/wiki.json: Artikel {article_id} führt {language!r} doppelt")
            else:
                languages.add(language)

            if not isinstance(page.get("title"), str) or not page["title"].strip():
                fail(f"{bundle.name}/wiki.json: Seite in {article_id} ohne Titel")

            # Eine Seite ohne Kategorie landet im Baum unter „Ohne Kategorie" —
            # in einer ausgelieferten Vorlage ist das ein Fehler, kein Zustand.
            category_key = page.get("category_key")
            if not isinstance(category_key, str) or not category_key:
                fail(f"{bundle.name}/wiki.json: Seite {page.get('title')!r} ohne category_key")
            elif category_key not in category_keys:
                fail(
                    f"{bundle.name}/wiki.json: Seite {page.get('title')!r} verweist auf "
                    f"unbekannte Kategorie {category_key!r}"
                )

            if not isinstance(page.get("content_html"), str) and not isinstance(page.get("content_json"), list):
                fail(f"{bundle.name}/wiki.json: Seite {page.get('title')!r} ohne Inhalt")

            collect_media_ids(page.get("content_json"), referenced_media)

    for media_id in sorted(referenced_media - set(media_by_id)):
        fail(f"{bundle.name}/wiki.json: Blockdokument referenziert unbekannte Medien-ID {media_id!r}")

    return document


def document_content(document: dict) -> dict:
    """Umfangsangaben für das Manifest aus wiki.json ableiten."""
    categories = document.get("categories") if isinstance(document.get("categories"), list) else []
    articles = document.get("articles") if isinstance(document.get("articles"), list) else []
    media = document.get("media") if isinstance(document.get("media"), list) else []

    pages = 0
    languages: set[str] = set()
    for article in articles:
        if not isinstance(article, dict):
            continue
        for page in article.get("pages") or []:
            if not isinstance(page, dict):
                continue
            pages += 1
            language = page.get("language_code")
            if isinstance(language, str) and language:
                languages.add(language)

    return {
        "categories": len(categories),
        "articles": len(articles),
        "pages": pages,
        "media": len(media),
        "languages": sorted(languages),
    }


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

    manifest = {
        "$schema": SCHEMA_URL,
        "format": PACKAGE_FORMAT,
        "format_version": PACKAGE_VERSION,
        "name": existing.get("name") if isinstance(existing.get("name"), str) else bundle.name,
        "document": {
            "format": DOCUMENT_FORMAT,
            "version": document.get("version", MAX_DOCUMENT_VERSION),
        },
        "content": document_content(document),
        "created_at": existing.get("created_at", "2026-08-13T12:00:00+00:00"),
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
        fail(f"schema/wiki-package.schema.json: {exc}")
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
        fail(f"{bundle.name}: manifest.json fehlt — scripts/build_wiki_manifest.py --write {bundle.name}")
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

    document = read_document(bundle)

    # Die Umfangsangabe ist deklarativ, aber sie darf nicht lügen: die
    # Download-Seite zeigt sie an.
    if document is not None and isinstance(manifest.get("content"), dict):
        expected = document_content(document)
        for key, value in expected.items():
            if manifest["content"].get(key) != value:
                fail(
                    f"{bundle.name}/manifest.json: content.{key} ist "
                    f"{manifest['content'].get(key)!r}, erwartet {value!r} — --write ausführen"
                )

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

    for required in ("wiki.json", "README.md"):
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Manifeste (neu) schreiben statt prüfen")
    mode.add_argument("--check", action="store_true", help="Manifeste prüfen (Default-Modus)")
    parser.add_argument("bundles", nargs="*", help="Bundle-Verzeichnisse (Default: alle WIKI-*)")
    args = parser.parse_args()

    bundles = find_bundles(args.bundles)
    if not bundles and not errors:
        print("Keine WIKI-*-Bundles gefunden — nichts zu tun.")
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
