# STICKER-DAKKS-18MM-JSON-SAMPLE — DAkkS-Aufkleber 18 mm (V2 / APEX)

V2-Nachbildung des **DAkkS-Kalibrieraufklebers 18 mm** (Phase C). Label 51×70 pt
Hochformat (≈ 18×24,7 mm), gefüllt aus einem **JSON-Datensatz** (Contract
`calibration-certificate` v1.1) statt aus SQL — DB-agnostisch, keine V1-Codespalten.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/dakks-aufkleber-18mm-json-sample.jrxml` | Label: Rahmen mit drei Feldern — Kalibrierzeichen, Kalibriermonat, nächster Monat. Kein QR, keine Variablen |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `calibration-certificate` v1.1, minimal) |
| `main_reports/dakks-aufkleber-18mm-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Gestaltung

Der Aufkleber folgt der **DAkkS-Kalibriermarke**: ein geschlossener Rahmen, darin
gestapelte Felder — oben die Registrierdaten der Kalibrierung
(*Kalibrierzeichen*), darunter der Kalibriermonat, unten der nächste Termin.

**Die Gewährleistungsmarke selbst zeichnet die Vorlage bewusst nicht.** Sie ist
ein geschütztes Bild, das ein akkreditiertes Labor von der DAkkS erhält und
selbst auf das Etikett setzt; eine Vorlage darf sie nicht nachbilden. Alles
andere auf dem Etikett sind Kundendaten.

Datumsfelder werden als **Jahr-Monat** gedruckt (`2026-06`), so wie es die
DAkkS-Marke vorsieht — nicht als Tagesdatum. Der Rahmen ist Pflicht: die Marke
darf laut Markenordnung nur innerhalb des Kalibrieretiketts verwendet werden.

**Ohne Akkreditierung** stünde das obere Feld leer. Dann trägt dieselbe Zone die
**Schein-Nr.** (`calibration.certificate_display`) — beschriftet als das, was sie
ist, nie als Marke getarnt. Leere Werte drucken leer, nie `null`.

## Felder

`accreditation.mark_number_1` (+ `mark_number_2`) — dieselben zwei Werte, die der
Kalibrierschein in seinem Kalibrierzeichen-Block druckt: `mark_number_1` die
erste Kennziffer (z. B. Auftragsnummer), `mark_number_2` das mehrzeilige
DAkkS-Kalibrierzeichen (`D-K-\nYYYYY-ZZ-N`). Dazu
`calibration.calibration_date`, `calibration.next_calibration_date` und
`calibration.certificate_display`. Dataset-Builder: Laravel
`CalibrationReportDataBuilder`.

## Systembericht-Platzhalter und Stapeldruck (ab calServer V2)

Dieses Bundle gehört auf den Platzhalter **Kalibrieraufkleber** in
**Administration > Berichtsverwaltung** (Grid `calibration`/Ordner `calibrations`). Der Platzhalter ist
ab Werk da, trägt das Kennzeichen *Systembericht* und ist als Etikett markiert —
das ist, was **„Etikett drucken"** an die Grid-Zeile hängt.

Der Contract wird am Bundle erkannt; eine Report-Variable `data_contract` ist auf
dem Platzhalter **nicht nötig** (der Grid-Standard ist bereits
`calibration-certificate`). Nötig bleibt sie nur, wenn das Bundle auf einer anders
konfigurierten Zeile liegt.

**Stapeldruck.** Werden im Grid mehrere Zeilen markiert, druckt calServer sie in
*einem* Lauf in eine PDF. Dafür schickt es statt eines Dokuments

```json
{ "meta": { "count": 40 }, "stickers": [ <dokument>, <dokument>, … ] }
```

und lässt den Runner `stickers` durchlaufen. Jedes Element ist ein
**vollständiges Dokument** in genau der Form, die `sample-data.json` zeigt —
deshalb funktioniert diese Vorlage in beiden Fällen unverändert. **Es ist keine
Stapel-Fassung der Vorlage nötig und keine gewünscht**: Wer hier auf ein Array
umbaut, bricht den Einzeldruck.

Entwurf und Vorschau laufen weiter gegen `sample-data.json`, also gegen einen
einzelnen Datensatz.

## ⚠️ Leeres Blatt = fehlende Datenquelle

Ohne JSON-Datenquelle rendert das Label leer. Vorschau: mitgelieferter Adapter
(Default über `com.jaspersoft.studio.data.defadapter`) → „Open → Preview". Live
(calServer V2): Report-Setting-Variable `data_contract = calibration-certificate`.
JasperReports **6.20.6** verbindlich.
