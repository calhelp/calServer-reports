# CMS-Frontend Design Preview

Diese schlanke Vorschau-Datei bindet das bereitgestellte Markup (Container, Cards, CTA-Gruppe, `design-preview__*`-Klassen, UIkit-Buttons) in ein eigenständiges Template ein. Alle Design-Tokens und Effekte sind im Namespace `.design-preview` gekapselt und können in Storybook, im CMS-Editor oder im Browser geprüft werden.

## Struktur
- `templates/marketing-landing.html` – statisches Template mit Hero, Karten, CTA-Gruppe und Redakteurs-Preview-Rahmen.
- `assets/design-preview.css` – Namespace-Styles & Tokens (Farben, Radius, Abstände, Schatten, Typografie) inklusive Hover/Reveal-States.
- `assets/design-preview.js` – statischer Slider (keine Auto-Rotation) plus IntersectionObserver für Scroll-Einblendungen.

## Nutzung
1. Öffne `templates/marketing-landing.html` direkt im Browser **oder** binde die Datei als Story in dein Storybook (z. B. per `iframe`).
2. UIkit wird per CDN geladen; die Namespace-Styles liegen im `assets`-Ordner und lassen sich bei Bedarf in das CMS-Bundle übernehmen.
3. Verhalten prüfen:
   - Slider: Navigiere über die Punkte, es gibt keine automatische Rotation.
   - Scroll-Effekte: Karten und Sektionen blenden beim Scrollen ruhig ein.
   - CTA-Gruppe: UIkit-Buttons mit Tokens aus dem `.design-preview` Namespace.
4. Für eine Redakteurs-Preview kann der Abschnitt "Redakteurs-Preview" direkt in den CMS-Editor übernommen werden, damit die gestaltete Vorschau dort sichtbar ist.

## Hinweise
- Alle Klassen sind neutral benannt, um Konflikte mit bestehenden CMS-Layouts zu vermeiden.
- Das Layout ist bewusst sachlich und ruhig gehalten (dezente Schatten, weiche Radien, keine Auto-Animationen).
