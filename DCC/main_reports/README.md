# 🧾 Digital Calibration Certificate (DCC)

Der Ordner enthält einen eigenständigen DCC-Report (`dcc-sample.jrxml`) inklusive
Subreports (`DCC-Standard.jrxml`, `DCC-Results.jrxml`). Er baut auf den gleichen
Daten wie der DAkkS-Sample-Report auf, verwendet aber eigene Namen/IDs und kann
parallel deployed werden.

## Inhalte
- **Hauptreport:** `DCC/main_reports/dcc-sample.jrxml`
- **Unterberichte:** `DCC/subreports/DCC-Standard.jrxml`, `DCC/subreports/DCC-Results.jrxml`
- **Schema & Beispiel:** `schema/dcc-certificate.xsd`, `sample-data/dcc-sample.json`
- **XML-Writer:** `scripts/dcc_xml_writer.py` erzeugt ein DCC-XML aus denselben
  Daten, die auch der JasperReport nutzt (MeasurementDetails=22 als Standard).

## Nutzung im calServer
1. Lege ein separates Report-Verzeichnis für den DCC an (z. B. `/calserver/reports/DCC`).
2. Lade `dcc-sample.jrxml` als Hauptreport hoch und setze `Reportpath` auf das
   neue Verzeichnis.
3. Hinterlege als Unterberichte `DCC-Standard.jasper` und `DCC-Results.jasper`
   im Subfolder `subreports` deines DCC-Pfades.
4. `MeasurementDetails` ist im DCC standardmäßig auf **22** gesetzt (DCC-Layout
   für die Messergebnisse). Andere Layouts (1/2/3/4) sind weiterhin verfügbar.

## XML + PDF im Paar
1. Exportiere/baue den PDF-Report wie gewohnt (z. B. via Workflow oder calServer-UI).
2. Rufe den XML-Writer auf derselben Datenbasis auf:
   ```bash
   python scripts/dcc_xml_writer.py \
     --input DCC/main_reports/sample-data/dcc-sample.json \
     --output build/dcc-sample.xml \
     --measurement-option 22 \
     --report-id 517d5a02-281b-4564-95c0-bdaf3cab5604 \
     --validate
   ```
   - `--input` erwartet JSON mit den Feldern aus der Hauptabfrage und dem
     `results`-Subreport.
   - `--validate` prüft das Ergebnis gegen `schema/dcc-certificate.xsd`
     (benötigt das Python-Paket `xmlschema`).
   - `--measurement-option` bleibt ohne Angabe automatisch bei **22**.
3. Lege PDF und XML gemeinsam im Ablageverzeichnis ab (gleicher Basisname
   empfohlen), um das digitale Zertifikat maschinenlesbar verfügbar zu machen.

## Hinweise
- Die DAkkS-Dateien bleiben unangetastet; der DCC nutzt eigene Namen, UUIDs und
  Pfade.
- Die Beispielwerte in `sample-data/dcc-sample.json` spiegeln das SQL des
  Hauptreports wider und können direkt als Fixture verwendet werden.
- Für automatisierten Upload liegt unter `scripts/` ein eigenes
  `dcc_upload_sample.bat` bereit.
