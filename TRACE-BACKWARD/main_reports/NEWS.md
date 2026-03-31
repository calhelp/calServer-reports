# Neue Reports: Rückführbarkeits-Analyse (Traceability)

**Zwei neue Berichte im calServer-Reports-Repository machen die messtechnische Rückführbarkeit sichtbar — in beide Richtungen.**

---

## Worum geht es?

Kalibrierungen bilden eine Kette: Ein Messmittel wird mit einem Referenznormal kalibriert, dieses Normal wurde selbst mit einem höherwertigen Normal kalibriert, und so weiter. Diese Kette — die **messtechnische Rückführbarkeit** — ist ein zentraler Bestandteil jeder Kalibrierung und wird bei Audits regelmäßig geprüft.

Bisher musste man diese Zusammenhänge im calServer manuell nachverfolgen. Die neuen Traceability-Reports automatisieren das.

---

## Die beiden neuen Berichte

### Wirkungsanalyse (Forward Trace)

> *Ein Referenznormal zeigt Abweichungen — welche Messmittel sind betroffen?*

Der Bericht **Forward Trace** startet bei einem Normal und zeigt alle Geräte, die damit kalibriert wurden — auch indirekt über mehrere Stufen. Das ist besonders nützlich, wenn:

- ein Normal **außerhalb der Toleranz** liegt und geprüft werden muss, welche Kalibrierungen betroffen sind,
- ein Normal **ausgetauscht** wird und die abhängigen Geräte identifiziert werden sollen,
- im Rahmen einer **Rückrufaktion** schnell alle betroffenen Instrumente ermittelt werden müssen.

### Rückführungskette (Backward Trace)

> *Mit welchen Normalen wurde dieses Gerät kalibriert — und wer hat die Normale kalibriert?*

Der Bericht **Backward Trace** startet bei einem Messmittel und zeigt die vollständige Normalkette aufwärts. Typische Anwendungsfälle:

- **Audit-Nachweis:** Lückenlose Dokumentation der Rückführbarkeit auf Knopfdruck.
- **Zertifikatserstellung:** Übersicht über alle eingesetzten Normale und deren Kalibrierstatus.
- **Qualitätssicherung:** Prüfen, ob alle Normale in der Kette selbst gültig kalibriert sind.

---

## Was zeigen die Berichte?

Beide Reports zeigen im Kopfbereich die **Stammdaten des analysierten Instruments** (Inventar-Nr., Beschreibung, Hersteller, Typ, Seriennummer) und darunter die Ergebnistabelle mit:

| Spalte | Inhalt |
| --- | --- |
| Stufe | Abstand zum Start-Instrument (1 = direkt, 2 = indirekt, …) |
| Inv.-Nr. | Inventarnummer |
| Beschreibung | Gerätebeschreibung |
| Hersteller | Hersteller |
| Typ | Gerätetyp |
| Seriennr. | Seriennummer |
| Kal.-Datum | Letztes Kalibrierdatum |
| Ergebnis | Bestanden / nicht bestanden |
| Fälligkeit | Nächstes Kalibrierdatum |
| Kal.-Kennz. | Kalibrierkennzeichnung |

Beide Berichte werden im **A4-Querformat** ausgegeben und unterstützen **Deutsch und Englisch** (Parameter `Sprache`).

---

## Einrichtung

Die Reports liegen im Repository unter `TRACE-FORWARD/` und `TRACE-BACKWARD/`. Sie können wie gewohnt über die Reportverwaltung im calServer hochgeladen werden.

**Benötigter Parameter:** `P_MTAG` — das ist die MTAG-ID des Instruments, das analysiert werden soll. Der calServer übergibt diesen Parameter automatisch, wenn der Report aus der Inventar-Ansicht heraus gestartet wird.

**Optional:** `maxDepth` begrenzt die Analysetiefe (Standard: 5 Stufen). In der Praxis sind Kalibrierungsketten selten tiefer als 3–4 Stufen.

---

## Technische Hinweise

- Kompatibel ab **MySQL 5.7** (keine CTEs erforderlich)
- Nur **aktive Kalibrierungen** werden berücksichtigt (`C2339 = 1`)
- **Zirkuläre Verweise** (A kalibriert B, B kalibriert A) werden automatisch erkannt und ausgeschlossen
- Unterstützt **Mandantentrennung** über den Parameter `PrefixTable`
- Ausgabeformat: **PDF** (weitere Formate über JasperReports möglich)

---

## Download

Die aktuellen Report-Pakete stehen als ZIP-Archiv zur Verfügung:

- [Aktuelle Downloads](https://calhelp.github.io/calServer-reports/downloads/)
- [GitHub-Repository](https://github.com/calhelp/calServer-reports)

---

*Die Traceability-Reports sind ein Community-Beitrag zum calServer-Reports-Projekt. Feedback, Verbesserungsvorschläge und Pull Requests sind jederzeit willkommen!*
