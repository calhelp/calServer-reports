# KALIBRIERKONTROLLBLATT-JSON-SAMPLE — Kalibrierkontrollblatt (V2 / APEX)

V2-Nachbildung des **Kalibrierkontrollblatts** (Phase C der
JasperReports-V2-Strategie). Im Gegensatz zum V1-Bundle `KALIBRIERKONTROLLBLATT`
(eingebettetes SQL über JDBC, Codespalten wie `I4206`, `C2301`) wird dieses Bundle
aus einem **JSON-Datensatz mit lesbaren API-Feldnamen** gefüllt — es enthält **kein
SQL** und ist unabhängig vom Datenbank-Backend (MySQL, PostgreSQL, MSSQL).

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/kalibrierkontrollblatt-json-sample.jrxml` | Hauptbericht: Prüfmittel-Stammdatengrid (Inventar-/Serien-Nr., Hersteller/Typ, Kostenstelle, Kalibrierintervall, strukturierter Standort, letzte/nächste Kalibrierung) + Kundenblock; alle Labels als `staticText` |
| `subreports/calibration-history.jrxml` | Kalibrierhistorie; `calibrations`-Array via `subDataSource("calibrations")` (Datum/nächste Fälligkeit/Zertifikat-Nr./Bearbeiter) |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `inventory-datasheet` **v1.1**) |
| `main_reports/kalibrierkontrollblatt-json-sample_adapter.xml` | Mitgelieferter Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Contract `inventory-datasheet` (v1.1)

Wurzelobjekt mit `meta`, `device`, `customer`, `calibrations[]`. Neu in v1.1 (für die
layouttreue Nachbildung genutzt): `device.active_location` (strukturierter Standort
`location_1..3`), `device.cost_center` und `device.last_calibration_date`. Dataset-Builder:
Laravel `InventoryReportDataBuilder`. Feldreferenz siehe `sample-data.json`.

## ⚠️ Warum ein leeres/weißes Blatt erscheinen kann

Datenquellenlos: der Bericht rendert nur mit übergebener **JSON-Datenquelle**. Ohne sie
(Studio-Preview ohne Adapter, oder Live-Generierung ohne die Report-Variable
`data_contract`) bleibt die Seite leer bzw. bricht auf `subDataSource(...)` ab — kein
Template-Fehler, sondern fehlende Datenanbindung. Abhilfe:

- **Vorschau (Jaspersoft Studio):** Der mitgelieferte Adapter
  `kalibrierkontrollblatt-json-sample_adapter.xml` (Default über
  `com.jaspersoft.studio.data.defadapter`) füllt die Vorschau aus `sample-data.json` —
  „Open → Preview" genügt.
- **Live (calServer V2):** Auf dem Report-Setting die Variable
  `data_contract = inventory-datasheet` setzen; das Backend liefert den Datensatz.

## Autoren-Hinweise

- JasperReports-Version **6.20.6** bleibt verbindlich (siehe `robots.md`).
- Labels als `staticText` halten — `$V{}`-Variablen in `title`/`columnHeader` ohne
  `initialValueExpression` würden vor dem ersten Record `null` drucken.
- Subreport-Teilmengen über `subDataSource("<array>")`.

## Parameter-Katalog (`parameters.json`)

Dieses Bundle liefert ein **Parameter-Manifest** (`parameters.json` an der
Bundle-Wurzel), damit calServer V2 die konfigurierbaren Parameter beim Anlegen
von Berichtsvariablen mit Beschreibung, Typ und Standardwert anbietet (siehe
[Konzept](https://github.com/calhelp/calServer-yii/blob/develop/docs/konzept-report-parameter-katalog.md)).

| Parameter | Rolle | Wirkung |
|-----------|-------|---------|
| `Company_footer` | variable (type) | Optionale Fußzeile am unteren Rand jeder Seite (Kalibrierkontrollblatt). Leerer Default → keine Änderung am aktuellen Layout; nur wenn gesetzt (Berichtsvariable `company_footer`), erscheint die Zeile. |

Gilt nur für V2-JSON-Bundles. Der optionale Fußzeilentext ist `isBlankWhenNull`
und standardmäßig leer — die pixelgenaue Abnahme des Layouts (report-runner)
bleibt wie gehabt maßgeblich.
