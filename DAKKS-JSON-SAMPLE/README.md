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
