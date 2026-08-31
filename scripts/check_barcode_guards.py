#!/usr/bin/env python3
"""CI-Validator: kein barcode4j-Symbol ohne Leer-Wächter.

Hintergrund: barcode4j — und damit jr:DataMatrix, jr:Code128, jr:Code39,
jr:EAN13 und Verwandte — wirft bei leerer Nachricht eine
`NullPointerException: Parameter msg must not be empty`. Ein Füllfehler bricht
in JasperReports den ganzen JOB ab, nicht die einzelne Seite: Beim Stapeldruck
nimmt ein Gerät ohne Barcode-Wert also den kompletten Etikettenstapel mit, und
im Druckdialog steht nur die Java-Meldung.

Leere Werte sind dabei erlaubt und vorgesehen: `barcode.value` des Contracts
`inventory-datasheet` ist null, wenn das in den Regeln konfigurierte
Barcode-Feld am Gerät leer ist ("ein Etikett ohne Barcode, kein gescheiterter
Bericht"). Die Vorlage muss das aushalten, und das geht nur über ein
printWhenExpression am Barcode-Element.

jr:QRCode ist ausgenommen: die ZXing-Anbindung rendert eine leere Nachricht
klaglos. Genau deshalb fällt der Fehler auch nur bei Mandanten auf, die auf
DataMatrix (Vorgabe) oder Code128/39 stehen.

Geprüft wird je Barcode-Komponente:
  - am umschliessenden <reportElement> steht ein <printWhenExpression>,
  - es nennt dieselbe Variable/dasselbe Feld wie die <codeExpression>,
  - und es prüft auf Leere (isEmpty() oder length()).

Der Wächter darf über eine Hilfsvariable laufen (`$V{hasCode}`); die
Variablenausdrücke des Berichts werden dafür eingesetzt, bevor geprüft wird.

Aufruf: python3 scripts/check_barcode_guards.py [DATEI_ODER_VERZEICHNIS ...]
Ohne Argumente wird das gesamte Repository durchsucht.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Alles ausser QRCode geht in barcode4j und verweigert die leere Nachricht.
EXEMPT_COMPONENTS = {"QRCode"}

# Die Komponenten-Namen, die JasperReports als Barcode kennt (jr:...).
BARCODE_COMPONENTS = {
    "Codabar", "Code128", "EAN128", "DataMatrix", "Code39", "Interleaved2Of5",
    "UPCA", "UPCE", "EAN13", "EAN8", "USPSIntelligentMail", "RoyalMailCustomer",
    "POSTNET", "PDF417", "QRCode",
}

TOKEN = re.compile(r"\$[VFP]\{([^}]+)\}")
EMPTINESS = ("isEmpty", "length()", "trim().equals(\"\")")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return "".join(element.itertext()).strip()


def variable_expressions(root: ET.Element) -> dict[str, str]:
    """Ausdruck je Berichtsvariable, damit ein Wächter eine Hilfsvariable
    benutzen darf, statt den Leertest ins printWhenExpression zu kopieren."""
    expressions: dict[str, str] = {}
    for element in root.iter():
        if local_name(element.tag) != "variable":
            continue
        name = element.get("name")
        if name is None:
            continue
        for child in element:
            if local_name(child.tag) == "variableExpression":
                expressions[name] = text_of(child)
    return expressions


def expand(expression: str, variables: dict[str, str], depth: int = 3) -> str:
    """Variablen im Ausdruck einsetzen (endlich oft, gegen Zyklen gedeckelt)."""
    for _ in range(depth):
        expanded = re.sub(
            r"\$V\{([^}]+)\}",
            lambda match: "(" + variables.get(match.group(1), match.group(0)) + ")"
            if match.group(1) in variables
            else match.group(0),
            expression,
        )
        if expanded == expression:
            break
        expression = expanded
    return expression


def check_file(path: Path) -> list[str]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"{path}: nicht parsebar ({exc})"]

    problems: list[str] = []
    variables = variable_expressions(root)

    for component_element in root.iter():
        if local_name(component_element.tag) != "componentElement":
            continue

        report_element = None
        barcode = None
        for child in component_element:
            name = local_name(child.tag)
            if name == "reportElement":
                report_element = child
            elif name in BARCODE_COMPONENTS:
                barcode = child

        if barcode is None or local_name(barcode.tag) in EXEMPT_COMPONENTS:
            continue

        symbology = local_name(barcode.tag)
        code_expression = None
        for child in barcode:
            if local_name(child.tag) == "codeExpression":
                code_expression = child
        code = text_of(code_expression)
        tokens = TOKEN.findall(code)
        if not tokens:
            # Eine Konstante kann nicht leer werden, solange sie es nicht ist.
            if code.strip('"').strip() == "":
                problems.append(f"{path}: {symbology} codiert eine leere Konstante")
            continue

        guard = ""
        if report_element is not None:
            for child in report_element:
                if local_name(child.tag) == "printWhenExpression":
                    guard = text_of(child)

        if not guard:
            problems.append(
                f"{path}: {symbology} ({code}) druckt ohne printWhenExpression — "
                f"ein leerer Wert bricht den ganzen Lauf ab"
            )
            continue

        # Die Prüfung läuft auf dem aufgelösten Wächter, der Text der Meldung
        # bleibt der, der in der Datei steht.
        resolved_guard = expand(guard, variables)
        resolved_code = expand(code, variables)
        tokens = TOKEN.findall(resolved_code) or tokens

        if not any(token in resolved_guard for token in tokens):
            problems.append(
                f"{path}: {symbology} ({code}) hat ein printWhenExpression, das den "
                f"codierten Wert nicht prüft: {guard}"
            )
            continue

        if not any(marker in resolved_guard for marker in EMPTINESS):
            problems.append(
                f"{path}: {symbology} ({code}) prüft nicht auf einen leeren Wert: {guard}"
            )

    return problems


def jrxml_files(arguments: list[str]) -> list[Path]:
    if not arguments:
        return sorted(REPO_ROOT.rglob("*.jrxml"))

    files: list[Path] = []
    for argument in arguments:
        path = Path(argument)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.jrxml")))
        else:
            files.append(path)
    return files


def main() -> int:
    files = jrxml_files(sys.argv[1:])
    problems: list[str] = []
    for path in files:
        problems.extend(check_file(path))

    if problems:
        for problem in problems:
            print(f"❌ {problem}", file=sys.stderr)
        print(
            f"\n{len(problems)} ungeschützte(s) Barcode-Element(e). "
            "Am <reportElement> ein <printWhenExpression> ergänzen, das den leeren "
            "Wert auslässt (Vorbild: STICKER-CAL-INV-ZEBRA-JSON-SAMPLE, Variable "
            "`hasCode`).",
            file=sys.stderr,
        )
        return 1

    print(f"Alle Barcode-Elemente in {len(files)} JRXML-Dateien sind gegen leere Werte geschützt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
