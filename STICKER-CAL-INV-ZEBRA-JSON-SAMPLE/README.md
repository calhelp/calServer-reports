# STICKER-CAL-INV-ZEBRA-JSON-SAMPLE — Zebra Inventar-/Kalibrier-Sticker (V2 / APEX)

V2-Nachbildung des kombinierten **Inventar-/Kalibrier-Stickers** für den
Zebra ZD621 30×15 mm @203 dpi (240×120 px), Phase C. Gefüllt aus einem
**JSON-Datensatz** (Contract `inventory-datasheet` v1.1) statt aus SQL —
DB-agnostisch, keine V1-Codespalten.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/cal-inv-zebra-json-sample.jrxml` | Label 240×120 px: **QR aus `device.asset_number`** (links) + Infospalte rechts (Inventar-Nr., OE-Bezeichnung, Kostenstelle, Standort, letzte + nächste Kalibrierung) |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `inventory-datasheet` v1.1) |
| `main_reports/cal-inv-zebra-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Felder

`device.asset_number` (QR + Text), `device.cost_center`, `device.active_location.location_1/2`,
`device.last_calibration_date`, `device.next_calibration_date`, `customer.name`
(OE-Bezeichnung/Gruppe). Dataset-Builder: Laravel `InventoryReportDataBuilder`.

> Der QR wird runner-seitig aus dem Feldwert gerendert (`<jr:QRCode>`, ZXing) — kein
> vorgeneriertes Bild, kein `Barcode`-Model, DB-agnostisch.

## ⚠️ Leeres Blatt = fehlende Datenquelle

Ohne JSON-Datenquelle rendert der Sticker leer. Vorschau: mitgelieferter Adapter
(Default über `com.jaspersoft.studio.data.defadapter`) → „Open → Preview". Live
(calServer V2): Report-Setting-Variable `data_contract = inventory-datasheet`.
JasperReports **6.20.6** verbindlich. Keine `$V{}`-Variablen (nur `staticText`/`$F{}`).
