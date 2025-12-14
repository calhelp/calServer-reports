# 📦 Delivery Standalone Report

Dieser Ordner enthält den eigenständigen Lieferreport **Free_Delivery** und den Unterbericht **Free_Delivery_Title**. Der Report wurde mit der Update-ID `ab625419-31d4-8603-1cb3-f768af3b9fb0` angeliefert und soll als vollständige Lieferung bereitgestellt werden.

## Struktur
- `main_reports/Free_Delivery.jrxml` – Hauptreport mit Positionstabelle und Subreport-Einbindung.
- `subreports/Free_Delivery_Title.jrxml` – Titel-/Adressblock für Kopfbereich des Lieferscheins.

## Hinweise zum Deploy
- Beim Kompilieren muss der Unterbericht als `Free_Delivery_Title.jasper` im Unterordner `subreports` liegen, damit der Hauptreport ihn findet.
- Stelle sicher, dass `Reportpath` im calServer auf das Verzeichnis dieser Vorlage zeigt und der Unterberichtpfad `.../subreports/Free_Delivery_Title.jasper` enthält; Standard ist ein leerer Pfad, damit deploymentspezifische Ziele gesetzt werden können.
- Die Vorlagen sind für JasperReports Library 6.20.6 (Jaspersoft Studio 7.0.2.final) ausgelegt.
- Für eine korrekte Anzeige von Umlauten und Sonderzeichen nutzen die Vorlagen – analog zum DAkkS-Report – DejaVu-Sans-Fonts mit Identity-H-Encoding als Standardstil.
- Parameterwerte werden als UTF-8 erwartet; die früheren ISO-Workarounds wurden entfernt. Platzhalter wie `_s_` werden weiterhin in Leerzeichen übersetzt, damit Übergaben aus der Web-App ohne zusätzliche Vorverarbeitung funktionieren.
