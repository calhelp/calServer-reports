#!/usr/bin/env python3
"""Derive TICKET-CONFIG-DAKKS-3D from the two-method TICKET-CONFIG-DAKKS.

Beide Pakete richten dasselbe Ticketmanagement für ein akkreditiertes Labor
ein. Der Unterschied ist allein die Bewertungssystematik: zwei Methoden
(Auswirkung × Wahrscheinlichkeit, 1…25) gegen drei (zusätzlich Erkennbarkeit,
1…125, die Risikoprioritätszahl der FMEA).

Alles andere — Typen, Kategorien, Prioritäten und die Skalen der ersten beiden
Ebenen — ist in beiden Paketen identisch und wird deshalb nicht zweimal
gepflegt, sondern hier abgeleitet. Ein Kategoriebaum, der in der 3D-Fassung
still hinterherhinkt, wäre sonst genau die Art Abweichung, die niemand bemerkt,
bis ein Labor beide Pakete vergleicht.

Erlaubte Abweichungen (nichts sonst):
  1. `risk.formula` → [Risk_1] * [Risk_2] * [Risk_3]
  2. `risk3` → die Skala der Erkennbarkeit (1…5)
  3. `matrix` → die vier Bänder über 1…125 statt über 1…25

Usage:
  python3 scripts/build_ticket_config_3d.py --write   # Paket neu erzeugen
  python3 scripts/build_ticket_config_3d.py --check   # committete Fassung prüfen

Danach immer das Manifest nachziehen:
  python3 scripts/build_config_manifest.py --write TICKET-CONFIG-DAKKS-3D
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCE = ROOT / "TICKET-CONFIG-DAKKS" / "ticket-config.json"
TARGET = ROOT / "TICKET-CONFIG-DAKKS-3D" / "ticket-config.json"

FORMULA = "[Risk_1] * [Risk_2] * [Risk_3]"

# Die dritte Ebene: Wie früh fällt die Sache auf? Ein Fehler, den erst der
# Ringversuch zeigt, ist gefährlicher als derselbe Fehler, den die
# Plausibilitätsprüfung am Arbeitsplatz abfängt — das ist der ganze Sinn der
# dritten Methode, und deshalb steigt das Gewicht mit sinkender Erkennbarkeit.
RISK3 = [
    {
        "key": "sofort-erkennbar",
        "title": "Sofort erkennbar",
        "weight": 1,
        "color": "00B050",
        "description": "Fällt bei der Arbeit selbst auf: Plausibilitätsgrenze, Zwischenprüfung, Warnung im System.",
    },
    {
        "key": "leicht-erkennbar",
        "title": "Leicht erkennbar",
        "weight": 2,
        "color": "92D050",
        "description": "Fällt bei der fachlichen Freigabe des Kalibrierscheins auf (Vier-Augen-Prinzip).",
    },
    {
        "key": "erkennbar",
        "title": "Erkennbar",
        "weight": 3,
        "color": "FFFF00",
        "description": "Fällt über Kontrollkarte, Wiederholmessung oder internes Audit auf, also Wochen bis Monate später.",
    },
    {
        "key": "schwer-erkennbar",
        "title": "Schwer erkennbar",
        "weight": 4,
        "color": "FFC000",
        "description": "Fällt erst beim Ringversuch, bei der Rekalibrierung des Normals oder in der Begutachtung auf.",
    },
    {
        "key": "kaum-erkennbar",
        "title": "Kaum erkennbar",
        "weight": 5,
        "color": "FF0000",
        "description": "Fällt nur durch eine Kundenreklamation auf oder bleibt unentdeckt.",
    },
]

# Bänder über das Produkt dreier Skalen (1…125). Dieselben vier Stufen und
# dieselben Prioritäten wie in der Zwei-Methoden-Fassung, nur anders geschnitten.
MATRIX = [
    {"risk": "1-9", "color": "00B050", "priority": "Niedrig", "sort_order": 1},
    {"risk": "10-29", "color": "FFFF00", "priority": "Normal", "sort_order": 2},
    {"risk": "30-59", "color": "FFC000", "priority": "Hoch", "sort_order": 3},
    {"risk": "60-125", "color": "FF0000", "priority": "Kritisch", "sort_order": 4},
]


def build() -> str:
    document = json.loads(SOURCE.read_text(encoding="utf-8"))

    document["risk"]["formula"] = FORMULA
    document["risk3"] = RISK3
    document["matrix"] = MATRIX

    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    generated = build()

    if mode == "--write":
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(generated, encoding="utf-8")
        print(f"wrote {TARGET.relative_to(ROOT)}")
        print("Manifest nachziehen: python3 scripts/build_config_manifest.py --write TICKET-CONFIG-DAKKS-3D")
        return 0

    if mode == "--check":
        if not TARGET.exists():
            print(f"MISSING {TARGET.relative_to(ROOT)}")
            return 1

        if TARGET.read_text(encoding="utf-8") != generated:
            print(f"DIVERGES {TARGET.relative_to(ROOT)} (mit --write neu erzeugen)")
            return 1

        print(f"ok {TARGET.relative_to(ROOT)}")
        return 0

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
