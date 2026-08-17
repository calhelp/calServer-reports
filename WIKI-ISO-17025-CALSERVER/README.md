# Wiki: QM-Handbuch nach ISO/IEC 17025 mit calServer-Umsetzung (Startvorlage)

Zweite Variante der 17025-Handbuchvorlage: derselbe Handbuchtext wie in
[`WIKI-ISO-17025`](../WIKI-ISO-17025/), aber jedes Kapitel endet mit drei
Abschnitten, die den Bogen zur Software schlagen — **wo die Anforderung in
calServer V2 landet, welcher Nachweis dort entsteht und was calServer nicht
leistet**. Dazu kommt ein 15. Kapitel: eine Abdeckungsmatrix über alle
Normabschnitte mit Lückenliste zum Abhaken.

**15 Kapitel (QMH-00 bis QMH-14) in je zwei Sprachen** (Deutsch und Englisch),
je Sprache eine Kategorie, im Format `calserver.wiki` (Version 1), paketiert als
`calserver.wiki-package`.

## Welche der beiden Varianten

| | `WIKI-ISO-17025` | `WIKI-ISO-17025-CALSERVER` (dieses Paket) |
| --- | --- | --- |
| Inhalt | Handbuchtext, softwareneutral | derselbe Text plus Umsetzung, Nachweis und Grenzen je Kapitel |
| Kapitel | 14 (QMH-00 bis QMH-13) | 15 (zusätzlich QMH-14 Abdeckungsmatrix) |
| Passt, wenn | das Labor calServer nicht oder nur am Rand einsetzt, oder das Handbuch bewusst werkzeugfrei bleiben soll | calServer die führende Aufzeichnung ist und im Audit gezeigt wird |
| Nicht gedacht für | — | beide Varianten parallel zu importieren: sie beschreiben dasselbe Handbuch zweimal |

Die Artikel beider Pakete haben **eigene `general_page_id`s**. Wer beide
importiert, bekommt 29 Artikel und muss selbst aufräumen — der Import löscht
grundsätzlich nichts.

## Was die drei Abschnitte je Kapitel leisten

| Abschnitt | Frage, die er beantwortet |
| --- | --- |
| Umsetzung in calServer | Wo landet die Anforderung, und was entsteht dort als Nachweis? Mit Modul, Menüpfad und Operation. |
| Nachweis im Audit | Was fragt eine Begutachtung, womit wird geantwortet, und wo im Programm liegt das? |
| Grenzen | Was calServer hier **nicht** leistet — als Aufgabenliste (`wiki-todo-list`), die offen bleibt, bis das Labor den Punkt außerhalb geregelt hat. |

Die Grenzen-Abschnitte sind der eigentliche Grund für diese Variante. Sie sagen
zum Beispiel, dass es keine Qualifikationsmatrix als Datenobjekt gibt, dass der
Sollbereich der Umgebungsbedingungen gedruckt und nicht geprüft wird, dass kein
Budget nach GUM gerechnet wird und dass die Freigabe eines Kalibrierscheins den
Akkreditierungsumfang bewusst nicht prüft. Wer eine Vorlage sucht, die überall
„erfüllt" schreibt, ist hier falsch: Eine Lücke, die im Handbuch steht, ist im
Audit ein bekannter Punkt mit Regelung — eine verschwiegene ist ein Befund.

## Paketinhalt

| Datei | Zweck |
| --- | --- |
| `manifest.json` | Manifest: jede Datei mit SHA-256-Prüfsumme und Größe |
| `wiki.json` | Das Wiki (2 Kategorien, 15 Artikel, 30 Seiten) |
| `README.md` | Diese Beschreibung |

Das Manifest ist der Manipulationsanker des Formats: calServer lehnt beim
Import jedes Paket ab, dessen Inhalt vom Manifest abweicht — in beide
Richtungen. Das maschinenlesbare Schema:
[`wiki-package.schema.json`](https://calhelp.github.io/calServer-reports/schema/wiki-package.schema.json).

Medien (`media/`) enthält dieses Paket nicht.

## Aufbau

Alle Kapitel liegen in einer Kategorie je Sprache — „Laborhandbuch DIN EN
ISO/IEC 17025:2018 mit calServer (Vorlage)" bzw. „Laboratory Manual DIN EN
ISO/IEC 17025:2018 with calServer (Template)". Die Nummerierung QMH-00 bis
QMH-14 gibt die Reihenfolge vor.

| Kapitel | Inhalt | Normkapitel | Trägt calServer |
| --- | --- | --- | --- |
| QMH-00 | Deckblatt, Platzhalter, Kapitelübersicht und Dokumentenlenkung | 8.3, 8.4 | teilweise |
| QMH-01 | Anwendungsbereich und Akkreditierungsumfang | 1, 5 | teilweise |
| QMH-02 | Unparteilichkeit und Vertraulichkeit | 4.1, 4.2 | teilweise |
| QMH-03 | Organisation und Verantwortlichkeiten | 5 | teilweise |
| QMH-04 | Personal und Qualifikation | 6.2 | gering |
| QMH-05 | Räumlichkeiten und Umgebungsbedingungen | 6.3 | gering |
| QMH-06 | Ausrüstung und Normale | 6.4 | weitgehend |
| QMH-07 | Metrologische Rückführbarkeit und externe Leistungen | 6.5, 6.6 | weitgehend |
| QMH-08 | Auftragsabwicklung und Kalibrierverfahren | 7.1, 7.2, 7.4 | weitgehend |
| QMH-09 | Ermittlung der Messunsicherheit | 7.6 (GUM, EA-4/02) | gering |
| QMH-10 | Sicherstellung der Validität der Ergebnisse | 7.7 | gering |
| QMH-11 | Kalibrierscheine und Konformitätsaussagen | 7.8 (ILAC-G8) | weitgehend |
| QMH-12 | Beschwerden, nichtkonforme Arbeit und Korrekturmaßnahmen | 7.9, 7.10, 8.7 | weitgehend |
| QMH-13 | Risiken und Chancen, interne Audits, Managementbewertung | 8.5, 8.8, 8.9 | teilweise |
| QMH-14 | Abdeckungsmatrix und Lückenliste (Arbeitsblatt) | alle | — |

Die Spalte „Trägt calServer" ist die Bewertung aus QMH-14: **weitgehend** heißt,
der Nachweis entsteht im Betrieb; **teilweise**, die Bausteine sind da und das
Zusammenführen ist Handarbeit; **gering**, das Wesentliche liegt außerhalb.
Bewertet ist der Auslieferungsstand von calServer V2, nicht eine bestimmte
Installation — zugebuchte Module und eigene Konfiguration verschieben das Bild.

Die englische Fassung trägt dieselben Nummern. Die Sprachvarianten eines
Kapitels hängen an derselben `general_page_id` und erscheinen in calServer als
Übersetzungen desselben Artikels.

## Passende Startpakete

Mehrere Kapitel verweisen auf Konfigurationspakete, die dieselbe Download-Seite
ausliefert. Zusammen ergeben sie eine Installation, in der die beschriebenen
Nachweise auch wirklich entstehen:

| Paket | Wofür | Kapitel |
| --- | --- | --- |
| [`status-inventory-dakks`](../STATUS-INVENTORY-DAKKS/) | Geräte-Lebenszyklus (frei, fällig, gesperrt …) | QMH-06 |
| [`status-calibration-dakks`](../STATUS-CALIBRATION-DAKKS/) | Ablauf einer Kalibrierung | QMH-08, QMH-11 |
| [`status-booking-dakks`](../STATUS-BOOKING-DAKKS/) | Ablauf eines Auftrags | QMH-08 |
| [`status-tickets-dakks`](../STATUS-TICKETS-DAKKS/) | Ablauf für Risiken, Abweichungen, Maßnahmen | QMH-12, QMH-13 |
| [`ticket-config-dakks`](../TICKET-CONFIG-DAKKS/) | Vorgangsarten, Themenfelder, Risikobewertung (zwei Methoden) | QMH-12, QMH-13 |
| [`ticket-config-dakks-3d`](../TICKET-CONFIG-DAKKS-3D/) | dasselbe mit drei Bewertungsmethoden | QMH-12, QMH-13 |
| [`category-inventory-dakks`](../CATEGORY-INVENTORY-DAKKS/) | Inventar-Kategoriebaum (Messgröße, Normalstufe) | QMH-01, QMH-06 |
| [`dakks-sample`](../DAKKS-SAMPLE/) | akkreditierter Kalibrierschein als Berichtsvorlage | QMH-11 |

## Import in calServer V2

1. Paket hier herunterladen (`wiki-iso-17025-calserver.zip`)
2. In calServer **Wiki → Importieren** öffnen (Recht `wiki_import`)
3. Datei auswählen, **Bestehende Seiten behalten** stehen lassen, importieren

Oder auf der Kommandozeile:

```bash
docker exec calserver-api-v2 php artisan wiki:import /pfad/wiki-iso-17025-calserver.zip
```

Der Import ist **idempotent**: Artikel werden über ihre `general_page_id`
wiedererkannt. Ein zweiter Durchlauf legt nichts doppelt an, und eigene
Änderungen am Text bleiben stehen. Wer eine überarbeitete Fassung dieser
Vorlage übernehmen will, importiert mit `--mode=overwrite`; der Paketinhalt
wird dann als **neue Revision** angelegt, die bisherige Fassung bleibt in der
Historie.

Die Seiten liegen als HTML im Paket und werden beim Import in Blöcke
umgewandelt — sie sind also im Blockeditor bearbeitbar, nicht als HTML-Insel
eingefroren. Einzige Ausnahme sind Tabellen mit verbundenen Zellen (das
Unsicherheitsbudget in QMH-09): die bleiben ein HTML-Block, weil der
Blockeditor keine `colspan` kennt.

## Wichtig: eine Startvorlage, kein fertiges Handbuch

Der Text ist ein Ausgangspunkt und muss vor der Freigabe an das eigene Labor
angepasst werden:

- Platzhaltertabelle in QMH-00 ausfüllen und die Platzhalter in allen Kapiteln
  ersetzen
- Beispielzeilen in den Tabellen (Akkreditierungsumfang, Normale,
  Unsicherheitsbudget) durch die eigenen Angaben ersetzen
- Kapitel streichen, die nicht zutreffen (etwa Probenahme oder
  Vor-Ort-Kalibrierung), statt sie leer stehen zu lassen
- Verweise auf die eigenen Verfahrensanweisungen ergänzen
- Freigabezeile besetzen: erstellt / geprüft / freigegeben mit Datum

Zusätzlich zu den Punkten, die auch für die softwareneutrale Variante gelten:

- **Die Abschnitte „Umsetzung in calServer" gegen die eigene Installation
  prüfen.** Menüpfade, Statusbezeichnungen, Rollennamen und zugebuchte Module
  (etwa das Siegel) weichen ab. Ein Verweis auf ein Modul, das die Installation
  nicht hat, ist im Audit schlechter als kein Verweis.
- **Die Grenzen-Listen abarbeiten, nicht abnicken.** Jeder Punkt beschreibt
  etwas, das das Labor außerhalb von calServer regeln muss. Abgehakt heißt
  geregelt und nachweisbar.
- **QMH-14 versionieren.** Die Bewertung gilt für einen Stand von calServer.
  Nach einem Update gehört sie durchgesehen, sonst behauptet das Handbuch
  Lücken, die es nicht mehr gibt — oder verschweigt neue.

Ein unverändert übernommenes Handbuch belegt gegenüber einer
Akkreditierungsstelle nichts — im Gegenteil, stehengebliebene Platzhalter
fallen im Audit sofort auf.

## Mitwirken

Korrekturen und Ergänzungen gern per Pull Request. Besonders willkommen:
Grenzen, die inzwischen keine mehr sind, und Lücken, die in dieser Fassung
fehlen. Nach jeder Änderung an `wiki.json` oder `README.md` das Manifest neu
rechnen — die Prüfsummen werden **nie** von Hand gepflegt:

```bash
python3 scripts/build_wiki_manifest.py --write WIKI-ISO-17025-CALSERVER
python3 scripts/build_wiki_manifest.py --check
```

Die `general_page_id` eines Kapitels bleibt dabei unangetastet: eine neue UUID
machte aus einem überarbeiteten Kapitel auf jeder Installation, die die Vorlage
schon importiert hat, ein zweites.
