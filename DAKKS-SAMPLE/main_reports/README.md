# 📜 DAkkS-Kalibrierschein (`dakks-sample.jrxml`)

Dieser Hauptbericht bildet einen vollständigen **DAkkS-konformen Kalibrierschein**
ab. Er kombiniert Stammdaten des kalibrierten Messmittels, Kundenangaben,
Kalibrierergebnisse und die notwendigen normativen Textbausteine. Die Vorlage
liegt unter `DAKKS-SAMPLE/main_reports/dakks-sample.jrxml` und bindet zwei
Unterberichte für Normale und Messergebnisse ein.

| Zielgruppe | Nutzen |
| --- | --- |
| **Normale Nutzer:innen** | Erzeugt in wenigen Schritten einen druckfertigen Kalibrierschein mit mehrsprachigem Layout. |
| **Administrator:innen / Entwickler:innen** | Liefert eine dokumentierte SQL-Abfrage, Parametrisierung und Subreport-Struktur für individuelle Erweiterungen. |

---

## 🚀 Schritt-für-Schritt: Kalibrierschein erzeugen

1. **Report öffnen** – im calServer oder lokal via JasperStarter.
2. **Kalibrierung wählen** – den Pflichtparameter `P_CTAG` mit der gewünschten
   Kalibrier-ID füllen. Die Abfrage zieht anschließend alle verknüpften Geräte-
   und Kundendaten.
3. **Pfad & Sprache setzen** – `Reportpath` auf das gemeinsame Verzeichnis mit
   den Unterberichten zeigen lassen und bei Bedarf `Sprache` (`Deutsch` /
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

## 1. Für normale Nutzer:innen

### Was zeigt der Bericht?

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
  vollständigen Standardformulierungen inline, sodass keine externe
  `messages.properties` mehr notwendig ist und Sonderzeichen unverfälscht
  erhalten bleiben.
* **QR-Code & Bilder:** `QR_Code_Value` sowie `P_Image_Path` erlauben das
  Einbinden von QR-Codes und Logos (z. B. DAkkS-Logo in der Fußzeile).
* **Unicode-Schrift:** Der Report nutzt die von JasperStarter mitgelieferten
  **DejaVu-Schriften** mit Identity-H-Encoding, sodass Umlaute und Sonderzeichen
  ohne eingebettete TTF-Datei erhalten bleiben. Zusätzliche Fonts lassen sich bei
  Bedarf als Font-Extension-JAR (z. B. im JDBC-Verzeichnis) nachrüsten.
* **Beschreibungstexte:** Parameter wie `Cert_description_1` oder
  `Measurements_description_1` enthalten bereits abgestimmte Formulierungen und
  können pro Kunde / Messmittel angepasst werden.
* **Seitenzahlen im Fließtext:** `Results_description` nutzt `msg(..., Seite)`
  und passt die Seitenreferenz beim Rendern automatisch an.

---

## 2. Für Administrator:innen & Entwickler:innen

### Messwert-Frames im Results-Unterbericht

Der Parameter `MeasurementDetails` (String, Default: `"1"`) steuert vier
alternative Messwert-Layouts im Subreport `Results.jrxml`. Alle Varianten
werden nur gedruckt, wenn Messdaten vorhanden sind (`HasMeasurementData`):

* Leere oder nicht-numerische Eingaben werden automatisch als `1` behandelt,
  sodass auch Aufrufe mit `MeasurementDetails=""` nicht mehr mit einer
  `NumberFormatException` abbrechen.

1. **Frame 1 – Basisdarstellung (`null`/`1`)**
   * Spalten: Messbedingungen, Sollwert, untere & obere Spezifikationsgrenze,
     Messwert, relative Abweichung, erweiterte Messunsicherheit, `% Tol`,
     Konformität.
   * Nutzt die Rohfelder (`lower_limit`/`upper_limit`, `exp_uncert`, `pass_fail`) und
     gibt sie ohne zusätzliche Formatierung aus.
2. **Frame 2 – formatierte Eingaben (`2`)**
   * Gleiche Spalten wie Frame 1, aber alle Soll-, Toleranz- und
     Unsicherheitswerte werden zusammengesetzt aus Wert, Präfix und Einheit
     (z. B. `fixq`, `fixq_p`, `fixq_u`). So lassen sich Vorzeichen, Prozent- und
     Einheitentexte kontrolliert übergeben.
3. **Frame 3 – autoformatierte Anzeige (`3`)**
   * Verwendet vorberechnete Variablen (`NominalValue`, `NegLimit`,
     `PosLimit`, `MeasuredValue`, `RoundedRelError`, `DisplayUncertainty`), die
     Einheiten zusammenführen und wissenschaftliche Schreibweisen berücksichtigen.
   * Eignet sich, wenn die Datenbankwerte minimal gepflegt sind und das Layout
     die Formatierung übernehmen soll.
4. **Frame 4 – ISO-konforme Unsicherheit (`4`)**
   * Identisch zu Frame 3, ersetzt die Unsicherheitsspalte jedoch durch
     `DisplayUncertaintyIsoP` und nutzt damit ISO-konforme Schreibweise mit
     explizitem `p`-Wert.

Alle Frames teilen sich den gleichen Spaltenkopf (de/en) und die gleiche
Konformitätslogik (`i.T.`, `?`, `!?`, `!` plus Akkreditierungsstern). Die Auswahl
erfolgt ausschließlich über den Parameterwert, wodurch zwischen Rohdaten- und
Darstellungsvarianten gewechselt werden kann, ohne den Report umzubauen.

### Datenquellen & Tabellen

Die Hauptabfrage kombiniert drei Kernbereiche der calServer-Datenbank:

* `$P!{PrefixTable}calibration c` – Zertifikatsdaten inkl. Felder
  `C2301`, `C2307`, `C2327`, `C2308`, `C2311`, `C2312`.
* `$P!{PrefixTable}inventory i` – Messmittelstammdaten (`I4201`–`I4206`, `I4224`).
* `$P!{PrefixTable}customers cu` – Auftraggeber:in für Anschrift und Namen.

### SQL-Auszug

```sql
SELECT CASE UPPER(COALESCE($P{Cert_field}, ''))
         WHEN 'C2396' THEN COALESCE(c.C2396, "")
         WHEN 'C2364' THEN COALESCE(c.C2364, "")
         WHEN 'C2356' THEN COALESCE(c.C2356, "")
         ELSE COALESCE(c.C2356, "")
       END AS cert_field,
       DATE_FORMAT(C2301, '%Y-%m')       AS cal_date,
       COALESCE(i.I4204, "")            AS I4204,
       COALESCE(i.I4201, "")            AS I4201,
       COALESCE(c.C2314, "--")          AS C2314
FROM   $P!{PrefixTable}calibration c
LEFT JOIN $P!{PrefixTable}inventory i ON i.MTAG = c.MTAG
LEFT JOIN $P!{PrefixTable}customers cu ON cu.KTAG = i.KTAG
WHERE  c.CTAG = $P{P_CTAG};
```

### Subreports & Ressourcen

* **`subreports/Standard.jrxml`** – listet die eingesetzten Normale inklusive
  Inventarnummer, Hersteller, Typ und Kalibrierstatus.
* **`subreports/Results.jrxml`** – erstellt die tabellarische
  Messergebnis-Dokumentation mit Toleranzen, Messunsicherheit und Symbolik.
* Beide Unterberichte benötigen dieselben Parameter (`PrefixTable`, `Sprache`,
  `P_CTAG`, optional `P_Image_Path`) und denselben Datenbank-Connection-Context;
  `Cert_field` wird zusätzlich in den Standard-Unterbericht durchgereicht.

### Vollständige Parameterübersicht

| Parameter | Pflicht | Standardwert | Zweck |
| --- | --- | --- | --- |
| `P_CTAG` | ✅ | leer | Schlüssel der Kalibrierung, steuert alle Haupt- und Unterberichte. |
| `Reportpath` | ✅ | `""` | Basisverzeichnis für Unterberichte (`.../DAKKS-SAMPLE`) mit den `.jrxml`-Dateien für Haupt- und Unterberichte. |
| `PrefixTable` | ➖ | `""` | Tabellenpräfix für mandantenfähige Installationen (z. B. `cal_`). |
| `Sprache` | ➖ | `Deutsch` | Sprache der Labels und Textbausteine (`Deutsch` / `Englisch`). |
| `QR_Code_Value` | ➖ | `""` | Inhalt für QR-/Barcode-Elemente. |
| `MeasurementDetails` | ➖ | `"1"` | Aktiviert eines der vier Frames im Results-Unterbericht (`1` = Standard; `2`/`3`/`4` siehe Abschnitt zu Messwert-Frames). |
| `ModernResultsHeader` | ➖ | `"N"` | Schaltet im `Results`-Unterbericht den modernen Tabellenkopf ein (`"Y"` für aktiv). |
| `ReportVariantCode` | ➖ | `""` | Ressourcenname für die Layoutsteuerung. Wenn in `resource.report_template` für diesen Namen der Wert `1` steht, wird die DIM-Variante aktiviert; sonst bleibt die Standardvariante aktiv. |
| `Cert_field` | ➖ | `""` | Steuert die Quelle der Zertifikatsnummer und das Kalibrierkennzeichen: optional `C2396`, `C2364` oder `C2356`; andere Werte fallen auf `C2356` zurück. Haupt- und Unterbericht (Kalibrierkennzeichen im Standard-Subreport) nutzen dieses Feld gemeinsam. |
| `P_Image_Path` | ➖ | `""` | Pfad für Logos/Siegel im Kopf- und Fußbereich. |
| `ReportVersion` | ➖ | `V0.8.2` | Versionskennzeichnung im Titelbereich. |
| `MarkNumber1`, `MarkNumber2` | ➖ | `123456`, `D-K-\nYYYYY-ZZ-N` | Markierungsnummern im Akkreditierungsblock; bei `MarkNumber1` wird nur die erste durch Leerzeichen getrennte Ziffernfolge dargestellt. |
| `sign_names` | ➖ | `Y` | Blendet die Namen im Unterschriftsbereich ein (`Y`, Standard auch bei fehlendem Parameter) oder aus (`N`). |
| `ExpUncType` | ➖ | `""` | Freitext für ergänzende Hinweise zur Messunsicherheit. |
| `Cert_description`, `Cert_description_1` | ➖ | vordefiniert | Normativer Vorspann zur Rückführbarkeit und Verbreitung. |
| `Asset_description` | ➖ | vordefiniert | Kurzbeschreibung des kalibrierten Messmittels. |
| `Results_description` | ➖ | sprachabhängig | Hinweis auf Seitenverweise der Messergebnisse. |
| `Measurements_description`, `Measurements_description_1` | ➖ | sprachabhängig | Erläuterungen zur Messunsicherheit/GUM. |
| `Uncertainty_description` | ➖ | sprachabhängig | Vollständiger Textblock zu Messunsicherheiten; überschreibt den Standardabschnitt. |
| `Conformity_description_1..3` | ➖ | sprachabhängig | Legenden für Konformitätsaussagen und Symbolik. |
| `Additional_information` | ➖ | sprachabhängig | Hinweise zur DAkkS-Anerkennung. |
| `Calibration_procedure_1`, `Calibration_procedure_2` | ➖ | sprachabhängig | Textbausteine zu den angewendeten Verfahren. |
| `Calibration_document` | ➖ | sprachabhängig | Verweis auf Verfahrensanweisung bzw. QMS-Dokument. |
| `environmental_conditions` | ➖ | `""` | Optionaler Freitext für Umgebungstemperatur und relative Luftfeuchte im Format `Text_Temperatur | Text_Feuchte`; ersetzt die Werte aus `C2311`/`C2312`, wenn angegeben. Wird ein Ressourcenname übergeben, werden Temperatur und Feuchte aus `resource.environment_resources` derselben Zeile gemäß dieser Logik übernommen. |

**Standardwerte aus der JRXML-Datei**

* Bei fehlenden Eingaben greift immer die Default-Logik des Reports: leere Strings für Pfad-/Logo-/QR-Parameter, `Deutsch` für die
  Sprachumschaltung und `"1"` für die Messwert-Frames.
* `Conformity_description_2` enthält jetzt eine mehrzeilige Kurzlegende (de/en), sodass statt der reinen Symbolfolge `? !? ! *`
  direkt eine verständliche Vorgabe ausgegeben wird.
* `ModernResultsHeader` startet mit `"N"`; der traditionelle Tabellenkopf wird also beibehalten, bis `"Y"` gesetzt wird.
* `MarkNumber1` (`123456`) und `MarkNumber2` (`D-K-\nYYYYY-ZZ-N`) liefern sofort druckbare Platzhalter, sodass der Report auch
  ohne eigene DAkkS-Kennung testbar bleibt.
* `sign_names` steht standardmäßig auf `"Y"` und blendet nur bei `"N"` die gedruckten Namen im Unterschriftsbereich aus.
* Alle Abschnittsumschalter (`ShowGroup1...`) stehen auf `"Y"` und blenden nur bei explizitem `"N"` einzelne Informationsblöcke
  aus; `0`/`false`/`no` werden ebenfalls als „nicht anzeigen“ interpretiert.

### Abschnittsumschalter (ShowGroup1...)

Alle Abschnitts-Parameter sind Strings (Default bzw. fehlender Parameter: `"Y"`) und können je nach Bedarf auf `"Y"` (anzeigen) oder `"N"` (ausblenden) gesetzt werden:

* `ShowGroup1CalibrationItem` – Kalibriergegenstand / Unit under test
* `ShowGroup1IncomingDate` – Datum der Anlieferung / Incoming Date
* `ShowGroup1Condition` – Zustand bei Eingang/Ausgang
* `ShowGroup1Spacer` – optionaler Abstand vor dem Verfahren
* `ShowGroup1Procedure` – Kalibrierverfahren
* `ShowGroup1ProcedureDocument` – Verfahrensanweisung / QMS-Dokument
* `ShowGroup1MeasurementConditions` – Messbedingungen
* `ShowGroup1CalibrationPlace` – Ort der Kalibrierung
* `ShowGroup1EnvironmentalConditions` – Umgebungsbedingungen
* `ShowGroup1StandardsTraceability` – Verwendete Normale / Rückführung
* `ShowGroup1ResultsIntro` – Einleitung zu den Messergebnissen
* `ShowGroup1MeasurementUncertainty` – Abschnitt „MESSUNSICHERHEITEN / UNCERTAINTY OF MEASUREMENTS“
* `ShowGroup1Conformity` – Abschnitt „KONFORMITÄT / CONFORMITY“
* `ShowGroup1AdditionalInformation` – Abschnitt „WEITERE HINWEISE / ADDITIONAL INFORMATION“
* `ShowGroup1ResultsDetails` – Tabellenabschnitt „MESSERGEBNISSE / MEASUREMENTS RESULTS“

**Unterberichte**

* `Standard.jrxml`: erwartet `PrefixTable`, `Sprache`, `P_CTAG` (Default: `Deutsch`, Beispiel-CTAG) für die Tabelle der eingesetzten Normale.
* `Results.jrxml`: erwartet `PrefixTable`, `P_CTAG`; optional `MeasurementDetails`, `ModernResultsHeader` (Standard: `"N"`) sowie `Debug` (`N`) für zusätzliche Protokolle.

### Typische Anpassungen

* **Weitere Sprachen** – zusätzliche Locale-Logik über `Sprache` ergänzen; die
  eingebetteten Default-Texte lassen sich bei Bedarf durch eigene Parameter-
  Werte oder optionale `resourceBundles` überschreiben.
* **Kundenspezifische Logos** – Bildplatzhalter mit `P_Image_Path` befüllen
  oder eigene Bildkomponenten einfügen.
* **Erweiterte Datenfelder** – zusätzliche Felder via `LEFT JOIN` in der
  Hauptabfrage ergänzen und als `<field>` registrieren.
* **Digital Signatures** – `REPORT_CONNECTION` für Scriptlets nutzen, um
  qualifizierte Signaturen einzubetten.

---

## 3. Troubleshooting & Tipps

* **Leere Ausgabe?** – prüfen, ob `P_CTAG` auf eine vorhandene Kalibrierung
  zeigt und ob der angemeldete Benutzer Zugriff auf die Tabellen hat.
* **Unterberichte fehlen:** sicherstellen, dass `Reportpath` auf den Ordner mit
  den `.jrxml`-Dateien zeigt (JasperReports kompiliert sie zur Laufzeit, falls
  keine `.jasper`-Dateien bereitliegen).
* **Falsche Sprache:** der Parameterwert muss exakt `Deutsch` oder `Englisch`
  lauten; ansonsten greift der deutsche Default.
* **Zertifikatsnummer fehlt:** optionalen Text über `Cert_field` setzen oder den
  Datenbankwert in `C2396` prüfen.
* **Seitenumbrüche anpassen:** der Haupttitel nutzt `isTitleNewPage="true"` –
  bei Bedarf kann die Startseite über den Report-Parameter `isTitleNewPage`
  angepasst werden.

---

Mit diesem README erhältst du sowohl eine fachliche Beschreibung als auch eine
technische Referenz für den DAkkS-Kalibrierschein.
