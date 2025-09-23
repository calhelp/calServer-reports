# 🗂️ Feld-/Sprachzuordnung (`field-names-language-overview.jrxml`)

Dieser Report liefert eine strukturierte Übersicht aller Felder eines Schemas und
zeigt, welche Übersetzungen für eine ausgewählte Sprache hinterlegt sind. Er
unterstützt Administrator:innen dabei, Übersetzungsstände zu prüfen, fehlende
Labels zu identifizieren und gemeinsam mit Fachbereichen Mehrsprachigkeit im
calServer zu pflegen.

---

## 🔍 Funktionsumfang

* Gruppiert alle Felder nach Tabelle/Modul.
* Listet Standardbezeichnungen, Übersetzungen, Datentyp und Pflichtkennzeichen.
* Zeigt Hinweise (`hint`/Hilfetexte) inkl. Sprachvariante.
* Markiert fehlende Übersetzungen mit dem Platzhalter `(keine Übersetzung)`.
* Enthält Zeitstempel der letzten Aktualisierung aus der Übersetzungstabelle.

---

## ⚙️ Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `SchemaName` | String | Pflicht. Name des logischen Schemas/Moduls (z. B. `inventory`). |
| `LanguageCode` | String | Pflicht. Sprachkürzel nach ISO-639-1 (`de`, `en`, …). `NULL` = alle Sprachen. |
| `PrefixTable` | String | Optional. Tabellenpräfix bei mandantenfähigen Installationen (z. B. `tenant1_`). |
| `ReportVersion` | String | Optional. Versionstext im Kopfbereich (Standard: `v1.0`). |

> 💡 **SQL-Parameterbindung:** `PrefixTable` wird als Tabellenpräfix in der
> SQL-Abfrage verwendet (`$P!{PrefixTable}`). `SchemaName` und `LanguageCode`
> filtern Datensätze via Prepared-Statement (`$P{...}`).

---

## 🗄️ Datenbasis

Die Vorlage greift auf folgende Tabellen zu:

* `${PrefixTable}field_metadata`
  * Stammdaten der Felder, inklusive technischem Schlüssel, Datentyp und
    Standardlabel.
* `${PrefixTable}field_metadata_translation`
  * Übersetzungen/Sprachvarianten der Feldlabels und Hilfetexte.

> ⚠️ Passe Tabellen- und Spaltennamen an deine calServer-Instanz an, falls sie
> abweichen. Die Struktur orientiert sich an der Standardinstallation.

---

## 🧾 Ausgabeformat

| Bereich | Inhalt |
| --- | --- |
| **Reporttitel** | "Feld- & Sprachübersicht" + Schema & Sprache. |
| **Gruppierung** | Je Tabelle ein Abschnitt mit Überschrift. |
| **Detailzeile** | Feldname, Standardlabel, Übersetzung, Datentyp, Pflicht, Hinweis & Änderungsdatum. |
| **Zusammenfassung** | Gesamtanzahl der gefundenen Felder. |

---

## ▶️ Nutzung

1. Report in Jaspersoft Studio oder calServer hochladen.
2. Parameter `SchemaName` und `LanguageCode` setzen.
3. Optional: `PrefixTable` für mandantenfähige Datenbanken ausfüllen.
4. Report ausführen – empfohlenes Format: PDF oder XLSX für Weiterverarbeitung.
5. Fehlende Übersetzungen im Ergebnis prüfen und im calServer nachpflegen.

---

## 🔗 Verknüpfungen & Subreports

* Der Report kommt ohne Subreports aus.
* Solltest du ergänzende Detailansichten (z. B. Historie, Feldverwendung) bauen,
  lege die JRXML-Dateien im Ordner `FIELD-NAMES/subreports/` ab und binde sie
  über zusätzliche Parameter (`Reportpath`, `SubreportPath`, …) ein.

---

## 🧪 Tests & Validierung

* SQL-Abfrage mit Beispielparametern (`SchemaName=inventory`, `LanguageCode=de`)
  gegen eine Testdatenbank ausführen.
* Prüfen, dass nur JRXML-Dateien in ZIP-Pakete aufgenommen werden (GitHub
  Actions erledigen das automatisch mit dem aktualisierten Workflow).

Viel Erfolg beim Einsatz des Feld-/Sprachreports! 💬
