# Inventarkategorien für Kalibrierlabore (DAkkS-Zuschnitt)

Startvorlage für den Inventar-Kategoriebaum eines akkreditierten
Kalibrierlabors. Oberste Ebene ist die **Messgröße**, darunter steht die
**Normalstufe** — dieselbe Gliederung, nach der auch der Akkreditierungsumfang
geschnitten ist, sodass sich Bestand und Umfang nebeneinanderlegen lassen.

## Was drin ist

```
Elektrische Messgrößen          Länge und Winkel
├── Bezugsnormale               ├── Bezugsnormale
├── Gebrauchsnormale            ├── Gebrauchsnormale
└── Prüfmittel                  └── Prüfmittel
Temperatur und Feuchte          Druck und Vakuum
Masse und Waagen                Kraft, Drehmoment und Härte
Volumen und Durchfluss          Zeit und Frequenz
Hilfs- und Betriebsmittel
├── Adapter und Leitungen
├── Klimaüberwachung
└── Prüfvorrichtungen
```

36 Kategorien: acht Messgrößen mit je drei Normalstufen, dazu ein Ast für
Ausstattung ohne eigene Messfunktion.

| Stufe | Bedeutung | Pflichtfelder |
|-------|-----------|---------------|
| Bezugsnormale | Höchste Rückführungsstufe des Labors, extern kalibriert | Seriennummer, Hersteller, Kalibrierintervall |
| Gebrauchsnormale | Tägliche Arbeit, gegen die Bezugsnormale kalibriert | Seriennummer, Kalibrierintervall |
| Prüfmittel | Messmittel ohne Normalcharakter | Seriennummer sichtbar, nicht pflichtig |
| Hilfs- und Betriebsmittel | Nicht kalibrierpflichtig | keine |

Die Pflichtfelder sind **Kategoriefelder** (`additional_field`): Sie wirken nur
für Geräte dieser Kategorie und lassen den Rest des Bestands unberührt. Ein
Bezugsnormal ohne Seriennummer ist nicht rückführbar — deshalb steht die
Pflicht dort und nicht global in der Feldverwaltung.

## Import

Berichtsverwaltung ist der falsche Ort; Kategorien gehören in die
**Administration → Kategorien**. Dort öffnet die Schaltfläche **Paket** den
Import (Berechtigung `category_import`).

Der Import ist **idempotent**: Wiedererkannt wird eine Kategorie über Typ,
übergeordnete Kategorie und Name. Ein zweiter Import legt keine Zwillinge an.
Im Modus „Bestehende behalten" (Vorgabe) bleiben vorhandene Kategorien
unverändert, es kommt nur dazu, was fehlt.

**Nicht im Paket:** Zuordnungen. Welches Gerät in welcher Kategorie hängt, ist
Bestand der Installation und wird durch den Import nicht angefasst.

## Anpassen

Die Datei `categories.json` lässt sich direkt bearbeiten und ohne Archiv
hochladen — calServer liest auch das nackte Dokument. Wer das ZIP anpasst, muss
danach das Manifest neu schreiben:

```bash
python3 scripts/build_config_manifest.py --write CATEGORY-INVENTORY-DAKKS
python3 scripts/build_config_manifest.py --check
```

Ohne passende Prüfsummen lehnt calServer das Archiv ab. Das ist der Grund,
warum ein Paket von einer Download-Seite überhaupt vertrauenswürdig ist.

## Grenzen

- **Kategorien sind einsprachig.** Dieses Paket ist deutsch; für eine andere
  Sprache ein eigenes Paket pflegen.
- **Die Messgrößen sind ein Vorschlag, kein Umfang.** Welche Größen ein Labor
  führt, steht in seiner Akkreditierungsurkunde. Nicht benötigte Äste vor dem
  Import löschen oder danach in calServer entfernen.
- **Keine Vererbung.** Kategoriefelder wirken je Kategorie, nicht auf
  Unterkategorien. Wer eine Pflicht für den ganzen Ast braucht, trägt sie in
  jede betroffene Kategorie ein.
