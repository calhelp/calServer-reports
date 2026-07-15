# INVENTORY-JSON-SAMPLE — V2-Bundle (JSON-Datasource)

Geräte-Datenblatt als **V2-Bundle** im Sinne von
[ADR-009](https://github.com/calhelp/calServer-yii/blob/develop/docs-v2/entwicklung/adr/009-report-data-contract-statt-sql-templates.md):
gefüllt aus dem Report-Data-Contract `inventory-datasheet` (JSON) mit lesbaren
API-Feldnamen statt aus eingebettetem SQL gegen V1-Codespalten.

Zweite Bundle-Familie neben `DAKKS-JSON-SAMPLE` — sie zeigt zusätzlich die
Bindung eines **Custom Fields** (`device.custom_fields.customer_tag`) und einer
wiederkehrenden Liste (Kalibrierhistorie) per `subDataSource`.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/inventory-json-sample.jrxml` | Datenblatt; liest Gerätefelder + ein Custom Field über `<fieldDescription>`-JSON-Pfade |
| `subreports/calibrations.jrxml` | Kalibrierhistorie; erhält das `calibrations`-Array via `subDataSource("calibrations")` |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `inventory-datasheet` v1.0) für den JSON-Data-Adapter in Jaspersoft Studio |

## Datenanbindung

- **Kein** `<queryString>`, **keine** `REPORT_CONNECTION`.
- Der Runner füllt den Hauptbericht mit einer `JsonDataSource`; das Datenblatt
  ist genau ein Datensatz (Wurzelobjekt).
- Custom Fields stehen unter ihrem `api_name` im `custom_fields`-Objekt bereit
  (`device.custom_fields.customer_tag`).
- Den Datensatz erzeugt das calServer-V2-Backend (`InventoryReportDataBuilder`).

Aktivierung in calServer: dem Report-Setting eine Report-Variable
`data_contract = inventory-datasheet` zuweisen (Details siehe V2-Doku
„V2-Berichte mit JSON-Datenquelle").

> **Status:** Referenz-/Beispielvorlage. JasperReports **6.20.6** bleibt
> verbindlich (siehe `robots.md`).
