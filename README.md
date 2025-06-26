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
├── main_reports/       # Hauptberichte, z. B. vollständige Kalibrierscheine
└── subreports/         # Unterberichte, z. B. Tabellen, Fußzeilen, Messwerte

ORDER-SAMPLE/
├── main_reports/       # Berichte für Aufträge, z. B. Angebots- oder Auftragsdokumente
└── subreports/         # Unterberichte wie Positionslisten oder Summenfelder

scripts/
└── dakks_upload_sample.bat  # Beispielskript für den automatisierten Report-Upload
````

**Hinweis:** Die Beispiele sind bewusst generisch gehalten. Sie können direkt als Grundlage für eigene Anpassungen verwendet werden.

---

## Voraussetzungen

* Aktive calServer-Instanz (Cloud oder On-Premise)
* Zugang zur **Reportverwaltung** im calServer (Admin-Berechtigung)
* JasperReports Editor (z. B. Jaspersoft Studio) zur Bearbeitung der JRXML-Dateien
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

Im Ordner `scripts` findest du das Batch-Skript `dakks_upload_sample.bat`, das Beispielberichte als ZIP-Archiv an die calServer-API sendet.

### Vorbereitung:

Bearbeite vor Ausführung die folgenden Variablen im Skript:

```bat
set DOMAIN=deine.domain.tld
set HTTP_X_REST_USERNAME=deinUser
set HTTP_X_REST_PASSWORD=deinPasswort
set HTTP_X_REST_API_KEY=deinApiKey
set REPORT_ID=cd5797da-e7a9-0bc6-fc73-dedc595bd59b
```

### Ausführung:

```cmd
dakks_upload_sample.bat
```

Das Skript erstellt automatisch ein ZIP-Archiv und lädt es via `curl` zur API deiner calServer-Instanz hoch.

---

## Repository klonen & Arbeiten mit GitHub Actions

1. **Repository klonen:**

   ```bash
   git clone https://github.com/calhelp/calServer-reports.git
   ```

2. **JRXML-Dateien bearbeiten** – Nutze Jaspersoft Studio oder einen anderen Editor.

3. **Änderungen committen & pushen** – Schicke deine Anpassungen per Pull Request (siehe [Contributing](#contributing--community)).

4. **Automatisiertes Deployment:**
   Der Workflow `.github/workflows/package-reports.yml` erstellt bei jedem Push automatisch ZIP-Archive der Haupt- und Unterberichte und lädt diese – sofern eingerichtet – über die API an deine calServer-Instanz hoch.
   Die dafür notwendigen Zugangsdaten werden sicher als GitHub Secrets verwaltet:

   * `DOMAIN`
   * `HTTP_X_REST_USERNAME`
   * `HTTP_X_REST_PASSWORD`
   * `HTTP_X_REST_API_KEY`

---

## 📦 Download der aktuellen Reportpakete

Alle aktuellen und früheren ZIP-Archive mit Reportvorlagen stehen als Release-Pakete zur Verfügung:

- [Letztes Release herunterladen (empfohlen)](https://github.com/calhelp/calServer-reports/releases/latest)
- [Alle Releases durchsuchen](https://github.com/calhelp/calServer-reports/releases)

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

*Letzte Aktualisierung: 2025-06-26*

```

