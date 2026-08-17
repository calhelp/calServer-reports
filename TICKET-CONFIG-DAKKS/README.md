# Ticketmanagement für ein akkreditiertes Labor (zwei Methoden)

Startvorlage für das Ticketmanagement von calServer V2, zugeschnitten auf ein
Labor nach ISO/IEC 17025: die Vorgangsarten, die Themenfelder, die Prioritäten
und die vollständige Risikobewertung mit **zwei** Methoden
(Auswirkung × Wahrscheinlichkeit, Werte 1 bis 25).

Wer mit drei Methoden bewertet (zusätzlich die Erkennbarkeit, Werte bis 125),
nimmt stattdessen [`TICKET-CONFIG-DAKKS-3D`](../TICKET-CONFIG-DAKKS-3D/). Alles
andere ist in beiden Paketen identisch.

## Was drin ist

| Teil | Inhalt |
|------|--------|
| Typen | 8 Vorgangsarten: Risiko, Chance, Abweichung, Beschwerde, Korrekturmaßnahme, Verbesserung, Auditfeststellung, Änderung |
| Kategorien | 20 Themenfelder entlang der Normabschnitte, von der Unparteilichkeit (4) bis zur Managementbewertung (8.9) |
| Prioritäten | Niedrig, Normal, Hoch, Kritisch |
| Auswirkung (`[Risk_1]`) | Skala 1 bis 5, beschrieben in der Sprache des Labors: von „intern bemerkt" bis „Akkreditierung gefährdet" |
| Wahrscheinlichkeit (`[Risk_2]`) | Skala 1 bis 5, an Häufigkeiten festgemacht statt an Gefühlen |
| Risiko-Matrix | 4 Bänder über 1 bis 25, je mit Farbe und automatisch gesetzter Priorität |
| Formel | `[Risk_1] * [Risk_2]` |

Nicht drin: **Ticket-Status**. Die liegen in calServer im gemeinsamen
Statuskatalog und haben ihr eigenes Format. Der passende Ablauf (Neu, Bewertet,
Maßnahme geplant, In Umsetzung, Wirksamkeit prüfen, Abgeschlossen, Kein
Handlungsbedarf) steht in [`STATUS-TICKETS-DAKKS`](../STATUS-TICKETS-DAKKS/) und
wird unter Administration → Statusverwaltung importiert. Beide Pakete gehören
zusammen.

Ebenfalls nicht drin: Tickets. Ein Paket trägt die Einrichtung, nicht den
Bestand.

## Warum Risiken und Chancen in einem System

ISO/IEC 17025 behandelt beide im selben Abschnitt (8.5, „Maßnahmen zum Umgang
mit Risiken und Chancen"), und beide brauchen denselben Nachweis: erkannt,
bewertet, entschieden, und bei Handlung wirksam geworden. Ein zweites Werkzeug
für Chancen hieße nur, den zweiten Nachweis woanders zu suchen.

Die Bewertung funktioniert für Chancen mit derselben Matrix, nur anders
gelesen:

| Ebene | Beim Risiko | Bei der Chance |
|-------|-------------|----------------|
| Auswirkung | Schaden, wenn es eintritt | Nutzen, wenn sie gelingt |
| Wahrscheinlichkeit | wie oft mit dem Eintritt zu rechnen ist | wie sicher sich der Nutzen einstellt |
| Ergebnis | Risikowert: hoch heißt „abstellen" | Bedeutung: hoch heißt „einplanen" |

Das ist eine Konvention, keine Rechenregel des Systems. Sie steht hier, damit
sie im Labor einheitlich angewendet wird, und gehört so in die
Verfahrensanweisung.

## Die Regeln zum Ergebnis

calServer setzt aus dem Risikowert Farbe und Priorität. Was daraus folgt, ist
Sache des Labors — hier der Vorschlag, der zu den vier Bändern passt und sich in
der Begutachtung erklären lässt:

| Band | Priorität | Entscheidung | Frist | Nachweis |
|------|-----------|--------------|-------|----------|
| 1–4 | Niedrig | Akzeptieren. Status „Kein Handlungsbedarf" mit Begründung, oder Sammelposten für die Managementbewertung | keine | Eintrag genügt |
| 5–9 | Normal | Maßnahme durch die fachlich zuständige Person | 3 Monate | Maßnahme dokumentiert, Wirksamkeit beim Abschluss beurteilt |
| 10–14 | Hoch | Maßnahme mit benannter Verantwortlicher, Freigabe durch die Qualitätsmanagement-Beauftragte | 1 Monat | Wirksamkeit gesondert belegt (Kontrollmessung, Audit, Kennzahl) |
| 15–25 | Kritisch | Sofortmaßnahme prüfen: Arbeit anhalten, Ergebnisse zurückrufen, Kunden informieren (7.10). Entscheidung durch die Laborleitung | sofort, Maßnahme innerhalb 1 Woche geplant | Wirksamkeit belegt, Vorgang in der Managementbewertung berichtet |

Zwei Punkte, die in der Begutachtung regelmäßig gefragt werden und die diese
Vorlage deshalb bewusst so schneidet:

- **Ein akzeptiertes Risiko ist eine Entscheidung, kein Vergessen.** Deshalb der
  Status „Kein Handlungsbedarf" statt „erledigt": Wer die Liste später liest,
  sieht die Begründung.
- **Wirksamkeit ist ein eigener Schritt.** Der Status „Wirksamkeit prüfen" liegt
  zwischen Umsetzung und Abschluss, weil 8.7 genau das verlangt: geprüft wird
  die Wirkung, nicht die Erledigung.

## Import

**Administration → Ticket-Verwaltung**, Schaltfläche **Paket** (Berechtigung
`support_config_import`). Wiedererkannt wird ein Eintrag am Titel, eine
Matrixzeile an ihrem Band; ein zweiter Import legt keine Zwillinge an.

Reihenfolge auf einer frischen Installation:

1. `TICKET-CONFIG-DAKKS` (dieses Paket) unter Ticket-Verwaltung
2. `STATUS-TICKETS-DAKKS` unter Statusverwaltung

Auf einer Installation, die schon Prioritäten oder Bewertungsstufen führt, gilt
der Modus:

- **Bestehende behalten** (Vorgabe): ergänzt nur, was fehlt. Formel und
  Ebenennamen werden übernommen, solange sie noch auf der Werksvorgabe stehen.
- **Bestehende überschreiben**: zieht zusätzlich Gewichte, Farben und
  Beschreibungen nach und setzt Formel und Ebenennamen auch dann, wenn dort
  schon eigene stehen.

Der Bericht nach dem Import nennt jede Zahl einzeln und jede Zeile, die nicht
durchkam.

## Anpassen

`ticket-config.json` lässt sich direkt bearbeiten und ohne Archiv hochladen.
Zwei Stellen, an denen ein Labor typischerweise ansetzt:

- **Kategorien kürzen.** 20 Themenfelder sind vollständig, nicht verbindlich.
  Wer die Liste kürzt, verliert nichts außer Auswahl — die Normabschnitte in
  den Titeln sind Orientierung für die Anwender, keine Logik.
- **Skalen umformulieren.** Die Gewichte 1 bis 5 müssen bleiben, damit die
  Matrixbänder passen; die Beschreibungen sollen die eigene Praxis treffen.

Nach Änderungen am Bundle das Manifest neu schreiben:

```bash
python3 scripts/build_config_manifest.py --write TICKET-CONFIG-DAKKS
python3 scripts/build_config_manifest.py --check
```

Wer die Zwei-Methoden-Fassung ändert, zieht die Drei-Methoden-Fassung nach —
sie wird daraus abgeleitet:

```bash
python3 scripts/build_ticket_config_3d.py --write
python3 scripts/build_config_manifest.py --write TICKET-CONFIG-DAKKS-3D
```

## Grenzen

- **Die Fristen der Tabelle oben setzt calServer nicht durch.** Das Produkt
  rechnet den Risikowert, färbt das Ticket und setzt die Priorität. Termine und
  Zuständigkeiten sind Verfahrensanweisung; wer sie technisch erzwingen will,
  arbeitet mit Fälligkeitsdatum und Benachrichtigungen im Ticket.
- **Keine Feldfunktionen.** Ticket-Status tragen in calServer keine
  Pflichtfeldregeln (anders als Kalibrier- oder Reparaturstatus). Dass ein
  Ticket vor dem Abschluss eine Wirksamkeitsbeurteilung trägt, ist damit
  organisatorisch geregelt, nicht technisch erzwungen.
- **Einsprachig (deutsch).** Die Ebenennamen werden als Übersetzungen der
  Schlüssel `Risk 1` bis `Risk 3` in der Kategorie `support` geschrieben; für
  eine weitere Sprache ein eigenes Paket pflegen.
- **Die Skalen sind ein Vorschlag, keine Norm.** ISO/IEC 17025 verlangt eine
  Risikobetrachtung, schreibt aber weder Skalen noch Bänder vor. Wer eine
  bestehende, gelebte Systematik hat, behält sie und importiert dieses Paket
  nicht.
