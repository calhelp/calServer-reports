# Wiki: QM-Handbuch nach ISO/IEC 17025 (Startvorlage)

Startvorlage für das Qualitätsmanagementhandbuch eines Kalibrierlabors,
gegliedert nach DIN EN ISO/IEC 17025:2018-03 — **14 Kapitel (QMH-00 bis
QMH-13) in je zwei Sprachen** (Deutsch und Englisch), je Sprache eine
Kategorie, im Format `calserver.wiki` (Version 1), paketiert als
`calserver.wiki-package`.

Anders als eine Kapitelübersicht der Norm ist das hier der **Handbuchtext
selbst**: durchformulierte Abschnitte, in denen alles Laborspezifische als
Platzhalter in eckigen Klammern steht (`[Laborname]`, `[DAkkS-Registriernummer]`,
`[Turnus]`). Jede Seite beginnt mit einem Hinweisblock „Vorlage – vor der
Freigabe anpassen", der auflistet, was zu ersetzen und was zu entscheiden ist.
Tabellen bringen die Struktur mit (Dokumentenkopf, Akkreditierungsumfang,
Rollenmatrix, Rückführungsplan, Unsicherheitsbudget, Aufbewahrungsfristen);
ihre Zeilen sind als Beispiel gekennzeichnet und werden vor der Freigabe
überschrieben.

## Paketinhalt

| Datei | Zweck |
| --- | --- |
| `manifest.json` | Manifest: jede Datei mit SHA-256-Prüfsumme und Größe |
| `wiki.json` | Das Wiki (2 Kategorien, 14 Artikel, 28 Seiten) |
| `README.md` | Diese Beschreibung |

Das Manifest ist der Manipulationsanker des Formats: calServer lehnt beim
Import jedes Paket ab, dessen Inhalt vom Manifest abweicht — in beide
Richtungen. Das maschinenlesbare Schema:
[`wiki-package.schema.json`](https://calhelp.github.io/calServer-reports/schema/wiki-package.schema.json).

Medien (`media/`) enthält dieses Paket nicht; das Format trägt sie, sobald eine
Vorlage Bilder mitbringt.

## Aufbau

Alle Kapitel liegen in einer Kategorie je Sprache — „Laborhandbuch DIN EN
ISO/IEC 17025:2018 (Vorlage)" bzw. „Laboratory Manual DIN EN ISO/IEC 17025:2018
(Template)". Die Nummerierung QMH-00 bis QMH-13 gibt die Reihenfolge vor.

| Kapitel | Inhalt | Normkapitel |
| --- | --- | --- |
| QMH-00 | Deckblatt, Platzhalter, Kapitelübersicht und Dokumentenlenkung | 8.3, 8.4 |
| QMH-01 | Anwendungsbereich und Akkreditierungsumfang | 1, 5 |
| QMH-02 | Unparteilichkeit und Vertraulichkeit | 4.1, 4.2 |
| QMH-03 | Organisation und Verantwortlichkeiten | 5 |
| QMH-04 | Personal und Qualifikation | 6.2 |
| QMH-05 | Räumlichkeiten und Umgebungsbedingungen | 6.3 |
| QMH-06 | Ausrüstung und Normale | 6.4 |
| QMH-07 | Metrologische Rückführbarkeit und externe Leistungen | 6.5, 6.6 |
| QMH-08 | Auftragsabwicklung und Kalibrierverfahren | 7.1, 7.2, 7.4 |
| QMH-09 | Ermittlung der Messunsicherheit | 7.6 (GUM, EA-4/02) |
| QMH-10 | Sicherstellung der Validität der Ergebnisse | 7.7 |
| QMH-11 | Kalibrierscheine und Konformitätsaussagen | 7.8 (ILAC-G8) |
| QMH-12 | Beschwerden, nichtkonforme Arbeit und Korrekturmaßnahmen | 7.9, 7.10, 8.7 |
| QMH-13 | Risiken und Chancen, interne Audits, Managementbewertung | 8.5, 8.8, 8.9 |

Die englische Fassung trägt dieselben Nummern (`QMH-00 Cover Page,
Placeholders and Document Control` und so weiter). Die Sprachvarianten eines
Kapitels hängen an derselben `general_page_id` und erscheinen in calServer als
Übersetzungen desselben Artikels.

Wo ein Kapitel einen Nachweis beschreibt, der in calServer entsteht (Normale
und Rückführbarkeit, Prüfmittelüberwachung, Kalibrierscheine, Beschwerden),
benennt es das Modul — als Hinweis auf die Stelle, nicht als Aussage über
Konformität.

## Import in calServer V2

1. Paket hier herunterladen (`wiki-iso-17025.zip`)
2. In calServer **Wiki → Importieren** öffnen (Recht `wiki_import`)
3. Datei auswählen, **Bestehende Seiten behalten** stehen lassen, importieren

Oder auf der Kommandozeile:

```bash
docker exec calserver-api-v2 php artisan wiki:import /pfad/wiki-iso-17025.zip
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

Ein unverändert übernommenes Handbuch belegt gegenüber einer
Akkreditierungsstelle nichts — im Gegenteil, stehengebliebene Platzhalter
fallen im Audit sofort auf.

## Mitwirken

Korrekturen und Ergänzungen gern per Pull Request. Nach jeder Änderung an
`wiki.json` oder `README.md` das Manifest neu rechnen — die Prüfsummen werden
**nie** von Hand gepflegt:

```bash
python3 scripts/build_wiki_manifest.py --write WIKI-ISO-17025
python3 scripts/build_wiki_manifest.py --check
```

Die `general_page_id` eines Kapitels bleibt dabei unangetastet: eine neue UUID
machte aus einem überarbeiteten Kapitel auf jeder Installation, die die Vorlage
schon importiert hat, ein zweites.
