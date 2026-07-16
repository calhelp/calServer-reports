# LOCATION-JSON-SAMPLE — Standort-/Leihbericht (V2 / APEX)

Standort-/Leihbericht als **V2-Bundle** im Sinne von
[ADR-009](https://github.com/calhelp/calServer-yii/blob/develop/docs-v2/entwicklung/adr/009-report-data-contract-statt-sql-templates.md):
gefüllt aus dem Report-Data-Contract `location-report` (JSON) mit lesbaren
API-Feldnamen statt aus eingebettetem SQL gegen V1-Codespalten.

Sechste Bundle-Familie; das Layout folgt dem V1-Leihschein
(`httpdocs/reports/locations/Location/main_reports/Location.jrxml`): Kunden- und
Lieferadresse mit Kontakten, Leihdaten (Leihdatum/-zeit, Rückgabedatum, Status),
Prüfmittel-Grid und Standortblock (`location_1..5`) mit Signaturzeilen.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/location-json-sample.jrxml` | Hauptbericht: Kopf mit Kunde-/Lieferadresse + Kontakten, Leihdaten-Block, Prüfmittel-Grid, Standortblock (`location_1..5`), Signaturzeilen (Entleiher/Ausgabe), Seiten-Footer |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `location-report` **v1.0**) |
| `main_reports/location-json-sample_adapter.xml` | Mitgelieferter Jaspersoft-Studio-**JSON-Data-Adapter** auf `sample-data.json` — macht die Vorschau turnkey (siehe „Vorschau ohne Backend") |

## ⚠️ Warum ein leeres/weißes Blatt erscheinen kann

Dieses Bundle ist **datenquellenlos**: Der Bericht enthält **kein** eingebettetes
SQL und **keine** Beispieldaten im Template selbst. Er rendert nur dann Inhalt,
wenn ihm eine **JSON-Datenquelle** übergeben wird. Wird er ohne Datenquelle
ausgeführt — z. B. „Preview" in Jaspersoft Studio ohne konfigurierten
Data-Adapter, oder Generierung in der Live-Umgebung **ohne** die Report-Variable
`data_contract` — bleibt die Seite leer. Das ist **kein** Template-Fehler,
sondern die fehlende Datenanbindung. Abhilfe:

- **Vorschau ohne Backend (Jaspersoft Studio):** Das Bundle bringt den Adapter
  `location-json-sample_adapter.xml` mit und referenziert ihn über die
  Report-Property `com.jaspersoft.studio.data.defadapter`. „Open → Preview"
  füllt den Bericht direkt aus `sample-data.json`. Falls die Studio-Version den
  Default-Adapter nicht automatisch zieht, den Adapter im Vorschau-Dropdown
  einmalig auswählen.
- **Live-Umgebung (calServer V2):** Auf dem Report-Setting die report-scoped
  Variable `data_contract = location-report` setzen — dann liefert das Backend
  (`LocationReportDataBuilder`) den JSON-Datensatz an den Runner. Ohne diese
  Variable läuft der klassische JDBC-Pfad, der hier mangels `<queryString>`
  keine Daten hat.

## Datenanbindung

- **Kein** `<queryString>`, **keine** `REPORT_CONNECTION`.
- Der Runner füllt den Hauptbericht mit einer `JsonDataSource`
  (`dataSourceType=json`, `dataJson`); der Bericht ist genau ein Datensatz
  (Wurzelobjekt).
- Das Rückgabedatum ist ein konfiguriertes Custom Field und wird unter seinem
  `api_name` gebunden: `location.custom_fields.rental_end`.
- Die Lieferadresse (`delivery_customer`) fällt **serverseitig** auf den
  Kunden zurück, wenn kein eigener Lieferkunde hinterlegt ist — das Template
  braucht keine Fallback-Logik.
- Den Datensatz erzeugt das calServer-V2-Backend (`LocationReportDataBuilder`).

Aktivierung in calServer: dem Report-Setting (grid_name `location`, Ordner
`locations`) eine Report-Variable `data_contract = location-report` zuweisen
(Details siehe V2-Doku „V2-Berichte mit JSON-Datenquelle").

## Contract `location-report` (v1.0)

| Block | Felder |
|-------|--------|
| `meta` | `contract`, `schema_version`, `generated_at`, `locale` |
| `location` | `location_1..5`, `location_date`, `location_time`, `is_active`, `status`, `custom_fields{}` (inkl. `rental_end`, wenn konfiguriert) |
| `device` | `asset_number`, `serial_number`, `description`, `manufacturer`, `model`, `type_code`, `next_calibration_date`, `custom_fields{}` (`{}` wenn kein Gerät verknüpft) |
| `customer` | `name`, `customer_number`, `street`, `zip`, `city`, `country`, `custom_fields{}` |
| `customer_contact` | `name`, `street`, `zip`, `city`, `email`, `phone` (`{}` wenn kein Kontakt verknüpft) |
| `delivery_customer` | wie `customer`; serverseitiger Fallback auf `customer` |
| `delivery_contact` | wie `customer_contact` |

> **Status:** Referenz-/Beispielvorlage. JasperReports **6.20.6** bleibt
> verbindlich (siehe `robots.md`).

## Parameter-Katalog (`parameters.json`)

Dieses Bundle liefert ein **Parameter-Manifest** (`parameters.json` an der
Bundle-Wurzel), damit calServer V2 die konfigurierbaren Parameter beim Anlegen
von Berichtsvariablen mit Beschreibung, Typ und Standardwert anbietet (siehe
[Konzept](https://github.com/calhelp/calServer-yii/blob/develop/docs/konzept-report-parameter-katalog.md)).

| Parameter | Rolle | Wirkung |
|-----------|-------|---------|
| `Company_footer` | variable (type) | Optionale Fußzeile am unteren Rand jeder Seite (Standort-/Leihbericht). Leerer Default → keine Änderung am aktuellen Layout; nur wenn gesetzt (Berichtsvariable `company_footer`), erscheint die Zeile. |

Gilt nur für V2-JSON-Bundles. Der optionale Fußzeilentext ist `isBlankWhenNull`
und standardmäßig leer — die pixelgenaue Abnahme des Layouts (report-runner)
bleibt wie gehabt maßgeblich.
