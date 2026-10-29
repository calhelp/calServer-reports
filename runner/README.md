# calScript Runner: versteckter Download-Spiegel

Dieser Ordner steuert, welche Versionen des calScript Runners (Messplatz-Programm
von calServer, gebaut im privaten Repository `calhelp/calServer-yii`) auf der
GitHub-Pages-Seite dieses Repositories ausgeliefert werden.

Die Pakete liegen **nicht** in diesem Repository. Der Workflow
`publish-downloads.yml` lädt sie beim Bauen der Seite aus den GitHub-Releases
von `calServer-yii` (Tag `calscript-runner-v<version>`) und legt sie unter

```
https://calhelp.github.io/calServer-reports/runner/<version>/<datei>
```

ab, zum Beispiel `runner/0.2.0/calscript-runner-0.2.0-windows-x64.zip`,
daneben `SHA256SUMS.txt`. calServer verlinkt genau diese Adressen auf der
Seite „Messplätze" (`config/calscript_runner.php`).

## Versteckt, nicht geheim

Die Dateien sind per direkter URL für jeden abrufbar (Endkunden haben keinen
Zugriff auf das private Repository). Sie werden aber nirgends verlinkt: nicht
auf der Downloads-Seite, nicht in `latest.json`, kein Verzeichnis-Listing
(`runner/` hat keine `index.html`, GitHub Pages antwortet dort mit 404). Die
Seite trägt zusätzlich eine `robots.txt` mit `Disallow: /runner/`. Hinweis:
Suchmaschinen lesen `robots.txt` nur an der Domain-Wurzel
(`calhelp.github.io/robots.txt`), die zu einem Repository `calhelp/calhelp.github.io`
gehören würde. Solange es das nicht gibt, schützt vor allem das Fehlen jeder
Verlinkung.

## Versionen pflegen

`versions.json` listet die Versionen, die veröffentlicht werden (neueste zuerst):

```json
{ "versions": ["0.2.0"] }
```

Der Release-Workflow in `calServer-yii` trägt eine neue Version nach dem Bau
automatisch hier ein (Commit auf `main`, der wie jeder Push die Paketierung
und damit die Veröffentlichung der Seite auslöst). Von Hand geht es genauso:
Version eintragen, mergen, fertig. Alte Versionen entfernen, sobald kein
calServer sie mehr verlinkt (`CALSCRIPT_RUNNER_VERSION`).

## Voraussetzung: Zugriffstoken

Das Repository `calServer-yii` ist privat. Der Workflow braucht deshalb das
Actions-Secret `CALSCRIPT_RUNNER_PAGES_TOKEN`: ein Fine-grained Personal Access
Token mit

- `calhelp/calServer-yii`: Contents **Read** (Release-Assets laden),
- `calhelp/calServer-reports`: Contents **Read and write** (nur vom
  Release-Workflow in `calServer-yii` gebraucht, um `versions.json` zu pflegen).

Dasselbe Token wird in beiden Repositories unter demselben Namen hinterlegt.
Fehlt das Secret oder eine gelistete Version, wird die Seite trotzdem gebaut;
der Schritt meldet eine Warnung und lässt den Runner-Ordner für diese Version
leer.
