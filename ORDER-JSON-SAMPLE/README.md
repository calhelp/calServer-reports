# ORDER-JSON-SAMPLE — Auftrag/Angebot/Rechnung (V2 / APEX)

V2-Nachbildung des **Auftragsbelegs** (Phase D). Im Gegensatz zum V1-Bundle
`ORDER-SAMPLE` (eingebettetes SQL + separater Statistics-Subreport, der die
Steuergruppen per GROUP-BY selbst nachquert) wird dieses Bundle aus einem
**JSON-Datensatz mit lesbaren API-Feldnamen** gefüllt — es enthält **kein SQL**
und ist unabhängig vom DB-Backend (MySQL, PostgreSQL, MSSQL).

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/order-json-sample.jrxml` | Hauptbericht: Briefkopf (Empfängeradresse + Meta-Box Belegnummer/Datum/Kunde/Kontakt), Betreff, Positionstabelle + Statistik. Alle Labels als `staticText` |
| `subreports/positions.jrxml` | Positionen; `positions`-Array via `subDataSource("positions")` (Pos/Beschreibung/Menge/Einzelpreis/Rabatt/Betrag/MwSt) |
| `subreports/tax-groups.jrxml` | Steuergruppen; `statistics.tax_groups`-Array via `subDataSource("statistics.tax_groups")` (USt. je Satz) |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `order-document` v1.0) |
| `main_reports/order-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Contract `order-document` (v1.0)

Wurzelobjekt mit `meta`, `document` (Nummer/Datum/Status/Kommentar/Rechtstext +
`custom_fields` für W41xx-Zusatzfelder), drei Adressrollen `customer`/`delivery`/
`invoice` (mit `contact`-Unterobjekt, serverseitig mit V1-Fallback aufgelöst),
`positions[]` und **serverseitig vorberechneter `statistics`** (`tax_groups[]` je
Steuersatz + Skalare `net_total`/`discount_amount`/`net_after_discount`/`vat_total`/
`gross_total`). **Jasper kann ein JSON-Array nicht gruppieren** — die
Steuergruppen-Aggregation macht daher der `OrderDocumentDataBuilder` (Laravel);
der Bericht druckt nur. Feldreferenz siehe `sample-data.json`.

> **Auftragsrabatt (W4114):** Die Muster sind rabattfrei, damit die Summen
> eindeutig sind. Die exakte V1-Rabatt-Steuer-Arithmetik bei mehreren Steuersätzen
> ist ein Dual-Run-Abstimmungspunkt (siehe Builder-Doku).

## ⚠️ Warum ein leeres/weißes Blatt erscheinen kann

Datenquellenlos: rendert nur mit übergebener **JSON-Datenquelle**. Ohne sie
(Studio-Preview ohne Adapter, oder Live-Generierung ohne `data_contract`) bleibt die
Seite leer bzw. bricht auf `subDataSource(...)` ab. Abhilfe:

- **Vorschau (Studio):** mitgelieferter Adapter (Default über
  `com.jaspersoft.studio.data.defadapter`) → „Open → Preview".
- **Live (calServer V2):** Report-Setting-Variable `data_contract = order-document`;
  Datensatz auch via `GET /api/v2/bookings/{id}/report-dataset`.

JasperReports **6.20.6** verbindlich.

## Parameter-Katalog (`parameters.json`)

Dieses Bundle liefert ein **Parameter-Manifest** (`parameters.json` an der
Bundle-Wurzel), damit calServer V2 die konfigurierbaren Parameter beim Anlegen
von Berichtsvariablen mit Beschreibung, Typ und Standardwert anbietet (siehe
[Konzept](https://github.com/calhelp/calServer-yii/blob/develop/docs/konzept-report-parameter-katalog.md)).

| Parameter | Rolle | Wirkung |
|-----------|-------|---------|
| `Company_footer` | variable (type) | Optionale Fußzeile am unteren Rand jeder Seite (Auftragsbeleg). Leerer Default → keine Änderung am aktuellen Layout; nur wenn gesetzt (Berichtsvariable `company_footer`), erscheint die Zeile. |

Gilt nur für V2-JSON-Bundles. Der optionale Fußzeilentext ist `isBlankWhenNull`
und standardmäßig leer — die pixelgenaue Abnahme des Layouts (report-runner)
bleibt wie gehabt maßgeblich.
