# 📄 Auftrags-/Angebotsdokument (`order-sample.jrxml`)

Dieser Report erzeugt kundenfertige Dokumente für Angebote, Aufträge,
Rechnungen oder Lieferungen. Er vereint Kopf- und Adressdaten, Positionslisten,
Rabatte sowie Summenlogik. Die Vorlage liegt unter
`ORDER-SAMPLE/main_reports/order-sample.jrxml` und bindet den Unterbericht
`Statistics.jasper` für Summen- und Steuerberechnungen ein.

| Zielgruppe | Nutzen |
| --- | --- |
| **Normale Nutzer:innen** | Liefert ein fertig formatiertes Dokument mit allen relevanten Kunden-, Liefer- und Rechnungsinformationen. |
| **Administrator:innen / Entwickler:innen** | Bietet eine komplexe SQL-Abfrage als Ausgangspunkt für individuelle Dokumenttypen und Automatisierungen. |

---

## 🚀 Schritt-für-Schritt: Dokument erzeugen

1. **Report starten** – in der calServer-Reportverwaltung oder über JasperStarter.
2. **Auftragskontext setzen** – `Auftragsid` (Pflicht) und optional
   `Auftragsnummer` mit dem gewünschten Geschäftsvorgang befüllen.
3. **Dokumenttyp wählen** – `Dokumenttyp` bestimmt Texte/Labels (z. B. Angebot,
   Auftrag, Rechnung, Lieferung) und steuert logische Verzweigungen im Layout.
4. **Artikeltypen filtern** – die Parameter `Articletype1` bis `Articletype3`
   definieren, welche Positionen aus `article` übernommen werden (Standard:
   Inventar- und Artikelpositionen).
5. **Kontaktdaten prüfen** – optionale Parameter wie `Return_address`,
   `Report_mail_address` oder `Report_phone_number` ergänzen Absenderdaten im
   Dokument.
6. **Report ausgeben** – PDF empfohlen; XLSX/HTML stehen ebenfalls zur Verfügung.

---

## 1. Für normale Nutzer:innen

### Was zeigt der Bericht?

* **Kopfbereich** – Dokumenttyp, Datum (`CurrentDate`), Referenzen und eigene
  Kontaktdaten.
* **Adressblöcke** – automatische Auswahl von Kunden-, Rechnungs- und
  Lieferadresse inkl. Ansprechpartner:innen. Fehlen spezielle Kontakte, werden
  Fallbacks aus den Kundenstammdaten genutzt.
* **Positionsliste** – sortiert nach Positionsnummer und Artikeltyp, inklusive
  Menge, Einheit, Einzelpreis, Rabatt und Zwischensummen.
* **Inventarbezug** – wenn Artikel mit Messmitteln verknüpft sind, wird die
  Inventarbezeichnung (`inventory_name`, `I4204`, `I4202`, `I4206`) angezeigt.
* **Summenbereich** – netto, Rabatt, Steuer und Gesamtsumme (über den
  Subreport `Statistics.jasper`) sowie ein freier Textblock aus
  `Report_description` (z. B. Zahlungsbedingungen).

### Alltagstipps

* **Sprachumschaltung:** Über `Sprache` stehen deutsche und englische Labels zur
  Verfügung. Weitere Sprachen können über Resource-Bundles ergänzt werden.
* **Absenderdaten:** `Return_address`, `Report_mail_address` und
  `Report_phone_number` füllen den Briefkopf ohne Layoutänderungen.
* **Artikelreihenfolge:** `Articletype*` steuert, welche Positionsarten (z. B.
  `inventory`, `article`, Dienstleistungen) angezeigt werden.
* **Freitext:** `Report_description` wird am Ende des Dokuments ausgegeben und
  eignet sich für Zahlungs- oder Lieferbedingungen.

---

## 2. Für Administrator:innen & Entwickler:innen

### Datenquellen & Tabellen

Die Hauptabfrage verbindet zahlreiche Kernmodule des calServer:

* `$P!{PrefixTable}booking b` – Kopf- und Bewegungsdaten des Vorgangs.
* `$P!{PrefixTable}article a` – Positionen, Preise, Mengen, Rabatte.
* `$P!{PrefixTable}collective_invoices ci` – Sammelrechnungs-Bezüge.
* `$P!{PrefixTable}customers c/bc/dc` – Kunden-, Rechnungs- und Lieferanschriften.
* `$P!{PrefixTable}contact tc/ti/td` – Ansprechpartner:innen für die jeweiligen
  Adressarten.
* `$P!{PrefixTable}standard_article sa`, `$P!{PrefixTable}prices p`,
  `$P!{PrefixTable}types t` – Artikelstammdaten und Preisgruppen.
* `$P!{PrefixTable}inventory i` – Messmittelinformationen für inventarbasierte
  Positionen.

### SQL-Auszug

```sql
SELECT b.uID,
       a.article_type,
       CONCAT_WS(" ", c.K4613, c.K4602) AS customer_name,
       CONCAT_WS("\n", ti.label, ti.name, ti.street) AS billing_contact,
       IF(a.discount IS NULL, 0, ROUND(a.discount, 2)) AS discount
FROM   $P!{PrefixTable}booking b
LEFT JOIN $P!{PrefixTable}article a
       ON (b.uID = a.booking_uID OR ci.other_booking_uID = a.booking_uID)
LEFT JOIN $P!{PrefixTable}collective_invoices ci ON ci.invoice_uID = b.uID
LEFT JOIN $P!{PrefixTable}customers c ON b.customer_KTAG = c.KTAG
LEFT JOIN $P!{PrefixTable}contact ti ON ti.uID = b.invoice_contact_id
WHERE  b.uID = $P{Auftragsid};
```

### Subreport & Summenlogik

* **`subreports/Statistics.jasper`** ermittelt Zwischensummen, Rabatt,
  Steuerbeträge pro Steuersatz sowie die Gesamtsumme. Über den Parameter
  `Report_description` wird außerdem ein freier Textblock ausgegeben.
* Der Unterbericht erhält sämtliche Artikeltyp-Parameter (`Articletype1-3`) und
  `Dokumenttyp`, um gleiche Filterlogik wie der Hauptreport zu gewährleisten.

### Parameterübersicht (Auswahl)

| Parameter | Funktion |
| --- | --- |
| `Auftragsid` | **Pflicht** – eindeutige ID des Vorgangs (`booking.uID`). |
| `Auftragsnummer` | Optionale Anzeige der Buchungsnummer (`b.number`). |
| `Dokumenttyp` | Steuert Labels/Logik (z. B. Angebot, Auftrag, Rechnung). |
| `Articletype1-3` | Filtert erlaubte Positionsarten im SELECT. |
| `Reportpath` | Pfad zum Unterbericht `Statistics.jasper`. |
| `PrefixTable` | Tabellenpräfix für mandantenfähige Installationen. |
| `Return_address`, `Report_mail_address`, `Report_phone_number` | Ergänzen Absenderdaten im Kopf. |
| `Report_description` | Freitext für Geschäftsbedingungen. |
| `Sprache` | Setzt Labels (Deutsch/Englisch). |
| `ReportVersion` | Kennzeichnet die Version im Dokumentkopf. |

### Erweiterungsideen

* **Zusätzliche Artikelgruppen** – weitere Parameter (`Articletype4` …) oder
  SQL-Bedingungen ergänzen.
* **Mehrsprachige Inhalte** – statische Texte in Resource-Bundles auslagern oder
  über `Sprache` erweitern.
* **Logo & Briefpapier** – Hintergrundbilder oder `P_Image_Path`-Konzepte aus
  anderen Reports übernehmen.
* **Automatisierte Serienläufe** – JasperStarter oder GitHub Actions nutzen, um
  Dokumente stapelweise zu erzeugen.

---

## 3. Troubleshooting & Tipps

* **Keine Positionen?** – prüfen, ob die Artikeltypen mit den realen Werten in
  `article.article_type` übereinstimmen und ob `a.uID` nicht `NULL` ist.
* **Falsche Adresse:** falls spezielle Kontakte fehlen, werden Fallbacks genutzt –
  ggf. `customer_contact_id`, `invoice_contact_id` oder `delivery_contact_id`
  im calServer pflegen.
* **Rabatte wirken nicht:** der Unterbericht berechnet Rabatte über `W4114`; ist
  der Wert `0` oder `NULL`, wird kein Abzug ausgewiesen.
* **Mehrsprachigkeit:** nicht erkannte Sprachwerte fallen auf Deutsch zurück –
  den Parameter exakt schreiben (`Deutsch`, `Englisch`).
* **Leere Summen:** sicherstellen, dass `Reportpath` korrekt auf das kompilierte
  Unterreport-Verzeichnis zeigt.

---

Dieser README liefert eine inhaltliche und technische Orientierung für das
Auftrags-/Angebotsdokument.
