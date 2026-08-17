# Standort- und Leihstatus für Kalibrierlabore

Startvorlage für das Statusmodell des Standortbereichs: wo ein Gerät steht und
bei wem es gerade ist. Jede Zeile im Standortgrid ist eine **Bewegung** eines
Geräts, und der Status sagt, worum es sich dabei handelt: eine Umsetzung im
Haus, eine Reservierung, eine laufende Leihe oder deren Ende.

## Die Zustände

| Reihenfolge | Status | Bedeutung | Pflichtfeld |
|-------------|--------|-----------|-------------|
| 10 | Standort | Gerät steht an diesem Ort, keine Leihe | Ort |
| 20 | Reservation | Zeitraum vorgemerkt, Gerät noch im Haus | Ende Leihzeitraum |
| 30 | Busy | Gerät ist heraus (im Verleih) | Ende Leihzeitraum |
| 40 | Zurückgegeben | Gerät zurück im Haus und geprüft, Eintrag ist Historie | Ende Leihzeitraum |
| 50 | Nicht zurückgegeben | Rückgabetermin verstrichen, Verbleib ungeklärt | Ende Leihzeitraum |

## Warum die Vorlage „Busy" und „Reservation" heißt

Drei der fünf Status liefert calServer bereits mit: **Standort**, **Busy** und
**Reservation**. Wiedererkannt wird ein Status beim Import über Bereich und
Titel — eine Vorlage mit „Verliehen" und „Reserviert" legte also Zwillinge
neben die vorhandenen Werte, und die Leihzeilen einer Installation verteilten
sich anschließend auf zwei Status mit derselben Bedeutung.

Die Vorlage spricht deshalb die Titel, die im Produkt stehen, und ergänzt nur,
was fehlt: das Ende einer Leihe. Wer die englischen Namen loswerden will,
benennt sie **nach** dem Import in der Statusverwaltung um; der Schlüssel ist
die interne uID, nicht die Beschriftung.

## Was die Feldfunktionen tun

**Ende Leihzeitraum wird Pflicht** (Reservation, Busy, Zurückgegeben, Nicht
zurückgegeben). Ab Werk ist das Feld sichtbar, aber freiwillig — und das ist
die teuerste Lücke im Modul: Die Verfügbarkeitsprüfung rechnet mit Datumsfeldern,
nicht mit Status. Eine Zeile ohne Ende blockiert nur ihren Starttag. Eine
Reservierung ohne Enddatum reserviert also nichts, und ein Gerät, das laut Liste
verliehen ist, lässt sich für denselben Zeitraum ein zweites Mal herausgeben.
Bei „Zurückgegeben" trägt dasselbe Feld die tatsächliche Rückgabe und schließt
den Zeitraum ab.

**Ort wird sichtbar und Pflicht** (Standort). Das Feld `location_2` steht ab
Werk nicht im Formular, nur in der Ansicht. Ein Standorteintrag ohne Ort ist
aber eine Bewegung ohne Ziel: Er beantwortet die Frage nicht, für die es ihn
gibt (ISO/IEC 17025 6.4.13 c: der aktuelle Standort gehört zu den Angaben, die
zu einem Ausrüstungsgegenstand geführt werden).

**Kunde wird beim reinen Standort freiwillig.** Ab Werk ist `customer_id`
Pflichtfeld des Bereichs — sinnvoll für eine Leihe, falsch für ein Gerät, das
nur von Halle 3 auf Prüfplatz 14 wandert. Ein Eintrag hat genau ein Ziel: Kunde,
eigener Standort oder Freitext. Die Feldfunktion nimmt die Pflicht für diesen
einen Status zurück, statt sie im ganzen Bereich zu lockern.

**Kundenkontakt wird sichtbar** (Busy). Der Leihschein und die Leihschein-Mail
gehen an eine Person, nicht an eine Firma. Ab Werk steht das Feld nicht im
Formular; im Verleihstatus gehört es dorthin — freiwillig, weil eine interne
Ausleihe keinen Kundenkontakt hat.

## Warum „Nicht zurückgegeben" ein eigener Status ist

Überfällig ist keine Statusfrage: Das Grid rechnet die Überschreitung aus dem
Rückgabedatum aus und hebt die Zeile rot hervor, ohne dass jemand etwas setzt.

„Nicht zurückgegeben" ist die Stufe danach und eine Entscheidung: nachgefragt,
keine Klärung, Verbleib offen. Für ein Kalibrierlabor ist das kein
Verwaltungsdetail, sondern ein Nachweisproblem. An einem Normal, dessen Zustand
und Handhabung seit Monaten niemand kennt, hängen Kalibrierungen, die andere
Ergebnisse stützen. Als eigener Status bleibt der Fall auffindbar, statt in der
Menge der offenen Leihen zu verschwinden.

## Import

**Administration → Statusverwaltung**, Schaltfläche **Paket** (Berechtigung
`status_import`). In der Vorgabe „Bestehende behalten" bleiben Standort, Busy
und Reservation unverändert und bekommen nur die Feldfunktionen dazu; die
beiden fehlenden Status werden angelegt. „Bestehende überschreiben" zieht
zusätzlich Farbe, Kurzname, Beschreibung und Sortierung dieser Vorlage nach.

## Anpassen

```bash
python3 scripts/build_config_manifest.py --write STATUS-LOCATION-DAKKS
python3 scripts/build_config_manifest.py --check
```

Passend dazu: [`LOCATION-JSON-SAMPLE`](../LOCATION-JSON-SAMPLE/) — der
Leihschein als Versanddokument, und [`STATUS-INVENTORY-DAKKS`](../STATUS-INVENTORY-DAKKS/)
für den Gerätestatus, der darüber entscheidet, ob ein Gerät überhaupt zur
Ausleihe angeboten wird.

## Grenzen

- **Die Schalter am Status kommen nicht mit.** Das Paketformat trägt
  Darstellung, Sortierung und Feldfunktionen; die Häkchen am Status
  (Wiedervorlage, neuer Standort, Erinnerungsbericht) bleiben außen vor. Neu
  angelegte Status bekommen die Vorgabe der Datenbank, die mitgelieferten
  behalten ihre Einstellung, weil sie wiedererkannt und nicht neu angelegt
  werden. Nach dem Import bei „Zurückgegeben" und „Nicht zurückgegeben" einmal
  nachsehen.
- **Kein automatischer Statuswechsel bei Rückgabe.** Statusregeln werten
  derzeit nur den Inventarbereich aus. Dass eine Leihe beim Erreichen des
  Rückgabedatums selbsttätig auf „Nicht zurückgegeben" springt, leistet die
  Vorlage nicht.
- **Die Pflicht wirkt im Formular.** Die Maske lässt einen Eintrag ohne
  Rückgabedatum nicht speichern; die API verlangt für sich genommen nur das
  Gerät. Ein Skript, das direkt gegen die API schreibt, umgeht die Regel.
- **Kein Grund bei „Nicht zurückgegeben".** Ein freies Bemerkungsfeld führt der
  Standortbereich ab Werk nur unter seinem V1-Code, und Feldfunktionen im Paket
  tragen ausschließlich lesbare Feldnamen. Wer den Grund erzwingen will, legt in
  der Feldverwaltung ein Textfeld für den Bereich Standort an und trägt es beim
  Status als Pflicht-Zusatzfeld nach — oder vor dem Import in `statuses.json`:

  ```json
  "field_rules": [
    { "field": "return_issue", "edit_visible": true, "edit_mandatory": true, "view_visible": true }
  ]
  ```

- **Keine Zeitvariable.** Eine Leihdauer aus Statuswechseln zu messen wäre
  doppelt: Der Zeitraum steht als Beginn und Ende an der Zeile selbst, und die
  Detailseite rechnet Dauer und Restlaufzeit daraus aus. Ausgewertet würde sie
  ohnehin nicht — Durchlaufzeiten werden bisher nur für Inventarvariablen
  materialisiert.
- **Einsprachig (deutsch).**
