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

`python3 scripts/build_dakks_json_clone.py --check` weist die Ableitung
byte-genau nach. **Nie von Hand editieren** — Mapping im Skript ändern und
mit `--write` neu generieren.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/dakks-json-sample.jrxml` | Hauptbericht (1:1 aus `DAKKS-SAMPLE/main_reports/dakks-sample.jrxml`) |
| `subreports/Standard.jrxml` | Verwendete Normale (1:1 aus V1 `Standard.jrxml`; `subDataSource("standards")`) |
| `subreports/Results.jrxml` | Messergebnisse mit allen V1-Layoutvarianten (`MeasurementDetails` 1/2/21/22/3/4, `ModernResultsHeader`; `subDataSource("results")`) |
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

## Prozedur und Umgebungsbedingungen: gepflegt wird an der Quelle

Vier Abschnitte des Scheins kommen aus der **Prozedur**, nicht aus Parametern.
Damit der Datensatz sie überhaupt trägt, muss die Berichtsvariable
`procedure_field` auf das Kalibrierfeld zeigen, das den Prozedurnamen führt
(V1-Original: `C2320`). Ohne sie bleibt der `procedure`-Block leer und der
Schein fällt auf seine Textbausteine zurück:

| Abschnitt | Feld der Prozedur | Fallback-Parameter |
|-----------|-------------------|--------------------|
| Kalibrierverfahren | `procedure.description` | `Calibration_procedure_1` |
| Verfahrensanweisung | `procedure.calibration_method` | `Calibration_document` |
| Messbedingungen | `procedure.measurement_conditions` | „im permanenten Labor" |
| Geltungsbereich | `procedure.scope` | `calibration_item` → `standards` → `Calibration_procedure_2` |

**Umgebungsbedingungen** kommen aus einer **Ressource**: `environmental_conditions`
benennt sie, gelesen wird ihr Feld „Umgebungsbedingungen"
(`resource.environment_resources`) → `environment.working_hours`. Das Format ist
ein Text mit `|` als Trenner — links die Temperatur, rechts die Feuchte, jeweils
mit Einheit, z. B. `21,0 ... 23,0 °C|40 ... 60 %`. Jede Hälfte fällt für sich auf
den an der Kalibrierung erfassten Wert zurück (`calibration.custom_fields.C2311`
bzw. `C2312`), wenn sie leer bleibt. So steht der Klimabereich des Labors einmal
an der Ressource statt in jedem Bericht erneut.

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
Zelle. In der Variante `MeasurementDetails=1` kommt ein zweites Gatter dazu:
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
