# PRICE-LIST-JSON-SAMPLE — Preisliste (V2)

Die **Preisliste**, wie ein Labor sie seinem Kunden übergibt: Kategoriebaum mit
den geltenden Kalibrierpreisen (Typausnahmen eingerückt), Zusatzleistungen mit
Mengenstaffel, Standardartikel und die Konditions-Fußnoten. Gefüllt aus einem
**JSON-Datensatz** (Contract `price-list` v1.0) statt aus SQL — DB-agnostisch,
keine V1-Codespalten.

## Der Briefkopf steht nicht in dieser Vorlage

Das ist der Punkt der Vorlage, nicht eine Lücke. Der Briefkopf kommt **je
Mandant** über das PDF-Overlay des Berichtswesens; die Vorlage hält dafür oben
im Titelband **128 pt (≈ 45 mm)** frei und druckt dort selbst nichts.

Eine fest eingebaute Absenderzeile wäre für jeden zweiten Mandanten falsch und
ließe sich nicht wegkonfigurieren, ohne die Vorlage zu ändern. Der Freiraum ist
bewusst **fest** und kein Parameter: eine Berichtsvariable könnte die
Bandgeometrie zur Laufzeit gar nicht verschieben, sie sähe nur so aus. Wer mehr
oder weniger Platz braucht, ändert die Bandhöhe und die y-Werte darunter — das
ist ein Layout-Eingriff und gehört in die Vorlage.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/price-list-json-sample.jrxml` | Hauptbericht: Briefkopf-Freiraum, Kopf (Titel, Preisgruppe, Stichtag, Währung, Ableitungsregel), Abschnittsüberschriften, Fußzeile |
| `subreports/price-list-categories.jrxml` | Kategoriebaum aus `list.calibration`; Obergruppen fett, Untergruppen eingerückt |
| `subreports/price-list-exceptions.jrxml` | Typausnahmen einer Kategorie (`exceptions`) — die einzige zweistufige Stelle des Bündels |
| `subreports/price-list-services.jrxml` | Zusatzleistungen aus `list.services` |
| `subreports/price-list-scales.jrxml` | Mengenstaffel einer Zeile (`scales`), als Kondition unter dem Betrag |
| `subreports/price-list-articles.jrxml` | Standardartikel aus `list.articles` |
| `subreports/price-list-surcharges.jrxml` | Konditions-Fußnoten aus `list.surcharges` |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `price-list` v1.0) |
| `main_reports/price-list-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Contract `price-list` (v1.0)

Dataset-Builder: Laravel `PriceListReportDataBuilder`; derselbe Aufbau, den die
Preislisten-Seite liest (`PriceListService`). Datensatz zum Vorlagenbau:
`GET /api/v2/price-list/reports/dataset`.

Der Umschlag trägt `meta` (Contract, Schema-Version, Erzeugungszeit, Locale) und
`list` mit `group`, `date`, `currency`, `derivation`, `surcharges[]`,
`calibration[]` (je Kategorie `number`, `name`, `depth`, `amount`, `derived`,
`inherited_from`, `exceptions[]`, `scales[]`), `services[]`, `articles[]` und
`counts`.

Zwei Feinheiten, die man beim Lesen des Datensatzes leicht übersieht:

- **Eine Kategorie ohne Betrag ist eine Überschrift, keine Lücke.** Sie bündelt
  ihre Untergruppen. Die Vorlage druckt dort nichts, nicht „0,00".
- **`derived` heißt abgeleitet, nicht geschätzt.** Der Betrag entsteht aus der
  Kondition der Preisgruppe auf dem Listenpreis; er ist so verbindlich wie ein
  eingetragener.

### Bewusst nicht gedruckt

`list.other_type_prices` — die bei 200 gekappte Liste der Typpreise **ohne**
Kategorie. Das ist ein Übergangsbestand auf dem Weg zur Kategorisierung, kein
Bestandteil einer Kundenliste; eine willkürlich abgeschnittene Aufzählung
gehört nicht auf ein Dokument, das man aus der Hand gibt. Wer sie braucht,
nimmt den CSV-Export der Preislisten-Seite.

## Zahlenformat folgt der Locale

Beträge stehen mit `pattern="#,##0.00"` und werden über `REPORT_LOCALE`
formatiert, das calServer je Mandant setzt — `de-DE` ergibt `84,15`, `en-US`
ergibt `84.15`. In Jaspersoft Studio ohne gesetzte Locale zeigt die Vorschau das
Format des Rechners; das ist kein Vorlagenfehler.

## ⚠️ Leeres Blatt = fehlende Datenquelle

Ohne JSON-Datenquelle bleibt die Seite leer bzw. bricht auf `subDataSource(...)`
ab. Vorschau: mitgelieferter Adapter (Default über
`com.jaspersoft.studio.data.defadapter`) → „Open → Preview". Live (calServer V2):
Report-Setting-Variable `data_contract = price-list`. JasperReports **6.20.6**
verbindlich.

## Parameter-Katalog (`parameters.json`)

| Parameter | Rolle | Wirkung |
|-----------|-------|---------|
| `List_title` | variable (type) | Überschrift des Dokuments; Vorgabe „Preisliste". |
| `Company_footer` | variable (type) | Optionale Fußzeile auf jeder Seite. Leer lassen, wenn der Briefkopf schon eine mitbringt. |
| `Reportpath` | system | Bundle-Wurzel für die Subreport-Auflösung, von calServer gesetzt. |

## Geprüft

Alle sieben JRXML übersetzen mit JasperReports 6.20.6, und der Hauptbericht
füllt gegen `sample-data.json` durch (eine Seite). Geprüft wurde dabei auch,
dass die zweistufige Auflösung `subDataSource("exceptions")` innerhalb des
Kategorie-Subreports wirklich greift — die Typausnahme erscheint eingerückt
unter ihrer Kategorie. Die pixelgenaue Abnahme des Layouts (report-runner)
bleibt wie gehabt maßgeblich.
