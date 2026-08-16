# Auftragsstatus für Kalibrierlabore

Startvorlage für das Statusmodell des Auftragsbereichs: vom Angebot bis zur
Rückgabe der Geräte. Der Auftrag ist die Klammer um alles, was zu einer
Kundensendung gehört — Kalibrierungen, Reparaturen, Lieferschein und Rechnung.

## Der Ablauf

| Reihenfolge | Status | Pflichtfelder in diesem Status |
|-------------|--------|-------------------------------|
| 10 | Angebot | — |
| 20 | Auftrag bestätigt | Kunde |
| 30 | In Bearbeitung | — |
| 40 | Versandbereit | — |
| 50 | Abgeschlossen | — |
| 60 | Storniert | Bemerkung (Grund) |

Dazu eine Zeitvariable **Durchlaufzeit Auftrag**, die von „Auftrag bestätigt"
bis „Abgeschlossen" misst (Format `d:h:m`). Sie misst bewusst nicht ab dem
Angebot: wie lange ein Kunde überlegt, ist keine Leistung des Labors.

## Zwei Feldfunktionen, zwei verschiedene Zwecke

**Kunde bei „Auftrag bestätigt".** Ein Angebot darf ohne Kunden im System
entstehen (Anfrage per Telefon, Interessent ohne Stammdatensatz). Sobald daraus
ein Auftrag wird, muss der Kunde stehen — sonst gibt es später nichts zu
adressieren und nichts zu berechnen. Die Pflicht sitzt deshalb genau an diesem
Übergang und nicht global auf dem Feld.

**Bemerkung bei „Storniert".** Das Feld ist in der Werksvorgabe gar nicht in
der Maske sichtbar. Die Feldfunktion blendet es in diesem einen Status ein und
macht es zugleich zur Pflicht — genau dafür sind Zusatzfelder da. Ein
stornierter Auftrag ohne Grund ist im Nachhinein nicht mehr auseinanderzuhalten:
Kunde abgesprungen, Angebot zu teuer, Gerät doch nicht kalibrierpflichtig, oder
Doppelerfassung.

## Import

**Administration → Statusverwaltung**, Schaltfläche **Paket** (Berechtigung
`status_import`). Wiedererkannt wird ein Status über Bereich und Titel; ein
zweiter Import legt keine Zwillinge an.

## Anpassen

```bash
python3 scripts/build_config_manifest.py --write STATUS-BOOKING-DAKKS
python3 scripts/build_config_manifest.py --check
```

## Grenzen

- **Kein Rechnungsstatus.** „Abgeschlossen" heißt hier: Geräte zurück,
  Auftrag abgerechnet. Wer den Zahlungseingang im Auftrag führen will, ergänzt
  einen Status „Berechnet" vor „Abgeschlossen" — das hängt daran, ob die
  Buchhaltung in calServer oder daneben läuft.
- **Die Auftragsnummer vergibt calServer.** `number` ist ein Zählerfeld
  (`StatusCounter`) und wird beim Statuswechsel gezogen, nicht per Feldfunktion
  gesetzt. Welcher Status den Zähler auslöst, steht in der Statusverwaltung am
  Status selbst.
- **Keine automatische Verknüpfung mit Kalibrierungen.** Dass ein Auftrag erst
  „Versandbereit" wird, wenn alle Positionen fertig sind, prüft niemand
  automatisch. Das wäre eine Folgeaktion in den Statusregeln und hängt an den
  Statusnamen der jeweiligen Installation.
- **Einsprachig (deutsch).**
