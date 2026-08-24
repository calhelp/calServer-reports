# DELIVERY-JSON-SAMPLE — Lieferschein (V2 / APEX)

V2-Nachbildung des **Lieferscheins** (Phase D), schlanke Variante des
Auftragsbelegs: Kopf + Lieferadresse + Positionen, **ohne Preise und ohne
Steuerstatistik**. Gefüllt aus einem **JSON-Datensatz** (Contract `order-document`
v1.0) statt aus SQL — DB-agnostisch, keine V1-Codespalten.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/delivery-json-sample.jrxml` | Hauptbericht: **Fensterbrief nach DIN 5008 Form B** — Anschriftfeld mit der **Lieferadresse** und Rücksendeangabe, Informationsblock rechts (Liefernummer/Datum/Kunden-Nr./Kontakt), Betreffzeile bei 98,4 mm, Falz- und Lochmarken, Positionstabelle (Pos/Beschreibung/Menge), Empfangs-Unterschriftszeile |
| `subreports/positions-delivery.jrxml` | Positionen; `positions`-Array via `subDataSource("positions")` — nur Pos/Beschreibung/Menge |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `order-document` v1.0, `document.status = "Lieferung"`) |
| `main_reports/delivery-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Contract `order-document` (v1.0)

Gleicher Contract wie `ORDER-JSON-SAMPLE`; der Lieferschein liest nur `document`,
die serverseitig aufgelöste `delivery`-Adressrolle (Fallback → Bestell-Kunde) und
`positions[]` (ohne Preis-/Steuerfelder). Dataset-Builder: Laravel
`OrderDocumentDataBuilder`.

## DIN-Form

Gleiche Geometrie wie der vollständige Auftragsbeleg (`ORDER-JSON-SAMPLE`):
Fensterbrief nach DIN 5008 Form B, Anschriftfeld 20 mm von links und 45 mm von
oben (85 × 45 mm), Informationsblock ab 125 mm, Betreffzeile bei 98,4 mm,
Falz- und Lochmarken bei 105 / 148,5 / 210 mm — abschaltbar über die
Berichtsvariable `show_fold_marks` (Parameter `Show_fold_marks`, Default `1`).
Im Titelband liegt das Anschriftfeld bei `x=37 y=52 241×128`, der
Informationsblock bei `x=297 y=66`, die Betreffzeile bei `y=203`; alle
Bandkoordinaten liegen hinter `topMargin=76`, auf dem Blatt also bei `76 + y`.
Für DIN 676 Form A (Anschriftfeld ab 27 mm) wird `y=52` zu `y=0`.

Im Anschriftfeld steht die **Lieferadresse** samt Ansprechpartner; die
Landzeile druckt nur bei einem Land abweichend vom Absenderland. Die
Rücksendeangabe kommt aus `supplier.sender_line` bzw. der Absenderanschrift,
also aus den `company_*`-Berichtsvariablen — dieselben, die Auftragsbeleg,
Leihschein und Versandschein nutzen.

### Freizone für vorgedrucktes Briefpapier

calServer legt die Bogenvorlage unter den Beleg (Berichtseinstellung
`use_template` = `pdf` oder `html`; Seite 1 der Vorlage auf Belegseite 1,
Seite 2 auf jede Folgeseite). Damit nichts in Kopf, Fuß oder Seitenrand des
Bogens läuft, hält der Beleg feste Grenzen ein:

| Zone | Grenze | Woher |
|---|---|---|
| Satzspiegel links | 20 mm (57 pt) | `leftMargin=20` + Inhalt ab `x=37` |
| Satzspiegel rechts | 195 mm (553 pt) | `rightMargin=42`, `columnWidth=533` |
| Oberkante Folgeseiten | 26,8 mm (76 pt) | `topMargin=76` |
| Oberkante Seite 1 | 45 mm (128 pt), Anschriftfeld | Titelband |
| Unterkante Inhalt | 249 mm (706 pt) | `bottomMargin=136` |

Die 20 mm links sind der Rand, den vorgedrucktes Briefpapier üblicherweise für
seine Kopf- und Fußlinien benutzt — Tabelle und Trennlinien stehen damit bündig
unter dem Bogen statt daneben. Trägt der Bogen die Falz- und Lochmarken schon
selbst, schaltet `show_fold_marks = 0` die eigenen ab. Ein Bogen mit höherem
Kopf oder Fuß braucht andere Ränder: das sind die vier Zahlen im
`<jasperReport>`-Element, sonst nichts.

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
