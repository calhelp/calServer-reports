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
  `Standard.jasper`) und die mehrseitige Ergebnisdokumentation (Subreport
  `Results.jasper`).

### Hinweise für den Alltag

* **Sprachwechsel:** Über `Sprache` werden alle Labels und Absätze automatisch
  auf Deutsch oder Englisch gesetzt.
* **QR-Code & Bilder:** `QR_Code_Value` sowie `P_Image_Path` erlauben das
  Einbinden von QR-Codes und Logos (z. B. DAkkS-Logo in der Fußzeile).
* **Beschreibungstexte:** Parameter wie `Cert_description_1` oder
  `Measurements_description_1` enthalten bereits abgestimmte Formulierungen und
  können pro Kunde / Messmittel angepasst werden.
* **Seitenzahlen im Fließtext:** `Results_description` nutzt `msg(..., Seite)`
  und passt die Seitenreferenz beim Rendern automatisch an.

---

## 2. Für Administrator:innen & Entwickler:innen

### Datenquellen & Tabellen

Die Hauptabfrage kombiniert drei Kernbereiche der calServer-Datenbank:

* `$P!{PrefixTable}calibration c` – Zertifikatsdaten inkl. Felder
  `C2301`, `C2307`, `C2327`, `C2308`, `C2311`, `C2312`.
* `$P!{PrefixTable}inventory i` – Messmittelstammdaten (`I4201`–`I4206`, `I4224`).
* `$P!{PrefixTable}customers cu` – Auftraggeber:in für Anschrift und Namen.

### SQL-Auszug

```sql
SELECT COALESCE(NULLIF($P{Cert_field}, ''), COALESCE(c.C2396, "")) AS cert_field,
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

* **`subreports/Standard.jasper`** – listet die eingesetzten Normale inklusive
  Inventarnummer, Hersteller, Typ und Kalibrierstatus.
* **`subreports/Results.jasper`** – erstellt die tabellarische
  Messergebnis-Dokumentation mit Toleranzen, Messunsicherheit und Symbolik.
* Beide Unterberichte benötigen dieselben Parameter (`PrefixTable`, `Sprache`,
  `P_CTAG`, optional `P_Image_Path`) und denselben Datenbank-Connection-Context.

### Vollständige Parameterübersicht

| Parameter | Pflicht | Standardwert | Zweck |
| --- | --- | --- | --- |
| `P_CTAG` | ✅ | leer | Schlüssel der Kalibrierung, steuert alle Haupt- und Unterberichte. |
| `Reportpath` | ✅ | `""` | Basisverzeichnis für Unterberichte (`.../DAKKS-SAMPLE`) inkl. kompilierten `.jasper`-Dateien. |
| `PrefixTable` | ➖ | `""` | Tabellenpräfix für mandantenfähige Installationen (z. B. `cal_`). |
| `Sprache` | ➖ | `Deutsch` | Sprache der Labels und Textbausteine (`Deutsch` / `Englisch`). |
| `QR_Code_Value` | ➖ | `""` | Inhalt für QR-/Barcode-Elemente. |
| `Cert_field` | ➖ | `""` | Optionaler Text für die angezeigte Zertifikatsnummer; leer lassen für den Wert aus `C2396`. |
| `P_Image_Path` | ➖ | `""` | Pfad für Logos/Siegel im Kopf- und Fußbereich. |
| `ReportVersion` | ➖ | `V0.8.2` | Versionskennzeichnung im Titelbereich. |
| `MarkNumber1`, `MarkNumber2` | ➖ | `123456`, `D-K-\nYYYYY-ZZ-N` | Markierungsnummern im Akkreditierungsblock. |
| `ExpUncType` | ➖ | `""` | Freitext für ergänzende Hinweise zur Messunsicherheit. |
| `Cert_description`, `Cert_description_1` | ➖ | vordefiniert | Normativer Vorspann zur Rückführbarkeit und Verbreitung. |
| `Asset_description` | ➖ | vordefiniert | Kurzbeschreibung des kalibrierten Messmittels. |
| `Results_description` | ➖ | sprachabhängig | Hinweis auf Seitenverweise der Messergebnisse. |
| `Measurements_description`, `Measurements_description_1` | ➖ | sprachabhängig | Erläuterungen zur Messunsicherheit/GUM. |
| `Conformity_description_1..3` | ➖ | sprachabhängig | Legenden für Konformitätsaussagen und Symbolik. |
| `Additional_information` | ➖ | sprachabhängig | Hinweise zur DAkkS-Anerkennung. |
| `Calibration_procedure_1`, `Calibration_procedure_2` | ➖ | sprachabhängig | Textbausteine zu den angewendeten Verfahren. |
| `Calibration_document` | ➖ | sprachabhängig | Verweis auf Verfahrensanweisung bzw. QMS-Dokument. |

**Unterberichte**

* `Standard.jrxml`: erwartet `PrefixTable`, `Sprache`, `P_CTAG` (Default: `Deutsch`, Beispiel-CTAG) für die Tabelle der eingesetzten Normale.
* `Results.jrxml`: erwartet `PrefixTable`, `P_CTAG`; optional `Debug` (`N`) für zusätzliche Protokolle.

### Typische Anpassungen

* **Weitere Sprachen** – zusätzliche Locale-Logik über `Sprache` und
  `resourceBundles` ergänzen.
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
  den kompilierten `.jasper`-Dateien zeigt.
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
