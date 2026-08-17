# Ticket-Status für ein akkreditiertes Labor

Der Ablauf, den ein Vorgang aus Risiko-, Chancen- und Maßnahmenmanagement nach
ISO/IEC 17025 durchläuft. Gehört zu den Ticketmanagement-Paketen
[`TICKET-CONFIG-DAKKS`](../TICKET-CONFIG-DAKKS/) (zwei Methoden) bzw.
[`TICKET-CONFIG-DAKKS-3D`](../TICKET-CONFIG-DAKKS-3D/) (drei Methoden), die
Vorgangsarten, Themenfelder und die Risikobewertung mitbringen.

## Der Ablauf

| Reihenfolge | Status | Bedeutung |
|-------------|--------|-----------|
| 10 | Neu | Erfasst, noch nicht bewertet |
| 20 | Bewertet | Auswirkung und Wahrscheinlichkeit stehen, der Risikowert ist berechnet |
| 30 | Maßnahme geplant | Maßnahme, Verantwortliche und Termin sind festgelegt |
| 40 | In Umsetzung | Die Maßnahme läuft |
| 50 | Wirksamkeit prüfen | Umgesetzt, Wirksamkeit noch nicht belegt |
| 60 | Abgeschlossen | Wirksamkeit belegt, Restrisiko akzeptiert |
| 70 | Kein Handlungsbedarf | Bewertet und bewusst nicht behandelt, mit Begründung |

## Warum die Wirksamkeit einen eigenen Status hat

Abschnitt 8.7 verlangt, die Wirksamkeit ergriffener Korrekturmaßnahmen zu
bewerten. Wer „umgesetzt" und „wirksam" in einem Status zusammenfasst, hat
diesen Nachweis nicht — und merkt es erst, wenn in der Begutachtung nach der
Wirksamkeitsbeurteilung gefragt wird. Der Zwischenstatus macht die offene
Prüfung sichtbar: Alles in „Wirksamkeit prüfen" ist Arbeit, die noch aussteht.

## Warum „Kein Handlungsbedarf" kein Abschluss ist

Ein akzeptiertes Risiko ist eine Entscheidung, kein Vergessen. 8.5.1 c) erlaubt
ausdrücklich, ein Risiko zu akzeptieren; verlangt wird, dass die Entscheidung
nachvollziehbar ist. Als eigener Status bleibt sie auffindbar, statt in der
Menge der abgeschlossenen Vorgänge zu verschwinden — und die Liste der
akzeptierten Risiken ist eine brauchbare Eingabe für die Managementbewertung
(8.9.2).

## Import

**Administration → Statusverwaltung**, Schaltfläche **Paket** (Berechtigung
`status_import`). Wiedererkannt wird ein Status über Bereich und Titel; ein
zweiter Import legt keine Zwillinge an.

## Grenzen

- **Keine Feldfunktionen.** Ticket-Status führen in calServer keine
  Feldregistry, anders als Kalibrier- oder Reparaturstatus. Dass ein Ticket vor
  dem Abschluss eine Wirksamkeitsbeurteilung trägt, lässt sich damit nicht
  technisch erzwingen; der Status macht es sichtbar, die Verfahrensanweisung
  verbindlich.
- **Keine Folgeaktionen im Paket.** E-Mail-Benachrichtigungen beim
  Statuswechsel hängen an Mailvorlagen, die je Installation anders heißen. Sie
  lassen sich nach dem Import in den Statusregeln ergänzen.
- **Einsprachig (deutsch).** Für eine andere Sprache ein eigenes Paket pflegen.
