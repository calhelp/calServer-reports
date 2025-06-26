# 📦 JasperReports-Upload für calServer

Dieses Archiv stellt die Standard-JasperReports des calServer gebündelt bereit.
Die enthaltenen Beispielordner können mit dem Skript zu einem ZIP-Archiv
verpackt und anschließend auf den Server hochgeladen werden.

## Zweck

Dieses Skript (`package_and_upload.bat`) automatisiert das Verpacken und den Upload angepasster JasperReports (`.jrxml`) an den calServer.

Es wird eine ZIP-Datei aus den Unterordnern `main_reports` und `subreports` erstellt und per API an den definierten Report-Endpunkt im calServer übermittelt – **per Doppelklick** auszuführen, ohne zusätzliche Tools.

---

## Voraussetzungen

- Windows 10 oder 11  
- Vorinstalliertes `curl` (ab Windows 10 Version 1803)  
- PowerShell (`Compress-Archive` ist Standard)

---

## Ordnerstruktur

Das Skript erwartet folgende Verzeichnisse:

```text
DAKKS-SAMPLE/
├── main_reports/
│   └── BerichtA.jrxml
└── subreports/
    └── BerichtB.jrxml
```

---

## Konfiguration im Skript

Im oberen Bereich der Datei `package_and_upload.bat` müssen folgende Werte angepasst werden:

```bat
:: === Konfiguration ===
set DOMAIN=deine.domain.tld
set HTTP_X_REST_USERNAME=deinUser
set HTTP_X_REST_PASSWORD=deinPasswort
set HTTP_X_REST_API_KEY=deinApiKey
set REPORT_ID=cd5797da-e7a9-0bc6-fc73-dedc595bd59b
```

Diese Zugangsdaten erhältst du vom calServer-Administrator.

---

## Funktionsweise

1. ZIP-Erzeugung mit PowerShell (nur `main_reports` und `subreports`)
2. ZIP-Datei wird im Verzeichnis `zip_output/` gespeichert
3. Inhalt der ZIP-Datei wird optional zur Kontrolle angezeigt
4. `curl` überträgt das Archiv an die definierte calServer-API
5. Erfolgsmeldung wird angezeigt

---

## Beispiel ZIP-Inhalt

```text
main_reports/Calibration.jrxml
subreports/Details.jrxml
```

---

## Ausführen

Starte das Skript einfach per Doppelklick oder Konsole:

```cmd
package_and_upload.bat
```

---

## Anwendungsfall

Das Skript eignet sich ideal für Entwickler:innen oder Admins, die regelmäßig Reports aktualisieren müssen. Durch den automatischen Upload entfällt das manuelle Einpflegen über die Weboberfläche.

---

## Erweiterungsideen

* Mehrere `REPORT_ID`s verwalten
* Unterstützung für weitere Report-Typen (`ORDER-SAMPLE`, etc.)
* Integration in CI/CD-Pipeline (z. B. mit GitHub Actions)

---

© calHelp / René Buske

Sehr aufmerksam – danke für den Hinweis!

