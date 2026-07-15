# DAKKS-JSON-SAMPLE — layouttreuer DAkkS-Kalibrierschein (V2 / APEX)

Dies ist die **layouttreue V2-Nachbildung des akkreditierten DAkkS-Kalibrierscheins**
(Phase 0 der
[JasperReports-V2-Strategie](https://github.com/calhelp/calServer-yii/blob/develop/docs/evaluierung-jasper-reports-v2.md),
[ADR-009](https://github.com/calhelp/calServer-yii/blob/develop/docs-v2/entwicklung/adr/009-report-data-contract-statt-sql-templates.md)).

Im Gegensatz zu den bestehenden V1-Bundles (eingebettetes SQL über JDBC mit
Codespalten wie `I4201`, `C2303`) wird dieses Bundle aus einem **JSON-Datensatz
mit lesbaren API-Feldnamen** gefüllt — es enthält **kein SQL** und ist damit
unabhängig vom Datenbank-Backend (MySQL, PostgreSQL, MSSQL).

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/dakks-json-sample.jrxml` | Hauptbericht: Labor-Kopf, zweisprachiges Objekt-Stammdatengrid, Kalibrierzeichen-Box (Line-Art), QR aus `device.asset_number`, Abschnittskörper (Verfahren, Messbedingungen), Signatur-/Freigabebereich, Seiten-Footer |
| `subreports/results.jrxml` | Messergebnis-Tabelle; `results`-Array via `subDataSource("results")` — mit SI-Wert+Präfix+Einheit-Konkatenation und per-Zeile `accred`-„*"-Symbol |
| `subreports/standards.jrxml` | Verwendete Normale; `standards`-Array via `subDataSource("standards")` — inkl. nächster Kalibrierung + Zertifikat-Nr. |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `calibration-certificate` **v1.1**) — als JSON-Data-Adapter in Jaspersoft Studio verwenden |

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

## Contract `calibration-certificate` (v1.1)

Wurzelobjekt mit den Blöcken `meta`, `laboratory`, `accreditation`,
`calibration`, `device`, `customer`, `procedure`, `standards[]`, `results[]`,
`signatures[]`, `texts`. Die Blöcke `laboratory`/`accreditation`/`procedure`/
`texts` und der Freigeber (`signatures[]`) stammen aus konfigurierten
Report-Variablen (`master_report_variable`, z. B. `lab_name`, `mark_number_1`,
`approver_name`, `traceability_note`) — nicht aus Entity-Daten. `results[]`
enthält je Wert das Triple `<feld>`/`<feld>_p` (SI-Präfix)/`<feld>_u` (Einheit)
plus `accred`. Jeder Entitätsblock trägt zusätzlich `custom_fields`. Feldreferenz
siehe `sample-data.json`.

## Autoren-Hinweise (Jaspersoft Studio)

1. In Studio einen **JSON-Data-Adapter** anlegen und auf `sample-data.json`
   zeigen lassen.
2. Felder über ihren JSON-Pfad (`<fieldDescription>`) binden, nicht über SQL.
3. Für wiederkehrende Listen (Ergebnisse, Normale) ein Subreport mit
   `subDataSource("<array>")` als Datenquelle verwenden.
4. JasperReports-Version **6.20.6** bleibt verbindlich (siehe `robots.md`).

> **Status:** Layouttreue V2-Nachbildung, über den report-runner zu PDF
> verifiziert. Die abschließende pixelgenaue Abnahme des akkreditierten Scheins
> erfolgt per Dual-Run-Sichtvergleich V1↔V2 in einer Live-Umgebung.
