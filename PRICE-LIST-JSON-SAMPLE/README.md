# PRICE-LIST-JSON-SAMPLE — Preisliste (V2)

Die **Preisliste**, wie ein Labor sie seinem Kunden übergibt: Kategoriebaum mit
den geltenden Kalibrierpreisen (Typausnahmen eingerückt), Zusatzleistungen mit
Mengenstaffel, Standardartikel und die Konditions-Fußnoten. Gefüllt aus einem
**JSON-Datensatz** (Contract `price-list` v1.2) statt aus SQL — DB-agnostisch,
keine V1-Codespalten. **Zweisprachig**, wenn der Datensatz es ist, und
**mehrspaltig**, wenn Kalibrierarten gepflegt sind.

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
| `subreports/price-list-categories.jrxml` | Kategoriebaum aus `list.calibration`; Obergruppen fett, Untergruppen eingerückt, Grundpreis plus bis zu drei Kalibrierart-Spalten |
| `subreports/price-list-exceptions.jrxml` | Typausnahmen einer Kategorie (`exceptions`) — die einzige zweistufige Stelle des Bündels |
| `subreports/price-list-services.jrxml` | Zusatzleistungen aus `list.services` |
| `subreports/price-list-scales.jrxml` | Mengenstaffel einer Zeile (`scales`), als Kondition unter dem Betrag |
| `subreports/price-list-articles.jrxml` | Standardartikel aus `list.articles` |
| `subreports/price-list-surcharges.jrxml` | Konditions-Fußnoten aus `list.surcharges` |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `price-list` v1.2) |
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

## Kalibrierarten sind Spalten, nicht Zeilen

Die Kalibrierart (ISO, DAkkS, …) ist in calServer normalerweise ein **Zuschlag**
— „DAkkS +30 %" — und steht dann als Fußnote unter „Konditionen". Das reicht,
solange der Zuschlag gleichmäßig ist.

Wer ihn nicht gleichmäßig hat, pflegt je Kalibrierart eine eigene Preiszeile
(Kategorie PK100.01: ISO 89,00, DAkkS 189,00). Die Preisfindung nimmt diese
Zeile immer vor dem Zuschlag; die Liste zeigte sie bis 1.2 gar nicht, und das
Kundendokument nannte damit einen anderen Betrag als die Rechnung.

Seit 1.2 druckt der Abschnitt Kalibrierpreise deshalb bis zu **drei zusätzliche
Betragsspalten**, eine je gepflegter Kalibrierart:

| Datensatz | Rolle |
|---|---|
| `list.complexities[]` | alle gepflegten Kalibrierarten mit `value` und `label`, in Reihenfolge des Feldmanagements |
| `list.complexity_1_label` … `_3_label` | die drei druckbaren Überschriften; **leer = Spalte gibt es nicht** und die Vorlage blendet sie weg |
| `amount_1` … `amount_3` an jeder Kategorie- und Ausnahmezeile | die Beträge, positionsgleich zu den Überschriften |
| `amounts` an denselben Zeilen | dieselben Beträge nach Kalibrierart benannt, mit `derived` und `inherited_from` |
| `list.complexities_truncated` | mehr als drei gepflegt: die Vorlage schreibt es unter die Konditionen |

**Warum beides, Position und Name.** Ein JRXML-Feldpfad steht zur Entwurfszeit
fest; der Schlüssel „DAkkS" entsteht erst beim Kunden. Die mitgelieferte Vorlage
liest deshalb die Positionen. Eine selbst gebaute Vorlage für **eine**
Installation kennt ihre Kalibrierarten und liest bequemer `amounts.DAkkS.amount`.

**Ohne gepflegte Zeilen ändert sich nichts.** `complexities` ist dann leer, alle
Überschriften sind leer, keine Spalte wird gedruckt — die Liste sieht aus wie vor
1.2, und die Fußnote macht wie gehabt ihre Arbeit.

**Eine leere Spalte zeigt nichts, nicht „0,00".** „Für diese Kalibrierart ist
nichts gepflegt" und „kostet nichts" sind verschiedene Aussagen; auf einem
Dokument, das man aus der Hand gibt, ist die Verwechslung teuer.

**Die Kappung bei drei ist Geometrie, keine Meinung.** JRXML kann Spalten nicht
zur Laufzeit einfügen, und mehr als vier Betragsspalten lassen auf A4 hoch
keinen Platz für Nummer und Bezeichnung. Wer mehr braucht, nimmt den CSV-Export
oder baut eine Querformat-Vorlage über `amounts`. Gekappt wird sichtbar: die
Vorlage schreibt es unter die Konditionen, statt so zu tun, als sei das alles.

## Die Währung steht im Kopf

Seit 1.2 nennt die Spaltenüberschrift die Währung („Betrag (EUR)"), und die
Zeilen des Abschnitts Kalibrierpreise drucken sie nicht mehr einzeln. Vier
Betragsspalten und daneben viermal „EUR" passen nicht auf die Seite, und echte
Laborlisten nennen die Währung ohnehin einmal oben. Die Abschnitte
Zusatzleistungen und Standardartikel haben nur einen Betrag und behalten ihre
Währungsangabe an der Zeile.

## Contract `price-list` (v1.2)

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

**Neu in 1.2** (additiv, 1.1-Vorlagen laufen unverändert weiter):
`list.complexities[]`, `list.complexity_1_label` … `_3_label`,
`list.complexities_truncated` sowie `amounts` und `amount_1` … `amount_3` an
jeder Kategorie-, Ausnahme- und Typzeile. Eine 1.1-Vorlage liest weiter nur
`amount` und druckt den Grundpreis wie bisher.

Eine Änderung ist **nicht** rein additiv und gehört auf den Zettel: `amount`
einer **Typzeile** (`exceptions[]`, `other_type_prices.entries[]`) kann jetzt
`null` sein. Ein Gerätetyp, für den nur eine DAkkS-Zeile gepflegt ist, hat
keinen Grundpreis; bis 1.1 fiel er komplett aus der Liste, jetzt steht er drin
und die Betragsspalte bleibt leer.

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

Für 1.2 kam ein dritter Lauf dazu, jeweils Kompilat **und** Füllung gegen
JasperReports 6.20.6: derselbe Datensatz mit zwei Kalibrierart-Spalten, mit
drei plus gesetztem `complexities_truncated`, und ganz ohne. **Ohne** stehen
Inhalt und Position jedes Textelements des Abschnitts A wieder dort, wo eine
einspaltige Liste sie hat; die Spalten kosten also nichts, solange niemand sie
pflegt. Mit Spalten wurde geprüft, dass die Überschriften vollständig stehen
(„DAkkS-Kalibrierung" passt nur zweizeilig in 64 pt) und dass die Beträge im
selben Raster fluchten wie die Kategorie darüber.

Die pixelgenaue Abnahme des Layouts (report-runner) bleibt wie gehabt
maßgeblich.
