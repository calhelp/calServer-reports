# FREE-DELIVERY-JSON-SAMPLE — Freier Versandschein (V2)

Das Lieferpapier für Geräte, zu denen es **keinen Auftrag gibt**: Warenannahme,
Rücksendung, Übergabe an ein Fremdlabor. Gedruckt aus dem Arbeitsplatz
„Schnellerfassung > Versandschein", nicht aus einem Datensatz — gefüllt aus
einem **JSON-Datensatz** (Contract `free-delivery-note` v1.0) statt aus SQL.

V2-Nachfolger von `DELIVERY-STANDALONE/main_reports/Free_Delivery.jrxml` (V1,
SQL mit `MTAG IN (…)`). Die V1-Vorlage bleibt im Repository: Sie läuft auf
V1-Installationen weiter, solange dort die alte Maske benutzt wird.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/free-delivery-json-sample.jrxml` | Hauptbericht: Fensterbrief nach DIN 5008 Form B, Informationsblock (Nummer/Datum/Kunden-Nr./Ansprechpartner/Sendungsnummer), Empfängerblock, Abhakliste, Prüfvermerk |
| `subreports/devices.jrxml` | Geräteliste als Abhakliste; `devices`-Array via `subDataSource("devices")` |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `free-delivery-note` v1.0, vier Positionen) |
| `main_reports/free-delivery-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |
| `parameters.json` | Parameter-Manifest für die Berichtsvariablen in calServer V2 |

## Contract `free-delivery-note` (v1.0)

Dataset-Builder: Laravel `FreeDeliveryNoteDataBuilder`. Blöcke:

| Block | Inhalt | Herkunft |
|-------|--------|----------|
| `meta` | `contract`, `schema_version`, `generated_at`, `generated_date`, `locale` | Server |
| `document` | `number`, `date`, `subject`, `customer_number`, `item_count` | Maske (Nummer/Datum/Betreff), Kundennummer fällt auf den Kunden zurück |
| `sender` | `contact_name`, `email`, `phone` | Maske, vorbelegt aus dem angemeldeten Benutzer |
| `customer` | Name, Nummer, Anschrift, `custom_fields` | gewählter Kunde |
| `customer_contact` | Name, Anschrift, E-Mail, Telefon | gewählter Lieferkontakt, roh |
| `delivery` | **aufgelöste** Versandanschrift: `name`, `contact_name`, `street`, `zip`, `city`, `country`, `email`, `phone` | Server |
| `devices[]` | `asset_number`, `serial_number`, `description`, `manufacturer`, `model`, `type_code`, `next_calibration_date`, `custom_fields` | gewählte Geräte, in der Reihenfolge der Erfassung |
| `shipping` | `tracking_number`, `note`, `item_count` | Maske; `item_count` zählt der Server |

**Warum `delivery` aufgelöst ankommt.** Ein Lieferkontakt ist in calServer oft
eine *Adresse* und keine Person („Wareneingang, Tor 3"). Ob die Sendung dorthin
geht oder an die Kundenanschrift, entscheidet deshalb der Server: Trägt der
Kontakt eine Anschrift, gewinnt sie; sonst steht die des Kunden im Fenster. Der
Empfängername ist immer der Kunde — ein Tor ist kein Rechtssubjekt. Die Vorlage
bindet damit **einen** Block statt einer Fallback-Kette, die sie richtig
erraten müsste.

**`devices[]` ist zeichengleich mit `location-report` v1.2.** Dieselbe Frage
(was liegt im Karton), dieselbe Antwort — deshalb ist der Unterbericht derselbe
wie beim Leihschein. Wer die Spalten anpasst, kopiert die Änderung ins andere
Bündel.

## Geometrie (Fensterbrief)

Wie beim Leihschein, siehe ADR `2026-08-16-der-leihschein-ist-ein-versanddokument`:

```
Anschriftfeld        20 mm von links, 45 mm von oben, 85 × 45 mm
Zusatz-/Vermerkzone  obere 17,7 mm  (Rücksendeangabe)
Anschriftzone        untere 27,3 mm (Lieferanschrift)
Betreffzeile         98,4 mm von oben
```

Umgerechnet (1 mm = 2,8346 pt, Seitenränder links 17 pt / oben 12 pt) liegt das
Anschriftfeld im Titelband bei `x=40, y=116, 241 × 128 pt` — **ein** Frame. Für
DIN 676 Form A (kurzer Briefkopf) wird `y=116` zu `y=64`, sonst nichts.

## ⚠️ Leeres Blatt = fehlende Datenquelle

Ohne JSON-Datenquelle bleibt die Seite leer bzw. bricht auf `subDataSource(...)`
ab. Vorschau: mitgelieferter Adapter (Default über
`com.jaspersoft.studio.data.defadapter`) → „Open → Preview".

Live (calServer V2): Report-Setting-Variable `data_contract = free-delivery-note`
— auf dem Systembericht-Platz „Versandschein" ist das der Vorgabewert des Grids,
eine Variable braucht es dort also nur, wenn davon abgewichen wird. Den
Datensatz zum Mitentwickeln liefert
`POST /api/v2/free-delivery-notes/reports/dataset` (Rumpf wie beim Drucken:
`report_id`, `inventory_ids`, Kopffelder). JasperReports **6.20.6** verbindlich.

## Einrichtung in calServer V2

1. Administration > Berichte: Der Platz **„Versandschein"** (Grid
   `free_delivery`, Ordner `individual_delivery`) existiert auf jeder
   Installation und ist nicht löschbar.
2. Dieses Bündel als ZIP hochladen.
3. Briefkopf wie bei jedem Bericht über das Overlay zuweisen.
4. Absenderangaben pflegen: `company_name`, `company_street`, `company_zip`,
   `company_city`, `company_country` (oder `company_sender_line`) — dieselben
   Variablen wie beim Auftragsbeleg. Ohne sie bleibt die Rücksendeangabe leer;
   das ist kein Fehler, der Umschlag trägt sie dann selbst.
5. Rechte: Der Arbeitsplatz hängt an der Operation
   `individual_delivery_report`. Die Auswahllisten der Maske folgen den
   gewöhnlichen Leserechten (`customers_view`, `inventory_view`).
