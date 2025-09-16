# Unterbericht `Statistics.jrxml`

Der Unterbericht `Statistics.jrxml` liefert sämtliche Summen-, Rabatt- und
Steuerberechnungen für das Hauptdokument `order-sample.jrxml`. Er wird im
Gruppenfuß des Hauptberichts eingebunden und nutzt dieselben Parameter für
Tabellenpräfix, Dokumenttyp und Artikeltypen.

---

## Funktionsumfang

* **Positionensummen:** Gruppiert alle Positionen eines Auftrags (`booking.uID`)
  und berechnet Netto-Zwischensummen je Steuersatz.
* **Rabattlogik:** Nutzt das Feld `W4114` aus `booking` als prozentuale Angabe
  und zieht den Wert (`discount`) automatisch von den Zwischensummen ab.
* **Steuerberechnung:** Multipliziert die Nettoanteile je Steuersatz (`tax`) und
  bildet Gesamtsteuer (`Order_Total_Tax`).
* **Endsumme:** Aggregiert Netto-, Steuer- und Rabattanteile zu `Order_Total`
  und gibt sie mit fett gedruckter Beschriftung aus.
* **Freitext:** Gibt den Inhalt des Parameters `Report_description` als
  abschließenden Hinweis- oder AGB-Block aus.

---

## SQL-Basis

```sql
SELECT tax,
       ROUND((SUM(old_total)) * tax / 100, 2) AS total_tax,
       SUM(old_total) AS total,
       total_new,
       IF(W4114 > 0, W4114, 0) AS W4114,
       IF(W4114 > 0, SUM(old_total) * W4114 / 100, 0) AS discount
FROM (
    SELECT b.uID,
           b.W4114,
           ROUND(a.tax) AS tax,
           ROUND(a.quantity * a.price - a.quantity * a.price *
                 (IF(a.discount IS NULL, 0, a.discount)) / 100, 2) AS old_total
    FROM $P!{PrefixTable}booking b
    LEFT JOIN $P!{PrefixTable}collective_invoices ci ON ci.invoice_uID = b.uID
    LEFT JOIN $P!{PrefixTable}article a ON (b.uID = a.booking_uID OR
         ci.other_booking_uID = a.booking_uID)
        AND a.article_type IN ('$P!{Articletype1}', '$P!{Articletype2}', '$P!{Articletype3}')
    WHERE b.uID = $P{Auftragsid} AND a.uID IS NOT NULL
) AS t
LEFT JOIN (
    SELECT b.uID,
           SUM(ROUND(a.quantity * a.price - a.quantity * a.price *
               (IF(a.discount IS NULL, 0, a.discount)) / 100, 2)) AS total_new
    FROM $P!{PrefixTable}booking b
    LEFT JOIN $P!{PrefixTable}collective_invoices ci ON ci.invoice_uID = b.uID
    LEFT JOIN $P!{PrefixTable}article a ON (b.uID = a.booking_uID OR
         ci.other_booking_uID = a.booking_uID)
        AND a.article_type IN ('$P!{Articletype1}', '$P!{Articletype2}', '$P!{Articletype3}')
    WHERE b.uID = $P{Auftragsid} AND a.uID IS NOT NULL
) AS t1 ON t.uID = t1.uID
GROUP BY tax;
```

---

## Wichtige Parameter & Variablen

| Name | Beschreibung |
| --- | --- |
| `PrefixTable` | Tabellenpräfix; muss mit dem Hauptreport übereinstimmen. |
| `Sprache` | Steuert alle Labels (Deutsch/Englisch). |
| `Dokumenttyp` | Passt Summenbeschriftungen an (`Angebot`, `Auftrag`, `Rechnung`, `Lieferung`). |
| `Articletype1-3` | Legen fest, welche Positionen in die Berechnung eingehen. |
| `Auftragsid` | Referenziert den aktuellen `booking`-Datensatz. |
| `Report_description` | Übergibt Freitext an den Schlussbereich. |
| `DETAIL_*` Variablen | Liefern lokalisierte Beschriftungen für Netto-, Rabatt- und Gesamtsummen. |
| `Sum_Netto`, `Sum_Discount`, `Order_Total`, `Order_Total_Tax` | Aggregierte Beträge zur Anzeige im Fuß. |

---

## Anpassungshinweise

* **Weitere Steuersätze:** Zusätzliche Gruppen oder Variablen können angelegt
  werden, falls landesspezifische Steuermodelle (z. B. 0 %, 7 %, 19 %) separat
  dargestellt werden sollen.
* **Währungsausgabe:** Standardmäßig werden Werte als Dezimalzahl mit "€"
  dargestellt. Über Formatmasken (`pattern="#,##0.00 ¤"`) lassen sich weitere
  Währungen einbinden.
* **Rabattlogik erweitern:** Bei Mischrabatten (Fixbetrag + Prozent) können
  zusätzliche Variablen angelegt und in `Order_Total` berücksichtigt werden.
* **Mehrsprachige Hinweise:** Freitext (`Report_description`) kann für andere
  Sprachen per Parameter oder Resource-Bundle angepasst werden.

---

Der Unterbericht bildet das finanzielle Rückgrat des Auftragsdokuments und kann
bei Bedarf leicht auf weitere Geschäftsprozesse angepasst werden.
