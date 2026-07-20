# ORDER-JSON-SAMPLE — Angebot/Auftragsbestätigung/Lieferschein/Rechnung (V2 / APEX)

V2-Nachbildung des **Auftragsbelegs** (Phase D). Im Gegensatz zum V1-Bundle
`ORDER-SAMPLE` (eingebettetes SQL + separater Statistics-Subreport, der die
Steuergruppen per GROUP-BY selbst nachquert) wird dieses Bundle aus einem
**JSON-Datensatz mit lesbaren API-Feldnamen** gefüllt — es enthält **kein SQL**
und ist unabhängig vom DB-Backend (MySQL, PostgreSQL, MSSQL).

**Ein** Template erzeugt — wie in V1 — je nach Auftragsstatus den passenden,
standardkonformen Beleg: **Angebot, Auftragsbestätigung, Lieferschein oder
Rechnung**. Der Server (Laravel `OrderDocumentDataBuilder`) leitet den
Dokumenttyp aus dem Status ab (`document.type`/`type_label`, Contract v1.2)
und löst den Briefkopf-Empfänger je Typ vor (`recipient`): Rechnungen
adressieren die Rechnungsadresse, Lieferscheine die Lieferadresse, alles
andere den Auftraggeber. Das Template verzweigt nur noch auf `document.type`.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `main_reports/order-json-sample.jrxml` | Hauptbericht: Absenderzeile + Briefkopf (`recipient` je Dokumenttyp, Meta-Box Belegnummer/Datum/Kunde/Kontakt/Lieferbedingung/-kosten), abweichende Liefer-/Rechnungsadresse als Info-Block, typabhängiger Betreff, Positionstabelle + Statistik + Zusatzfelder, Rechnungs-/Lieferschein-Spezifika, Fußzeile mit Firmen-/Steuer-/Bankangaben. Alle Labels als `staticText` |
| `subreports/positions.jrxml` | Positionen; `positions`-Array via `subDataSource("positions")` (Pos/Beschreibung/Menge/Einzelpreis/Rabatt/Betrag/MwSt) |
| `subreports/positions-delivery.jrxml` | Positionen **ohne Preise** für Lieferscheine (Pos/Beschreibung/Menge/Einheit); wird bei `document.type = delivery_note` automatisch gewählt |
| `subreports/tax-groups.jrxml` | Steuergruppen; `statistics.tax_groups`-Array via `subDataSource("statistics.tax_groups")` (USt. je Satz — § 14 UStG-Aufschlüsselung) |
| `subreports/custom-fields.jrxml` | Zusatzfelder (W41xx); `document.custom_fields_list`-Array via `subDataSource("document.custom_fields_list")` — Label/Wert je konfiguriertem Feld, generisch |
| `main_reports/sample-data.json` | Beispiel-Datensatz (Contract `order-document` v1.2) |
| `main_reports/order-json-sample_adapter.xml` | Jaspersoft-Studio-JSON-Data-Adapter für die Vorschau |

## Contract `order-document` (v1.2)

Wurzelobjekt mit `meta`, `document` (Nummer/Datum/Status/**Typ**/Kommentar/
Rechtstext, `delivery_condition`/`delivery_costs`, `custom_fields` als Objekt
**und** `custom_fields_list` als geordnete `[{key,label,value}]`-Liste für die
W41xx-Zusatzfelder), `supplier` (Aussteller), drei Adressrollen
`customer`/`delivery`/`invoice` (mit `contact`-Unterobjekt, serverseitig mit
V1-Fallback aufgelöst), dem vorgelösten Briefkopf-`recipient`, `positions[]`
und **serverseitig vorberechneter `statistics`** (`tax_groups[]` je Steuersatz +
Skalare `net_total`/`discount_amount`/`net_after_discount`/`vat_total`/
`gross_total`). **Jasper kann ein JSON-Array/-Objekt nicht gruppieren bzw.
iterieren** — deshalb liefert der `OrderDocumentDataBuilder` (Laravel) die
Steuergruppen vorberechnet und die Zusatzfelder zusätzlich als **Liste**
(`custom_fields_list`), damit das Template sie generisch (ohne Kenntnis der
Feldbedeutung) rendern kann; der Bericht druckt nur. Feldreferenz siehe
`sample-data.json`.

### Statusabhängiger Dokumenttyp (v1.2)

`document.type` wird serverseitig aus dem (aufgelösten) Statustitel nach den
V1-Statusgruppen abgeleitet; `document.type_label` ist die gedruckte
Überschrift:

| Status (V1-Gruppe) | `document.type` | Überschrift | Besonderheiten im Template |
|---|---|---|---|
| Offer / Angebot | `offer` | Angebot | Preistabelle + Summen, Angebotstext (`booking_offer_report_description`) |
| Order / Auftrag | `order_confirmation` | Auftragsbestätigung | Preistabelle + Summen, Auftragstext (`booking_order_report_description`) |
| Delivery / Lieferung, Order_in_house / Auftrag im Haus | `delivery_note` | Lieferschein | **Empfänger = Lieferadresse**, Positionen **ohne Preise** (`positions-delivery`), keine Summen-/Steuerbox, Empfangsbestätigung mit Unterschriftszeilen, Liefertext (`booking_delivery_report_description`) |
| Billing / Invoice / Rechnung | `invoice` | Rechnung | **Empfänger = Rechnungsadresse**, USt.-Aufschlüsselung je Satz, Leistungsdatum-Hinweis, Zahlungsbedingungen (`supplier.payment_terms`), Rechnungstext (`booking_billing_report_description`) |
| sonstige Status | `document` | Statustitel | neutrales Belegformat (Verhalten wie bisher) |

Zudem löst der Builder seit v1.2 die in `bookings.status` gespeicherte
**Status-uID zum Statustitel** auf (`document.status`) — vorher erschien bei
V2-Datensätzen die rohe UUID im Betreff.

### `supplier` — Aussteller aus Report-Variablen (v1.2)

Der `supplier`-Block trägt die Pflichtangaben des Rechnungsausstellers
(§ 14 UStG: vollständiger Name + Anschrift, Steuernummer/USt-IdNr.) sowie
Fußzeilen-/Bank-/Zahlungsangaben. Quelle sind globale Report-Variablen
(`report_type` = `booking` oder `all`):

`company_name`, `company_sender_line`, `company_street`, `company_zip`,
`company_city`, `company_country`, `company_phone`, `company_email`,
`company_web`, `company_tax_number`, `company_vat_id`,
`company_commercial_register`, `company_managing_director`,
`company_bank_name`, `company_iban`, `company_bic`, `company_payment_terms`.

Nicht konfigurierte Variablen fehlen im Block; das Template blendet leere
Zeilen aus (durchgängig `isBlankWhenNull` — es wird nie „null" gedruckt).

> **v1.1 → v1.2 (additiv, nicht brechend):** neu sind `document.type`,
> `document.type_label`, die Statustitel-Auflösung in `document.status`, die
> statusgruppen-spezifische Auswahl der `description`-Variable (V1-Parität:
> offer/order/billing/delivery) sowie die Blöcke `supplier` und `recipient`.
> Bestehende v1.0/v1.1-Bindungen bleiben unverändert.
>
> **Ausblick ZUGFeRD:** Für Rechnungen ist eine optionale hybride
> ZUGFeRD-/Factur-X-Ausgabe (PDF/A-3 + EN-16931-XML) geplant — Konzept siehe
> [`docs/konzept-zugferd-rechnung.md`](https://github.com/calhelp/calServer-yii/blob/develop/docs/konzept-zugferd-rechnung.md)
> im calServer-yii-Repo. Der v1.2-Datensatz (supplier/recipient/tax_groups)
> liefert dafür bereits die wesentlichen EN-16931-Felder.

> **Auftragsrabatt (W4114):** Die Muster sind rabattfrei, damit die Summen
> eindeutig sind. Die exakte V1-Rabatt-Steuer-Arithmetik bei mehreren Steuersätzen
> ist ein Dual-Run-Abstimmungspunkt (siehe Builder-Doku).

## ⚠️ Warum ein leeres/weißes Blatt erscheinen kann

Datenquellenlos: rendert nur mit übergebener **JSON-Datenquelle**. Ohne sie
(Studio-Preview ohne Adapter, oder Live-Generierung ohne `data_contract`) bleibt die
Seite leer bzw. bricht auf `subDataSource(...)` ab. Abhilfe:

- **Vorschau (Studio):** mitgelieferter Adapter (Default über
  `com.jaspersoft.studio.data.defadapter`) → „Open → Preview".
- **Live (calServer V2):** Report-Setting-Variable `data_contract = order-document`;
  Datensatz auch via `GET /api/v2/bookings/{id}/report-dataset`.

JasperReports **6.20.6** verbindlich.

## Parameter-Katalog (`parameters.json`)

Dieses Bundle liefert ein **Parameter-Manifest** (`parameters.json` an der
Bundle-Wurzel), damit calServer V2 die konfigurierbaren Parameter beim Anlegen
von Berichtsvariablen mit Beschreibung, Typ und Standardwert anbietet (siehe
[Konzept](https://github.com/calhelp/calServer-yii/blob/develop/docs/konzept-report-parameter-katalog.md)).

| Parameter | Rolle | Wirkung |
|-----------|-------|---------|
| `Company_footer` | variable (type) | Optionale Fußzeile am unteren Rand jeder Seite (Auftragsbeleg). Leerer Default → keine Änderung am aktuellen Layout; nur wenn gesetzt (Berichtsvariable `company_footer`), erscheint die Zeile. |

Gilt nur für V2-JSON-Bundles. Der optionale Fußzeilentext ist `isBlankWhenNull`
und standardmäßig leer — die pixelgenaue Abnahme des Layouts (report-runner)
bleibt wie gehabt maßgeblich.
