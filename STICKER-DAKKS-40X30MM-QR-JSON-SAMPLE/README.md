# STICKER-DAKKS-40X30MM-QR-JSON-SAMPLE — DAkkS-Aufkleber 40×30 mm mit QR (V2 / APEX)

DAkkS-Kalibrieraufkleber **40×30 mm** (113×85 pt) mit **QR-Deep-Link auf die
Geräteseite**, gefüllt aus einem **JSON-Datensatz** (Contract
`calibration-certificate` **v1.6**) statt aus SQL — DB-agnostisch, keine
V1-Codespalten.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/dakks-aufkleber-40x30mm-qr-json-sample.jrxml` | Etikett: Rahmen, links Kalibrierzeichen + Kalibrier-/Folgemonat, rechts QR und lesbare Nummer |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `calibration-certificate` v1.6) |
| `main_reports/dakks-aufkleber-40x30mm-qr-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Gestaltung

Dieselbe Anatomie wie die 12- und 18-mm-Bundles — geschlossener Rahmen, darin
oben die Registrierdaten der Kalibrierung (*Kalibrierzeichen*), darunter der
Kalibriermonat, unten der nächste Termin — plus den QR, den die
DAkkS-Kalibriermarke als optionales Element zulässt.

**Die Gewährleistungsmarke selbst zeichnet die Vorlage bewusst nicht.** Sie ist
ein geschütztes Bild, das ein akkreditiertes Labor von der DAkkS erhält und
selbst auf das Etikett setzt.

Datumsfelder drucken **Jahr-Monat** (`2026-06`), wie in den kleineren Bundles.
**Ohne Akkreditierung** trägt die obere Zone die **Schein-Nr.**
(`calibration.certificate_display`) statt eines leeren Kastens. Leere Werte
drucken leer, nie `null`.

## Der QR

Der QR codiert `qr.url` — den öffentlichen Deep-Link auf die Geräteseite der
**QR-Code-Rolle** (`/v2/qr/{uuid}`). Scannen führt ohne Anmeldung auf
Stammdaten, Kalibrierstatus und Dokumente des Geräts.

**Voraussetzung:** QR-Links müssen eingeschaltet sein (QR-Code-Rolle mit
`qrlink_enable` und ein öffentlicher Benutzer). Sind sie aus, liefert der
Datensatz `qr.url = null` — dann codiert derselbe QR den konfigurierten
Barcode-Wert (`barcode.value`, sonst `device.asset_number`), und die
Beschriftung wechselt von *Gerät scannen* auf *Inventar-Nr.* Ein leeres weisses
Quadrat wäre die schlechtere Vorgabe.

Der Link steht **je Datensatz im Dokument**. Der alte V1-Jasper-Parameter
`QR_Code_Value` gilt je Druckauftrag — im Stapeldruck zeigten damit alle vierzig
Aufkleber auf dasselbe Gerät.

### Warum 40×30 mm und nicht 18 mm

Die Etikettengrösse folgt aus der URL-Länge, nicht aus Geschmack:

| Grösse | Wert |
|--------|------|
| Deep-Link mit uuid | ~74 Zeichen |
| QR-Version bei Fehlerkorrektur M | 5 (37×37 Module) |
| Modulraster inkl. Ruhezone | ~45 Module |
| QR-Feld in der Vorlage | 50×50 pt = 17,6 mm |
| Modulgrösse auf Papier | **0,39 mm = 3,1 Punkte bei 203 dpi** |

Drei Punkte je Modul ist die Grenze, ab der ein Thermodrucker mit 203 dpi
zuverlässig lesbare Symbole liefert. Auf einem 18-mm-DAkkS-Etikett bliebe neben
17,6 mm QR nichts mehr für Kalibrierzeichen und Datum — deshalb dieses Bundle
statt einer Quetschung. **Wer das QR-Feld verkleinert, macht den Aufkleber
unscannbar.**

Die Fehlerkorrektur steht auf **M (15 %)**, nicht auf der Jasper-Vorgabe L
(7 %): ein Aufkleber lebt am Gerät und sammelt Kratzer, Öl und angehobene Ecken.
Für rauhe Umgebungen genügt ein `errorCorrectionLevel="Q"` im JRXML — das kostet
vier weitere Module (Version 6), also 0,35 mm je Modul und 2,8 Punkte; auf
300-dpi-Druckern unkritisch, auf 203 dpi grenzwertig.

## Felder

`accreditation.mark_number_1` (+ `mark_number_2`) — dieselben zwei Werte, die
der Kalibrierschein in seinem Kalibrierzeichen-Block druckt. Dazu
`calibration.calibration_date`, `calibration.next_calibration_date`,
`calibration.certificate_display`, `qr.url`, `barcode.value` und
`device.asset_number`. Dataset-Builder: Laravel `CalibrationReportDataBuilder`.

## Systembericht-Platzhalter und Stapeldruck

Dieses Bundle gehört auf den Platzhalter **Kalibrieraufkleber** in
**Administration > Berichtsverwaltung** (Grid `calibration`/Ordner
`calibrations`) — dieselbe Zeile, auf der sonst das 12- oder 18-mm-Bundle liegt.
Der Platzhalter ist ab Werk da, trägt das Kennzeichen *Systembericht* und ist
als Etikett markiert; das ist, was **„Etikett drucken"** an die Grid-Zeile hängt.

Der Contract wird am Bundle erkannt; eine Report-Variable `data_contract` ist
auf dem Platzhalter **nicht nötig** (der Grid-Standard ist bereits
`calibration-certificate`).

**Stapeldruck.** Werden im Grid mehrere Zeilen markiert, druckt calServer sie in
*einem* Lauf in eine PDF:

```json
{ "meta": { "count": 40 }, "stickers": [ <dokument>, <dokument>, … ] }
```

Jedes Element ist ein **vollständiges Dokument** in der Form, die
`sample-data.json` zeigt — deshalb trägt jeder Aufkleber im Stapel seinen
eigenen QR. **Es ist keine Stapel-Fassung der Vorlage nötig und keine
gewünscht**: Wer hier auf ein Array umbaut, bricht den Einzeldruck.

## ⚠️ Leeres Blatt = fehlende Datenquelle

Ohne JSON-Datenquelle rendert das Etikett leer. Vorschau: mitgelieferter Adapter
(Default über `com.jaspersoft.studio.data.defadapter`) → „Open → Preview". Live
(calServer V2): Report-Setting-Variable `data_contract = calibration-certificate`.
JasperReports **6.20.6** verbindlich.
