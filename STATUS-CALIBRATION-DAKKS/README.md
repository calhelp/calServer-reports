# Kalibrierstatus für akkreditierte Labore

Startvorlage für das Statusmodell des Kalibrierbereichs. Sechs Status entlang
des Auftragswegs, dazu die Feldfunktionen, die dafür sorgen, dass ein Auftrag
nicht ohne Ergebnis abgeschlossen werden kann.

## Der Ablauf

| Reihenfolge | Status | Pflichtfelder in diesem Status |
|-------------|--------|-------------------------------|
| 10 | Geplant | — |
| 20 | In Arbeit | — |
| 30 | Messung abgeschlossen | Kalibrierdatum, Techniker |
| 40 | Freigabe ausstehend | — |
| 50 | Abgeschlossen | **Prüfentscheid**, Kalibrierdatum, Kalibrierscheinnummer |
| 60 | Storniert | Bemerkung |

Dazu eine Zeitvariable **Durchlaufzeit Kalibrierung**, die von „Geplant" bis
„Abgeschlossen" misst (Format `d:h:m`).

## Warum der Prüfentscheid erst am Ende Pflicht ist

Das Feld `cal_result` (bestanden / nicht bestanden / mit Einschränkung) ist der
Kern dieser Vorlage. Es steht **nicht** global auf Pflicht, sondern nur im
Status „Abgeschlossen":

- Früher im Ablauf gibt es die Angabe schlicht noch nicht. Eine globale Pflicht
  hieße, beim Anlegen etwas einzutragen, das erst die Messung ergibt — und was
  einmal eingetragen ist, wird selten korrigiert.
- Am Ende ist sie unverzichtbar. calServer lässt den Übergang nach
  „Abgeschlossen" nicht zu, solange das Feld leer ist; ein Kalibrierschein ohne
  Konformitätsaussage entsteht damit gar nicht erst.

Dasselbe gilt für die Kalibrierscheinnummer: Sie entsteht bei der Ausstellung,
nicht bei der Auftragsannahme.

**„Nicht bestanden" ist kein Status.** Ein durchgefallenes Gerät durchläuft
denselben Weg, der Unterschied steht im Prüfentscheid. Ein eigener Status
dafür würde die Auswertung zerreißen: Der Auftrag wäre je nach Ergebnis in
einem anderen Zustand, obwohl er in beiden Fällen fertig bearbeitet ist.

## Import

**Administration → Statusverwaltung**, Schaltfläche **Paket** (Berechtigung
`status_import`). Wiedererkannt wird ein Status über Bereich und Titel; ein
zweiter Import legt keine Zwillinge an.

Die Feldfunktionen werden in beiden Modi geschrieben — auch dann, wenn es den
Status schon gibt. Genau deshalb spielt man die Vorlage ein.

**Feldnamen:** Im Paket stehen die lesbaren Namen (`cal_result`,
`certificate_number`, `technician`). Beim Import legt calServer sie auf die
Spalte, die die jeweilige Installation verwendet — auf einer Installation mit
V1-Codes also auf `C2323`, `C2306`, `C2307`. Ein Feld, das es dort nicht gibt,
wird übersprungen und im Bericht genannt, statt den Import abzubrechen.

## Anpassen

`statuses.json` lässt sich direkt bearbeiten und ohne Archiv hochladen. Nach
Änderungen am Bundle das Manifest neu schreiben:

```bash
python3 scripts/build_config_manifest.py --write STATUS-CALIBRATION-DAKKS
python3 scripts/build_config_manifest.py --check
```

## Grenzen

- **Keine Folgeaktionen im Paket.** E-Mail-Benachrichtigungen beim
  Statuswechsel hängen an Mailvorlagen, die je Installation anders heißen; die
  Vorlage bringt deshalb keine mit. Sie lassen sich nach dem Import in den
  Statusregeln ergänzen.
- **Die Freigabestufe ersetzt keine Rechteprüfung.** Dass die technische
  Prüfung eine zweite Person macht, regelt die Rollenverteilung, nicht der
  Status.
- **Einsprachig (deutsch).** Für eine andere Sprache ein eigenes Paket pflegen.
