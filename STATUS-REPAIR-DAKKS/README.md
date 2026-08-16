# Reparaturstatus für Kalibrierlabore

Startvorlage für das Statusmodell des Reparaturbereichs: der Weg eines Geräts
von der Annahme bis zur Rückgabe, samt der Feldfunktionen, die dafür sorgen,
dass am Ende dokumentiert ist, was gemacht wurde.

## Der Ablauf

| Reihenfolge | Status | Pflichtfelder in diesem Status |
|-------------|--------|-------------------------------|
| 10 | Eingegangen | Fehlerbeschreibung, Inventar |
| 20 | In Diagnose | — |
| 30 | Kostenvoranschlag offen | Reparaturaktion (Befund und geplanter Aufwand) |
| 40 | In Reparatur | — |
| 50 | Abgeschlossen | Reparaturaktion, Wartungsdatum |
| 60 | Nicht repariert | Reparaturaktion (Begründung) |

Dazu eine Zeitvariable **Durchlaufzeit Reparatur**, die von „Eingegangen" bis
„Abgeschlossen" misst (Format `d:h:m`).

## Warum an drei Stellen dasselbe Feld Pflicht ist

`notes` heißt in der Werksvorgabe **Reparaturaktion** und ist das Feld, in dem
steht, was tatsächlich getan wurde. Es taucht dreimal als Pflichtfeld auf, und
jedes Mal aus einem anderen Grund:

- **Kostenvoranschlag offen** — hier steht der Befund. Ohne ihn kann niemand
  entscheiden, ob der Aufwand sich lohnt, und der Kunde bekommt eine Zahl ohne
  Begründung.
- **Abgeschlossen** — hier steht die ausgeführte Arbeit. Ein Gerät, das repariert
  wurde und dessen Reparatur nicht dokumentiert ist, ist für die nächste
  Kalibrierung ein unbeschriebenes Blatt.
- **Nicht repariert** — hier steht, warum nicht: nicht reparabel, unwirtschaftlich
  oder vom Kunden abgelehnt. Diese drei Fälle enden gleich und sind fachlich
  verschieden; ohne Begründung sieht später jeder Abbruch gleich aus.

Die **Fehlerbeschreibung** (`description`) ist bei der Annahme Pflicht: was der
Kunde gemeldet hat, wird beim Eingang aufgeschrieben und nicht später aus der
Erinnerung rekonstruiert.

## Nach der Reparatur kommt die Kalibrierung

Ein instandgesetztes Messmittel ist nicht automatisch wieder gültig kalibriert.
Der Status „Abgeschlossen" schiebt das Gerät deshalb fachlich zurück in den
Kalibrierablauf — **erzwungen wird das hier nicht**. Eine Folgeaktion, die beim
Abschluss automatisch eine Kalibrierung anlegt, hängt an den Statusnamen und
Vorlagen der jeweiligen Installation und gehört in die Statusregeln, nicht in
eine Vorlage.

Wer das automatisieren will: Administration → Statusverwaltung → Regeln, dort
eine Aktion auf den Übergang nach „Abgeschlossen" legen.

## Import

**Administration → Statusverwaltung**, Schaltfläche **Paket** (Berechtigung
`status_import`). Wiedererkannt wird ein Status über Bereich und Titel; ein
zweiter Import legt keine Zwillinge an.

**Feldnamen:** Im Paket stehen die lesbaren Namen (`description`, `notes`,
`repair_date`, `inventory_id`). Beim Import legt calServer sie auf die Spalte,
die die jeweilige Installation verwendet. Ein Feld, das es dort nicht gibt,
wird übersprungen und im Bericht genannt, statt den Import abzubrechen.

## Anpassen

```bash
python3 scripts/build_config_manifest.py --write STATUS-REPAIR-DAKKS
python3 scripts/build_config_manifest.py --check
```

## Grenzen

- **Keine Umlaufregel.** Anders als beim [Gerätestatus](../STATUS-INVENTORY-DAKKS/)
  steht hier kein `active = false`: Reparaturzeilen sind Vorgänge, keine Geräte,
  und werden vom Leihmodul nicht ausgewertet. Dass ein Gerät während der
  Reparatur nicht verliehen wird, regelt sein **Gerätestatus**.
- **Keine Preise.** Ob ein Kostenvoranschlag angenommen wurde, steht im Auftrag
  ([Auftragsstatus](../STATUS-BOOKING-DAKKS/)), nicht in der Reparaturzeile.
- **Einsprachig (deutsch).**
