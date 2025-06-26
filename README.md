# 📑 calServer Reports

Dieses Repository bündelt Beispielberichte (JRXML) für den calServer. Die Ordner `DAKKS-SAMPLE` und `ORDER-SAMPLE` enthalten je einen Satz von `main_reports` und `subreports`, die als Vorlage oder Testbasis dienen.

## Berichte im calServer hochladen

Die Registrierung neuer Reports erfolgt im Admin-Backend unter **Reportverwaltung**. Hier werden die hochgeladenen JRXML-Dateien mit Metadaten versehen. Wichtige Felder:

- **Grid Name** – Zuordnung zum Modul, etwa INVENTORY oder CALIBRATION
- **Schaltflächenname** – Name des Aufrufs im Frontend
- **Vorlagenname / Verzeichnisname / Dateiname** – Pfad zur JRXML- oder PDF-Vorlage
- **Format** – gewünschtes Ausgabeformat, z. B. `pdf`
- **Enabled** – nur aktivierte Reports sind für Nutzer sichtbar

Die physische JRXML-Datei muss im angegebenen Verzeichnis auf dem Server liegen. Statische PDF-Layouts können im Dialog **Vorlagendateien** per Drag‑&‑Drop hochgeladen werden. Weitere Anpassungen wie Variablen, Unterschriften oder Freigaberegeln lassen sich in den jeweiligen Bereichen der Reportverwaltung pflegen.

## Helferskript

Unter `scripts` liegt das Batch-Skript `dakks_upload_sample.bat`. Es packt einen Beispielordner in ein ZIP und sendet ihn via `curl` an die API des calServer. Vor dem Ausführen sind Domain, Nutzername, Passwort, API-Key und Report-ID im Skript anzupassen:

```bat
set DOMAIN=deine.domain.tld
set HTTP_X_REST_USERNAME=deinUser
set HTTP_X_REST_PASSWORD=deinPasswort
set HTTP_X_REST_API_KEY=deinApiKey
set REPORT_ID=cd5797da-e7a9-0bc6-fc73-dedc595bd59b
```

Aufgerufen wird anschließend:

```cmd
dakks_upload_sample.bat
```

## Verzeichnisübersicht

```text
DAKKS-SAMPLE/
├── main_reports/
└── subreports/

ORDER-SAMPLE/
├── main_reports/
└── subreports/
```

© calHelp / René Buske
