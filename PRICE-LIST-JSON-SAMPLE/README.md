# PRICE-LIST-JSON-SAMPLE — Preisliste (V2)

Die **Preisliste**, wie ein Labor sie seinem Kunden übergibt: Kategoriebaum mit
den geltenden Kalibrierpreisen (Typausnahmen eingerückt), Zusatzleistungen mit
Mengenstaffel, Standardartikel und die Konditions-Fußnoten. Gefüllt aus einem
**JSON-Datensatz** (Contract `price-list` v1.1) statt aus SQL — DB-agnostisch,
keine V1-Codespalten. **Zweisprachig**, wenn der Datensatz es ist.

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

## Zweisprachig, ohne Fallunterscheidung in der Vorlage

Eine Preisliste geht an einen deutschen und an einen ausländischen Kunden.
calServer führt dafür je Preiskategorie und je Katalogartikel einen **zweiten
Namen**; welche Sprache das ist, entscheidet eine Einstellung des Mandanten.

**Die Vorlage entscheidet nichts davon.** Der Datensatz-Builder löst die
angeforderte Fassung auf, bevor er den Datensatz herausgibt:

| Fassung (`list.language.mode`) | `name` | `name_secondary` |
|---|---|---|
| `primary` | der gepflegte Name | `null` |
| `secondary` | der Name in der Zweitsprache (fehlt er: der gepflegte) | `null` |
| `both` | der gepflegte Name | der Name in der Zweitsprache, sonst `null` |

Damit folgt **jede** Vorlage der Sprachwahl, die nur `name` liest — auch eine
selbst gebaute aus der Zeit vor 1.1. Die mitgelieferten Subreports drucken
zusätzlich `name_secondary` als eingerückte zweite Zeile; ist das Feld leer,
fällt die Zeile weg (`isRemoveLineWhenBlank`) und das Layout ist Punkt für
Punkt dasselbe wie zuvor. Der Kopf nennt die Fassung („Sprache: Deutsch /
English"), sobald sie nicht die erste ist — sonst sieht man einem Blatt auf dem
Schreibtisch nicht an, welche Liste man in der Hand hält.

Eine Fallunterscheidung in JRXML wäre der teuerste Ort dafür: drei Fassungen in
einer Vorlage sind drei Vorlagen in einer, und jede Änderung müsste sie alle
treffen.

## Contract `price-list` (v1.1)

Dataset-Builder: Laravel `PriceListReportDataBuilder`; derselbe Aufbau, den die
Preislisten-Seite liest (`PriceListService`). Datensatz zum Vorlagenbau:
`GET /api/v2/price-list/reports/dataset`.

Der Umschlag trägt `meta` (Contract, Schema-Version, Erzeugungszeit, Locale) und
`list` mit `group`, `date`, `currency`, `language`, `derivation`, `surcharges[]`,
`calibration[]` (je Kategorie `number`, `name`, `name_secondary`, `depth`,
`amount`, `derived`, `inherited_from`, `exceptions[]`, `scales[]`), `services[]`,
`articles[]` und `counts`.

`list.language` trägt `mode` (`primary` / `secondary` / `both`), `primary`,
`primary_label`, `secondary` und `secondary_label`. `secondary` ist `null`,
wenn der Mandant nur eine Sprache führt — dann ist `mode` immer `primary`.

**Neu in 1.1** (additiv, 1.0-Vorlagen laufen unverändert weiter):
`list.language` und `name_secondary` an jeder benannten Zeile.

Zwei Feinheiten, die man beim Lesen des Datensatzes leicht übersieht:

- **Eine Kategorie ohne Betrag ist eine Überschrift, keine Lücke.** Sie bündelt
  ihre Untergruppen. Die Vorlage druckt dort nichts, nicht „0,00".
- **`derived` heißt abgeleitet, nicht geschätzt.** Der Betrag entsteht aus der
  Kondition der Preisgruppe auf dem Listenpreis; er ist so verbindlich wie ein
  eingetragener.
- **Gerätetypen tragen keinen Zweitnamen.** „Fluke 87V" heißt in jeder Sprache
  so; die Typausnahmen bleiben deshalb einsprachig, auch in der Fassung `both`.

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
unter ihrer Kategorie.

Für 1.1 kam ein zweiter Lauf dazu: derselbe Datensatz einmal mit und einmal
ohne Zweitnamen. **Ohne** sind Inhalt und Position jedes Textelements
identisch mit der Ausgabe der 1.0-Vorlage — die zweite Zeile kostet eine
einsprachige Liste also keinen Millimeter. Der mitgelieferte
`sample-data.json` steht bewusst auf `mode: both` und lässt zwei Zeilen
unübersetzt (`Klimaschrank / Ofen`, `Express-Bearbeitung`), damit beide Fälle
in der Vorschau sichtbar sind.

Die pixelgenaue Abnahme des Layouts (report-runner) bleibt wie gehabt
maßgeblich.
