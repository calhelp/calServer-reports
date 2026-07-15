# STICKER-DAKKS-18MM-JSON-SAMPLE — DAkkS-Aufkleber 18 mm (V2 / APEX)

V2-Nachbildung des **DAkkS-Kalibrieraufklebers 18 mm** (Phase C). Label 51×70 pt
Landscape (≈ 18×24,7 mm), gefüllt aus einem **JSON-Datensatz** (Contract
`calibration-certificate` v1.1) statt aus SQL — DB-agnostisch, keine V1-Codespalten.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/dakks-aufkleber-18mm-json-sample.jrxml` | Label: Rahmen (Line-Art), „DAkkS", Akkreditierungs-Markennummer, Kalibrier- + nächstes Datum. Kein QR, keine Variablen |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `calibration-certificate` v1.1, minimal) |
| `main_reports/dakks-aufkleber-18mm-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Felder

`accreditation.mark_number_1` (+ `mark_number_2`), `calibration.calibration_date`,
`calibration.next_calibration_date`. Dataset-Builder: Laravel `CalibrationReportDataBuilder`.

## ⚠️ Leeres Blatt = fehlende Datenquelle

Ohne JSON-Datenquelle rendert das Label leer. Vorschau: mitgelieferter Adapter
(Default über `com.jaspersoft.studio.data.defadapter`) → „Open → Preview". Live
(calServer V2): Report-Setting-Variable `data_contract = calibration-certificate`.
JasperReports **6.20.6** verbindlich.
