# DAKKS-JSON-SAMPLE — V2-Pilot (JSON-Datasource)

Dies ist das **Pilot-Bundle für calServer V2** (Phase 0 der
[JasperReports-V2-Strategie](https://github.com/calhelp/calServer-yii/blob/develop/docs/evaluierung-jasper-reports-v2.md),
[ADR-009](https://github.com/calhelp/calServer-yii/blob/develop/docs-v2/entwicklung/adr/009-report-data-contract-statt-sql-templates.md)).

Im Gegensatz zu den bestehenden V1-Bundles (eingebettetes SQL über JDBC mit
Codespalten wie `I4201`, `C2303`) wird dieses Bundle aus einem **JSON-Datensatz
mit lesbaren API-Feldnamen** gefüllt — es enthält **kein SQL** und ist damit
unabhängig vom Datenbank-Backend (MySQL, PostgreSQL, MSSQL).

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/dakks-json-sample.jrxml` | Hauptbericht; liest die Felder über `<fieldDescription>`-JSON-Pfade (z. B. `device.serial_number`) |
| `subreports/results.jrxml` | Messergebnis-Tabelle; erhält das `results`-Array via `subDataSource("results")` |
| `subreports/standards.jrxml` | Verwendete Normale; erhält das `standards`-Array via `subDataSource("standards")` |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `calibration-certificate` v1.0) — als JSON-Data-Adapter in Jaspersoft Studio verwenden |

## Datenanbindung

- **Kein** `<queryString>`, **keine** `REPORT_CONNECTION`.
- Der Runner füllt den Hauptbericht mit einer `JsonDataSource` aus dem
  mitgelieferten Datensatz (`dataSourceType=json`, `dataJson`).
- Subreports holen ihre Teilmenge über
  `((JsonDataSource)$P{REPORT_DATA_SOURCE}).subDataSource("<array>")` — keine
  Connection, kein eigenes SQL.
- Den Datensatz erzeugt das calServer-V2-Backend
  (`CalibrationReportDataBuilder`); zum Testen/Entwerfen dient
  `sample-data.json`, abrufbar auch über
  `GET /api/v2/calibrations/{ctag}/report-dataset`.

## Contract `calibration-certificate` (v1.0)

Wurzelobjekt mit den Blöcken `meta`, `calibration`, `device`, `customer`,
`standards[]`, `results[]`. Jeder Entitätsblock trägt zusätzlich ein
`custom_fields`-Objekt mit den benutzerdefinierten Feldern unter ihrem
`api_name`. Feldreferenz siehe `sample-data.json`.

## Autoren-Hinweise (Jaspersoft Studio)

1. In Studio einen **JSON-Data-Adapter** anlegen und auf `sample-data.json`
   zeigen lassen.
2. Felder über ihren JSON-Pfad (`<fieldDescription>`) binden, nicht über SQL.
3. Für wiederkehrende Listen (Ergebnisse, Normale) ein Subreport mit
   `subDataSource("<array>")` als Datenquelle verwenden.
4. JasperReports-Version **6.20.6** bleibt verbindlich (siehe `robots.md`).

> **Status:** Referenz-/Pilotvorlage. Das Layout demonstriert den
> JSON-Datasource-Mechanismus; die layouttreue Nachbildung des akkreditierten
> DAkkS-Scheins erfolgt im weiteren Verlauf von Phase 0 gegen den
> Dual-Run-Sichtvergleich.
