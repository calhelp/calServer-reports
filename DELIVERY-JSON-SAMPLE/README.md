# DELIVERY-JSON-SAMPLE — Lieferschein (V2 / APEX)

V2-Nachbildung des **Lieferscheins** (Phase D), schlanke Variante des
Auftragsbelegs: Kopf + Lieferadresse + Positionen, **ohne Preise und ohne
Steuerstatistik**. Gefüllt aus einem **JSON-Datensatz** (Contract `order-document`
v1.0) statt aus SQL — DB-agnostisch, keine V1-Codespalten.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/delivery-json-sample.jrxml` | Hauptbericht: Briefkopf mit **Lieferadresse** (Meta-Box Liefernummer/Datum/Kunde/Kontakt), Positionstabelle (Pos/Beschreibung/Menge), Empfangs-Unterschriftszeile |
| `subreports/positions-delivery.jrxml` | Positionen; `positions`-Array via `subDataSource("positions")` — nur Pos/Beschreibung/Menge |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `order-document` v1.0, `document.status = "Lieferung"`) |
| `main_reports/delivery-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Contract `order-document` (v1.0)

Gleicher Contract wie `ORDER-JSON-SAMPLE`; der Lieferschein liest nur `document`,
die serverseitig aufgelöste `delivery`-Adressrolle (Fallback → Bestell-Kunde) und
`positions[]` (ohne Preis-/Steuerfelder). Dataset-Builder: Laravel
`OrderDocumentDataBuilder`.

## ⚠️ Leeres Blatt = fehlende Datenquelle

Ohne JSON-Datenquelle bleibt die Seite leer bzw. bricht auf `subDataSource(...)` ab.
Vorschau: mitgelieferter Adapter (Default über `com.jaspersoft.studio.data.defadapter`)
→ „Open → Preview". Live (calServer V2): Report-Setting-Variable
`data_contract = order-document`; Datensatz auch via
`GET /api/v2/bookings/{id}/report-dataset`. JasperReports **6.20.6** verbindlich.

## Parameter-Katalog (`parameters.json`)

Dieses Bundle liefert ein **Parameter-Manifest** (`parameters.json` an der
Bundle-Wurzel), damit calServer V2 die konfigurierbaren Parameter beim Anlegen
von Berichtsvariablen mit Beschreibung, Typ und Standardwert anbietet (siehe
[Konzept](https://github.com/calhelp/calServer-yii/blob/develop/docs/konzept-report-parameter-katalog.md)).

| Parameter | Rolle | Wirkung |
|-----------|-------|---------|
| `Company_footer` | variable (type) | Optionale Fußzeile am unteren Rand jeder Seite (Lieferschein). Leerer Default → keine Änderung am aktuellen Layout; nur wenn gesetzt (Berichtsvariable `company_footer`), erscheint die Zeile. |

Gilt nur für V2-JSON-Bundles. Der optionale Fußzeilentext ist `isBlankWhenNull`
und standardmäßig leer — die pixelgenaue Abnahme des Layouts (report-runner)
bleibt wie gehabt maßgeblich.
