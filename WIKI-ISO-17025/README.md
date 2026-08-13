# Wiki: QM-Gerüst nach ISO/IEC 17025

Gerüst für die Managementdokumentation eines Kalibrier- oder Prüflabors,
gegliedert nach den Kapiteln 4 bis 8 der DIN EN ISO/IEC 17025:2018 — **26
Artikel in je zwei Sprachen** (Deutsch und Englisch), verteilt auf sechs
Kategorien je Sprache, im Format `calserver.wiki` (Version 1), paketiert als
`calserver.wiki-package`.

Jeder Artikel nennt die Anforderung in eigenen Worten, eine
Umsetzungs-Checkliste als Aufgabenliste und die Nachweise, die im Audit
verlangt werden. Wo es passt, benennt er das calServer-Modul, in dem der
Nachweis entsteht.

## Paketinhalt

| Datei | Zweck |
| --- | --- |
| `manifest.json` | Manifest: jede Datei mit SHA-256-Prüfsumme und Größe |
| `wiki.json` | Das Wiki (12 Kategorien, 26 Artikel, 52 Seiten) |
| `README.md` | Diese Beschreibung |

Das Manifest ist der Manipulationsanker des Formats: calServer lehnt beim
Import jedes Paket ab, dessen Inhalt vom Manifest abweicht — in beide
Richtungen. Das maschinenlesbare Schema:
[`wiki-package.schema.json`](https://calhelp.github.io/calServer-reports/schema/wiki-package.schema.json).

Medien (`media/`) enthält dieses Paket nicht; das Format trägt sie, sobald eine
Vorlage Bilder mitbringt.

## Aufbau

| Kategorie | Normkapitel | Artikel |
| --- | --- | --- |
| ISO 17025 – Überblick | – | Die Norm im Überblick |
| ISO 17025 – Allgemeine Anforderungen | 4 | Unparteilichkeit, Vertraulichkeit |
| ISO 17025 – Strukturelle Anforderungen | 5 | Struktur und Verantwortlichkeiten |
| ISO 17025 – Ressourcen | 6 | Personal, Räumlichkeiten, Ausrüstung, Rückführbarkeit, externe Leistungen |
| ISO 17025 – Prozessanforderungen | 7 | Auftragsprüfung, Methoden, Probenahme, Prüfgegenstände, technische Aufzeichnungen, Messunsicherheit, Validität, Berichte, Beschwerden, nichtkonforme Arbeit, Datenlenkung |
| ISO 17025 – Managementsystem | 8 | Dokumentenlenkung, Aufzeichnungen, Risiken, Verbesserung, interne Audits, Managementbewertung |

Dieselben sechs Kategorien gibt es auf Englisch; die Sprachvarianten eines
Artikels hängen an derselben `general_page_id` und erscheinen in calServer als
Übersetzungen desselben Artikels.

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

## Wichtig: ein Gerüst, kein QM-Handbuch

Die Texte sind ein Ausgangspunkt. Sie müssen an das eigene Labor angepasst
werden:

- Verantwortliche Person je Kapitel eintragen
- Verweise auf die eigenen Verfahrensanweisungen ergänzen
- Nicht zutreffende Abschnitte begründet streichen statt leer stehen lassen

Ein unverändert übernommenes Gerüst belegt gegenüber einer
Akkreditierungsstelle nichts. Wo ein Artikel ein calServer-Modul benennt, ist
das ein Hinweis auf die Stelle, an der der Nachweis entsteht, keine Aussage
über Konformität.

## Mitwirken

Korrekturen und Ergänzungen gern per Pull Request. Nach jeder Änderung an
`wiki.json` oder `README.md` das Manifest neu rechnen — die Prüfsummen werden
**nie** von Hand gepflegt:

```bash
python3 scripts/build_wiki_manifest.py --write WIKI-ISO-17025
python3 scripts/build_wiki_manifest.py --check
```
