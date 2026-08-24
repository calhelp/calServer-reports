# STICKER-DAKKS-12MM-JSON-SAMPLE — DAkkS-Aufkleber 12 mm (V2 / APEX)

V2-Nachbildung des **DAkkS-Kalibrieraufklebers 12 mm** (Phase C). Micro-Label
34×47 pt (≈ 12×16,6 mm), gefüllt aus einem **JSON-Datensatz** (Contract
`calibration-certificate` v1.1) statt aus SQL — DB-agnostisch, kein V1-Codespalten.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/dakks-aufkleber-12mm-json-sample.jrxml` | Micro-Label: Rahmen mit drei Feldern — Kalibrierzeichen (zwei Zeilen), Kalibriermonat. Kein QR, keine Variablen |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `calibration-certificate` v1.1, minimal) |
| `main_reports/dakks-aufkleber-12mm-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Gestaltung

Gleiche Anatomie wie das 18-mm-Etikett, ein Feld kürzer: geschlossener Rahmen,
darin die Registrierdaten der Kalibrierung (*Kalibrierzeichen*) und der
Kalibriermonat — das Minimum, das die DAkkS-Kalibriermarke verlangt. Das Datum
der nächsten Kalibrierung ist bei der DAkkS optional und passt auf 12 mm nicht
mehr; wer es braucht, nimmt das 18-mm-Bundle.

**Die Gewährleistungsmarke selbst zeichnet die Vorlage bewusst nicht.** Sie ist
ein geschütztes Bild, das ein akkreditiertes Labor von der DAkkS erhält und
selbst auf das Etikett setzt.

Das Kalibrierdatum wird als **Jahr-Monat** gedruckt (`2026-06`), so wie es die
DAkkS-Marke vorsieht. **Ohne Akkreditierung** trägt die obere Zone die
**Schein-Nr.** (`calibration.certificate_display`) statt eines leeren Kastens.
Leere Werte drucken leer, nie `null`.

## Felder

`accreditation.mark_number_1` (+ `mark_number_2`) — dieselben zwei Werte, die der
Kalibrierschein in seinem Kalibrierzeichen-Block druckt. Dazu
`calibration.calibration_date` und `calibration.certificate_display`.
Dataset-Builder: Laravel `CalibrationReportDataBuilder`.

## Systembericht-Platzhalter und Stapeldruck (ab calServer V2)

Dieses Bundle gehört auf den Platzhalter **Kalibrieraufkleber** in
**Administration > Berichtsverwaltung** (Grid `calibration`/Ordner `calibrations`). Der Platzhalter ist
ab Werk da, trägt das Kennzeichen *Systembericht* und ist als Etikett markiert —
das ist, was **„Etikett drucken"** an die Grid-Zeile hängt.

Der Contract wird am Bundle erkannt; eine Report-Variable `data_contract` ist auf
dem Platzhalter **nicht nötig** (der Grid-Standard ist bereits
`calibration-certificate`). Nötig bleibt sie nur, wenn das Bundle auf einer anders
konfigurierten Zeile liegt.

**Stapeldruck.** Werden im Grid mehrere Zeilen markiert, druckt calServer sie in
*einem* Lauf in eine PDF. Dafür schickt es statt eines Dokuments

```json
{ "meta": { "count": 40 }, "stickers": [ <dokument>, <dokument>, … ] }
```

und lässt den Runner `stickers` durchlaufen. Jedes Element ist ein
**vollständiges Dokument** in genau der Form, die `sample-data.json` zeigt —
deshalb funktioniert diese Vorlage in beiden Fällen unverändert. **Es ist keine
Stapel-Fassung der Vorlage nötig und keine gewünscht**: Wer hier auf ein Array
umbaut, bricht den Einzeldruck.

Entwurf und Vorschau laufen weiter gegen `sample-data.json`, also gegen einen
einzelnen Datensatz.

## ⚠️ Leeres Blatt = fehlende Datenquelle

Ohne JSON-Datenquelle rendert das Label leer. Vorschau: mitgelieferter Adapter
(Default über `com.jaspersoft.studio.data.defadapter`) → „Open → Preview". Live
(calServer V2): Report-Setting-Variable `data_contract = calibration-certificate`.
JasperReports **6.20.6** verbindlich.
