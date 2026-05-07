# DAkkS-Kalibrierschein (`DAKKS-SAMPLE`)

> **Artefakt:** `dakks-sample`  
> **Hauptbericht:** `DAKKS-SAMPLE/main_reports/dakks-sample.jrxml`  
> **Unterberichte:** `DAKKS-SAMPLE/subreports/Standard.jrxml`, `DAKKS-SAMPLE/subreports/Results.jrxml`

---

## 1. Zweck des Berichts

Der Bericht erzeugt einen vollständig **DAkkS-konformen Kalibrierschein** im
calServer. Er kombiniert:

- Stammdaten des kalibrierten Messmittels (Bezeichnung, Typ, Serien-/Inventarnummer),
- Auftraggeberdaten (Kunde, Adresse, interne Referenzen),
- Kalibrier­ergebnisse inklusive Toleranzen, Messunsicherheit und Konformitäts­symbolik,
- die normativ vorgeschriebenen Textbausteine (Rückführbarkeit, Messunsicherheit,
  Konformität, Zusatz­hinweise, Verfahren) sowie
- den DAkkS-Akkreditierungs­block (Markennummer, Logo, Unterschriften).

Damit deckt der Bericht den typischen Anwendungs­fall einer akkreditierten
Kalibrierstelle ab und ist gleichzeitig flexibel genug, um über Parameter an
Kundenwünsche, Sprachen und Messmittel­varianten angepasst zu werden – ohne den
Report selbst zu verändern.

| Zielgruppe | Nutzen |
| --- | --- |
| **Anwender:innen** | Erzeugt mit wenigen Parametern einen druckfertigen, mehrsprachigen Kalibrierschein. |
| **Administrator:innen / Entwickler:innen** | Dokumentierte SQL-Abfrage, Parameter­steuerung und Subreport-Struktur als Basis für individuelle Erweiterungen. |

---

## 2. Schritt-für-Schritt: Kalibrierschein erzeugen

1. **Report öffnen** – im calServer oder lokal via JasperStarter.
2. **Kalibrierung wählen** – den Pflicht­parameter `P_CTAG` mit der gewünschten
   Kalibrier-ID füllen. Die Abfrage zieht anschließend alle verknüpften Geräte-
   und Kundendaten.
3. **Pfad & Sprache setzen** – `Reportpath` auf das Verzeichnis mit den
   Unterberichten zeigen lassen und bei Bedarf `Sprache` (`Deutsch` /
   `Englisch`) anpassen.
   * Für JasperStarter steht unter
     `DAKKS-SAMPLE/main_reports/dakks-sample_params.properties` eine
     Vorlage bereit (je Parameter eine `key=value`-Zeile).
4. **Textbausteine prüfen** – optionale Parameter wie
   `Cert_description`, `Measurements_description` oder
   `Conformity_description_*` enthalten bereits DAkkS-konforme Standardtexte
   und lassen sich bei Bedarf überschreiben.
5. **Report ausgeben** – typischerweise als PDF, alternativ in jedem von
   JasperReports unterstützten Format.

---

## 3. Inhalt des Berichts

* **Titel- und Kopfbereich** – dynamischer Titel (`Kalibrierschein` /
  `Calibration Certificate`) inkl. Zertifikatsnummer aus `C2396`,
  optional über `Cert_field` überschreibbar.
* **Messmittel-Stammdaten** – Bezeichnung, Typ, Serien- und Inventarnummern
  (`I4204`, `I4203`, `I4202`, `I4201`) sowie optionaler QR-/Barcode-Wert.
* **Auftraggeber:in** – Kund:innenname und Adresse (`customer`), Datum der
  Kalibrierung (`C2301`) sowie interne Referenzen (`C2307`, `C2327`).
* **Kalibrierstatus** – Informationen zu letzter und nächster Kalibrierung
  (`C2308`, `C2311`, `C2312`) inklusive Hervorhebung der beteiligten Personen.
* **Normative Textblöcke** – vordefinierte Absätze zu Rückführbarkeit,
  Messunsicherheit, Konformität und Zusatzinformationen, um DAkkS-Anforderungen
  zu erfüllen.
* **Unterberichte** – Abschnitt „Eingesetzte Normale“ (Subreport
  `Standard.jrxml`) und die mehrseitige Ergebnisdokumentation (Subreport
  `Results.jrxml`).

### Hinweise für den Alltag

* **Sprachwechsel & Textblöcke:** Über `Sprache` werden alle Labels und Absätze
  automatisch auf Deutsch oder Englisch gesetzt. Die JRXML-Datei enthält die
  vollständigen Standard­formulierungen inline, sodass keine externe
  `messages.properties` notwendig ist und Sonderzeichen unverfälscht erhalten
  bleiben.
* **QR-Code & Bilder:** `QR_Code_Value` sowie `P_Image_Path` erlauben das
  Einbinden von QR-Codes und Logos (z. B. DAkkS-Logo in der Fußzeile).
* **Unicode-Schrift:** Der Report nutzt die von JasperStarter mitgelieferten
  **DejaVu-Schriften** mit Identity-H-Encoding, sodass Umlaute und Sonderzeichen
  ohne eingebettete TTF-Datei erhalten bleiben.
* **Seitenzahlen im Fließtext:** `Results_description` nutzt `msg(..., Seite)`
  und passt die Seitenreferenz beim Rendern automatisch an.

---

## 4. Parameter

Alle Parameter sind Strings, sofern nicht anders angegeben. Defaults stammen aus
der JRXML-Datei und greifen automatisch, wenn der Parameter beim Aufruf nicht
gesetzt wird. Die Spalte „Pflicht“ verwendet ✅ für zwingend erforderliche und ➖
für optionale Parameter.

### 4.1 Pflichtparameter {#params-required}

| Parameter | Pflicht | Standardwert | Beschreibung |
| --- | --- | --- | --- |
| `P_CTAG` | ✅ | – | Schlüssel (CTAG) der Kalibrierung in der calServer-Datenbank. Steuert sämtliche Datenbank­abfragen im Haupt- und in den Unterberichten und entscheidet damit, welche Kalibrierung gedruckt wird. |
| `Reportpath` | ✅ | `""` | Absolutes Basis­verzeichnis, in dem Haupt- und Unterberichte als `.jrxml`/`.jasper` liegen (typischerweise `.../DAKKS-SAMPLE`). Wird vom Hauptreport benötigt, um die Subreports `Standard` und `Results` zur Laufzeit auflösen zu können. |

### 4.2 Mandanten-, Sprach- und Anzeige­parameter {#params-locale}

| Parameter | Pflicht | Standardwert | Beschreibung |
| --- | --- | --- | --- |
| `PrefixTable` | ➖ | `""` | Tabellen­präfix für mandanten­fähige Installationen (z. B. `cal_`). Wird per `$P!{PrefixTable}` direkt in die SQL-Statements eingesetzt und gilt zugleich für die Unterberichte. |
| `Sprache` | ➖ | `Deutsch` | Sprache aller Labels und eingebetteten Textbausteine. Erlaubte Werte: exakt `Deutsch` oder `Englisch`; abweichende Werte fallen auf `Deutsch` zurück. |
| `ReportVersion` | ➖ | `V0.8.2` | Versions­kennzeichnung, die im Titelbereich des Berichts ausgegeben wird. |
| `ReportVariantCode` | ➖ | `""` | Ressourcenname für die Layout­steuerung. Steht in `resource.report_template` für diesen Namen der Wert `1`, wird Variante `1` (mit Lücken) aktiviert; sonst läuft Variante `0` (Standard). Leer = Variante `0`. |

### 4.3 Bilder, Codes und Akkreditierungs­block {#params-images}

| Parameter | Pflicht | Standardwert | Beschreibung |
| --- | --- | --- | --- |
| `P_Image_Path` | ➖ | `""` | Pfad zu Logos/Siegeln, die im Kopf- und Fußbereich (z. B. DAkkS-Logo) eingeblendet werden. Wird auch an den Subreport `Results` durchgereicht. |
| `QR_Code_Value` | ➖ | `""` | Inhalt für das QR-/Barcode-Element (z. B. URL zum digitalen Zertifikat). Bleibt der Wert leer, wird kein QR-Code gerendert. |
| `MarkNumber1` | ➖ | `123456` | Erste Markennummer im Akkreditierungs­block. Es wird nur die erste durch Leerzeichen getrennte Ziffernfolge dargestellt, sodass z. B. `123456 (intern)` zu `123456` reduziert wird. |
| `MarkNumber2` | ➖ | `D-K-\nYYYYY-ZZ-N` | Zweite Markennummer (Akkreditierungs­kennung). `\n` erzeugt einen Zeilenumbruch im gedruckten Block. |
| `sign_names` | ➖ | `Y` | Steuert die Anzeige der Namen im Unterschriftsbereich. Werte: `Y` (anzeigen, Default auch bei fehlendem Parameter) oder `N` (ausblenden). |

### 4.4 Zertifikats- und Inhaltssteuerung {#params-content}

| Parameter | Pflicht | Standardwert | Beschreibung |
| --- | --- | --- | --- |
| `Cert_field` | ➖ | `""` | Quelle der Zertifikats­nummer und des Kalibrier­kennzeichens. Erlaubte Werte: `C2396`, `C2364` oder `C2356`; andere Werte fallen auf `C2356` zurück. Wird zugleich an den Subreport `Standard` durchgereicht. |
| `MeasurementDetails` | ➖ | `1` | Wählt eines der vier Messwert-Layouts im Subreport `Results` (`1` Basis­darstellung, `2` formatierte Eingaben, `3` autoformatierte Anzeige, `4` ISO-konforme Unsicherheit). Leere oder nicht-numerische Eingaben werden als `1` behandelt. |
| `ModernResultsHeader` | ➖ | `N` | Schaltet im `Results`-Unterbericht den modernen Tabellen­kopf ein (`Y`) oder behält den klassischen Kopf bei (`N`). |
| `ExpUncType` | ➖ | `""` | Freitext für ergänzende Hinweise zur erweiterten Messunsicherheit (z. B. `k=2`-Anmerkungen). |
| `environmental_conditions` | ➖ | `""` | Optionaler Freitext für Umgebungs­temperatur und relative Luft­feuchte im Format `Text_Temperatur \| Text_Feuchte`. Ersetzt die Werte aus `C2311`/`C2312`, wenn angegeben. Ist ein Ressourcen­name übergeben, werden Temperatur und Feuchte aus `resource.environment_resources` derselben Zeile übernommen. |

### 4.5 Normative Textbausteine {#params-textblocks}

Alle Textbaustein-Parameter sind optional. Sie sind im JRXML mit DAkkS-konformen
Standard­formulierungen (de/en gemäß `Sprache`) vorbelegt; durch Übergabe eines
eigenen Werts wird der Standard überschrieben.

| Parameter | Pflicht | Standardwert | Beschreibung |
| --- | --- | --- | --- |
| `Cert_description` | ➖ | sprachabhängig | Einleitender Vorspann zum Zertifikat (Geltungs­bereich, Verbreitung). |
| `Cert_description_1` | ➖ | sprachabhängig | Folgeabsatz zur Rückführbarkeit / Akkreditierung. |
| `Asset_description` | ➖ | sprachabhängig | Kurzbeschreibung des kalibrierten Messmittels (Asset). |
| `Results_description` | ➖ | sprachabhängig | Hinweistext zu den Mess­ergebnissen; nutzt `msg(..., Seite)` für dynamische Seitenverweise. |
| `Measurements_description` | ➖ | sprachabhängig | Erläuterung zur Methodik der Mess­unsicherheit (z. B. GUM). |
| `Measurements_description_1` | ➖ | sprachabhängig | Folgeabsatz zur Mess­unsicherheits­methodik. |
| `Uncertainty_description` | ➖ | sprachabhängig | Vollständiger Textblock zu Messunsicherheiten. Wird der Parameter gesetzt, ersetzt er den kompletten Standard­abschnitt. |
| `Conformity_description_1` | ➖ | sprachabhängig | Einleitung zur Konformitäts­bewertung. |
| `Conformity_description_2` | ➖ | sprachabhängig | Mehrzeilige Kurzlegende zu den Konformitäts­symbolen (`?`, `!?`, `!`, `*`). |
| `Conformity_description_3` | ➖ | sprachabhängig | Abschluss­hinweis zur Konformitäts­aussage. |
| `Additional_information` | ➖ | sprachabhängig | Zusatzhinweise, u. a. zur internationalen DAkkS-Anerkennung. |
| `Calibration_procedure_1` | ➖ | sprachabhängig | Erster Textbaustein zum angewendeten Kalibrier­verfahren. |
| `Calibration_procedure_2` | ➖ | sprachabhängig | Zweiter Textbaustein zum Kalibrier­verfahren (z. B. Verweis auf Norm). |
| `Calibration_document` | ➖ | sprachabhängig | Verweis auf Verfahrens­anweisung bzw. QMS-Dokument. |

### 4.6 Abschnittsumschalter (`ShowGroup1*`) {#params-showgroup}

Alle Abschnitts­parameter sind Strings (Default bzw. fehlender Parameter: `Y`)
und können auf `Y` (anzeigen) oder `N` (ausblenden) gesetzt werden. Die Werte
`0`, `false` oder `no` werden ebenfalls als „nicht anzeigen“ interpretiert.

| Parameter | Pflicht | Standardwert | Beschreibung |
| --- | --- | --- | --- |
| `ShowGroup1CalibrationItem` | ➖ | `Y` | Abschnitt „Kalibriergegenstand / Unit under test“. |
| `ShowGroup1IncomingDate` | ➖ | `Y` | Abschnitt „Datum der Anlieferung / Incoming Date“. |
| `ShowGroup1Condition` | ➖ | `Y` | Abschnitt „Zustand bei Eingang/Ausgang“. |
| `ShowGroup1Spacer` | ➖ | `Y` | Optionaler Abstand vor dem Verfahren. |
| `ShowGroup1Procedure` | ➖ | `Y` | Abschnitt „Kalibrierverfahren“. |
| `ShowGroup1ProcedureDocument` | ➖ | `Y` | Abschnitt „Verfahrens­anweisung / QMS-Dokument“. |
| `ShowGroup1MeasurementConditions` | ➖ | `Y` | Abschnitt „Messbedingungen“. |
| `ShowGroup1CalibrationPlace` | ➖ | `Y` | Abschnitt „Ort der Kalibrierung“. |
| `ShowGroup1EnvironmentalConditions` | ➖ | `Y` | Abschnitt „Umgebungsbedingungen“. |
| `ShowGroup1StandardsTraceability` | ➖ | `Y` | Abschnitt „Verwendete Normale / Rückführung“. |
| `ShowGroup1ResultsIntro` | ➖ | `Y` | Einleitung zu den Mess­ergebnissen. |
| `ShowGroup1MeasurementUncertainty` | ➖ | `Y` | Abschnitt „MESSUNSICHERHEITEN / UNCERTAINTY OF MEASUREMENTS“. |
| `ShowGroup1Conformity` | ➖ | `Y` | Abschnitt „KONFORMITÄT / CONFORMITY“. |
| `ShowGroup1AdditionalInformation` | ➖ | `Y` | Abschnitt „WEITERE HINWEISE / ADDITIONAL INFORMATION“. |
| `ShowGroup1ResultsDetails` | ➖ | `Y` | Tabellen­abschnitt „MESSERGEBNISSE / MEASUREMENTS RESULTS“. |

---

## 5. Unterberichte

Beide Unterberichte verwenden die gleiche Datenbank­verbindung wie der
Hauptreport und teilen sich die Parameter `PrefixTable`, `Sprache`, `P_CTAG`
sowie optional `P_Image_Path`. `Cert_field` wird zusätzlich an
`Standard.jrxml` durchgereicht.

### 5.1 `subreports/Standard.jrxml`

* **Zweck:** Tabelle der eingesetzten Normale (Referenz­geräte) inklusive
  Inventar­nummer, Beschreibung, Hersteller, Typ sowie letztem und nächstem
  Kalibrier­datum und Kalibrier­kennzeichen.
* **SQL-Grundlage:**
  ```sql
  SELECT DISTINCT i.I4201, i.I4202, i.I4203, i.I4204,
                  c.C2301, c.C2303, c.C2364
  FROM $P!{PrefixTable}standards t
  LEFT JOIN $P!{PrefixTable}inventory  i ON t.C2430 = i.MTAG
  LEFT JOIN $P!{PrefixTable}calibration c ON c.MTAG = i.MTAG AND c.C2339 = 1
  WHERE t.CTAG = $P{P_CTAG};
  ```
* **Layout:** Querformat-Tabelle mit sieben Spalten (`Inv.Nr`, `Beschreibung`,
  `Hersteller`, `Typ`, `letzte Kal.`, `nächste Kal.`, `Kalibrier­kennzeichen`).
  Die Spaltenüberschriften richten sich nach `Sprache`.

### 5.2 `subreports/Results.jrxml`

* **Zweck:** Listet die Mess­ergebnisse der gewählten Kalibrierung. Je Zeile
  werden Beschreibung, Sollwert, Messwert, zulässige Abweichungen, Mess­unsicher­heit
  und Status­symbol ausgegeben.
* **SQL-Grundlage:** Liest direkt aus `$P!{PrefixTable}results` und reduziert
  alle Felder per `COALESCE(...)` auf Strings. Filter: `WHERE ctag = $P{P_CTAG}`.
* **Besonderheiten:**
  * `NominalValue` und `MeasuredValue` kombinieren Wert, Prüfschritt und Einheit.
  * `ToleranceRange` entscheidet automatisch zwischen ±-Anzeige und
    Min/Max-Spalten.
  * `RoundedTolErr` rundet auf eine Nachkommastelle und hängt `%` an.
  * `FormattedUncertainty` formatiert wissenschaftliche Schreib­weisen
    (`×10ⁿ`), sofern keine HTML-Markups vorliegen.
  * `SymbolStatus` leitet aus `pass_fail` die Konformitäts­symbolik
    (`iO`, `?`, `!?`, `!`) ab, sofern kein individueller Kommentar (`remark`)
    hinterlegt ist.
* **Frame-Auswahl über `MeasurementDetails`** – siehe Parameter­tabelle, Abschnitt 4.4.

### 5.3 Integration & Pflege

* Subreports werden im Hauptreport als kompiliertes `.jasper` referenziert
  (`Standard.jasper` bzw. `Results.jasper`). Stelle sicher, dass die
  `.jrxml`-Dateien vor dem Ausführen kompiliert werden, damit die
  Subreport-Pfade auflösbar sind.
* Struktur- oder Parameter­änderungen sollten sowohl im Haupt- als auch im
  jeweiligen Unterreport gepflegt werden.
* Durch konsequente Nutzung von `PrefixTable` lassen sich die Reports in
  Mandanten­umgebungen mit Tabellen­präfixen wiederverwenden.

---

## 6. Datenquellen & SQL des Hauptberichts

Die Hauptabfrage kombiniert drei Kernbereiche der calServer-Datenbank:

* `$P!{PrefixTable}calibration c` – Zertifikats­daten inkl. Felder
  `C2301`, `C2307`, `C2327`, `C2308`, `C2311`, `C2312`.
* `$P!{PrefixTable}inventory  i` – Messmittel­stammdaten
  (`I4201`–`I4206`, `I4224`).
* `$P!{PrefixTable}customers cu` – Auftraggeber:in für Anschrift und Namen.

```sql
SELECT CASE UPPER(COALESCE($P{Cert_field}, ''))
         WHEN 'C2396' THEN COALESCE(c.C2396, "")
         WHEN 'C2364' THEN COALESCE(c.C2364, "")
         WHEN 'C2356' THEN COALESCE(c.C2356, "")
         ELSE COALESCE(c.C2356, "")
       END AS cert_field,
       DATE_FORMAT(C2301, '%Y-%m')   AS cal_date,
       COALESCE(i.I4204, "")          AS I4204,
       COALESCE(i.I4201, "")          AS I4201,
       COALESCE(c.C2314, "--")        AS C2314
FROM   $P!{PrefixTable}calibration c
LEFT JOIN $P!{PrefixTable}inventory  i ON i.MTAG = c.MTAG
LEFT JOIN $P!{PrefixTable}customers cu ON cu.KTAG = i.KTAG
WHERE  c.CTAG = $P{P_CTAG};
```

### Typische Anpassungen

* **Weitere Sprachen** – zusätzliche Locale-Logik über `Sprache` ergänzen; die
  eingebetteten Default-Texte können durch eigene Parameter­werte oder
  optionale `resourceBundles` überschrieben werden.
* **Kundenspezifische Logos** – Bildplatzhalter mit `P_Image_Path` befüllen
  oder eigene Bildkomponenten einfügen.
* **Erweiterte Datenfelder** – zusätzliche Felder via `LEFT JOIN` in der
  Hauptabfrage ergänzen und als `<field>` registrieren.
* **Digitale Signaturen** – `REPORT_CONNECTION` für Scriptlets nutzen, um
  qualifizierte Signaturen einzubetten.

---

## 7. Troubleshooting

* **Leere Ausgabe** – prüfen, ob `P_CTAG` auf eine vorhandene Kalibrierung
  zeigt und ob der angemeldete Benutzer Zugriff auf die Tabellen hat.
* **Unterberichte fehlen** – sicherstellen, dass `Reportpath` auf den Ordner mit
  den `.jrxml`-Dateien zeigt (JasperReports kompiliert sie zur Laufzeit, falls
  keine `.jasper`-Dateien bereitliegen).
* **Falsche Sprache** – der Parameterwert muss exakt `Deutsch` oder `Englisch`
  lauten; ansonsten greift der deutsche Default.
* **Zertifikatsnummer fehlt** – optionalen Text über `Cert_field` setzen oder
  den Datenbankwert in `C2396` prüfen.
* **Seitenumbrüche anpassen** – der Haupttitel nutzt `isTitleNewPage="true"`;
  bei Bedarf die Startseite über den Report-Parameter `isTitleNewPage` anpassen.
