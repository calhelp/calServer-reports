# Unterberichte (DAkkS-Kalibrierschein)

Der Hauptbericht `dakks-sample.jrxml` bindet zwei Unterberichte ein. Beide
verwenden die gleiche Datenbankverbindung wie der Hauptreport und erwarten die
Parameter `PrefixTable`, `Sprache` und `P_CTAG`. `Results.jrxml` erhält
zusätzlich `P_Image_Path`, um Grafiken oder Symbole anzuzeigen.

---

## `Standard.jrxml`

* **Zweck:** Dokumentiert die eingesetzten Normale (Referenzgeräte) inklusive
  Inventarnummer, Beschreibung, Hersteller, Typ sowie letztem und nächstem
  Kalibrierdatum.
* **SQL-Grundlage:**
  ```sql
  SELECT DISTINCT i.I4201, i.I4202, i.I4203, i.I4204,
                  c.C2301, c.C2303, c.C2364
  FROM $P!{PrefixTable}standards t
  LEFT JOIN $P!{PrefixTable}inventory i ON t.C2430 = i.MTAG
  LEFT JOIN $P!{PrefixTable}calibration c ON c.MTAG = i.MTAG AND c.C2339 = 1
  WHERE t.CTAG = $P{P_CTAG};
  ```
* **Layout:** Querformat-Tabelle mit sieben Spalten (`Inv.Nr`, `Beschreibung`,
  `Hersteller`, `Typ`, `letzte Kal`, `nächste Kal`, `Kalibrierkennzeichen`).
  Die Bezeichnungen passen sich über den Parameter `Sprache` automatisch an.
* **Anpassungstipps:** Zusätzliche Informationen (z. B. Standort oder
  Seriennummern) können über weitere Felder im SELECT ergänzt und per
  `<textField>` eingebunden werden.

---

## `Results.jrxml`

* **Zweck:** Listet die Messergebnisse zur ausgewählten Kalibrierung. Je Zeile
  werden Beschreibung, Sollwert, Messwert, zulässige Abweichungen,
  Messunsicherheit und Statussymbol ausgegeben.
* **SQL-Grundlage:** Liest direkt aus `$P!{PrefixTable}results` und reduziert
  alle Felder per `COALESCE(...)` auf Strings. Gefiltert wird über
  `WHERE ctag = $P{P_CTAG}`.
* **Besonderheiten:**
  * `NominalValue` und `MeasuredValue` kombinieren Wert, Prüfschritt und Einheit
    zu einer formatierten Anzeige.
  * `ToleranceRange` entscheidet automatisch, ob ein ±-Wert angezeigt wird oder
    ob Min-/Max-Spalten untereinander erscheinen.
  * `RoundedTolErr` rundet numerische Abweichungen auf eine Nachkommastelle und
    hängt `%` an.
  * `FormattedUncertainty` formatiert wissenschaftliche Schreibweisen (z. B.
    `×10<sup>n</sup>`), falls keine HTML-Markups vorhanden sind.
  * `SymbolStatus` leitet aus dem Feld `test_status` die Symbolik (`iO`, `?`,
    `!?`, `!`) ab, sofern kein individueller Kommentar (`remark`) hinterlegt ist.
* **Druckaufbereitung:** Der Spaltenkopf ist fest definiert (`Beschreibung`,
  `Sollwert`, `Messwert`, `Zul. Abweichung`, `Messunsicherheit`, `Bemerkung`).
  Für weitere Sprachen können die Labels direkt in den `<staticText>`-Elementen
  angepasst oder in ein Resource-Bundle ausgelagert werden.

---

## Integration & Pflege

* Unterberichte werden im Hauptreport als kompiliertes `.jasper` referenziert
  (`Standard.jasper` bzw. `Results.jasper`). Stelle sicher, dass die
  `.jrxml`-Dateien vor dem Ausführen kompiliert werden (z. B. per Build- oder
  Deploy-Schritt), damit die Subreport-Pfade auflösbar sind.
* Struktur oder Parameteränderungen sollten sowohl im Haupt- als auch im
  jeweiligen Unterreport gepflegt werden.
* Durch die konsequente Nutzung von `PrefixTable` lassen sich die Reports in
  Mandantenumgebungen mit Tabellenpräfixen wiederverwenden.
