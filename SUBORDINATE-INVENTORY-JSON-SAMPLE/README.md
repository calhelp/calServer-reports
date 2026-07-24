# SUBORDINATE-INVENTORY-JSON-SAMPLE — V2-Bundle (JSON-Datasource)

Gerät mit Details und **allen untergeordneten Geräten** als V2-Bundle im Sinne
von [ADR-009](https://github.com/calhelp/calServer-yii/blob/develop/docs-v2/entwicklung/adr/009-report-data-contract-statt-sql-templates.md)
und [ADR-011](https://github.com/calhelp/calServer-yii/blob/develop/docs-v2/entwicklung/adr/011-untergeordnete-inventare-v2.md):
gefüllt aus dem Report-Data-Contract `inventory-datasheet` (ab Schema **1.2**)
mit lesbaren API-Feldnamen statt aus eingebettetem SQL gegen V1-Codespalten.

Der Contract 1.2 liefert zusätzlich zum Gerät:

- `parent` — das übergeordnete Gerät (V1: `I4217` / „Accessory Asset"),
  leeres Objekt bei einem Root-Gerät;
- `children` — den **kompletten Teilbaum** der untergeordneten Geräte,
  tiefensortiert, mit `level` (1 = direkte Kinder, 2 = deren Kinder usw.).

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/subordinate-inventory-json-sample.jrxml` | Gerätedetails + Zeile „Übergeordnetes Gerät" (nur wenn vorhanden) + Abschnitt „Untergeordnete Geräte" |
| `subreports/children.jrxml` | Teilbaum-Tabelle (Ebene, Inventar-Nr., Serien-Nr., Beschreibung, Standort, nächste Kalibrierung); erhält das `children`-Array via `subDataSource("children")` |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `inventory-datasheet` v1.2) für den JSON-Data-Adapter in Jaspersoft Studio |
| `parameters.json` | Parameter-Manifest (nur Systemparameter `Reportpath`) |

## Datenanbindung

- **Kein** `<queryString>`, **keine** `REPORT_CONNECTION`.
- Der Runner füllt den Hauptbericht mit einer `JsonDataSource`; das Datenblatt
  ist genau ein Datensatz (Wurzelobjekt).
- Den Datensatz erzeugt das calServer-V2-Backend
  (`InventoryReportDataBuilder`, Schema 1.2) — ohne die `children`-Sektion im
  Contract bleibt der Subreport leer.

Aktivierung in calServer: Report-Setting auf dem Inventar-Grid anlegen
(Kontext „Detail") und dieses Bundle als ZIP hochladen — mehr ist nicht
nötig. calServer erkennt bei hochgeladenen Bundles ein query-loses
Haupt-JRXML automatisch und sendet den Default-Contract des Grids mit
(`inventory-datasheet`). Die Report-Variable `data_contract` ist nur noch
als Override bzw. Escape-Hatch (`jdbc` erzwingt den klassischen
JDBC-Pfad) oder für per Pfad referenzierte, nicht hochgeladene Vorlagen
relevant (Details siehe V2-Doku „V2-Berichte mit JSON-Datenquelle").

> **Status:** Referenz-/Beispielvorlage. JasperReports **6.20.6** bleibt
> verbindlich (siehe `robots.md`).
