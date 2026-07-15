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
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `calibration-certificate` **v1.1**) |
| `main_reports/dakks-json-sample_adapter.xml` | Mitgelieferter Jaspersoft-Studio-**JSON-Data-Adapter** auf `sample-data.json` — macht die Vorschau turnkey (siehe „Vorschau ohne Backend") |

## ⚠️ Warum ein leeres/weißes Blatt erscheinen kann

Dieses Bundle ist **datenquellenlos**: Der Bericht enthält **kein** eingebettetes
SQL und **keine** Beispieldaten im Template selbst. Er rendert nur dann Inhalt,
wenn ihm eine **JSON-Datenquelle** übergeben wird. Wird er ohne Datenquelle
ausgeführt — z. B. „Preview" in Jaspersoft Studio ohne konfigurierten
Data-Adapter, oder Generierung in der Live-Umgebung **ohne** die Report-Variable
`data_contract` — bleibt die Seite leer bzw. der Lauf bricht auf dem
Subreport-`subDataSource(...)`-Aufruf ab. Das ist **kein** Template-Fehler,
sondern die fehlende Datenanbindung. Abhilfe:

- **Vorschau ohne Backend (Jaspersoft Studio):** Das Bundle bringt den Adapter
  `dakks-json-sample_adapter.xml` mit und referenziert ihn über die
  Report-Property `com.jaspersoft.studio.data.defadapter`. „Open → Preview"
  füllt den Schein direkt aus `sample-data.json`. Falls die Studio-Version den
  Default-Adapter nicht automatisch zieht, den Adapter im Vorschau-Dropdown
  einmalig auswählen.
- **Live-Umgebung (calServer V2):** Auf dem Report-Setting die report-scoped
  Variable `data_contract = calibration-certificate` setzen — dann liefert das
  Backend (`CalibrationReportDataBuilder`) den JSON-Datensatz an den Runner.
  Ohne diese Variable läuft der klassische JDBC-Pfad, der hier mangels
  `<queryString>` keine Daten hat.

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

1. Der mitgelieferte **JSON-Data-Adapter** (`dakks-json-sample_adapter.xml`)
   zeigt bereits auf `sample-data.json` und ist als Default-Adapter hinterlegt —
   „Preview" genügt. (Alternativ selbst einen JSON-Data-Adapter anlegen.)
2. Felder über ihren JSON-Pfad (`<fieldDescription>`) binden, nicht über SQL.
3. Für wiederkehrende Listen (Ergebnisse, Normale) ein Subreport mit
   `subDataSource("<array>")` als Datenquelle verwenden.
4. JasperReports-Version **6.20.6** bleibt verbindlich (siehe `robots.md`).

> **Status:** Layouttreue V2-Nachbildung, über den report-runner zu PDF
> verifiziert. Die abschließende pixelgenaue Abnahme des akkreditierten Scheins
> erfolgt per Dual-Run-Sichtvergleich V1↔V2 in einer Live-Umgebung.
