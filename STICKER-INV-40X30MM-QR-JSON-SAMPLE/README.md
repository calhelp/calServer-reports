# STICKER-INV-40X30MM-QR-JSON-SAMPLE — Geräteetikett 40×30 mm mit QR (V2 / APEX)

Geräteetikett **40×30 mm** (113×85 pt) mit **QR-Deep-Link auf die Geräteseite**,
gefüllt aus einem **JSON-Datensatz** (Contract `inventory-datasheet` **v1.4**)
statt aus SQL — DB-agnostisch, keine V1-Codespalten.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/inv-aufkleber-40x30mm-qr-json-sample.jrxml` | Etikett: Rahmen, links Inventarnummer + Bezeichnung + nächster Termin, rechts QR und lesbare Nummer |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `inventory-datasheet` v1.4) |
| `main_reports/inv-aufkleber-40x30mm-qr-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Was das von `STICKER-CAL-INV-ZEBRA-JSON-SAMPLE` unterscheidet

Das Zebra-Etikett codiert `barcode.value` — die **Nummer**, die ein Handscanner
als Text zurückliest. Dieses Etikett codiert `qr.url` — die **Adresse** der
öffentlichen Geräteseite der QR-Code-Rolle (`/v2/qr/{uuid}`). Scannen mit dem
Telefon öffnet ohne Anmeldung Stammdaten, Kalibrierstatus und Dokumente.

Dasselbe Gerät, zwei verschiedene Aufgaben: Der Lagerscanner will die Nummer,
der Techniker vor der Maschine will die Seite. Deshalb zwei Bundles und kein
Schalter.

**Im QR steht der Link — sonst nichts.** Kein Rückfall auf eine Nummer: Sonst
wäre dasselbe Symbol mal eine Adresse und mal eine Nummer, je nach Einstellung,
und genau diese Zweideutigkeit ist der Grund, warum dieses Bundle neben dem
Zebra-Etikett steht statt es zu ersetzen.

**Voraussetzung:** QR-Links müssen eingeschaltet sein (QR-Code-Rolle mit
`qrlink_enable` und ein öffentlicher Benutzer). Sind sie aus, liefert der
Datensatz `qr.url = null` — dann wird **kein QR gedruckt**; die rechte Hälfte
trägt stattdessen die lesbare Nummer gross, beschriftet als *Inventar-Nr.* Wer
dauerhaft ohne QR-Links arbeitet, nimmt besser das Zebra-Bundle: Das codiert die
Nummer und ist für seinen Zweck gebaut.

## Warum 40×30 mm

Die Etikettengrösse folgt aus der URL-Länge, nicht aus Geschmack:

| Grösse | Wert |
|--------|------|
| Deep-Link mit uuid | ~74 Zeichen |
| QR-Version bei Fehlerkorrektur M | 5 (37×37 Module) |
| Modulraster inkl. Ruhezone | ~45 Module |
| QR-Feld in der Vorlage | 50×50 pt = 17,6 mm |
| Modulgrösse auf Papier | **0,39 mm = 3,1 Punkte bei 203 dpi** |

Drei Punkte je Modul ist die Grenze, ab der ein 203-dpi-Thermodrucker
zuverlässig lesbare Symbole liefert. **Wer das QR-Feld verkleinert, macht das
Etikett unscannbar.**

Gleicher Zuschnitt wie [`STICKER-DAKKS-40X30MM-QR-JSON-SAMPLE`](../STICKER-DAKKS-40X30MM-QR-JSON-SAMPLE) —
eine Rolle Etikettenmaterial bedient Geräteetikett und Kalibrieraufkleber.

Die Fehlerkorrektur steht auf **M (15 %)**, nicht auf der Jasper-Vorgabe L
(7 %): ein Etikett lebt am Gerät und sammelt Kratzer, Öl und angehobene Ecken.

## Felder

`device.asset_number`, `device.description` (ersatzweise `device.manufacturer` +
`device.model`, damit die mittlere Zone nicht leer bleibt),
`device.next_calibration_date`, `qr.url` und `barcode.value`.
Dataset-Builder: Laravel `InventoryReportDataBuilder`.

### Bekannte Grenze: lange Komposita

Die Bezeichnung steht in einer 17-mm-Spalte. Ein deutsches Kompositum, das
breiter ist als die Spalte, bricht **mitten im Wort** — JasperReports trennt
nicht silbenweise. Die Schriftgrösse ist deshalb auf 4,5 pt gesetzt, womit
Wörter bis etwa 20 Zeichen (`Buegelmessschraube`) in eine Zeile passen. Was
darüber liegt (`Praezisionsdrehmomentschluessel`), bricht weiterhin hart. Das
ist ein Schönheitsfehler, kein Informationsverlust: Identität trägt die
Inventarnummer, Details trägt der QR.

## Systembericht-Platzhalter und Stapeldruck

Dieses Bundle gehört auf den Platzhalter **Geräteetikett** in
**Administration > Berichtsverwaltung** (Grid `inventory`/Ordner `inventories`)
— dieselbe Zeile, auf der sonst das Zebra-Bundle liegt. Der Platzhalter ist ab
Werk da, trägt das Kennzeichen *Systembericht* und ist als Etikett markiert;
das ist, was **„Etikett drucken"** an die Grid-Zeile hängt.

**Stapeldruck.** Werden im Grid mehrere Zeilen markiert, druckt calServer sie in
*einem* Lauf in eine PDF:

```json
{ "meta": { "count": 40 }, "stickers": [ <dokument>, <dokument>, … ] }
```

Jedes Element ist ein **vollständiges Dokument** in der Form, die
`sample-data.json` zeigt — deshalb trägt jedes Etikett im Stapel seinen eigenen
QR. **Es ist keine Stapel-Fassung der Vorlage nötig und keine gewünscht**: Wer
hier auf ein Array umbaut, bricht den Einzeldruck.

## ⚠️ Leeres Blatt = fehlende Datenquelle

Ohne JSON-Datenquelle rendert das Etikett leer. Vorschau: mitgelieferter Adapter
(Default über `com.jaspersoft.studio.data.defadapter`) → „Open → Preview". Live
(calServer V2): Report-Setting-Variable `data_contract = inventory-datasheet`.
JasperReports **6.20.6** verbindlich.
