# Traceability Reports (Rückführbarkeit)

Kalibrierungen verknüpfen ein **Messmittel** (DUT – Device Under Test) mit
einem oder mehreren **Referenznormalen** (Standards). Jedes Normal besitzt
selbst eine Kalibrier-Historie und kann wiederum mit höherwertigen Normalen
kalibriert worden sein. So entsteht eine Kette – die **messtechnische
Rückführbarkeit (Traceability)**.

Diese beiden Berichte machen die Kette in beide Richtungen sichtbar:

---

## Wirkungsanalyse / Impact Analysis (`Forward_Trace.jrxml`)

> *„Unser Referenznormal zeigt Abweichungen – welche Geräte sind betroffen?"*

Ausgehend von einem **Normal** listet der Bericht alle Messmittel auf, die
direkt oder indirekt damit kalibriert wurden. Das ist z. B. nötig, wenn:

* ein Normal **außerhalb der Toleranz** liegt und geprüft werden muss,
  welche Kalibrierungen möglicherweise ungültig sind,
* ein Normal **aus dem Verkehr gezogen** wird und die betroffenen Geräte
  einem anderen Normal zugeordnet werden sollen,
* im Rahmen einer **Rückrufaktion** schnell alle abhängigen Instrumente
  ermittelt werden müssen.

Der Bericht zeigt im Kopfbereich die Stammdaten des Normals (Inv.-Nr.,
Seriennummer, Beschreibung, Typ, Hersteller, Modell) und darunter die
betroffenen Geräte, gegliedert nach Tiefenstufe.

---

## Rückführungskette / Traceability Chain (`Backward_Trace.jrxml`)

> *„Mit welchen Normalen wurde dieses Gerät kalibriert – und wer hat die
> Normale kalibriert?"*

Ausgehend von einem **Messmittel** zeigt der Bericht die vollständige
Normalkette aufwärts bis zum höchsten Referenznormal. Typische Einsatz-
situationen:

* **Audit-Nachweis:** Prüfer:innen und Akkreditierungsstellen verlangen
  den lückenlosen Nachweis der messtechnischen Rückführbarkeit.
* **Kalibrierzertifikate:** Beim Erstellen eines Zertifikats soll
  dokumentiert werden, mit welchen Normalen (und deren eigener
  Kalibrier-Historie) das Gerät kalibriert wurde.
* **Qualitätssicherung:** Sicherstellen, dass alle eingesetzten Normale
  selbst gültig kalibriert sind.

Der Bericht zeigt im Kopfbereich die Stammdaten des Messmittels und
darunter die Normalkette, gegliedert nach Tiefenstufe.

---

## Parameter

| Name | Typ | Pflicht | Standard | Beschreibung |
| --- | --- | --- | --- | --- |
| `P_MTAG` | String | Ja | `""` | MTAG des Start-Instruments (Normal bei Forward Trace, DUT bei Backward Trace). |
| `maxDepth` | String | Nein | `5` | Maximale Tiefe der Analyse (1–5 Stufen). |
| `PrefixTable` | String | Nein | `""` | Tabellenpräfix für Mandantentrennung (z. B. `thermo_`). |
| `Sprache` | String | Nein | `Deutsch` | Spaltenüberschriften auf Deutsch oder Englisch. |

### Beispiel: JasperStarter

```bash
jasperstarter process Forward_Trace.jrxml \
  -o "../pdf/Forward-Trace" -f pdf \
  -t mysql -H mysql_db -n calserver -u user -p pass \
  -P P_MTAG=0038e950-df7f-bf73-f5d7-fc371a1a94f0 \
     maxDepth=5 \
     PrefixTable=thermo_ \
     Sprache=Deutsch \
     REPORT_LOCALE=de_DE
```

---

## Was zeigt der Bericht?

### Kopfbereich (Geräte-Stammdaten)

Beide Berichte zeigen im Kopf die Stammdaten des analysierten Instruments:
Inventar-Nr., Seriennummer, Beschreibung, Typ, Hersteller, Modell und MTAG.

### Ergebnistabelle

Die Tabelle listet die gefundenen Instrumente mit folgenden Spalten
(zweisprachig Deutsch/Englisch):

| Spalte | Inhalt |
| --- | --- |
| Stufe | Wie viele Schritte vom Start-Instrument entfernt |
| Inv.-Nr. | Inventar-/Asset-Nummer des Instruments |
| Seriennr. | Seriennummer |
| Beschreibung | Gerätebeschreibung (eingerückt je Stufe) |
| Hersteller | Hersteller des Instruments |
| Modell | Modellbezeichnung |
| Kal.-Datum | Datum der letzten Kalibrierung |
| Ergebnis | Kalibrierungsergebnis (z. B. bestanden/nicht bestanden) |
| Zertifikat-Nr. | Nummer des Kalibrierzertifikats |
| Fälligkeit | Nächstes Kalibrierdatum |
| Kal.-Kennz. | Kalibrierkennzeichnung |

### Fußzeile

Anzahl der gefundenen Instrumente und Seitennummerierung.

---

## Hinweise

* **Seitenformat:** A4 Querformat – genug Platz für alle elf Spalten.
* **Nur aktive Kalibrierungen:** Beide Berichte berücksichtigen
  ausschließlich die jeweils aktive Kalibrierung eines Instruments
  (`C2339 = 1`).
* **Zyklen-Schutz:** Zirkuläre Verweise (A kalibriert B, B kalibriert A)
  werden erkannt und ausgeschlossen.
* **Max. 5 Stufen:** In der Praxis sind Kalibrierungsketten selten tiefer
  als 3–4 Stufen. Der Parameter `maxDepth` begrenzt die Tiefe auf
  maximal 5.
* **MySQL 5.7+:** Kompatibel ab MySQL 5.7 (keine CTEs erforderlich).
