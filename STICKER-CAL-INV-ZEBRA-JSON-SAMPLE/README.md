# STICKER-CAL-INV-ZEBRA-JSON-SAMPLE — Zebra Inventar-/Kalibrier-Sticker (V2 / APEX)

V2-Nachbildung des kombinierten **Inventar-/Kalibrier-Stickers** für den
Zebra ZD621 30×15 mm @203 dpi (240×120 px), Phase C. Gefüllt aus einem
**JSON-Datensatz** (Contract `inventory-datasheet` v1.1) statt aus SQL —
DB-agnostisch, keine V1-Codespalten.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/cal-inv-zebra-json-sample.jrxml` | Label 240×120 px: **QR aus `device.asset_number`** (links) + Infospalte rechts (Inventar-Nr., OE-Bezeichnung, Kostenstelle, Standort, letzte + nächste Kalibrierung) |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `inventory-datasheet` v1.1) |
| `main_reports/cal-inv-zebra-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Felder

`barcode.value` + `barcode.type` (der Code), `device.asset_number` (Text),
`device.cost_center`, `device.active_location.location_1/2`,
`device.last_calibration_date`, `device.next_calibration_date`, `customer.name`
(OE-Bezeichnung/Gruppe). Dataset-Builder: Laravel `InventoryReportDataBuilder`.

> **Der Code kommt aus `barcode`, nicht aus `device.asset_number`.** Welches Feld
> codiert wird und in welcher Symbologie, entscheiden die Regeln
> (*Grundeinstellungen > Barcode & Etikett*); der Datensatz liefert beides fertig
> aufgelöst. Deshalb passt diese eine Datei auch beim Kunden, der eine Hausnummer
> aus einem Zusatzfeld codiert — sonst bräuchte er einen Fork.
>
> Die Symbologie schaltet über `printWhenExpression` gegen `barcode.type`:
> `qrcode` (ZXing), `datamatrix`, `code128`, `code39` (barcode4j). Ein Wert, für
> den keine Komponente da ist, druckt schlicht keinen Code — das Etikett bleibt
> lesbar.
>
> Gerendert wird runner-seitig aus dem Feldwert — kein vorgeneriertes Bild, kein
> `Barcode`-Model, DB-agnostisch.

## Systembericht-Platzhalter und Stapeldruck (ab calServer V2)

Dieses Bundle gehört auf den Platzhalter **Geräteetikett** in
**Administration > Berichtsverwaltung** (Grid `inventory`/Ordner `inventories`). Der Platzhalter ist
ab Werk da, trägt das Kennzeichen *Systembericht* und ist als Etikett markiert —
das ist, was **„Etikett drucken"** an die Grid-Zeile hängt.

Der Contract wird am Bundle erkannt; eine Report-Variable `data_contract` ist auf
dem Platzhalter **nicht nötig** (der Grid-Standard ist bereits
`inventory-datasheet`). Nötig bleibt sie nur, wenn das Bundle auf einer anders
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

Ohne JSON-Datenquelle rendert der Sticker leer. Vorschau: mitgelieferter Adapter
(Default über `com.jaspersoft.studio.data.defadapter`) → „Open → Preview". Live
(calServer V2): Report-Setting-Variable `data_contract = inventory-datasheet`.
JasperReports **6.20.6** verbindlich. Keine `$V{}`-Variablen (nur `staticText`/`$F{}`).
