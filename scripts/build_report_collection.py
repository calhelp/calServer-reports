#!/usr/bin/env python3
"""Sammelpaket aller Berichtspakete bauen (all-reports.zip).

    build_report_collection.py ZIP_DIR OUTPUT_ZIP [--commit SHA] [--json META_JSON]

Legt jedes Berichtspaket aus ZIP_DIR flach in OUTPUT_ZIP ab
(`dakks-json-sample.zip`, `order-json-sample.zip`, …). Ein Berichtspaket ist
ein ZIP mit `main_reports/` darin; Prüfpläne, Wiki-, Kategorie-, Status- und
Ticket-Pakete haben keins und bleiben draußen, weil sie nicht in die
Berichtsverwaltung gehören.

Das Ergebnis nimmt calServer V2 unter Administration › Berichte ›
„Alle Berichtsdateien aktualisieren“ direkt an (Form „Sammlung“ in
laravel/app/Services/Report/ReportPackageBatchService.php, calhelp/calServer-yii):
jedes innere ZIP ist ein Paket, zugeordnet wird über den Dateinamen ohne
Endung — gegen den Namen des Pakets, das am Bericht hängt, und bei den fest
zugewiesenen Berichten gegen das Referenz-Bundle (SystemReportCatalog). Die
Paketnamen hier dürfen sich deshalb nicht ändern.

Dazu kommt LIESMICH.txt mit Stand und Inhaltsliste; der Import überspringt
alles, was weder .zip noch .jrxml ist.

--json schreibt Name, Größe, sha256 und Paketliste für latest.json.
Exit 1, wenn kein Berichtspaket gefunden wurde.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# Obergrenze des Uploads in calServer (Sammel-Import). Darüber nimmt der
# Import das Archiv nicht mehr an, also lieber hier laut scheitern.
UPLOAD_LIMIT_BYTES = 20 * 1024 * 1024


def is_report_bundle(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path) as zf:
            return any(
                name.replace("\\", "/").startswith("main_reports/")
                for name in zf.namelist()
            )
    except zipfile.BadZipFile:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("zip_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--commit", default="")
    parser.add_argument("--json", dest="json_out", type=Path)
    args = parser.parse_args()

    output = args.output.resolve()
    bundles = sorted(
        p
        for p in args.zip_dir.glob("*.zip")
        if p.resolve() != output and is_report_bundle(p)
    )
    if not bundles:
        print(f"Keine Berichtspakete (ZIP mit main_reports/) in {args.zip_dir}.", file=sys.stderr)
        return 1

    built_at = datetime.now(timezone.utc).replace(microsecond=0)
    names = [p.name for p in bundles]
    readme = "\n".join(
        [
            "calServer – alle Berichtspakete",
            "",
            f"Stand: {built_at.isoformat()}"
            + (f" (calServer-reports {args.commit[:7]})" if args.commit else ""),
            "Quelle: https://calhelp.github.io/calServer-reports/downloads/",
            "",
            "Einspielen: calServer V2, Administration › Berichte ›",
            "„Alle Berichtsdateien aktualisieren“, dieses ZIP hochladen.",
            "Die Vorschau zeigt je Bericht, welches Paket es ersetzen würde;",
            "zugeordnet wird über den Dateinamen. Nichts wird ohne Bestätigung",
            "geschrieben.",
            "",
            f"Enthaltene Pakete ({len(names)}):",
            *[f"  {name}" for name in names],
            "",
        ]
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    # Die Pakete sind selbst komprimiert; STORED spart nur Rechenzeit.
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("LIESMICH.txt", readme, compress_type=zipfile.ZIP_DEFLATED)
        for bundle in bundles:
            zf.write(bundle, arcname=bundle.name)

    size = output.stat().st_size
    if size > UPLOAD_LIMIT_BYTES:
        print(
            f"{output.name} ist {size} Bytes groß; calServer nimmt höchstens "
            f"{UPLOAD_LIMIT_BYTES} Bytes an.",
            file=sys.stderr,
        )
        return 1

    sha256 = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"{output.name}: {len(names)} Berichtspakete, {size} Bytes, sha256 {sha256}")
    for name in names:
        print(f"  {name}")

    if args.json_out:
        args.json_out.write_text(
            json.dumps(
                {
                    "filename": output.name,
                    "sizeBytes": size,
                    "sha256": sha256,
                    "builtAt": built_at.isoformat(),
                    "packages": names,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
