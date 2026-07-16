# REPAIR-JSON-SAMPLE — Reparaturbericht (V2 / APEX)

Reparaturbericht als **V2-Bundle** im Sinne von
[ADR-009](https://github.com/calhelp/calServer-yii/blob/develop/docs-v2/entwicklung/adr/009-report-data-contract-statt-sql-templates.md):
gefüllt aus dem Report-Data-Contract `repair-report` (JSON) mit lesbaren
API-Feldnamen statt aus eingebettetem SQL gegen V1-Codespalten.

Fünfte Bundle-Familie (nach Kalibrierschein, Geräte-Datenblatt,
Auftrag/Lieferschein). V1 liefert keinen eingebauten Reparatur-JRXML mit —
dieses Layout ist bewusst neu entworfen: Prüfmittel-Stammdatengrid,
Fehlerbeschreibung, Reparaturaktion, Datum/Status und Signaturzeilen.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/repair-json-sample.jrxml` | Hauptbericht: Kopf mit Prüfmittel-Grid (Inventar-/Serien-Nr., Hersteller/Typ, nächste Kalibrierung, Kunde), Reparaturdatum + Status, Abschnitte Fehlerbeschreibung (`repair.description`) und Reparaturaktion (`repair.notes`), Signaturzeilen, Seiten-Footer |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `repair-report` **v1.0**) |
| `main_reports/repair-json-sample_adapter.xml` | Mitgelieferter Jaspersoft-Studio-**JSON-Data-Adapter** auf `sample-data.json` — macht die Vorschau turnkey (siehe „Vorschau ohne Backend") |

## ⚠️ Warum ein leeres/weißes Blatt erscheinen kann

Dieses Bundle ist **datenquellenlos**: Der Bericht enthält **kein** eingebettetes
SQL und **keine** Beispieldaten im Template selbst. Er rendert nur dann Inhalt,
wenn ihm eine **JSON-Datenquelle** übergeben wird. Wird er ohne Datenquelle
ausgeführt — z. B. „Preview" in Jaspersoft Studio ohne konfigurierten
Data-Adapter, oder Generierung in der Live-Umgebung **ohne** die Report-Variable
`data_contract` — bleibt die Seite leer. Das ist **kein** Template-Fehler,
sondern die fehlende Datenanbindung. Abhilfe:

- **Vorschau ohne Backend (Jaspersoft Studio):** Das Bundle bringt den Adapter
  `repair-json-sample_adapter.xml` mit und referenziert ihn über die
  Report-Property `com.jaspersoft.studio.data.defadapter`. „Open → Preview"
  füllt den Bericht direkt aus `sample-data.json`. Falls die Studio-Version den
  Default-Adapter nicht automatisch zieht, den Adapter im Vorschau-Dropdown
  einmalig auswählen.
- **Live-Umgebung (calServer V2):** Auf dem Report-Setting die report-scoped
  Variable `data_contract = repair-report` setzen — dann liefert das Backend
  (`RepairReportDataBuilder`) den JSON-Datensatz an den Runner. Ohne diese
  Variable läuft der klassische JDBC-Pfad, der hier mangels `<queryString>`
  keine Daten hat.

## Datenanbindung

- **Kein** `<queryString>`, **keine** `REPORT_CONNECTION`.
- Der Runner füllt den Hauptbericht mit einer `JsonDataSource`
  (`dataSourceType=json`, `dataJson`); der Bericht ist genau ein Datensatz
  (Wurzelobjekt).
- Custom Fields (z. B. Techniker, Kosten, Ersatzteile) stehen unter ihrem
  `api_name` im Objekt `repair.custom_fields` bereit, sobald sie in calServer
  als Felder der Reparatur-Tabelle konfiguriert sind.
- Den Datensatz erzeugt das calServer-V2-Backend (`RepairReportDataBuilder`).

Aktivierung in calServer: dem Report-Setting (grid_name `repair`, Ordner
`repairs`) eine Report-Variable `data_contract = repair-report` zuweisen
(Details siehe V2-Doku „V2-Berichte mit JSON-Datenquelle").

## Contract `repair-report` (v1.0)

| Block | Felder |
|-------|--------|
| `meta` | `contract`, `schema_version`, `generated_at`, `locale` |
| `repair` | `description`, `notes`, `repair_date`, `repair_time`, `status_code`, `status`, `custom_fields{}` |
| `device` | `asset_number`, `serial_number`, `description`, `manufacturer`, `model`, `type_code`, `next_calibration_date`, `custom_fields{}` (`{}` wenn kein Gerät verknüpft) |
| `customer` | `name`, `customer_number`, `street`, `zip`, `city`, `custom_fields{}` (`{}` wenn kein Kunde verknüpft) |

> **Status:** Referenz-/Beispielvorlage. JasperReports **6.20.6** bleibt
> verbindlich (siehe `robots.md`).
