# 📑 calServer Reports

**Willkommen beim Community-Projekt für calServer Reportvorlagen!**  
In diesem Repository bündeln wir Beispielberichte (JRXML) für den calServer, schaffen einen Raum für gemeinsames Bugfixing, aktiven Austausch und die nachhaltige Weiterentwicklung von Reportvorlagen.

> **Hinweis:** Dieses Projekt richtet sich an alle calServer-Kund:innen und Anwender:innen, die Reports erstellen, anpassen oder verbessern möchten. Ziel ist es, die Qualität, Vielfalt und Praxistauglichkeit der Reports kontinuierlich zu steigern.

---

## 🌟 Übersicht

- [Was ist dieses Projekt?](#was-ist-dieses-projekt)
- [Projektstruktur & Beispielberichte](#projektstruktur--beispielberichte)
- [Voraussetzungen](#voraussetzungen)
- [Berichte im calServer hochladen](#berichte-im-calserver-hochladen)
- [Skripte für Upload und Automatisierung](#skripte-für-upload-und-automatisierung)
- [Repository klonen & Arbeiten mit GitHub Actions](#repository-klonen--arbeiten-mit-github-actions)
- [Ausblick: calServer V2 und die Zukunft der Reportvorlagen](#ausblick-calserver-v2-und-die-zukunft-der-reportvorlagen)
- [Contributing & Community](#contributing--community)
- [Fehler melden & Support](#fehler-melden--support)
- [Lizenz](#lizenz)
- [Kontakt & Dank](#kontakt--dank)

---

## Was ist dieses Projekt?

Dieses Repository ist der zentrale Ort zur **gemeinsamen Entwicklung, Pflege und Verbesserung von JasperReports-Vorlagen (JRXML)** für den calServer.  

Es bietet:

- **Beispielreports** zur Orientierung und als Startpunkt für eigene Anpassungen
- **Ordnerstrukturen für verschiedene Anwendungsfälle** (z. B. DAKKS-Berichte, Auftragsberichte)
- **Community-getriebene Fehlerbehebung** (Bugfixing) und Feature-Requests
- **Hilfestellung beim Hochladen, Testen und Deployen von Reports**

---

## Projektstruktur & Beispielberichte

Die bereitgestellten Verzeichnisse gliedern sich wie folgt:

```text
DAKKS-SAMPLE/
├── fonts/              # Schriftarten (DejaVu) für konsistente PDF-Ausgabe
├── main_reports/       # Hauptberichte, z. B. vollständige Kalibrierscheine
├── subreports/         # Unterberichte, z. B. Tabellen, Fußzeilen, Messwerte
└── preview.jpg         # Vorschaubild des Beispielreports

DCC/
├── fonts/              # Schriftarten für den DCC-Report
├── main_reports/       # Digitaler Kalibrierschein (DCC) mit XML-Schema
└── subreports/         # Unterberichte analog zum DCC-Hauptreport

DELIVERY-STANDALONE/
├── main_reports/       # Eigenständiger Lieferschein-Report
└── subreports/         # Unterbericht für Kopf-/Adressblock

FIELD-NAMES/
├── main_reports/       # Übersichten zu Feldbezeichnungen & Sprachvarianten
└── subreports/         # Platz für optionale Detail- oder Ergänzungsreports

INVENTORY-SAMPLE/
├── main_reports/       # Messmittelberichte & Inventarlisten
└── subreports/         # Unterberichte für Messwerte, Historien usw.

KALIBRIERKONTROLLBLATT/
├── main_reports/       # Kalibrierkontrollblatt (Geräte- und Kundendaten)
└── subreports/         # Kalibrierhistorie als Unterbericht

ORDER-SAMPLE/
├── main_reports/       # Berichte für Aufträge, z. B. Angebots- oder Auftragsdokumente
└── subreports/         # Unterberichte wie Positionslisten oder Summenfelder

TRACE-FORWARD/
├── main_reports/       # Wirkungsanalyse: betroffene Geräte bei Normalen-Abweichung
│   └── Forward_Trace.jrxml
└── subreports/

TRACE-BACKWARD/
├── main_reports/       # Rückführungskette: lückenloser Audit-Nachweis
│   └── Backward_Trace.jrxml
└── subreports/

STICKERS/
└── ...                 # Aufkleber- und Etikettenvorlagen (versch. Formate)

downloads/
└── ...                 # GitHub-Pages-Downloads (generiert durch Workflow)

pages/
└── index.html          # Projekt-Landing-Page für GitHub Pages

schema/
└── report-parameters.schema.json  # JSON-Schema für parameters.json (V2-JSON-Bundles)

scripts/
├── check_jasper_version.sh         # Prüft JRXML-Versionen auf 6.20.6
├── check_parameters_manifest.py    # CI-Validator für parameters.json-Manifeste
├── generate_parameters_manifest.py # Erzeugt ein parameters.json-Gerüst aus dem Haupt-JRXML
├── dakks_upload_sample.bat         # Beispielskript für den automatisierten Report-Upload
├── dcc_upload_sample.bat           # Upload-Beispiel für DCC-Reports
└── dcc_xml_writer.py               # Hilfsskript zum Erzeugen von DCC-XML
````

**Hinweis:** Die Beispiele sind bewusst generisch gehalten. Sie können direkt als Grundlage für eigene Anpassungen verwendet werden.

### Parameterreferenz für den DAkkS-Report

Der Hauptbericht `DAKKS-SAMPLE/main_reports/dakks-sample.jrxml` akzeptiert alle gängigen calServer-Parameter (z. B. `P_CTAG`, `Reportpath`, `Sprache`, optionale Textbausteine). Eine detaillierte Tabelle mit Pflichtfeldern, Standardwerten und Unterbericht-Parametern findest du im [README des DAkkS-Berichts](DAKKS-SAMPLE/README.md#4-parameter).

---

## Voraussetzungen

* Aktive calServer-Instanz (Cloud oder On-Premise)
* Zugang zur **Reportverwaltung** im calServer (Admin-Berechtigung)
* JasperReports Editor (z. B. Jaspersoft Studio) zur Bearbeitung der JRXML-Dateien. 
  Stelle sicher, dass die Vorlagen mit **JasperReports Library 6.20.6** exportiert werden. 
  Das Skript `scripts/check_jasper_version.sh` bricht andernfalls mit der Meldung 
  `Expected JasperReports Library version 6.20.6` ab.
* Grundkenntnisse in Git und (optional) GitHub Actions

---

## Berichte im calServer hochladen

Um eigene Reports in den calServer zu integrieren, befolge diese Schritte:

1. **Navigiere ins Admin-Backend** → **Reportverwaltung**.
2. Lade die gewünschte(n) JRXML-Datei(en) hoch und ergänze die Metadaten:

   * **Grid Name**: Modulzuordnung, z. B. INVENTORY, CALIBRATION, ORDER.
   * **Schaltflächenname**: Bezeichnung des Report-Buttons im Frontend.
   * **Vorlagenname / Verzeichnisname / Dateiname**: Pfad zur JRXML- oder PDF-Vorlage auf dem Server.
   * **Format**: z. B. `pdf` (weitere Formate wie HTML, XLSX nach Bedarf).
   * **Enabled**: Nur aktivierte Reports sind für Nutzer\:innen sichtbar.
3. **Speichern** und die physischen Dateien im angegebenen Verzeichnis ablegen.

   * **Statische PDFs** können direkt im Dialog „Vorlagendateien“ per Drag & Drop hochgeladen werden.
   * **Erweiterte Einstellungen** wie Variablen, Unterschriftenfelder oder Freigaberegeln lassen sich ebenfalls hier verwalten.

**Praxis-Tipp:**
Nutze Versionierung für Reports, um bei Fehlern jederzeit auf eine frühere Variante zurückzugreifen!

---

## Skripte für Upload und Automatisierung

Im Ordner `scripts` findest du neben dem Batch-Skript `dakks_upload_sample.bat` weitere Hilfen:

- `check_jasper_version.sh` prüft alle JRXML-Dateien auf die erwartete JasperReports-Version 6.20.6.
- `check_parameters_manifest.py` validiert `parameters.json`-Manifeste gegen das Schema und das Haupt-JRXML (läuft auch als CI-Check, siehe unten).
- `generate_parameters_manifest.py` erzeugt ein `parameters.json`-Gerüst aus den `<parameter>`-Deklarationen eines Haupt-JRXML.
- `dcc_upload_sample.bat` zeigt einen Upload-Workflow für DCC-Reports.
- `dcc_xml_writer.py` unterstützt bei der Erzeugung von DCC-XML.

### Parameter beschreiben (`parameters.json`, nur V2-JSON-Bundles)

V2-JSON-Bundles (Bundles **ohne eingebettetes SQL**, die der report-runner aus
einem JSON-Datensatz füllt — erkennbar am Suffix `-JSON-SAMPLE`) können ihre
konfigurierbaren Parameter in einem **Manifest `parameters.json`** an der
Bundle-Wurzel beschreiben (gleiche Ebene wie die README). calServer V2 liest
das Manifest direkt aus dem hochgeladenen ZIP und bietet die Parameter beim
Anlegen von Berichtsvariablen mit Label, Beschreibung, Typ und Standardwert
zur Auswahl an. Referenzbeispiel: [`DAKKS-JSON-SAMPLE/parameters.json`](DAKKS-JSON-SAMPLE/parameters.json).

**Wichtig:** Klassische V1/JDBC-Bundles (mit eingebettetem SQL) bekommen
**kein** Manifest — calServer ignoriert es dort, und der CI-Check bricht mit
einem Fehler ab.

Workflow für Berichtsentwickler:

1. Parameter wie gewohnt im JRXML deklarieren. Namen konfigurierbarer
   Parameter **mit Großbuchstaben beginnen** (`Company_footer`, nicht
   `company_footer`) — calServer injiziert Berichtsvariablen als
   `$P{ucfirst(variable_name)}`, kleingeschriebene Parameternamen sind von
   Variablen nicht erreichbar.
2. Gerüst erzeugen: `python3 scripts/generate_parameters_manifest.py MEIN-BUNDLE -o MEIN-BUNDLE/parameters.json`
3. Labels und Beschreibungen (deutsch **und** englisch), Rollen
   (`variable`/`prompt`/`system`), Scope-Empfehlungen und Eingabetypen
   ergänzen — Format siehe [`schema/report-parameters.schema.json`](schema/report-parameters.schema.json).
4. Lokal prüfen: `python3 scripts/check_parameters_manifest.py MEIN-BUNDLE`
   — derselbe Check läuft in jedem Pull Request (Workflow „Validate Reports“).

Der Paket-Build nimmt das Manifest automatisch in das Bundle-ZIP auf.

### Vorbereitung:

Bearbeite vor Ausführung die folgenden Variablen im Skript:

```bat
set DOMAIN=deine.domain.tld
set HTTP_X_REST_USERNAME=deinUser
set HTTP_X_REST_PASSWORD=deinPasswort
set HTTP_X_REST_API_KEY=deinApiKey
set REPORT_ID=cd5797da-e7a9-0bc6-fc73-dedc595bd59b
```

Die benötigte **Report-ID** kannst du direkt im calServer ermitteln: In der
Berichtsübersicht öffnest du beim gewünschten Eintrag das Menü
„**Actions**" und klickst auf **Copy ID**. Damit wird die eindeutige ID in
deine Zwischenablage kopiert und lässt sich in der Variablen `REPORT_ID`
einfügen.

### Ausführung:

```cmd
dakks_upload_sample.bat
```

Das Skript erstellt automatisch ein ZIP-Archiv und lädt es via `curl` zur API deiner calServer-Instanz hoch.

## Repository klonen & Arbeiten mit GitHub Actions

1. **Repository klonen:**

   ```bash
   git clone https://github.com/calhelp/calServer-reports.git
   ```

2. **JRXML-Dateien bearbeiten** – Nutze Jaspersoft Studio oder einen anderen Editor.

3. **Änderungen committen & pushen** – Schicke deine Anpassungen per Pull Request (siehe [Contributing](#contributing--community)).

4. **Automatisiertes Deployment:**
   Der Workflow `.github/workflows/package-reports.yml` erstellt bei jedem Push automatisch ZIP-Archive der Haupt- und Unterberichte und lädt diese – sofern eingerichtet – über die API an deine calServer-Instanz hoch.
   **Regel für Reportpakete ohne Subreports:** Das ZIP enthält immer einen `subreports/`-Ordner. Wenn es keine Unterberichte gibt, wird ein Platzhalter `subreports/.keep` erzeugt, damit der Ordner im Archiv vorhanden bleibt.
   Die dafür notwendigen Zugangsdaten werden sicher als GitHub Secrets verwaltet:

   * `DOMAIN`
   * `HTTP_X_REST_USERNAME`
   * `HTTP_X_REST_PASSWORD`
   * `HTTP_X_REST_API_KEY`

---

## 📦 Download der aktuellen Reportpakete

Alle aktuellen und früheren ZIP-Archive mit Reportvorlagen stehen als Release-Pakete zur Verfügung:

- [Latest Downloads (immer aktuelle Artefakte)](https://calhelp.github.io/calServer-reports/downloads/)
- [Letztes Release herunterladen (empfohlen)](https://github.com/calhelp/calServer-reports/releases/latest)
- [Alle Releases durchsuchen](https://github.com/calhelp/calServer-reports/releases)

**Hinweis für GitHub Pages:** Die Downloads-Seite wird vom Workflow `publish-downloads` gebaut und über die GitHub-Actions-Pages-Quelle (`actions/deploy-pages`) veröffentlicht — die Pages-Quelle muss in den Repo-Einstellungen auf **„GitHub Actions"** stehen (kein `gh-pages`-Branch nötig). Der Workflow muss mindestens einmal erfolgreich gelaufen sein.

**Troubleshooting-Checkliste (optional):**
- Existiert der Branch `gh-pages`?
- War der letzte `publish-downloads`-Run erfolgreich?
- Ist die Pages-Source auf `gh-pages` gesetzt?

Für Entwickler:innen und zum Testen der jeweils frisch gebauten Version gibt es zusätzlich temporäre „Artifacts“ im Bereich  
[GitHub Actions](https://github.com/calhelp/calServer-reports/actions).

---

## Ausblick: calServer V2 und die Zukunft der Reportvorlagen

calServer V2 verwendet ein neues Datenbankschema mit **lesbaren Feldnamen** (`serial_number`, `next_calibration_date`) statt der bisherigen Metrologie-Codes (`I4202`, `C2303`). Für die Reportvorlagen bedeutet das:

- **Die bestehenden Bundles in diesem Repository bleiben der stabile V1-Stand** (eingebettetes SQL über JDBC mit den Codespalten). Sie laufen unverändert auf allen V1-Systemen und werden weiter mit Bugfixes gepflegt.
- **V2-Bundles** (Ordner mit Endung `-JSON-SAMPLE`, z. B. `DAKKS-JSON-SAMPLE`, `INVENTORY-JSON-SAMPLE`) nutzen eine **JSON-Datasource** mit lesbaren API-Feldnamen (`$F{serial_number}` statt `$F{I4202}`). Die Daten liefert das calServer-Backend als berichtsförmiges JSON-Paket — die Vorlagen enthalten kein eigenes SQL mehr und funktionieren dadurch unabhängig vom Datenbank-Backend (MySQL, PostgreSQL, MSSQL). Auf der [Downloads-Seite](https://calhelp.github.io/calServer-reports/downloads/) erscheinen sie in der eigenen Kategorie **„APEX · V2 (JSON-Datenquelle)"** (APEX = interner Codename für V2), getrennt von den V1-Vorlagen.
- Bestehende Vorlagen bitte **nicht** auf das V2-Schema-SQL umschreiben — die Strategie und der Migrationspfad sind hier dokumentiert: [Evaluierung: JasperReports-Strategie für calServer V2](https://github.com/calhelp/calServer-yii/blob/develop/docs/evaluierung-jasper-reports-v2.md).
- Als Übersetzungshilfe zwischen alten Codes und neuen Feldnamen dient weiterhin der [FIELD-NAMES-Report](FIELD-NAMES/) sowie die Mapping-Referenz in der Strategie-Dokumentation.

---

## Contributing & Community

**Wir freuen uns auf deine Beiträge!**
Egal ob Bugfix, Feature, Report-Idee oder Feedback – jede Unterstützung ist willkommen.

**So bringst du dich ein:**

1. Forke das Repository.
2. Erstelle einen neuen Branch für deine Änderungen.
3. Sende einen Pull Request mit einer kurzen, aussagekräftigen Beschreibung.
4. Nutze die GitHub-Issue-Funktion, um Bugs zu melden oder Wünsche zu äußern.

**Verhaltenskodex:**
Wir legen Wert auf einen freundlichen, offenen und respektvollen Umgang. Bitte beachte die üblichen Community-Regeln.

---

## Fehler melden & Support

Bei Fragen oder Problemen:

* **Nutze die GitHub Issues:**
  Beschreibe dein Anliegen so detailliert wie möglich (Schritte, Screenshot, ggf. calServer-Version).

* **Support:**
  Für individuellen Support, Anpassungen oder Schulungen rund um calServer-Reports kannst du dich gern an [calHelp](https://calhelp.de) wenden.

---

## Lizenz

Dieses Projekt und die darin enthaltenen Beispielvorlagen stehen unter der [MIT-Lizenz](LICENSE), sofern im jeweiligen Unterordner oder in einzelnen Dateien nichts anderes vermerkt ist.

---

## Kontakt & Dank

**calHelp / René Buske**
Web: [calhelp.de](https://calhelp.de)
E-Mail: [info@calhelp.de](mailto:info@calhelp.de)

---

**Danke an alle Mitwirkenden und an die gesamte calServer-Community für Ideen, Feedback und gemeinsames Vorankommen!**

---

*Letzte Aktualisierung: 2026-07-15*

```
