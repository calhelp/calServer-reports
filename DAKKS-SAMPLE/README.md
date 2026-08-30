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
| `PageNumberPosition` | ➖ | `HeaderLeft` | Position der Seitenzahl »Seite x von y« (Sprachwahl über `Sprache`). Erlaubte Werte: `HeaderLeft`, `HeaderCenter`, `HeaderRight`, `FooterLeft`, `FooterCenter`, `FooterRight` oder `None` (Seitenzahl ausblenden). `HeaderLeft` (Default) entspricht der bisherigen Anzeige oben links. **`Header*`-Positionen erscheinen erst ab Seite 2** – die Titelseite (Seite 1) hat keinen Seitenkopf und weist dort nur die Gesamtseitenzahl (»Anzahl Seiten des Kalibrierscheines«) aus; **`Footer*`-Positionen** werden auch auf Seite 1 in der Fußzeile gedruckt. |
| `PageNumberBilingual` | ➖ | `Y` | Zweisprachige Seitenzahl. `Y` (Default) = zweizeilig: primäre Sprache (gemäß `Sprache`) oben, die andere Sprache darunter (kleiner/kursiv), z. B. »Seite 3 von 7« über »Page 3 of 7«. `N` = nur eine Sprache gemäß `Sprache`. Wirkt an der über `PageNumberPosition` gewählten Position; `None` blendet weiterhin alles aus. Wie bei `PageNumberPosition` erscheint die Zahl bei `Header*`-Positionen erst ab Seite 2 (Titelseite ohne Seitenkopf). |
| `PrefixTable` | ➖ | `""` | Tabellen­präfix für mandanten­fähige Installationen (z. B. `cal_`). Wird per `$P!{PrefixTable}` direkt in die SQL-Statements eingesetzt und gilt zugleich für die Unterberichte. |
| `Sprache` | ➖ | `Deutsch` | Sprache aller Labels und eingebetteten Textbausteine. Erlaubte Werte: exakt `Deutsch` oder `Englisch`; abweichende Werte fallen auf `Deutsch` zurück. |
| `ReportVersion` | ➖ | `V0.8.2` | Versions­kennzeichnung, die im Titelbereich des Berichts ausgegeben wird. |
| `ReportVariantCode` | ➖ | `""` | Ressourcenname für die Layout­steuerung. Steht in `resource.report_template` für diesen Namen der Wert `1`, wird Variante `1` (mit Lücken) aktiviert; sonst läuft Variante `0` (Standard). Leer = Variante `0`. |

### 4.3 Bilder, Codes und Akkreditierungs­block {#params-images}

| Parameter | Pflicht | Standardwert | Beschreibung |
| --- | --- | --- | --- |
| `ShowMarkOnFollowingPages` | ➖ | `Y` | Blendet den Kennzeichnungs-/Akkreditierungsblock (`MarkNumber1`, `MarkNumber2`, Kalibrierdatum oben rechts) auf Folgeseiten ein/aus. `Y` = auf allen Seiten anzeigen (Default). `N` = nur auf Seite 1 anzeigen, ab Seite 2 ausblenden. |
| `P_Image_Path` | ➖ | `""` | Pfad zu Logos/Siegeln, die im Kopf- und Fußbereich (z. B. DAkkS-Logo) eingeblendet werden. Wird auch an den Subreport `Results` durchgereicht. |
| `QR_Code_Value` | ➖ | `""` | Inhalt für das QR-/Barcode-Element (z. B. URL zum digitalen Zertifikat). Bleibt der Wert leer, wird kein QR-Code gerendert. |
| `MarkNumber1` | ➖ | `123456` | Erste Markennummer im Akkreditierungs­block. Es wird nur die erste durch Leerzeichen getrennte Ziffernfolge dargestellt, sodass z. B. `123456 (intern)` zu `123456` reduziert wird. |
| `MarkNumber2` | ➖ | `D-K-\nYYYYY-ZZ-N` | Zweite Markennummer (Akkreditierungs­kennung). `\n` erzeugt einen Zeilenumbruch im gedruckten Block. |
| `sign_names` | ➖ | `Y` | Steuert die Anzeige der Namen im Unterschriftsbereich. Werte: `Y` (anzeigen, Default auch bei fehlendem Parameter) oder `N` (ausblenden). |

### 4.4 Zertifikats- und Inhaltssteuerung {#params-content}

| Parameter | Pflicht | Standardwert | Beschreibung |
| --- | --- | --- | --- |
| `Cert_field` | ➖ | `""` | Quelle der Zertifikats­nummer und des Kalibrier­kennzeichens. Erlaubte Werte: `C2396`, `C2395`, `C2364` oder `C2356`; andere Werte fallen auf `C2356` zurück. Wird zugleich an den Subreport `Standard` durchgereicht. |
| `MeasurementDetails` | ➖ | `1` | Wählt eines der Messwert-Layouts im Subreport `Results` (`1` Basis­darstellung, `2`/`22` formatierte Eingaben, `21` Kurzform ohne Spezifikations­spalten, `3` autoformatierte Anzeige, `4` ISO-konforme Unsicherheit). Leere, nicht-numerische **und unbekannte** Eingaben werden als `1` behandelt — eine `5` druckte bis dahin eine komplett leere Ergebnistabelle, ohne Kopf und ohne Hinweis. **Die Variante entscheidet über das Layout, nicht darüber, ob Zahlen erscheinen** – Sollwert und Messwert greifen auf das jeweils andere Spaltenpaar zurück (siehe Abschnitt 5.2). |
| `ModernResultsHeader` | ➖ | `Y` | Tabellenkopf-Stil im `Results`-Unterbericht. Standard ist der moderne Kopf ohne umlaufende Rahmen (gilt auch für leere oder unbekannte Werte); nur ein explizites `N` schaltet auf den klassischen Kopf mit Rahmen zurück. Beide Stile sind je `MeasurementDetails`-Variante an den Datenspalten ausgerichtet. |
| `ExpUncType` | ➖ | `""` | Freitext für ergänzende Hinweise zur erweiterten Messunsicherheit (z. B. `k=2`-Anmerkungen). |
| `environmental_conditions` | ➖ | `""` | Name der Ressource, deren Klimabereich gedruckt wird. Der Bericht joint `resource.name = $P{environmental_conditions}` und liest deren Feld „Umgebungs­bedingungen“ (`environment_resources`) – ein Text mit `\|` als Trenner, links die Temperatur, rechts die Feuchte, jeweils mit Einheit, z. B. `21,0 ... 23,0 °C\|40 ... 60 %`. **Jede Hälfte fällt für sich zurück:** bleibt sie leer, druckt der Schein den an der Kalibrierung erfassten Wert (`C2311` + ` °C` bzw. `C2312` + ` %`). So steht der Klimabereich des Labors einmal an der Ressource statt in jedem Bericht erneut. |

### 4.5 Normative Textbausteine {#params-textblocks}

Alle Textbaustein-Parameter sind optional. Sie sind im JRXML mit DAkkS-konformen
Standard­formulierungen (de/en gemäß `Sprache`) vorbelegt; durch Übergabe eines
eigenen Werts wird der Standard überschrieben.

**Die Prozedur schlägt den Parameter.** Die drei `Calibration_*`-Bausteine sind
reine Fallbacks: Liefert die zur Kalibrierung gehörende Prozedur einen Text,
gewinnt sie. Gepflegt gehören diese Angaben deshalb an die Prozedur – sie gelten
dort je Prüfmittel, der Parameter dagegen je Bericht. Welches Kalibrierfeld den
Prozedurnamen trägt, entscheidet der Join `procedures.procedure_name = c.C2320`
(V2: die Berichtsvariable `procedure_field`); ohne treffende Prozedur bleiben
alle vier Prozedur-Abschnitte bei ihren Fallbacks.

| Abschnitt | Feld der Prozedur | Fallback |
| --- | --- | --- |
| Kalibrier­verfahren | `procedure_description` | `Calibration_procedure_1` → „Kalibrierverfahren nicht angegeben“ |
| Verfahrens­anweisung | `calibration_method` | `Calibration_document` → „Verfahrensanweisung nicht angegeben“ |
| Messbedingungen | `measurement_conditions` | „im permanenten Labor“ |
| Geltungs­bereich | `scope` | `calibration_item` → `standards` → `Calibration_procedure_2` → „--“ |

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
| `Calibration_procedure_1` | ➖ | sprachabhängig | Fallback für das angewendete Kalibrier­verfahren. Der bessere Ort ist das Feld „Beschreibung“ der Prozedur. |
| `Calibration_procedure_2` | ➖ | sprachabhängig | Fallback für den Geltungs­bereich, wenn weder Prozedur-Scope noch Kalibrier­gegenstand noch Normale gefüllt sind. Der bessere Ort ist das Feld „Geltungsbereich“ der Prozedur. |
| `Calibration_document` | ➖ | sprachabhängig | Fallback für die Verfahrens­anweisung bzw. das QMS-Dokument. Der bessere Ort ist das Feld „Kalibriermethode“ der Prozedur. |

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
| `ShowGroup1Procedure` | ➖ | `Y` | Abschnitt „Kalibrierverfahren“ (Text aus der Prozedur, siehe 4.5). |
| `ShowGroup1ProcedureDocument` | ➖ | `Y` | Abschnitt „Verfahrens­anweisung / QMS-Dokument“ (Kalibriermethode der Prozedur, siehe 4.5). |
| `ShowGroup1MeasurementConditions` | ➖ | `Y` | Abschnitt „Messbedingungen“ (Feld „Messbedingungen“ der Prozedur, siehe 4.5). |
| `ShowGroup1CalibrationPlace` | ➖ | `Y` | Abschnitt „Ort der Kalibrierung“. |
| `ShowGroup1EnvironmentalConditions` | ➖ | `Y` | Abschnitt „Umgebungsbedingungen“ (Ressource aus `environmental_conditions`, siehe 4.4). |
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
* **Woher Sollwert und Messwert kommen:** Beide stehen je nach Erfassungsweg in
  einem von zwei Spaltenpaaren — `fixq`/`varq` (Sollwert des Prüfschritts und
  Ablesung) oder `sys_actual`/`uut_ind` (Wert des Normals und Anzeige des
  Prüflings). MET/CAL liefert beide Paare; die calServer-Messwertaufnahme füllt
  `sys_actual`/`uut_ind` nur für numerische Schritte mit gesetztem `tol_ref`.
  Jede Layout-Variante band früher genau ein Paar und druckte eine leere Spalte,
  wenn der Wert im anderen stand — sichtbar als Ergebnistabelle ohne Zahlen bei
  ungesetztem `MeasurementDetails`. Heute greifen die Variablen `FixqValue` /
  `SysActualValue` / `VarqValue` / `UutIndValue` auf die Schwesterspalte zurück,
  wenn die eigene leer ist; Präfix und Einheit folgen der Spalte, aus der der
  Wert stammt. **Sind beide Paare gefüllt, druckt jede Variante unverändert das
  Paar, das sie schon immer gedruckt hat.**
* **Messbedingungen (`test_desc`):** Die erste Spalte trägt die Bezeichnung des
  Prüfschritts aus der Prozedur. Wer sie sprechend haben will („Kanal 1,
  Anzeigeabweichung bei 15 °C“), pflegt sie in der Prozedur — der Bericht
  formatiert sie nur.
* **Einheiten in den Wertespalten:** Die Varianten `2`, `21`, `22`, `3` und `4`
  setzen jede Wertespalte nach derselben Regel zusammen — Wert, SI-Vorsatz,
  Einheit, Vorsatz und Einheit zusammengeschrieben (`9.9 mg`, nicht `9.9 m g`).
  Trägt der Wert die Einheit schon im Text (`10 V`, `i.O.`), kommt nichts dazu;
  geprüft wird der Rest hinter der Zahl, damit das `E` einer
  Exponentialschreibweise nicht für eine Einheit gehalten wird. Variante `1` ist
  die Basisdarstellung und druckt bewusst die Rohwerte ohne Vorsatz und Einheit;
  ihre Spalten sind 54 px breit und nehmen keine Einheit mehr auf. Wer Einheiten
  im Ausdruck braucht, nimmt `2` oder `22` — dieselben Spalten, formatiert.
* **Die Varianten auf einen Blick:**

  | Variante | Spalten (links nach rechts) | Sollwert / Messwert aus | Einheiten in den Wertespalten |
  | --- | --- | --- | --- |
  | `1` | Messbedingungen · Sollwert · untere Spez. · Messwert · obere Spez. · % rel. Abw. · erw. MU · % Tol · Konformität | `fixq` / `varq` | nein (Basisdarstellung, Rohwerte) |
  | `2` | wie `1`, breitere Spalten | `fixq` / `varq` | ja |
  | `22` | wie `2` | `sys_actual` / `uut_ind` | ja |
  | `21` | Messbedingungen · Sollwert · Messwert · % rel. Abw. · erw. MU | `sys_actual` / `uut_ind` | ja |
  | `3` | Messbedingungen · Sollwert · Messwert · % rel. Abw. · erw. MU · % Tol · Konformität | `fixq` / `varq` | ja |
  | `4` | wie `3`, Unsicherheit aus `exp_uncert_iso_p` statt `exp_uncert_iso_e` | `fixq` / `varq` | ja |

  Jede Spalte jeder Variante hat eine Datenzelle, und jede Datenzelle steht
  exakt unter ihrem Spaltenkopf — in beiden Kopfstilen. `21` und `22` drucken
  bewusst das andere Spaltenpaar; welches von beiden der Sollwert ist, hängt am
  Toleranzbezug der Prozedur, deshalb gibt es die Varianten überhaupt.

* **Besonderheiten:**
  * Variante `1` druckt den Sollwert in der Spalte `Sollwert / True Value`, die
    ihr Tabellenkopf seit jeher ausweist; bis dahin war die Spalte in beiden
    Kopfstilen ohne Datenzelle und damit immer leer.
  * `ToleranceRange` entscheidet automatisch zwischen ±-Anzeige und
    Min/Max-Spalten.
  * `RoundedRelError` rundet die relative Abweichung auf eine Nachkommastelle;
    `RoundedTolErr` rundet die Toleranzausnutzung auf ganze Prozent und deckelt
    sie bei `>500`. Das Prozentzeichen steht im Spaltenkopf, nicht in der Zelle.
  * `FormattedUncertainty` formatiert wissenschaftliche Schreib­weisen
    (`×10ⁿ`), sofern keine HTML-Markups vorliegen.
  * `ExpUncertaintyDisplay` setzt die erweiterte Messunsicherheit aus
    `exp_uncert`, `exp_uncert_p` und `exp_uncert_u` zusammen (`°C` wird zu `K`);
    die Varianten `3`/`4` ziehen den fertigen Text aus `exp_uncert_iso_e` bzw.
    `exp_uncert_iso_p` vor, sofern er gefüllt ist.
  * Die Konformitätsspalte übersetzt `pass_fail` in die Symbolik der Legende
    (`i.T.`, `?`, `!?`, `!`). Sie erwartet MET/TEAMs Schreibweise (`Pass`,
    `Fail`, `Pass Indeterminate`, `Fail Indeterminate`); alles andere — auch
    ein bereits übersetztes Symbol — druckt eine leere Zelle.
  * **Akkreditierungsumfang (`accred`):** Das `*` der Legende bedeutet
    „Messergebnisse nicht im Akkreditierungsumfang des Kalibrierlaboratoriums"
    und markiert damit die Ausnahme, nicht die Regel. Drei Zustände:

    | `accred` | Bedeutung | Druck |
    | --- | --- | --- |
    | `1`, `y`, `yes`, `ja`, `true` | im Akkreditierungsumfang | kein Zeichen |
    | `0`, `n`, `no`, `nein`, `false` | **nicht** im Umfang, kennzeichnungspflichtig | `*` |
    | leer / nicht gesetzt | keine Aussage erfasst | kein Zeichen |

    Der dritte Zustand ist der Grund, warum die Abfrage `accred` nicht mehr auf
    `0` zurückfallen lässt (`COALESCE(accred, '')`): sonst wäre „nie gepflegt"
    dasselbe wie „außerhalb des Umfangs" und jede in calServer erfasste Zeile
    trüge die Fußnote — die Messwertaufnahme schreibt das Feld nicht. Der
    Schein behauptet nichts, was niemand erfasst hat.
  * Das Zeichen steht in den Varianten `1`, `2`, `22`, `3` und `4` hinter der
    Konformitätsaussage. Variante `21` hat keine Konformitätsspalte und hängt
    es deshalb an die Messbedingung — die Kennzeichnungspflicht gilt in jeder
    Variante.
  * **Zeilenumbruch statt Textverlust:** Jede Zelle des Detailbands wächst mit
    ihrem Inhalt (`textAdjust="StretchHeight"`), alle Zellen einer Zeile werden
    gleich hoch (`stretchType="ContainerHeight"`) und der Text sitzt oben. Ein
    langer Wert läuft damit in die nächste Zeile, statt am Spaltenrand
    abgeschnitten zu werden — betroffen waren vor allem `test_desc`
    („Messbedingungen“, 70 px in Variante `1`), Werte mit Vorsatz und
    ausgeschriebener Einheit (`1234.5678 Milli Ampere`) und die gedeckelte
    Toleranzausnutzung `>500` in der 16 px schmalen Spalte `% Tol`. Kurze
    Zeilen bleiben exakt 14 px hoch, die Seitenaufteilung bestehender Scheine
    ändert sich dadurch nicht.
  * Der Tabellenkopf existiert je `MeasurementDetails`-Variante in einer
    modernen (Standard, ohne umlaufende Rahmen) und einer klassischen
    Ausführung (`ModernResultsHeader=N`); beide sind an den Datenspalten
    der jeweiligen Variante ausgerichtet.
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

### Prozedurtexte tragen Auszeichnung — und zwar eine begrenzte

Die vier Prozedurfelder (`p.calibration_item`, `p.calibration_method`,
`p.procedure_description`, `p.measurement_conditions`) landen in Textfeldern
mit `markup="html"`. JasperReports schickt sie damit durch seinen
Markup-Prozessor (`JEditorPaneHtmlMarkupProcessor`), und der ist **kein
Browser**: Er parst mit Swings `HTMLEditorKit` und übernimmt aus dem Ergebnis
ausschliesslich Zeichenlauf-Attribute.

| Übernommen | Verworfen |
|------------|-----------|
| `b`/`strong`, `i`/`em`, `u`, `s`/`strike`/`del` | Tabellen, Bilder, alles Eingebettete |
| `sub`, `sup` | `text-align`, Einzüge, `class`, alle CSS-Layoutregeln |
| `br`, `p` (Zeilen- und Absatzumbruch) | `div` und Unbekanntes (Inhalt bleibt, Hülle fällt) |
| `ul`, `ol`, `li` (Aufzählungszeichen, Nummerierung) | — |
| `font`/`span` mit Farbe, Grösse, Schriftfamilie; `a href` | — |

Die letzte Zeile ist der Sonderfall: Der Prozessor kann sie, calServer
**schreibt sie trotzdem nicht** in die Spalten. Eine Schriftfamilie aus dem
Markup ersetzt die Berichtsschrift (DejaVu Sans) durch eine, die im PDF nicht
eingebettet ist — Umlaute fallen dann auf ein Ersatzglyph zurück; Überschriften
bringen über Swings Standard-Stylesheet ihre eigene Grösse mit. Der
Prozedur-Editor in calServer bietet deshalb nur die erste Hälfte der linken
Spalte an, und `App\Support\ReportHtml` setzt sie beim Speichern durch.

**Für eine eigene Befüllung dieser Spalten heisst das zweierlei:** Klartext muss
escaped sein — ein „<" verschluckt sonst still den Rest der Zeile („U < 10 V"
druckt als „U") —, und ein Zeilenumbruch muss als `<br/>` kommen, weil `\n` in
HTML ein Leerzeichen ist.

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
