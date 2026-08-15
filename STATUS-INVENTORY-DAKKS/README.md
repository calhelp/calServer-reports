# Gerätestatus für Kalibrierlabore

Startvorlage für das Statusmodell des Inventarbereichs: der Lebenszyklus eines
Messmittels vom Betrieb bis zur Aussonderung, samt der Regel, dass eine
Sperrung begründet werden muss.

## Die Zustände

| Reihenfolge | Status | Im Umlauf | Pflichtfeld |
|-------------|--------|-----------|-------------|
| 10 | In Betrieb | ja | — |
| 20 | Eingelagert | ja | — |
| 30 | In Kalibrierung | nein | — |
| 40 | In Reparatur | nein | — |
| 50 | Gesperrt | nein | siehe unten |
| 60 | Ausgesondert | nein, ausgeblendet | siehe unten |

„Im Umlauf" ist keine Beschriftung, sondern Verhalten: calServer bietet Geräte
in Status mit `active = false` oder `hide = true` im Leihmodul nicht an und
zählt sie nicht als blockierenden Teil eines Sets. Ein Gerät in Kalibrierung
oder Reparatur ist damit für die Ausleihe unsichtbar, ohne dass jemand es
manuell sperren muss.

## Kein Pflichtfeld ab Werk — und warum nicht

Naheliegend wäre, im Status „Gesperrt" eine Begründung zu verlangen: Warum
stand das Gerät still, ab wann, wer hat entschieden? Genau so ist das
[Kalibrierstatus-Paket](../STATUS-CALIBRATION-DAKKS/) geschnitten.

Der Inventarbereich führt werksseitig aber **kein freies Bemerkungsfeld** — die
Werksregistry kennt nur `description`, und das ist die Gerätebezeichnung, nicht
der Sperrgrund. Eine Feldfunktion auf ein nicht vorhandenes Feld würde beim
Import stillschweigend übersprungen (mit Warnung im Bericht) und wäre damit
eine Zusage, die die Vorlage nicht hält.

**So rüstet ein Labor sie nach:** In der Feldverwaltung ein Textfeld für den
Bereich Inventar anlegen (etwa `blocking_reason`), dann in der
Statusverwaltung beim Status „Gesperrt" als Zusatzfeld auf Pflicht setzen —
oder vor dem Import in `statuses.json` eintragen:

```json
"field_rules": [
  { "field": "blocking_reason", "edit_visible": true, "edit_mandatory": true, "view_visible": true }
]
```

Für die Aussonderung gilt dasselbe, dort zusätzlich mit `hide = true`: Das
Gerät verschwindet aus den Standardlisten, seine Historie bleibt aber
vollständig erhalten. Löschen wäre der falsche Weg — an einem ausgesonderten
Normal hängen Kalibrierungen, die andere Ergebnisse stützen.

## Import

**Administration → Statusverwaltung**, Schaltfläche **Paket** (Berechtigung
`status_import`). Wiedererkannt wird ein Status über Bereich und Titel.

## Anpassen

```bash
python3 scripts/build_config_manifest.py --write STATUS-INVENTORY-DAKKS
python3 scripts/build_config_manifest.py --check
```

## Grenzen

- **Die Umlaufregel ist eine Setzung.** Wer Geräte auch während der
  Kalibrierung verleihen will (etwa bei interner Kalibrierung im Haus), setzt
  `active` für „In Kalibrierung" auf `true`.
- **Kein automatischer Statuswechsel.** Dass ein Gerät bei nicht bestandener
  Kalibrierung auf „Gesperrt" geht, ist eine Folgeaktion in den Statusregeln
  und nicht Teil dieser Vorlage — sie hängt an den Statusnamen der jeweiligen
  Installation.
- **Einsprachig (deutsch).**
