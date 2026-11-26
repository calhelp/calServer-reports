# DAKKS-JSON-SAMPLE — exakter V1-DAkkS-Kalibrierschein mit JSON-Datenquelle

Dieses Bundle ist die **byte-genaue Kopie des akkreditierten V1-Originals**
[`DAKKS-SAMPLE`](../DAKKS-SAMPLE/) — gleicher Aufbau, gleiche Bänder, gleiche
Ausdrücke, **alle 52 V1-Parameter unverändert** — nur die Datenquelle ist
getauscht: statt eingebettetem SQL über JDBC füllt der report-runner die
Vorlage aus dem calServer-Report-Data-Contract `calibration-certificate`
(**v1.2**, JSON).

Die Kopie ist **per Konstruktion exakt**: die drei JRXMLs werden nicht von
Hand gepflegt, sondern mit
[`scripts/build_dakks_json_clone.py`](../scripts/build_dakks_json_clone.py)
mechanisch aus dem V1-Original abgeleitet. Erlaubte Unterschiede sind genau:

1. `<queryString>` entfernt (kein SQL),
2. jedes `<field>` erhält eine `<fieldDescription>` mit seinem JSON-Pfad
   (Feldname und -klasse bleiben — alle `$F{…}`-Ausdrücke sind unverändert),
3. die zwei Subreport-Aufrufe lesen `subDataSource("standards")` bzw.
   `subDataSource("results")` statt `$P{REPORT_CONNECTION}`,
4. Report-Name + Studio-Default-Adapter (Vorschau-Komfort),
5. `Results`: Feld `row_num` als `java.lang.Integer` statt des abstrakten
   `java.lang.Number` (JsonDataSource-Anforderung; im Layout ungenutzt).
6. Freigabezeile (ab Contract-Version 1.16): Name und Datum unter „Freigabe
   des Kalibrierscheins durch" kommen aus dem Block `release` und tragen die
   Stempelkennungen `stamp.release_name` / `stamp.release_date`, dazu eine
   unsichtbare Box `stamp.release_signature` für die Unterschrift. Siehe
   [Freigabezeile](#freigabezeile-ab-contract-version-116).

`python3 scripts/build_dakks_json_clone.py --check` weist die Ableitung
byte-genau nach. **Nie von Hand editieren** — Mapping im Skript ändern und
mit `--write` neu generieren.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/dakks-json-sample.jrxml` | Hauptbericht (1:1 aus `DAKKS-SAMPLE/main_reports/dakks-sample.jrxml`) |
| `subreports/Standard.jrxml` | Verwendete Normale (1:1 aus V1 `Standard.jrxml`; `subDataSource("standards")`) |
| `subreports/Results.jrxml` | Messergebnisse mit allen V1-Layoutvarianten (`MeasurementDetails` 1/2/21/22/3/4/5/51/52, `ModernResultsHeader`; `subDataSource("results")`) |
| `subreports/TextBlocks.jrxml` | Text und Bilder eines Abschnitts aus den Textbausteinen (1:1 aus `DAKKS-SAMPLE`; `JsonDataSource` über `Text_blocks_*`, ab Contract-Version 1.15) |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `calibration-certificate` **v1.2**) |
| `main_reports/dakks-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Adapter auf `sample-data.json` (turnkey-Vorschau) |
| `parameters.json` | **Kompletter Katalog aller 52 V1-Parameter** (Labels, Beschreibung, Defaults, Gruppen) für die calServer-Berichtsvariablen-UI |

## Parameter

Alle 52 Parameter des V1-Originals sind deklariert und wirken wie in V1 —
maschinenlesbar beschrieben in [`parameters.json`](../DAKKS-JSON-SAMPLE/parameters.json):
`Sprache`, `MarkNumber1/2`, `PageNumberPosition`, `MeasurementDetails`,
`ModernResultsHeader`, alle `ShowGroup1*`-Abschnittsschalter samt Overrides
und sämtliche Textbausteine (`Cert_description`, `Uncertainty_description`, …).
Gepflegt werden sie wie in V1 als **Berichtsvariablen**; calServer reicht
jede Variable unter `Ucfirst(name)` **und** ihrem Rohnamen durch (nötig für
die kleingeschriebenen V1-Parameter `environmental_conditions`/`sign_names`).
Automatisch versorgt werden `P_CTAG`, `Sprache` (aus der Datensatz-Locale)
und `QR_Code_Value` (calServer-Kurz-URL `/inventory/qrcode/{id}`,
per gleichnamiger Variable übersteuerbar).

`ShowCalibrationMark` steuert den Kalibrierzeichen-Kasten: `Y` druckt Kasten,
Beschriftung und Werte, `V` nur die drei Werte (laufende Nummer, D-K-Nummer,
Kalibriermonat) für Briefpapier, das das komplette Kalibrierzeichen mit leerem
Kasten trägt, `N` blendet alles auf allen Seiten aus, auch auf dem Deckblatt.
Die Flächen stehen im README von `DAKKS-SAMPLE`, Abschnitt 4.3.
`MeasurementDetails` ist im Manifest
eine Auswahlliste; jede Variante bringt dort eine Kurzbeschreibung und eine
Beispieltabelle (`options[].description`, `options[].preview`) mit, die calServer
an der Variablenauswahl als Vorschau zeigt.

Neu gegenüber V1 ist `PageNumberShowTotal`: `Y` (Standard) druckt
„Seite x von y / Page x of y", `N` nur „Seite x / Page x" wie im früheren
Layout. Links platzierte Seitenzahlen fluchten mit dem Fließtext.

**Datenseitige Variablen** (füllen den JSON-Datensatz, Contract v1.2):

| Variable | Wirkung |
|----------|---------|
| `cert_field` | Altspaltenname des Zertifikatsnummern-Felds → `calibration.certificate_display` + Zertifikatsspalte der Normale |
| `procedure_field` | Altspaltenname des Prozedur-Referenzfelds → füllt den `procedure`-Block aus der Prozedur-Tabelle |
| `environmental_conditions` | Ressourcen-Name → `environment.working_hours` („Temp\|Feuchte") |
| `reportVariantCode` | Ressourcen-Name → `report_variant.template` („1"/„0", DIM-Layoutvariante) |

## Datenanbindung

- **Kein** `<queryString>`, **keine** `REPORT_CONNECTION` — der Runner füllt
  mit einer `JsonDataSource` (`dataSourceType=json`, `dataJson`); die
  Subreports iterieren `standards[]`/`results[]` per `subDataSource`.
- calServer erkennt das SQL-lose Bundle beim Generieren **automatisch** und
  baut den Datensatz (`CalibrationReportDataBuilder`, Contract v1.2) — keine
  `data_contract`-Variable nötig (Override möglich).
- **Backend-Mindestversion:** Contract **v1.2**. Gegen ein v1.1-Backend
  fehlen u. a. `calibration.place` und die Normale-Zellen → „null"-Drucke.

## DAkkS-Schein als DCC (PTB 3.3.0) ausgeben

Derselbe Contract, der die PDF-Vorlage füllt, kann **zusätzlich** als offizielles
**Digital Calibration Certificate** nach PTB-Standard ausgegeben werden
(https://wiki.dcc.ptb.de/) — der DAkkS-Schein wird so „als DCC wählbar",
**ohne zweite Datenquelle**.

```bash
python3 scripts/dcc330_writer.py \
  --input DAKKS-JSON-SAMPLE/main_reports/sample-data.json \
  --output build/dakks-dcc-3.3.0.xml --validate
```

- **Eingang:** exakt der Contract `calibration-certificate` **v1.2** (dieselbe
  `sample-data.json`, die den Report speist).
- **Ausgang:** `dcc:digitalCalibrationCertificate` `schemaVersion="3.3.0"`,
  validiert gegen [`DCC/main_reports/schema/dcc-v3.3.0.xsd`](../DCC/main_reports/schema/dcc-v3.3.0.xsd)
  (importiert D-SI- und XML-DSig-Schema).
- **Messwerte in D-SI:** je Ergebniszeile werden Nennwert, Messwert (mit
  erweiterter Messunsicherheit, k=2 / 95 %) und die Toleranzgrenzen als
  `si:real` (Wert + `si:unit` in Backslash-Notation, z. B. `\volt`, `\ohm`)
  ausgegeben. Wert/Präfix/Einheit (`fixq`/`fixq_p`/`fixq_u` …) werden dabei in
  die SI-Basiseinheit skaliert, sodass Wert und Unsicherheit dieselbe Einheit
  tragen.
- **Mapping v1.2 → DCC 3.3.0:** Labor/Kunde/Gerät/Unterzeichner →
  `administrativeData` (coreData, items, calibrationLaboratory, respPersons,
  customer); Akkreditierungskennzeichen → `statements`; `results[]` →
  `measurementResults`.
- **Beispielausgabe (eingecheckt):**
  [`main_reports/sample-dcc-3.3.0.xml`](main_reports/sample-dcc-3.3.0.xml).
- **Guardrail:** [`scripts/check_dcc330.py`](../scripts/check_dcc330.py) prüft die
  D-SI-Helfer, regeneriert das Sample deterministisch (Parität) und validiert
  es gegen das XSD (überspringt die XSD-Prüfung offline anstandslos). Läuft im
  CI-Workflow `validate-reports.yml`.

> Die PDF (Jasper) und das DCC-XML bilden das digitale Zertifikat als Paar;
> `dcc330_writer.py` ist der PTB-3.3.0-Nachfolger des einfacheren
> `dcc_xml_writer.py` (calhelp-Format).

## Ergebnistabelle: welche Felder wo landen

Die Messwertspalten hängen an zwei gleichwertigen Spaltenpaaren des Contracts,
und die Layout-Variante entscheidet nur noch, welches sie **zuerst** liest:

| Spalte des Scheins | primär | Rückfall |
|--------------------|--------|----------|
| Sollwert (Varianten `1`, `2`, `3`, `4`) | `results[].fixq` (+`_p`/`_u`) | `sys_actual` |
| Sollwert (Varianten `21`, `22`) | `results[].sys_actual` (+`_p`/`_u`) | `fixq` |
| Messwert (Varianten `1`, `2`, `3`, `4`) | `results[].varq` (+`_p`/`_u`) | `uut_ind` |
| Messwert (Varianten `21`, `22`) | `results[].uut_ind` (+`_p`/`_u`) | `varq` |
| untere/obere Spezifikation (`1`, `2`, `22`) | `results[].lower_limit` / `upper_limit` (+`_p`/`_u`) | – |
| erweiterte Messunsicherheit (`1`, `2`, `21`, `22`) | `results[].exp_uncert` (+`_p`/`_u`) | – |
| erweiterte Messunsicherheit (`3`) | `results[].exp_uncert_iso_e`, sonst `exp_uncert` | – |
| erweiterte Messunsicherheit (`4`) | `results[].exp_uncert_iso_p`, sonst `exp_uncert` | – |
| Messbedingungen | `results[].test_desc` | – |
| % rel. Abweichung | `results[].rel_err` | – |
| % Tol (`1`, `2`, `22`, `3`, `4`) | `results[].tol_err` | – |
| Test (`5`, `51`, `52`) | `results[].test_step` (Hauptnummer, vierstellig) | – |
| Bereich (`5`, `51`, `52`) | `results[].uut_range` (+`_p`/`_u`) | – |
| Richtiger Wert / Anzeige (`5`, `51`, `52`) | `results[].sys_actual` / `uut_ind` (+`_p`/`_u`) | `fixq` / `varq` |
| Messbedingung, zweite Zeile (`5`, `51`, `52`) | `results[].condition2` | `@` + `mod1` (+`_p`/`_u`) |
| Toleranz (`5`, `51`, `52`) | `results[].tol_pos` / `tol_neg` (+`_p`/`_u`) | `tol`, sonst halbe Spanne der Grenzen |
| Abweichung (`5`, `51`, `52`) | `results[].error` (+`_p`/`_u`) | Anzeige − richtiger Wert |
| % Tol. mit Pass/Fail (`52` ohne), Hinweise (`5`, `51`, `52`) | `results[].tol_err`, `pass_fail`, `accred_mark` (ersatzweise `accred`) | – |
| erw. MU im technischen Format (`52`) | `results[].exp_uncert` (+`_p`/`_u`), zwei signifikante Stellen, SI-Vorsatz | Darstellung wie `5`, wenn der Wert keine Zahl ist |

Die Varianten `5`, `51` und `52` bilden das MET/CAL-Layout nach (Test, Bereich,
Toleranz, Abweichung). Die Schlüssel `test_step`, `uut_range`, `mod1`,
`condition2`, `error`, `tol`, `tol_pos` und `tol_neg` liefert der Contract ab
**v1.11**; gegen ein älteres Backend bleiben Test und Bereich leer, Toleranz
und Abweichung werden aus Grenzen und Anzeige berechnet. Details in
[`DAKKS-SAMPLE/README.md`](../DAKKS-SAMPLE/README.md), Abschnitt 5.2.

Die `_p`/`_u`-Geschwister sind keine Zierde: die Varianten `2`, `21`, `22`, `3`
und `4` drucken Wert, SI-Vorsatz und Einheit als eine Angabe (`9.9 mg`).
Variante `1` ist die Basisdarstellung und druckt bewusst nur den Rohwert.

`sys_actual`/`uut_ind` füllt die calServer-Messwertaufnahme nur für numerische
Prüfschritte mit gesetztem `tol_ref`; MET/CAL-Importe liefern beide Paare. Ohne
den Rückfall blieb die Ergebnistabelle deshalb bei ungesetztem
`MeasurementDetails` leer, obwohl die Zeilen die Werte trugen. **Sind beide
Paare gefüllt, druckt jede Variante unverändert das Paar, das sie schon immer
gedruckt hat.**

`test_desc` ist die Bezeichnung des Prüfschritts aus der Prozedur — sprechende
Messbedingungen entstehen dort, nicht im Bericht.

Zu lange Inhalte brechen um, statt verloren zu gehen: die Zellen des
Detailbands wachsen mit ihrem Text, alle Zellen einer Zeile bleiben gleich hoch
und der Text sitzt oben. Das betraf vor allem `test_desc` (70 px breit in
Variante `1`), Werte mit ausgeschriebener Einheit (`10 kΩ`) und dreistellige
`% Tol`. Kurze Zeilen behalten ihre bisherige Höhe von 14 px.

## Prozedur und Umgebungsbedingungen: gepflegt wird an der Quelle

Vier Abschnitte des Scheins kommen aus der **Prozedur**, nicht aus Parametern.
Damit der Datensatz sie überhaupt trägt, muss die Berichtsvariable
`procedure_field` auf das Kalibrierfeld zeigen, das den Prozedurnamen führt
(V1-Original: `C2320`) — einzutragen ist der **Feldname**, nicht der Name einer
Prozedur. Sie steht mit dieser Erklärung als `role: data` im
[`parameters.json`](../DAKKS-JSON-SAMPLE/parameters.json), calServer bietet sie
beim Hochladen des Pakets also von sich aus an.

Ohne sie bleibt der `procedure`-Block leer und der Schein fällt auf seine
Textbausteine zurück — je Bericht derselbe Text, für jedes Gerät, ohne dass
irgendwo ein Fehler erscheint:

| Abschnitt (Bandbeschriftung) | Feld der Prozedur | Fallback |
|------------------------------|-------------------|----------|
| KALIBRIERGEGENSTAND | `procedure.calibration_item` | Parameter `Asset_description` |
| KALIBRIERVERFAHREN | `procedure.calibration_method` | `Calibration_document`, sonst „Verfahrensanweisung nicht angegeben" |
| VERFAHRENSANWEISUNG | `procedure.description` | `Calibration_procedure_1`, sonst „Kalibrierverfahren nicht angegeben" |
| MESSBEDINGUNGEN | `procedure.measurement_conditions` | „im permanenten Labor" |

Die Feldzuordnung ist stimmig — die **Fallback-Parameter** sind es nicht: Unter
der Überschrift KALIBRIERVERFAHREN springt `Calibration_document` ein und
schreibt „Verfahrensanweisung nicht angegeben", unter VERFAHRENSANWEISUNG
`Calibration_procedure_1` mit „Kalibrierverfahren nicht angegeben". Wer die
Parameternamen als Wegweiser nimmt, füllt also den falschen. Das kommt
unverändert aus dem akkreditierten V1-Original und wird hier **nicht**
stillschweigend gerichtet: Die JSON-Kopie ist mechanisch abgeleitet und
byte-genau nachweisbar. Was sich gefahrlos richten lässt, sind die
Beschreibungen im Parameter-Katalog — und die sagen es jetzt.

`procedure.standards` und `procedure.scope` sind als Variablen deklariert
(`procedure_standards_var`, `procedure_scope_var`), aber **an kein Textfeld
gebunden** — der Schein druckt sie nicht. Eine frühere Fassung dieser Tabelle
führte „Geltungsbereich" als eigenen Abschnitt; den gibt es im Layout nicht.

### Diese vier Felder tragen Auszeichnung — und zwar eine begrenzte

Alle vier Textfelder stehen im Layout auf `markup="html"`. JasperReports
schickt ihren Inhalt damit durch seinen Markup-Prozessor
(`JEditorPaneHtmlMarkupProcessor`), und der ist **kein Browser**: Er parst mit
Swings `HTMLEditorKit` und übernimmt aus dem Ergebnis ausschliesslich
Zeichenlauf-Attribute.

| Übernommen | Verworfen |
|------------|-----------|
| `b`/`strong`, `i`/`em`, `u`, `s`/`strike`/`del` | Tabellen, Bilder, alles Eingebettete |
| `sub`, `sup` | `text-align`, Einzüge, `class`, alle CSS-Layoutregeln |
| `br`, `p` (Zeilen- und Absatzumbruch) | `div` und Unbekanntes (Inhalt bleibt, Hülle fällt) |
| `ul`, `ol`, `li` (Aufzählungszeichen, Nummerierung inkl. `type`/`start`) | — |
| `font`/`span` mit Farbe, Grösse, Schriftfamilie; `a href` | — |

Die letzte Zeile ist der Sonderfall: Der Prozessor kann sie, calServer
**liefert sie trotzdem nicht**. Eine Schriftfamilie aus dem Markup ersetzt die
Berichtsschrift (DejaVu Sans) durch eine, die im PDF nicht eingebettet ist —
Umlaute und Sonderzeichen fallen dann auf ein Ersatzglyph zurück. Überschriften
bringen über Swings Standard-Stylesheet ihre eigene Schriftgrösse mit, und
Farbe ist auf einem akkreditierten Schein keine Angabe, die aus einem Freitext
kommen sollte. Was calServer schreibt, ist deshalb genau die erste Hälfte der
linken Spalte (`App\Support\ReportHtml` setzt sie durch, der Prozedur-Editor
bietet auch nur sie an).

**Für eigene Datenquellen heisst das zweierlei:** Klartext in diesen Feldern
muss escaped sein — ein „<" verschluckt sonst still den Rest der Zeile („U <
10 V" druckt als „U") —, und ein Zeilenumbruch muss als `<br/>` kommen, weil
`\n` in HTML ein Leerzeichen ist.

**Umgebungsbedingungen** kommen aus einer **Ressource**: `environmental_conditions`
benennt sie, gelesen wird ihr Feld „Umgebungsbedingungen"
(`resource.environment_resources`) → `environment.working_hours`. Das Format ist
ein Text mit `|` als Trenner — links die Temperatur, rechts die Feuchte, jeweils
mit Einheit, z. B. `21,0 ... 23,0 °C|40 ... 60 %`. Jede Hälfte fällt für sich auf
den an der Kalibrierung erfassten Wert zurück (`calibration.custom_fields.C2311`
bzw. `C2312`), wenn sie leer bleibt. So steht der Klimabereich des Labors einmal
an der Ressource statt in jedem Bericht erneut.

## Textbausteine mit Bildern (ab Contract-Version 1.15)

Die Abschnitte Kalibrierverfahren, Messunsicherheiten und Weitere Hinweise
kommen in V2 aus den Textbausteinen der Prüfprozedur. Reiner Text landet wie
bisher als HTML in `Calibration_document` (und `procedure.calibration_method`), `Uncertainty_description` und
`Additional_information`. Enthält ein Baustein des Abschnitts ein Bild, setzt
calServer zusätzlich `Text_blocks_method`, `Text_blocks_uncertainty` oder
`Text_blocks_notes`: eine JSON-Liste aus `{kind: text, html}` und
`{kind: image, image (Base64), width, caption}`. Ist der Parameter gesetzt,
druckt der Subreport `TextBlocks` den Abschnitt statt des Textfelds; leer
bleibt alles wie bisher. Die drei Parameter stehen als `role: system` im
[`parameters.json`](../DAKKS-JSON-SAMPLE/parameters.json), die Berichtsvariablen
bieten sie also nicht zur Eingabe an.

Der Datensatz trägt die Bilder zusätzlich in `text_blocks.{abschnitt}[]` als
Segment mit `kind: image`, `image_width`, `image_mime` und `image_data`
(Base64), für Vorlagen, die den Abschnitt selbst aus dem Datensatz bauen.

Breiten sind 25, 50, 75 und 100 % der Textbreite (535 pt). Ein Bild mit
weniger Pixeln, als die Breite in Punkten hat, druckt kleiner als gewählt;
druckreif ist es ab etwa 150 dpi, für die volle Breite also ab rund 1.100 px.

## Freigabezeile (ab Contract-Version 1.16)

Bis 1.15 druckte die Vorlage unter „Freigabe des Kalibrierscheins durch" das
Zusatzfeld `C2327` und als Datum den Tag des Erzeugens. Das passte nicht, wenn
das Feld anders belegt ist (bei einem Kunden stand dort der Kalibrierbereich),
und im Freigabevorgang trug der Schein den Tag des Antrags statt den der
Freigabe. Ab 1.16 liest die Zeile den Block `release` des Datensatzes:

| Feld | JSON-Pfad | Druck |
|------|-----------|-------|
| `release_state` | `release.state` | `approved`, `pending` oder `none` |
| `release_approver` | `release.approved_by_name` | Name unter „Freigabe … durch" |
| `release_date` | `release.issue_date` | Datum links (`Y-m-d`, gedruckt als `dd.MM.yyyy`) |

Was in `release` steht, entscheidet calServer: freigegeben heißt die Person,
die entschieden hat (Vorname Nachname aus dem Benutzerkonto), mit dem Datum
der Entscheidung; offen heißt beides leer; ohne Freigabevorgang das Feld, das
die Berichtsvariable `approver_field` nennt (Vorgabe `C2327`, `-` heißt kein
Feld), mit dem Tag des Erzeugens. Fehlt der Block (älteres calServer), druckt
die Vorlage genau wie V1.

Die beiden Felder und die Box `stamp.release_signature` darüber tragen eine
Stempelkennung im `key`. Der report-runner meldet, wo sie nach dem Umbruch
gelandet sind, und calServer stempelt bei der Freigabe-Entscheidung Name,
Datum und Unterschrift auf den eingefrorenen Schein, ohne ihn neu zu
erzeugen. Eine eigene Vorlage bekommt dasselbe Verhalten, wenn sie dieselben
Kennungen setzt.

## Konformitätsspalte: welche Werte die Vorlage liest

Die Spalte „Konformität" hängt an **einem** Feld: `results[].pass_fail`.
`Results.jrxml` vergleicht den Wert (case-insensitiv, getrimmt) gegen genau
vier Schreibweisen — MET/TEAMs `Points.cPointPassFailStatus`:

| `pass_fail` | Druck | Bedeutung laut Legende |
|-------------|-------|------------------------|
| `Pass` | `i.T.` | in Toleranz |
| `Fail` | `!` | außerhalb der Spezifikation |
| `Pass Indeterminate` | `?` | innerhalb, aber mit Messunsicherheit keine Konformitätsaussage möglich |
| `Fail Indeterminate` | `!?` | außerhalb, aber keine negative Konformitätsaussage möglich |

Alles andere — auch leer, auch `P`/`F`, auch `Conditional` — druckt eine leere
Zelle.

Welche Zeichen vorkommen, hängt von der Entscheidungsregel der Kalibrierung ab:
Unter den beiden binären Regeln entscheidet calServer nur `Pass` oder `Fail`,
`?` und `!?` kommen dann nicht vor. Die passende Legende setzt calServer in
`Conformity_description_1` bis `_3`, der Datensatz trägt die Regel im Block
`decision_rule` (ab Contract-Version 1.9).

Das `*` daneben ist eine eigene Aussage: „nicht im Akkreditierungsumfang“
(Legende `Conformity_description_3`). Gebunden ist das Druckfeld
`results[].accred_mark` (ab Contract-Version 1.14): `*` kennzeichnet die
Zeile, jeder andere Wert, auch der leere, druckt kein Zeichen. calServer
rechnet es aus `accred` und dessen Herkunft `accred_source`, weil dasselbe
Feld zwei Lesarten trägt: die eigene Erfassung schreibt `1` für „im Umfang“,
MET/CAL setzt das Flag `ACCRED` für die gekennzeichnete Zeile.

Fehlt `accred_mark` im Datensatz (älterer Contract), fällt die Vorlage auf
`results[].accred` in der MET/CAL-Lesart zurück: `1`/`ja`/`true` und
`2`…`32767` = Flag gesetzt (`*`), `0`/`nein`/`false` = Flag nicht gesetzt
(kein Zeichen), leer = keine Aussage erfasst (kein Zeichen). Ein Datensatz,
der das Feld mitführt, muss es deshalb in **jeder** Zeile mitführen, auch
leer: ein fehlender Schlüssel ist nicht „kein Zeichen“, sondern „alte
Lesart“. In der Variante `MeasurementDetails=1` kommt ein zweites Gatter dazu:
gedruckt wird nur, wenn `fsc` „EVAL" oder „PICE" enthält.

Die Felder `conformity`, `test_status` und `guardband_meth` des Contracts sind
**nicht** gebunden: das Bundle ist die byte-genaue Kopie des V1-Originals, und
das kannte sie nicht. calServer normalisiert deshalb backendseitig nach
`pass_fail` (`CalibrationReportDataBuilder`), bevor der Datensatz hier ankommt —
eine Zeile, deren Entscheidung nur in `test_status` steht (MET/TRACK, alte
V1-Laufzeit), erscheint dadurch mit Konformität statt mit leerer Spalte.

## ⚠️ Leeres/weißes Blatt?

Das Bundle ist datenquellenlos. Ohne JSON-Datenquelle (Studio-Preview ohne
Adapter, oder Backend älter als die Auto-Erkennung) bleibt die Seite leer.
Studio: mitgelieferten Adapter wählen („Open → Preview" nutzt ihn über die
`defadapter`-Property automatisch). Live: aktuelles calServer V2 genügt.

## Bekannte, dokumentierte Abweichungen zum V1-SQL

- Zustand Ein-/Ausgang: die V2-Synchronisation typisiert die Altspalte
  numerisch; der Datensatz liest den Rohwert (`calibration.condition`).
- `--`-Defaults der Altspalten für Temperatur/Feuchte/Auftragsnummer sind
  datenseitig nicht reproduzierbar (leer statt „--"; nur bei leeren Daten
  sichtbar, Ausdrücke sind guarded).
- Zertifikatsnummern-Fallback ohne `cert_field`-Variable ist die kanonische
  `certificate_number` (V1-Yii-Default war eine feste Altspalte).
- Das `SELECT DISTINCT` der Normale-Abfrage (Dedupe) entfällt.

> **Status:** Referenzvorlage der V2-Strategie (ADR-009). JasperReports
> **6.20.6** bleibt verbindlich (siehe `robots.md`).
