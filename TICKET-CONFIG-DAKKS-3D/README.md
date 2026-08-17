# Ticketmanagement für ein akkreditiertes Labor (drei Methoden)

Dieselbe Startvorlage wie [`TICKET-CONFIG-DAKKS`](../TICKET-CONFIG-DAKKS/) — 8
Vorgangsarten, 20 Themenfelder nach ISO/IEC 17025, vier Prioritäten — nur mit
**drei** Bewertungsmethoden statt zwei:

```
Risikowert = Auswirkung × Wahrscheinlichkeit × Erkennbarkeit     (1 … 125)
```

Die dritte Ebene ist die Erkennbarkeit, wie in der FMEA. Sie beantwortet die
Frage, die in einem Labor über den tatsächlichen Schaden entscheidet: **Wann
fällt die Sache auf?** Ein Messfehler, den die Plausibilitätsgrenze am
Arbeitsplatz abfängt, kostet eine Wiederholmessung. Derselbe Fehler, der erst im
Ringversuch auffällt, steckt bis dahin in jedem ausgegebenen Kalibrierschein.
Deshalb steigt das Gewicht, je später etwas auffällt.

| Stufe | Gewicht | Wann es auffällt |
|-------|---------|------------------|
| Sofort erkennbar | 1 | bei der Arbeit selbst: Plausibilitätsgrenze, Zwischenprüfung, Warnung im System |
| Leicht erkennbar | 2 | bei der fachlichen Freigabe (Vier-Augen-Prinzip) |
| Erkennbar | 3 | über Kontrollkarte, Wiederholmessung oder internes Audit |
| Schwer erkennbar | 4 | erst beim Ringversuch, bei der Rekalibrierung des Normals oder in der Begutachtung |
| Kaum erkennbar | 5 | nur durch Kundenreklamation, oder gar nicht |

## Die Bänder

Dieselben vier Stufen und dieselben Prioritäten wie in der
Zwei-Methoden-Fassung, nur über 1 bis 125 geschnitten:

| Band | Farbe | Priorität |
|------|-------|-----------|
| 1–9 | grün | Niedrig |
| 10–29 | gelb | Normal |
| 30–59 | orange | Hoch |
| 60–125 | rot | Kritisch |

Die Entscheidungsregeln je Band (wer entscheidet, welche Frist, welcher
Nachweis) stehen im README der Zwei-Methoden-Fassung und gelten unverändert.

## Welche Fassung passt

- **Zwei Methoden**, wenn die Risikobetrachtung noch aufgebaut wird oder das
  Labor eine schlanke Systematik führt. Die klassische Matrix ist in der
  Begutachtung erklärbar, und jede Bewertung braucht zwei Angaben statt drei.
- **Drei Methoden**, wenn die Erkennbarkeit real unterschiedlich ist — typisch
  in Laboren mit vielen Verfahren, langen Kalibrierintervallen der Normale oder
  ausgeprägter Prozessüberwachung. Der Preis: eine Angabe mehr je Ticket, und
  drei Skalen, die konsistent bleiben müssen.

Die Fassung lässt sich später wechseln: Die dritte Ebene zählt nur, wenn die
Formel `[Risk_3]` enthält. Die Bänder der Matrix müssen beim Wechsel aber
mitgehen, sonst greift kein Band mehr — 1 bis 25 gegen 1 bis 125.

## Import

**Administration → Ticket-Verwaltung**, Schaltfläche **Paket** (Berechtigung
`support_config_import`). Dazu gehört [`STATUS-TICKETS-DAKKS`](../STATUS-TICKETS-DAKKS/)
unter Administration → Statusverwaltung.

**Nicht beide Ticketmanagement-Pakete importieren.** Sie tragen dieselben
Kataloge, aber unterschiedliche Matrixbänder und Formeln; nacheinander
eingespielt stünden acht Bänder in der Matrix, von denen sich die Hälfte
überlappt.

## Anpassen

Diese Fassung wird aus der Zwei-Methoden-Fassung **abgeleitet** und nicht von
Hand bearbeitet — sonst laufen die Kataloge der beiden Pakete auseinander, ohne
dass es jemand bemerkt. Änderungen an Typen, Kategorien, Prioritäten oder den
ersten beiden Skalen gehören nach `TICKET-CONFIG-DAKKS`, danach:

```bash
python3 scripts/build_ticket_config_3d.py --write
python3 scripts/build_config_manifest.py --write TICKET-CONFIG-DAKKS-3D
python3 scripts/build_config_manifest.py --check
```

Die dritte Skala, die Formel und die Bänder stehen im Skript
(`scripts/build_ticket_config_3d.py`) und werden dort geändert.

## Grenzen

Dieselben wie bei der Zwei-Methoden-Fassung (Fristen setzt calServer nicht
durch, Ticket-Status tragen keine Pflichtfeldregeln, einsprachig deutsch), und
eine dazu: **drei Ebenen sind unvollständig schnell.** Solange eine von der
Formel genutzte Ebene am Ticket nicht ausgewählt ist, hat das Ticket keinen
Risikowert — mit drei Ebenen passiert das öfter als mit zwei.
