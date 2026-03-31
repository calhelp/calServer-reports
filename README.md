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

ORDER-SAMPLE/
├── main_reports/       # Berichte für Aufträge, z. B. Angebots- oder Auftragsdokumente
└── subreports/         # Unterberichte wie Positionslisten oder Summenfelder

FORWARD-TRACE/
├── main_reports/       # Wirkungsanalyse: betroffene Geräte bei Normalen-Abweichung
│   └── Forward_Trace.jrxml
└── subreports/

BACKWARD-TRACE/
├── main_reports/       # Rückführungskette: lückenloser Audit-Nachweis
│   └── Backward_Trace.jrxml
└── subreports/

STICKERS/
└── ...                 # Aufkleber- und Etikettenvorlagen (versch. Formate)

downloads/
└── ...                 # GitHub-Pages-Downloads (generiert durch Workflow)

pages/
└── index.html          # Projekt-Landing-Page für GitHub Pages

scripts/
├── check_jasper_version.sh  # Prüft JRXML-Versionen auf 6.20.6
├── dakks_upload_sample.bat  # Beispielskript für den automatisierten Report-Upload
├── dcc_upload_sample.bat    # Upload-Beispiel für DCC-Reports
└── dcc_xml_writer.py        # Hilfsskript zum Erzeugen von DCC-XML
````

**Hinweis:** Die Beispiele sind bewusst generisch gehalten. Sie können direkt als Grundlage für eigene Anpassungen verwendet werden.

### Parameterreferenz für den DAkkS-Report

Der Hauptbericht `DAKKS-SAMPLE/main_reports/dakks-sample.jrxml` akzeptiert alle gängigen calServer-Parameter (z. B. `P_CTAG`, `Reportpath`, `Sprache`, optionale Textbausteine). Eine detaillierte Tabelle mit Pflichtfeldern, Standardwerten und Unterbericht-Parametern findest du im [README des DAkkS-Hauptberichts](DAKKS-SAMPLE/main_reports/README.md#vollständige-parameterübersicht).

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
- `dcc_upload_sample.bat` zeigt einen Upload-Workflow für DCC-Reports.
- `dcc_xml_writer.py` unterstützt bei der Erzeugung von DCC-XML.

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

**Hinweis für GitHub Pages:** Die Downloads-Seite funktioniert nur, wenn GitHub Pages auf den Branch `gh-pages` zeigt und der Workflow `publish-downloads` mindestens einmal erfolgreich gelaufen ist.

**Troubleshooting-Checkliste (optional):**
- Existiert der Branch `gh-pages`?
- War der letzte `publish-downloads`-Run erfolgreich?
- Ist die Pages-Source auf `gh-pages` gesetzt?

Für Entwickler:innen und zum Testen der jeweils frisch gebauten Version gibt es zusätzlich temporäre „Artifacts“ im Bereich  
[GitHub Actions](https://github.com/calhelp/calServer-reports/actions).

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

*Letzte Aktualisierung: 2026-03-31*

```
