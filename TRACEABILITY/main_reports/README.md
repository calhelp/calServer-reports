# Traceability Reports (Rückführbarkeit)

Dieses Verzeichnis enthält zwei eigenständige Berichte zur rekursiven
Rückführbarkeits-Analyse von Kalibrierungen. Beide Reports nutzen
MySQL-8-CTEs (`WITH RECURSIVE`) und können direkt über JasperStarter oder den
calServer ausgeführt werden.

| Zielgruppe | Nutzen |
| --- | --- |
| **Qualitätsmanagement** | Lückenlose Rückführbarkeit für Audits nachweisen oder betroffene Geräte bei Normalen-Abweichungen identifizieren. |
| **Administrator:innen / Entwickler:innen** | Dokumentierte SQL-Rekursion, Parametrisierung und Layout für eigene Erweiterungen. |

---

## Berichte im Überblick

### `Forward_Trace.jrxml` – Wirkungsanalyse / Impact Analysis

* **Eingabe:** MTAG eines Standards (Referenznormal).
* **Ergebnis:** Alle Instrumente (DUTs), die direkt oder indirekt mit diesem
  Standard kalibriert wurden – rekursiv über beliebig viele Stufen.
* **Anwendungsfall:** Ein Standard fällt aus der Toleranz. Welche Geräte sind
  potenziell betroffen und müssen nachkalibriert werden?

### `Backward_Trace.jrxml` – Rückführungskette / Traceability Chain

* **Eingabe:** MTAG eines DUT (Device Under Test).
* **Ergebnis:** Die vollständige Standardkette aufwärts bis zum höchsten
  Referenznormal – rekursiv über beliebig viele Stufen.
* **Anwendungsfall:** Audit-Nachweis der lückenlosen messtechnischen
  Rückführbarkeit eines kalibrierten Instruments.

---

## Parameter

| Name | Typ | Pflicht | Standard | Beschreibung |
| --- | --- | --- | --- | --- |
| `instrumentId` | String | Ja | — | MTAG des Start-Instruments (Standard bei Forward Trace, DUT bei Backward Trace). |
| `maxDepth` | String | Nein | `10` | Maximale Rekursionstiefe. Wird in der SQL-Abfrage per `CAST(... AS SIGNED)` konvertiert. |
| `PrefixTable` | String | Nein | `""` | Tabellenpräfix für Mandantentrennung (z. B. `thermo_`). |
| `Sprache` | String | Nein | `Deutsch` | Steuert die Spaltenüberschriften (`Deutsch` / `Englisch`). |

### Beispiel: JasperStarter

```bash
jasperstarter process Forward_Trace.jrxml \
  -o "../pdf/Forward-Trace" -f pdf \
  -t mysql -H mysql_db -n calserver -u user -p pass \
  -P instrumentId=0038e950-df7f-bf73-f5d7-fc371a1a94f0 \
     maxDepth=10 \
     PrefixTable=thermo_ \
     Sprache=Deutsch \
     REPORT_LOCALE=de_DE
```

---

## Spalten-Layout (A4 Querformat)

Beide Reports verwenden dasselbe Layout mit elf Spalten:

| # | DE-Bezeichnung | EN-Bezeichnung | Datenquelle | Breite (px) |
| --- | --- | --- | --- | --- |
| 1 | Tiefe | Depth | `depth` | 35 |
| 2 | Inv.-Nr. | Asset No. | `I4201` | 70 |
| 3 | Seriennr. | Serial No. | `I4202` | 65 |
| 4 | Beschreibung | Description | `I4203` | 120 |
| 5 | Hersteller | Manufacturer | `I4206` | 65 |
| 6 | Modell | Model | `I4207` | 55 |
| 7 | Kal.-Datum | Cal. Date | `C2301` | 65 |
| 8 | Erg. | Result | `C2323` | 40 |
| 9 | Zertifikat-Nr. | Certificate No. | `C2308` | 75 |
| 10 | Fälligkeit | Due Date | `C2303` | 65 |
| 11 | Kal.-Kennz. | Cal. Mark | `C2364` | 147 |

Die Beschreibungsspalte wird je Tiefenstufe automatisch eingerückt.

---

## SQL-Logik

Beide Berichte nutzen `WITH RECURSIVE`-CTEs (MySQL 8+):

* **Forward Trace:** Anker = alle DUTs, deren aktive Kalibrierung (`C2339 = 1`)
  den gegebenen Standard in der `standards`-Tabelle referenziert (`C2430`).
  Rekursion: Jedes gefundene DUT kann selbst als Standard gedient haben.

* **Backward Trace:** Anker = alle Standards der aktiven Kalibrierung des
  gegebenen DUTs. Rekursion: Jeder Standard hat selbst eine aktive Kalibrierung,
  deren eingesetzte Standards ermittelt werden.

### Zyklen-Vermeidung

Theoretisch kann ein zirkulärer Verweis auftreten (A kalibriert B, B kalibriert A).
Die Queries verhindern Endlosschleifen durch:

1. **`visited_path`** – kommaseparierter String aller bereits besuchten MTAGs.
2. **`FIND_IN_SET(neuer_MTAG, visited_path) = 0`** – prüft, ob ein MTAG bereits
   besucht wurde.
3. **`depth < CAST($P{maxDepth} AS SIGNED)`** – Hard-Limit als zusätzliche
   Sicherheit.

### Performance-Hinweise

* Die `standards`-Tabelle hat Indizes auf `C2430`, `CTAG` und `MTAG`.
* `calibration` hat einen kombinierten Index auf (`C2339`, `MTAG`).
* Bei großen Datenbeständen kann `maxDepth` auf 5–7 begrenzt werden.

---

## Technische Details

* **JasperReports:** 6.20.6 / Jaspersoft Studio 7.0.2
* **Schrift:** DejaVu Sans, Identity-H-Encoding (nicht eingebettet)
* **Seitenformat:** A4 Querformat (842 × 595 px), Ränder 20 px
* **NULL-Sicherheit:** `COALESCE()` in SQL, `isBlankWhenNull="true"` im Layout
* **Zweisprachige Spaltenköpfe:** Deutsch (fett, 8 pt) + Englisch (kursiv, 7 pt)
* **Datumformat:** `dd.MM.yyyy`
* **Paginierung:** „Seite X / Y" in der Fußzeile
