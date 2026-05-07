# 🧾 Kalibrierkontrollblatt

Dieses Verzeichnis enthält die Reportvorlagen für das **Kalibrierkontrollblatt** – ein kompaktes Übersichtsdokument mit Geräte-/Kundendaten und der Kalibrierhistorie als Unterbericht.

## Struktur
- `main_reports/kalibrierkontrollblatt.jrxml` – Hauptbericht (Geräte- und Kundendaten, Rahmenlayout).
- `subreports/Calibration-3.jrxml` – Unterbericht mit der Liste der Kalibrierungen zum jeweiligen Messmittel (`MTAG`).

## Wichtige Parameter
| Parameter      | Beschreibung                                                                 |
| -------------- | ---------------------------------------------------------------------------- |
| `Reportpath`   | Verzeichnispfad zur Vorlage im calServer (Standardwert leer, wird gesetzt).  |
| `PrefixTable`  | Präfix der Inventartabelle, z. B. `thermo_`.                                 |
| `Sprache`      | Anzeigesprache (`Deutsch` oder `English`).                                   |
| `P_MTAG`       | Eindeutiger Messmittel-Tag, für den die Kalibrierhistorie geladen wird.      |

## Hinweise zum Deploy
- Beim Kompilieren muss der Unterbericht als `Calibration-3.jasper` im Unterordner `subreports` liegen, damit der Hauptreport ihn findet.
- Die Vorlagen sind für **JasperReports Library 6.20.6** (Jaspersoft Studio 7.0.2.final) ausgelegt.
- Der Unterbericht erwartet die calServer-Tabelle `calibration` mit den Spalten `C2301`, `C2303`, `C2307`, `C2314` und `C2341`. Diese Spalten sind installationsabhängig (Custom Fields) – fehlen sie, schlägt das Rendern mit einer `Unknown column`-Meldung fehl.
- Die `ORDER BY`-Klausel referenziert die Tabelle ohne hartkodierten Schemanamen (`calibration.\`C2301\``), damit der Report unabhängig vom Datenbanknamen (z. B. `calserver`, `metbase`) funktioniert.

## Lokaler Testaufruf

```bash
cd KALIBRIERKONTROLLBLATT/main_reports
jasperstarter process kalibrierkontrollblatt.jrxml \
  -o "../pdf/_" -f pdf \
  -P REPORT_LOCALE=de_DE @kalibrierkontrollblatt_params.properties \
  -t mysql -u <USER> -p <PASS> -H <HOST> -n <DBNAME>
```

Stelle sicher, dass `<DBNAME>` auf die tatsächliche calServer-Datenbank zeigt (z. B. `calserver` oder `metbase`).
