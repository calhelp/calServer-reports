# 📘 Inventory Report (`inventory-sample.jrxml`)

Dieser Report liefert eine kompakte **Übersicht über ein Messmittel** und vereint Stammdaten,
Nutzungs- und Kalibrierungsinformationen. Die Vorlage liegt im Verzeichnis
`INVENTORY-SAMPLE/main_reports/inventory-sample.jrxml`.

| Zielgruppe | Nutzen |
| --- | --- |
| **Normale Nutzer:innen** | Schneller Überblick über Gerätedaten, Eigentümer, aktuelle Nutzung und Kalibrierstatus. |
| **Administrator:innen / Entwickler:innen** | Technische Details zu Datenquellen, SQL-Query, Parametern und Erweiterungsmöglichkeiten. |

---

## 🚀 Schritt-für-Schritt: Bericht erzeugen

1. **Report starten** – z. B. direkt im calServer oder per JasperStarter.
2. **Gerät auswählen** – Parameter `P_MTAG` mit der gewünschten Messmittelnummer füllen.
3. **Ausgabeformat wählen** – typischerweise `PDF`, optional weitere Jasper-Formate.
4. **Bericht prüfen** – Gerätedaten, Eigentümer, aktueller Nutzender, Barcode/QR-Code und letzte Kalibrierung erscheinen kompakt auf einer Seite.

---

## 1. Für normale Nutzer:innen

### Was zeigt der Bericht?

* **Gerätedaten** – Inventarnummer, Seriennummer, Hersteller, Typ.
* **Eigentümer (Kunde)** – Firma oder Abteilung, der das Gerät zugeordnet ist.
* **Nutzende Person** – letzter Standorteintrag, inklusive Ansprechpartner.
* **Standortadresse** – Anschrift bzw. Abteilung aus der jüngsten Standortbuchung.
* **Barcode/QR-Code** – direkt scannbar für Inventur und Geräteverwaltung.
* **Kalibrierung** – Datum und Bearbeiter der letzten Kalibrierung.

### Anpassungsideen ohne Programmierung

* **Felder verschieben oder ausblenden** – per Drag & Drop im Layout (Jaspersoft Studio).
* **Beschriftungen ändern** – z. B. „Kunde“ → „Auftraggeber“.
* **Adressdarstellung reduzieren** – nur Name anzeigen, falls Straße/PLZ nicht benötigt werden.
* **Sprache wechseln** – über den Parameter `Sprache` (DE/EN) Labels austauschen.

---

## 2. Für Administrator:innen & Entwickler:innen

### Datenquellen & Tabellen

Der Report greift auf folgende Tabellen der Datenbank `calserver` zu:

* `$P!{PrefixTable}inventory i` – Stammdaten zum Messmittel.
* `$P!{PrefixTable}customers c` – Eigentümer:in (Auftraggeber:in).
* `$P!{PrefixTable}barcode b` – Barcode-/QR-Code-Werte.
* `$P!{PrefixTable}location l` – letzter Standorteintrag (`L2815 = 1`).
* `$P!{PrefixTable}customers uc` – aktuelle nutzende Person (`l.L2801 = uc.KTAG`).
* `$P!{PrefixTable}calibration cal` – letzte Kalibrierung (`C2339 = 1`).

### SQL-Query (vereinfacht)

```sql
SELECT
  -- Inventory
  i.I4201 AS inv_I4201,
  i.I4202 AS inv_I4202,
  -- ... weitere Felder ...
  -- Customer (Eigentümer)
  c.K4602 AS cust_K4602,
  c.K4603 AS cust_K4603,
  -- ...
  -- Barcode
  b.barcode_value AS bc_barcode_value,
  b.barcode_type  AS bc_barcode_type,
  -- Location
  l.L2801 AS loc_L2801,
  l.L2802 AS loc_L2802,
  l.L2809 AS loc_L2809,
  -- ...
  -- User-Customer (aktueller Nutzender)
  uc.K4602 AS ucust_K4602,
  uc.K4603 AS ucust_K4603,
  uc.K4604 AS ucust_K4604,
  uc.K4605 AS ucust_K4605,
  uc.K4606 AS ucust_K4606,
  -- Calibration
  cal.C2301 AS cal_C2301,
  cal.C2307 AS cal_C2307,
  cal.C2314 AS cal_C2314
  -- ...
FROM $P!{PrefixTable}inventory i
LEFT JOIN $P!{PrefixTable}customers c  ON i.KTAG = c.KTAG
LEFT JOIN $P!{PrefixTable}barcode b    ON i.MTAG = b.barcode_key
LEFT JOIN $P!{PrefixTable}location l   ON l.MTAG = i.MTAG AND l.L2815 = 1
LEFT JOIN $P!{PrefixTable}customers uc ON l.L2801 = uc.KTAG
LEFT JOIN $P!{PrefixTable}calibration cal ON cal.MTAG = i.MTAG AND cal.C2339 = 1
WHERE i.MTAG = $P{P_MTAG};
```

### Feld-Präfixe im Report

* `inv_*` → Felder aus `inventory`
* `cust_*` → Eigentümer:in aus `customers`
* `bc_*` → Barcode-/QR-Code-Werte
* `loc_*` → aktueller Standort (location)
* `ucust_*` → aktuelle nutzende Person
* `cal_*` → letzte Kalibrierung

### Beispiel: Ausgabe der nutzenden Person

```java
(
  ($F{ucust_K4602} != null ? $F{ucust_K4602} : "") +
  ($F{ucust_K4603} != null ? " " + $F{ucust_K4603} : "") +
  ($F{ucust_K4604} != null ? "\n" + $F{ucust_K4604} : "") +
  ($F{ucust_K4605} != null ? " " + $F{ucust_K4605} : "") +
  ($F{ucust_K4606} != null ? " " + $F{ucust_K4606} : "")
) +
($F{loc_L2809} != null
  ? "\nStart: " + new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm").format($F{loc_L2809})
  : ""
)
```

### Parameterübersicht

| Parameter | Beschreibung |
| --- | --- |
| `Reportpath` | Basisverzeichnis, in dem Subreports gesucht werden. |
| `PrefixTable` | Optionales Tabellenpräfix (z. B. `cal_`). |
| `Sprache` | Sprachumschaltung für Labels (`DE` / `EN`). |
| `QR_Code_Value` | Daten oder URL für den QR-Code. |
| `P_MTAG` | **Pflichtparameter** – eindeutige Geräte-ID (Messmittelnummer). |

---

## 3. Anpassungen & Erweiterungen

* **Neue Datenfelder** – im `SELECT` ergänzen und als `<field>` im JRXML anlegen.
* **Layout-Updates** – Texte, Reihenfolge, Farben frei im Designer bearbeiten.
* **Adressformat** – wahlweise im SQL per `CONCAT_WS` oder direkt im Bericht zusammenstellen.
* **Zusätzliche Tabellen** – per `LEFT JOIN` anbinden (z. B. Dokumente, Messwerte).

---

## 4. Troubleshooting & Tipps

* **Leere Felder?** – Prüfen, ob die Werte in der Datenbank gepflegt sind.
* **Mehrere Standort- oder Kalibrierungseinträge?** – Der Report holt immer nur den aktuellsten (`L2815 = 1`, `C2339 = 1`).
* **Performance optimieren** – bei großen Datenmengen empfiehlt sich ein vorbereiteter View in MySQL.

---

Damit ist der Bericht sowohl für **Endanwender:innen verständlich** als auch für **Administrator:innen/Entwickler:innen** leicht anpassbar dokumentiert.
