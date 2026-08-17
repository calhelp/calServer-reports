# LOCATION-JSON-SAMPLE — Leihschein / Versandschein (V2 / APEX)

Standort-/Leihbericht als **V2-Bundle** im Sinne von
[ADR-009](https://github.com/calhelp/calServer-yii/blob/develop/docs-v2/entwicklung/adr/009-report-data-contract-statt-sql-templates.md):
gefüllt aus dem Report-Data-Contract `location-report` (JSON) mit lesbaren
API-Feldnamen statt aus eingebettetem SQL gegen V1-Codespalten.

Seit Contract **v1.2** ist der Bericht als **Versanddokument** gesetzt: ein
Fensterbrief nach DIN 5008 Form B mit der Lieferadresse im Anschriftfeld und
einer Prüfmittelliste zum Abhaken. Begründung:
[ADR 2026-08-16](https://github.com/calhelp/calServer-yii/blob/develop/laravel/docs/adr/2026-08-16-der-leihschein-ist-ein-versanddokument.md).

## Referenz-Bundle für den Systembericht „Leihschein"

Dieses Bundle ist die empfohlene Vorlage für den **Leihschein**, den calServer
beim Buchen einer Ausleihe erzeugt und der Leihschein-E-Mail anhängt.

Dafür gibt es auf jeder calServer-V2-Installation eine feste Zeile in
**Administration > Berichtsverwaltung > Master-Reports**: den Platzhalter
**Leihschein** (Etikett „Systembericht", Grid `location`, Ordner `locations`).
Er wird bei der Installation angelegt, ist nicht löschbar und wartet auf sein
Bundle — hochladen genügt, danach hängt der Leihschein an der Mail. Solange
nichts hochgeladen ist, geht die Mail ohne Anhang raus.

Details: [Systemberichte](https://github.com/calhelp/calServer-yii/blob/develop/docs-v2/admin/berichte/systemberichte.md).

Als Referenz gedacht, nicht als Vorschrift: Ein eigenes Layout wird auf
derselben Zeile genauso hochgeladen.

## Fensterbrief: die Geometrie

| Element | Lage (ab Blattkante) | Im Titelband (pt) |
|---------|----------------------|-------------------|
| Anschriftfeld (Frame) | 20 mm links, 45 mm oben, 85 × 45 mm | `x=40 y=116 w=241 h=128` |
| Rücksendeangabe | Zusatz-/Vermerkzone, 12 mm ab Feldoberkante | Frame-intern `y=34` |
| Lieferanschrift | Anschriftzone, 17,7 mm ab Feldoberkante | Frame-intern `y=50` |
| Betreffzeile | 98,4 mm oben | `y=267` |
| Falz-/Lochmarken | linker Rand bei 105 / 148,5 / 210 mm | Hintergrundband |

Das passt in einen DIN-lang-Fensterumschlag nach DIN 680 (Fenster 20 mm von
links, 15 mm von unten) bei Falzung auf 105 mm und 210 mm.

**Form A statt Form B?** Wer einen kurzen Briefkopf hat und das Anschriftfeld
schon ab 27 mm setzen will, ändert **eine** Zahl: `y="116"` am Frame
`Anschriftfeld` wird zu `y="64"`. Deshalb steckt der ganze Block in einem Frame.

**Der linke 12-pt-Streifen ist frei.** Dort liegen die Falz- und Lochmarken; der
Textkörper beginnt bei `x=12` (rund 10 mm ab Blattkante). Wer Elemente ergänzt,
setzt sie nicht auf `x=0`, sonst läuft die Lochmarke bei 148,5 mm hindurch.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/location-json-sample.jrxml` | Hauptbericht: Anschriftfeld mit Rücksendeangabe, Informationsblock rechts (Kunden-Nr., Ansprechpartner, Telefon, Versanddatum, Rückgabe, Status, Sendungsnummer), Betreffzeile, Entleiher-Block, Versandhinweis, Prüfvermerk, Falzmarken, Seiten-Footer |
| `subreports/devices.jrxml` | Sendungsinhalt als Abhakliste — je Gerät eine Zeile mit Ankreuzfeld, Positionsnummer und nächster Kalibrierung; Spaltenköpfe wiederholen sich auf Folgeseiten |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `location-report` **v1.2**) |
| `main_reports/location-json-sample_adapter.xml` | Mitgelieferter Jaspersoft-Studio-**JSON-Data-Adapter** auf `sample-data.json` — macht die Vorschau turnkey (siehe „Vorschau ohne Backend") |

## Was das Blatt kann

- **Fensterbrief.** Die Lieferadresse steht im Fenster, darüber die
  Rücksendeangabe. Kein Adressetikett mehr, kein Abtippen.
- **Abhakliste.** Jede Position trägt ein Ankreuzfeld und eine Nummer, über der
  Tabelle steht die Positionszahl aus dem Datensatz (nicht die gedruckte
  Zeilenzahl — weicht beides ab, ist genau das der Befund). Am Ende ein
  Prüfvermerk „Sendung vollständig und unbeschädigt erhalten" mit Datumslinie.
- **Keine Unterschriftszeilen.** Das Blatt reist mit der Sendung; niemand
  quittiert es am Tresen. Wer im eigenen Layout gegenzeichnen lässt, baut sie
  wieder ein.
- **Sendungsdaten.** Sendungsverfolgungsnummer im Informationsblock,
  Versandhinweis (Bemerkung der Buchung) über der Tabelle. Beide fehlen
  spurlos, wenn sie leer sind.
- **Kein Standortblock.** `location_1..5` sind auf einer Leihe interne
  Platzierungsfelder, und eines davon ist auf vielen Anlagen als
  `[CURRENT_USER]` konfiguriert — unter „Standort" stand dann der Name des
  Buchenden. Der Contract liefert die Felder weiter, das Referenz-Layout
  druckt sie nicht.

## Datenanbindung

- **Kein** `<queryString>`, **keine** `REPORT_CONNECTION`.
- Der Runner füllt den Hauptbericht mit einer `JsonDataSource`
  (`dataSourceType=json`, `dataJson`); der Bericht ist genau ein Datensatz
  (Wurzelobjekt).
- Das **Rückgabedatum** ist seit v1.2 ein eigenes Feld: `location.rental_end`.
  Bis v1.1 stand es unter `location.custom_fields.rental_end` — dort ist es
  seit ADR-013 leer, weil die Leihende eine physische Spalte wurde und
  `custom_fields` nur JSON-Felder trägt. Das Backend spiegelt den Wert
  zusätzlich unter dem alten Schlüssel, damit v1.1-Vorlagen weiterlaufen.
- Das **Prüfmittel-Grid** läuft über `subDataSource("devices")` in
  `subreports/devices.jrxml`. Ein Set (Koffer) wird als **ein** Objekt
  verliehen und auf **einem** Schein quittiert, also stehen seine Teile mit
  darauf. `device` bleibt daneben bestehen, damit eine gegen v1.0 geschriebene
  Vorlage weiterläuft. Welche Geräte zum Koffer gehören, beantwortet
  serverseitig ein einziger Resolver über die Elternkette — bis August 2026
  hing das an einem Pfad-Cache, und auf Anlagen mit importierten Beständen kam
  der Koffer als eine Position auf dem Papier an.
- **Sendungsnummer und Bemerkung** liest das Backend, nicht das Template: Der
  Block `shipping` kommt gefüllt an, unabhängig davon, unter welchem `api_name`
  die Installation die beiden Felder führt (Details unten).
- `location_1..5` und `status` liefern **lesbaren Text**, keine uIDs: Ist ein
  Standortfeld als `[CURRENT_USER]` konfiguriert, hält die Spalte eine
  Benutzer-uID — der Datensatz trägt den Namen. Genauso wird der Status-uID zum
  Status-Titel. (Das Referenz-Layout druckt `location_1..5` nicht, siehe oben —
  ein eigenes Layout bekommt sie aufbereitet.)
- Die Lieferadresse (`delivery_customer`) fällt **serverseitig** auf den
  Kunden zurück, wenn kein eigener Lieferkunde hinterlegt ist — das Template
  braucht keine Fallback-Logik.
- Den Datensatz erzeugt das calServer-V2-Backend (`LocationReportDataBuilder`).

Aktivierung in calServer: Bundle auf ein Report-Setting mit grid_name
`location` und Ordner `locations` hochladen — für den Leihschein ist das der
Systembericht-Platzhalter (siehe oben). Der Contract wird am Bundle erkannt
(kein `<queryString>` → `location-report`); eine Report-Variable
`data_contract` ist nur nötig, wenn davon abgewichen werden soll (Details siehe
V2-Doku „V2-Berichte mit JSON-Datenquelle").

## ⚠️ Warum ein leeres/weißes Blatt erscheinen kann

Dieses Bundle ist **datenquellenlos**: Der Bericht enthält **kein** eingebettetes
SQL und **keine** Beispieldaten im Template selbst. Er rendert nur dann Inhalt,
wenn ihm eine **JSON-Datenquelle** übergeben wird. Wird er ohne Datenquelle
ausgeführt — z. B. „Preview" in Jaspersoft Studio ohne konfigurierten
Data-Adapter, oder Generierung in der Live-Umgebung **ohne** die Report-Variable
`data_contract` — bleibt die Seite leer. Das ist **kein** Template-Fehler,
sondern die fehlende Datenanbindung. Abhilfe:

- **Vorschau ohne Backend (Jaspersoft Studio):** Das Bundle bringt den Adapter
  `location-json-sample_adapter.xml` mit und referenziert ihn über die
  Report-Property `com.jaspersoft.studio.data.defadapter`. „Open → Preview"
  füllt den Bericht direkt aus `sample-data.json`. Falls die Studio-Version den
  Default-Adapter nicht automatisch zieht, den Adapter im Vorschau-Dropdown
  einmalig auswählen.
- **Live-Umgebung (calServer V2):** Auf dem Report-Setting die report-scoped
  Variable `data_contract = location-report` setzen — dann liefert das Backend
  (`LocationReportDataBuilder`) den JSON-Datensatz an den Runner. Ohne diese
  Variable läuft der klassische JDBC-Pfad, der hier mangels `<queryString>`
  keine Daten hat.

## Contract `location-report` (v1.2)

| Block | Felder |
|-------|--------|
| `meta` | `contract`, `schema_version`, `generated_at`, `generated_date`, `locale` |
| `location` | `location_1..5`, `location_date`, `location_time`, **`rental_end`** (v1.2), `is_active`, `status`, `custom_fields{}` |
| `shipping` | **v1.2** — `tracking_number`, `note`, `item_count` |
| `device` | `asset_number`, `serial_number`, `description`, `manufacturer`, `model`, `type_code`, `next_calibration_date`, `custom_fields{}` (`{}` wenn kein Gerät verknüpft) |
| `devices[]` | **v1.1** — alle Geräte der Leihe, Wurzelgerät zuerst; Felder wie `device`. Bei einer Einzelbuchung genau ein Eintrag. |
| `customer` | `name`, `customer_number`, `street`, `zip`, `city`, `country`, `custom_fields{}` |
| `customer_contact` | `name`, `street`, `zip`, `city`, `email`, `phone` (`{}` wenn kein Kontakt verknüpft) |
| `delivery_customer` | wie `customer`; serverseitiger Fallback auf `customer` |
| `delivery_contact` | wie `customer_contact` |

v1.2 ist **additiv**: Jedes Feld aus v1.0/v1.1 behält Namen und Bedeutung.

> **Status:** Referenz-/Beispielvorlage. JasperReports **6.20.6** bleibt
> verbindlich (siehe `robots.md`).

## Parameter-Katalog (`parameters.json`)

Dieses Bundle liefert ein **Parameter-Manifest** (`parameters.json` an der
Bundle-Wurzel), damit calServer V2 die konfigurierbaren Parameter beim Anlegen
von Berichtsvariablen mit Beschreibung, Typ und Standardwert anbietet (siehe
[Konzept](https://github.com/calhelp/calServer-yii/blob/develop/docs/konzept-report-parameter-katalog.md)).

| Parameter | Rolle | Wirkung |
|-----------|-------|---------|
| `Company_sender_line` | variable (global) | Die Rücksendeangabe über der Anschrift. Leer → aus den vier folgenden zusammengesetzt |
| `Company_name`, `Company_street`, `Company_zip`, `Company_city` | variable (global) | Absenderanschrift. Dieselben `company_*`-Variablen nutzt der Auftragsbeleg |
| `Company_country` | variable (global) | Absenderland. Steuert zugleich die Landzeile des Empfängers — gedruckt nur bei abweichendem Land |
| `Show_fold_marks` | variable (type) | `0` schaltet Falz- und Lochmarken ab (vorgedrucktes Briefpapier) |
| `Company_footer` | variable (type) | Optionale Fußzeile am unteren Rand jeder Seite. Leerer Default → keine Änderung am Layout |

Sind die `company_*`-Variablen nicht gepflegt, bleibt die Rücksendeangabe leer —
kein Fehler, der Umschlag trägt sie dann selbst.

### Sendungsnummer und Bemerkung

Beide Angaben sind mandantenkonfigurierte Standortfelder — wie sie heißen,
entscheidet die Installation. Deshalb rät das Backend nicht, sondern lässt sich
das Feld nennen:

| Berichtsvariable (`report_type = location`) | Zeigt auf das Feld mit |
|---------------------------------------------|------------------------|
| `shipping_tracking_field` | der Sendungsverfolgungsnummer |
| `shipping_note_field` | der Bemerkung zur Sendung |

Inhalt ist der `api_name` des Feldes aus der Feldverwaltung; der physische
Spaltenschlüssel geht genauso, die Registry übersetzt ihn. Heißt das Feld
bereits `tracking_number` bzw. `shipping_note`, findet der Bericht es ohne
Variable. Ist nichts konfiguriert, bleiben `shipping.tracking_number` und
`shipping.note` leer, und Sendungsnummer wie Hinweis verschwinden spurlos vom
Blatt. Am Template ändert das nichts — es sieht nur `shipping.*`.
