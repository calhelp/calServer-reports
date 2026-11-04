# Vorschaubilder der JSON-Beispielberichte

Gerendert mit JasperReports 6.20.6 aus den `sample-data.json` der jeweiligen
`*-JSON-SAMPLE`-Bundles (reine Demodaten, keine Kundendaten). Die
Akkreditierungsnummer in den Etiketten ist für die Bilder durch den Platzhalter
`D-K-00000-00-00` ersetzt.

| Bild | Bundle |
|------|--------|
| `jasper-kalibrierschein-dakks-seite1.webp`, `jasper-kalibrierschein-normale.webp`, `jasper-kalibrierschein-messergebnisse.webp` | `DAKKS-JSON-SAMPLE` (Seiten 1, 2, 5) |
| `jasper-auftragsbestaetigung.webp` | `ORDER-JSON-SAMPLE` |
| `jasper-preisliste.webp` | `PRICE-LIST-JSON-SAMPLE` |
| `jasper-kalibrierkontrollblatt.webp` | `KALIBRIERKONTROLLBLATT-JSON-SAMPLE` |
| `jasper-versandschein.webp` | `FREE-DELIVERY-JSON-SAMPLE` |
| `jasper-reparaturbericht.webp` | `REPAIR-JSON-SAMPLE` |
| `jasper-kalibrieretiketten.webp` | `STICKER-DAKKS-40X30MM-QR`, `STICKER-INV-40X30MM-QR`, `STICKER-CAL-INV-ZEBRA`, `STICKER-DAKKS-18MM` (`-JSON-SAMPLE`) |

Verwendet auf calserver.com unter /funktionen/berichtswesen.

## E-Rechnung (ZUGFeRD)

`rechnung-zugferd.pdf` ist `ORDER-JSON-SAMPLE` mit `document.type = invoice`,
danach mit dem `ZugferdInvoiceService`/`ZugferdXmlBuilder` aus calServer-yii
(horstoeko/zugferd, Profil EN 16931) zur hybriden PDF/A-3-Rechnung mit
eingebetteter `factur-x.xml` gemacht. XSD-Prüfung bestanden; Beträge im XML
(245,00 netto, 41,15 USt., 286,15 brutto) gleich dem Papierbild.
`jasper-rechnung-zugferd.webp` zeigt die Rechnung mit einem Ausschnitt der XML.
