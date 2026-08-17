# robots.md — AI/Agent Rules for calServer-reports (STRUCTURE + PACKAGING are binding)

This repo is organized as **report bundles** that are packaged by GitHub Actions into ZIPs.
Your changes MUST satisfy the structural + packaging constraints, otherwise builds fail or required files vanish from the ZIP.

---

## 0) Golden Rule
A report is only "valid" if it:
1) has the required folder structure,
2) contains at least one *.jrxml in scope,
3) survives the packaging filter rules (allowed file types),
4) lands in the `report-zips` artifact (then it appears on the Downloads site automatically),
5) (optional) has a consistent API upload mapping (if auto-deploy is expected),
6) (optional) is included in release-reports.yml if releases must contain it.

---

## 0.1) JasperReports version (MUST)
Use and target **JasperReports 6.20.6** for JRXML compatibility.

### Implication
- Do not introduce JRXML features requiring a newer Jasper version unless version policy is explicitly updated.
- When validating report execution/rendering, assume runtime/compiler behavior of 6.20.6.

---

## 0.2) V2 direction (announced)
The existing bundles in this repo are the stable **V1 contract**: embedded SQL executed over a JDBC connection (`$P{REPORT_CONNECTION}`) against the V1 column codes (`I42xx`, `C23xx`, ...).

### Rules
- Do **NOT** rewrite existing bundles to query the calServer V2 schema (readable column names). They stay on the V1 contract and receive bug fixes only.
- **V2 bundles** use **JSON datasources** with readable API field names (`$F{serial_number}` instead of `$F{I4202}`); the data is supplied by the calServer backend, not by SQL inside the template.
- **Exception — exact V1 clones:** a V2 bundle that is a byte-exact clone of a V1 original (e.g. `DAKKS-JSON-SAMPLE`, derived from `DAKKS-SAMPLE` by `scripts/build_dakks_json_clone.py`) KEEPS the V1 field names inside the template; the readable api_name lives in each field's `<fieldDescription>` JSON path. Never hand-edit such a clone — change the mapping in the build script and regenerate (`--write`), verify with `--check`.
- Strategy and migration path: https://github.com/calhelp/calServer-yii/blob/develop/docs/evaluierung-jasper-reports-v2.md
- JasperReports 6.20.6 (section 0.1) remains binding for all bundles until the version policy is explicitly updated.

### V2 (APEX) packaging rules (MUST — now live)
- **Naming:** a V2 bundle folder ends with `-JSON-SAMPLE` (e.g. `DAKKS-JSON-SAMPLE`); its ZIP name is the lowercased form (e.g. `dakks-json-sample`). The packaging workflows and the downloads page key off this suffix.
- **JSON sample allowed:** V2 bundles ship a `main_reports/sample-data.json` (a JSON data-adapter fixture). The `create_zip()` allowlist matches `*-JSON-SAMPLE` and keeps `*.json` — do NOT drop the sample. (Baseline allowlist is `*.jrxml`/`*.md` only; without the `*.json` branch the sample is deleted before zipping.)
- **Downloads page:** the page (`downloads/index.html`) is the calServer **template page** — reports are one bundle class on it, next to stickers, Prüfpläne and Wiki templates. **V2 is the default and is never marked as V2.** Rules:
  - V2 bundles are sorted **by topic** into `Kalibrier- & Zertifikatsberichte`, `Geräte & Inventar`, `Aufträge & Belege` or `Sticker & Etiketten` (keyword rules in `getCategory()`, evaluated after the `-json-sample` check; the sticker rule runs first so `sticker-dakks-*-json-sample` does not fall into the DAkkS rule). A V2 bundle matching no rule lands in `Weitere` — extend `getCategory()` **and** `CATEGORIES` in `downloads/index.html` instead of leaving it there.
  - V1 (BASE) bundles are legacy and all collect in the single category **"calServer V1 (Legacy)"**, sorted last. That category is the fallback for everything without the `-json-sample` suffix, so V1 bundles need no entry anywhere. No new V1 bundles — see the rules above.
  - `TITLE_MAP` (info pages): V2 titles carry **no** version suffix; V1 titles carry `(calServer V1)` so the legacy twin of a V2 bundle stays distinguishable.
  - For each new V2 bundle: add a `get_last_modified` line + `README_MAP`/`TITLE_MAP` entry in `publish-downloads.yml`.
- **No API upload / no release (for now):** V2 bundles are **downloads-page only**. Do NOT add `/api/report/<uuid>` upload steps or `release-reports.yml` entries for them unless that policy is explicitly changed.
- Structure (`main_reports/` + `subreports/`) and the 6.20.6 pin apply unchanged.

---

## 0.3) Prüfplan packages (`calserver.procedure-package`) — MUST

This repo also hosts **Prüfplan bundles** (test plans for calServer V2). They are a
**separate bundle class**: NO JasperReports involved, none of the report rules
(sections 0.1, 1, 2, 6) apply to them. An AI agent should be able to author a
valid Prüfplan bundle end-to-end from this section alone.

### Naming and structure (MUST)
- Folder `PRUEFPLAN-<SLUG>/` (e.g. `PRUEFPLAN-FLUKE-23`); ZIP name is the
  lowercased form (`pruefplan-fluke-23`). Never use the `-JSON-SAMPLE` suffix —
  that triggers the report (APEX) packaging rules and the JRXML assertion.
- Required files at the bundle root: `manifest.json`, `README.md`,
  `procedure.json`. Optional: `images/` (png/jpg/jpeg/gif/svg/webp) and
  `docs/` (pdf/md/txt/csv/xlsx/docx), both FLAT (depth 1), file names
  `[A-Za-z0-9][A-Za-z0-9._-]*`, max 128 chars.
- NO `main_reports/`, NO `subreports/`, NO `*.jrxml`, NO SQL, no other file
  types. The format owner is calServer V2
  (`laravel/app/Services/Procedure/ProcedurePackageService.php` in
  calhelp/calServer-yii); the machine-readable manifest schema is
  `schema/procedure-package.schema.json` (published to Pages).

### Content rules for `procedure.json` (MUST)
> These content rules are shared with calServer's **internal AI** (the
> Prüfplan draft assistant in the step editor): its system prompt
> (`laravel/app/Services/Ai/ProcedurePlanService.php::systemPrompt()` in
> calhelp/calServer-yii) carries the same metrological guardrails. If you
> change a rule here, update that prompt too — and vice versa. There is
> deliberately no runtime sharing across the two repos.

- Header: `{"format": "calserver.procedure", "version": 3, "name": "...", "test_steps": [...]}`.
  Version 3 is the current maximum — never write a higher version.
- **Step images (document version 3):** any step may carry
  `"images": ["<basename>", ...]` — each entry MUST be a file in the
  bundle's `images/` folder (`scripts/build_pruefplan_manifest.py --check`
  enforces existence). calServer shows these pictures right at the step in
  measurement capture. Use them for connection diagrams on group headers,
  measuring guides and test patterns on confirmation steps (e.g. an LCD
  test pattern with "everything as pictured? yes/no" as a
  `TEXT(Y=PASS)` step). The step references by name; the bytes travel in
  `images/` and become plan attachments on import.
- `row_number` gapless from 1; `test_step` numbers unique, decimal
  sub-numbering (`1`, `1.001`, `1.002`, …) below a group header.
- A group starts with a step `"test_type": "Header"`; ONLY headers may carry
  `group_defaults` (allowed keys: `config`, `test_value_p`, `test_value_u`,
  `range`, `resolution`, `tolerance`, `uncertainty`, `k`, `decision_rule`).
  Steps below inherit them until the next header — put the metrology on the
  header once instead of repeating it per measurement point.
- **Every `Manual Test` needs an evaluation** via its effective `config` (own
  or inherited): `NUMERIC,NOMINAL` / `NUMERIC,UUT INDICATED` for measurement
  points, `TEXT(Y=PASS)` for a yes/no confirmation (visual check, functional
  check; `TEXT(N=PASS)` inverts — no = pass). A `Manual Test` without any of
  these is a DEAD step in measurement capture: `stepKind()` classifies it as
  informational, it can neither be measured nor confirmed. Instructions that
  need no confirmation (e.g. "attach the calibration label") are
  `"test_type": "Message"` instead.
- `test_mode` is HTML (calServer renders it); `test_mode_markdown` optional.
- Metrological guardrails: state tolerances from the manufacturer's data
  sheet (and say in the README that they must be re-checked against the
  edition valid for the device under test); uncertainties as expanded
  measurement uncertainty (k = 2) of the actual setup, never as a
  substitute for a real budget; keep TUR ≥ 4:1 where the setup allows it and
  say so in the header's test_mode where it deliberately does not (see
  `PRUEFPLAN-MESSSCHIEBER-150MM` — its 3:1 and 2.5:1 groups are intentional
  and documented); DC voltage groups end with a polarity-reversal point
  (same magnitude as the largest positive point, negative sign).

### Manifest (MUST)
- NEVER edit `manifest.json` by hand and NEVER invent sha256 values.
  Regenerate: `python3 scripts/build_pruefplan_manifest.py --write <BUNDLE>`,
  then verify: `python3 scripts/build_pruefplan_manifest.py --check`.
  CI runs `--check` on every push/PR (validate-reports.yml) and fails on any
  drift: unlisted file, missing file, wrong checksum, disallowed entry.
- Keep `created_at`/`plan`/`description` stable across `--write` runs (the
  script preserves them); `plan` is provenance only — calServer always
  imports a package as a new template at version 0.1.

### Packaging & downloads page (MUST)
- `package-reports.yml`: add an `upload-artifact` step for the bundle folder
  and a `create_pruefplan_zip "<BUNDLE>" "<zip-name>"` call (NOT
  `create_zip()` — that stages `main_reports/` and fails without a JRXML).
- `publish-downloads.yml`: add a `get_last_modified` line plus `README_MAP`
  and `TITLE_MAP` entries (`Prüfplan: <DUT> mit <Normal>`); no `SCHEMA_MAP`.
- Category on the downloads page is automatic: any ZIP name containing
  `pruefplan` lands in **"Prüfpläne"** (`downloads/index.html`,
  `getCategory()`).
- Downloads-page only: NO `/api/report/<uuid>` upload step, NO
  `release-reports.yml` entry.

### Verify locally
- `python3 scripts/build_pruefplan_manifest.py --check` is green
- `cd <BUNDLE> && zip -r /tmp/<zip-name>.zip .` produces a ZIP that calServer
  V2 imports as-is (Kalibrierungen → Prüfpläne → Importieren)

---

## 0.4) Wiki packages (`calserver.wiki-package`) — MUST

This repo also hosts **Wiki bundles** (knowledge-base templates for calServer
V2, e.g. the ISO/IEC 17025 quality-management manual starter). Like the Prüfplan
bundles they are a **separate bundle class**: NO JasperReports involved, none
of the report rules (sections 0.1, 1, 2, 6) apply. An AI agent should be able
to author a valid Wiki bundle end-to-end from this section alone.

**Why they live here and not in the product:** calServer imports, this repo
publishes. A wiki template is editorial content — it changes when a standard
or our wording changes, not when the product ships. Bundling it into
calServer would mean a product release for a text fix, and a migration would
write into a customer's knowledge base unasked. Decision:
`laravel/docs/adr/2026-09-11-wiki-vorlagen-kommen-ueber-den-import-nicht-ueber-eine-migration.md`
in calhelp/calServer-yii.

### Naming and structure (MUST)
- Folder `WIKI-<SLUG>/` (e.g. `WIKI-ISO-17025`); ZIP name is the lowercased
  form (`wiki-iso-17025`). Never use the `-JSON-SAMPLE` suffix — that triggers
  the report (APEX) packaging rules and the JRXML assertion.
- Required files at the bundle root: `manifest.json`, `README.md`,
  `wiki.json`. Optional: `media/` (images and attachments), FLAT (depth 1),
  file names `[A-Za-z0-9][A-Za-z0-9._-]*`, max 128 chars.
- NO `main_reports/`, NO `subreports/`, NO `*.jrxml`, NO SQL. The format owner
  is calServer V2 (`laravel/app/Services/Wiki/WikiPackageService.php` in
  calhelp/calServer-yii); the machine-readable manifest schema is
  `schema/wiki-package.schema.json` (published to Pages).

### Content rules for `wiki.json` (MUST)
- Header: `{"format": "calserver.wiki", "version": 1, "categories": [...],
  "articles": [...], "media": []}`. Version 1 is the current maximum — never
  write a higher version.
- **Categories are language-bound.** Each entry needs a bundle-internal `key`,
  a `title`, a `language_code`. The key is the only link a page has to its
  category; row IDs mean nothing across installations, which is why the
  importer re-recognises a category by (title, language).
- **Articles group language variants.** Each article carries a stable
  `general_page_id` (a UUID) and a `pages[]` list with one entry per language.
  That UUID is the idempotency anchor: importing the same bundle twice creates
  nothing the second time. NEVER regenerate the UUIDs of a published bundle —
  a new UUID makes an updated article a second article on every installation
  that already imported the old one.
- Every page needs `language_code`, `title`, `category_key` and content. A page
  without `category_key` lands under "Ohne Kategorie" in the tree — in a
  shipped template that is a defect, and `--check` fails on it.
- Content is `content_html` (preferred for hand-authored bundles) and/or
  `content_json` (the block document). With HTML only, calServer converts to
  blocks on import, so the page is editable in the block editor rather than a
  frozen HTML island. Useful markup: `<h2>`/`<h3>`, `<p>`, `<ul>`/`<ol>`,
  `<table>`, plus `<ul class='wiki-todo-list'><li data-checked='false'>` for a
  checklist. Use single quotes for attributes so the JSON stays readable.
  One conversion limit worth knowing: a `<table>` with `colspan`/`rowspan`
  stays an `html` block (the block editor has no merged cells). Content is
  preserved, editing is markup-level — so use merged cells only where the
  table really needs them (a summing row, say).
- **Images** live in `media/` and are declared in the top-level `media[]` array
  (`id`, `file`, `filename`, `mime_type`, `kind`); blocks reference them by
  `props.mediaId`, never by file name. `--check` enforces that every referenced
  ID is declared and every declared file exists.
- Write the template as a **starter, not a finished manual**. Two shapes work:
  the requirement plus checklist and records, or the manual text itself with
  every lab-specific detail as a bracketed placeholder (`[Laborname]`,
  `[Turnus]`) and a "adapt before release" callout at the top of each page.
  Never invent lab-specific facts (scope rows, uncertainty figures, intervals)
  as if they were real; mark example rows as examples. Say so in the README —
  an unchanged template proves nothing to an accreditation body, and leftover
  placeholders stand out in an audit.
- A topic MAY ship **two variants**: a tool-neutral one and one that carries the
  calServer implementation (`WIKI-ISO-17025` and `WIKI-ISO-17025-CALSERVER`).
  Rules for the second kind: it is a **separate bundle** with its own categories
  and its own `general_page_id`s — never an extra language or an extra category
  inside the neutral one, and never a `--mode=overwrite` upgrade path from it.
  Every product claim MUST be traceable to `docs-v2` in calhelp/calServer-yii;
  where a doc page describes a function that V2 does not have, the bundle says
  it is missing rather than repeating the claim. State what the product does
  **not** cover as plainly as what it does — a gap named in a manual is a known
  point in an audit, a hidden one is a finding. Say in the README which variant
  a lab should pick and that importing both is not intended.

### Manifest (MUST)
- NEVER edit `manifest.json` by hand and NEVER invent sha256 values.
  Regenerate: `python3 scripts/build_wiki_manifest.py --write <BUNDLE>`,
  then verify: `python3 scripts/build_wiki_manifest.py --check`.
  CI runs `--check` on every push/PR (validate-reports.yml) and fails on any
  drift: unlisted file, missing file, wrong checksum, disallowed entry, or a
  `content` block that no longer matches `wiki.json`.
- Keep `name`/`description`/`created_at`/`locale` stable across `--write` runs
  (the script preserves them); `content` is derived and must not be hand-set.

### Packaging & downloads page (MUST)
- `package-reports.yml`: add an `upload-artifact` step for the bundle folder
  and a `create_wiki_zip "<BUNDLE>" "<zip-name>"` call (NOT `create_zip()` —
  that stages `main_reports/` and fails without a JRXML).
- `publish-downloads.yml`: add a `get_last_modified` line plus `README_MAP`
  and `TITLE_MAP` entries (`Wiki: <Thema>`); no `SCHEMA_MAP`.
- Category on the downloads page is automatic: any ZIP name starting with
  `wiki-` lands in **"Wiki-Vorlagen"** (`downloads/index.html`,
  `getCategory()`).
- Downloads-page only: NO `/api/report/<uuid>` upload step, NO
  `release-reports.yml` entry.

### Verify locally
- `python3 scripts/build_wiki_manifest.py --check` is green
- `cd <BUNDLE> && zip -r /tmp/<zip-name>.zip .` produces a ZIP that calServer
  V2 imports as-is (Wiki → Importieren, permission `wiki_import`)

---

## 0.5) Konfigurationspakete (`calserver.category-package` / `calserver.status-package` / `calserver.ticket-config-package`) — MUST

This repo also hosts **configuration packages** for calServer V2: category
trees, status models and the ticket-management setup. Like the Prüfplan and
Wiki bundles they are a **separate bundle class**: NO JasperReports involved,
none of the report rules (sections 0.1, 1, 2, 6) apply. An AI agent should be
able to author a valid configuration bundle end-to-end from this section alone.

**Why they live here and not in the product:** a category tree, a status model
and a lab's risk scales are editorial content of a laboratory, not product
code. They change when a lab's scope or process changes, not when calServer
ships a release. calServer imports; this repo maintains the content.

### Naming and structure (MUST)

- Folder `CATEGORY-<SLUG>/`, `STATUS-<SLUG>/` or `TICKET-CONFIG-<SLUG>/` (e.g.
  `CATEGORY-INVENTORY-DAKKS`, `STATUS-CALIBRATION-DAKKS`, `STATUS-REPAIR-DAKKS`,
  `TICKET-CONFIG-DAKKS`); ZIP name is the lowercased form. Never use the
  `-JSON-SAMPLE` suffix — that triggers the report (APEX) packaging rules and
  the JRXML assertion.
- **One package per module.** A status package carries one `type`; a lab that
  only wants the calibration statuses must not have to take the order module
  with it. The four shipped sets (`calibration`, `inventory`, `repair`,
  `booking`) are the pattern for any further one.
- Required files at the bundle root, and **nothing else**: `manifest.json`,
  `README.md`, plus `categories.json` (CATEGORY-*), `statuses.json` (STATUS-*)
  or `ticket-config.json` (TICKET-CONFIG-*). NO subfolders, NO images, NO
  `main_reports/`, NO `*.jrxml`.
- The format owner is calServer V2
  (`laravel/app/Services/Category/CategoryPackageService.php`,
  `laravel/app/Services/Status/StatusPackageService.php` and
  `laravel/app/Services/Ticket/TicketConfigPackageService.php` in
  calhelp/calServer-yii); the machine-readable manifest schemas are
  `schema/category-package.schema.json`, `schema/status-package.schema.json`
  and `schema/ticket-config-package.schema.json` (published to Pages).

### Content rules (MUST)

- **Keys are package-internal, uIDs are never written.** A category is
  recognised on import by (type, parent, name), a status by (type, title).
  `parent_key`, `from_key`/`to_key` and `start_key`/`stop_key` reference the
  `key` of another entry **in the same document**; parents MUST appear before
  their children.
- **Categories:** `type` is one of `inventory`, `calibration`, `repair`,
  `booking` (never `types` — that is an assignment discriminator, not a
  catalogue). Assignments (`category_item`) are NOT part of a package: which
  device sits in which category is the installation's stock, not a template.
- **Statuses:** `type` is one of `inventory`, `calibration`, `booking`,
  `repair`, `location`, `notepad`, `support_tickets`. `active: false` or
  `hide: true` takes a record out of circulation (the loan module reads that) —
  use it deliberately, and say so in the README.
- **Field rules carry the readable field name**, never a V1 metrology code:
  `{"field": "cal_result", "edit_mandatory": true}`. The importer maps it to
  whatever column reference the target installation uses. A field the target
  does not have is **skipped with a warning**, so a rule on a customer-specific
  field does not break the package — but it also does nothing. Only reference
  factory fields (`database/data/default_field_definitions.json` in
  calhelp/calServer-yii) unless the README explains the prerequisite.
- Statuses that carry no field rules are allowed and useful; a package whose
  every status is decoration should say in its README why. Ticket statuses
  (`support_tickets`) carry NONE — that module has no field registry, and a
  field rule on it is reported as a warning on import.
- **Ticket configuration:** one document carries the whole setup — `types`,
  `categories`, `priorities`, the scales `risk1`/`risk2`/`risk3`, the `matrix`
  and `risk` (formula plus `dimension_labels`). Rules that the manifest script
  enforces, because they are the failure modes that survive an import
  unnoticed:
  - Every level needs an integer `weight` >= 1. A level without weight counts
    as 0 and drags every ticket carrying it down to risk value 0.
  - `matrix` bands reference a priority by **title**, and that priority MUST be
    in the same document. A band is `5` or `10-29`, at most 10 characters
    (the column is `varchar(10)`), and bands MUST cover the whole reachable
    range 1 … (product of the highest weights of the dimensions the formula
    uses). Two-method bands under a three-method formula leave everything above
    25 without colour and without priority.
  - The formula and `risk3` must agree: `[Risk_3]` in the formula requires a
    non-empty `risk3` and vice versa.
  - **Deadlines (document version 2).** A `matrix` row may carry `due_days`
    (deadline in calendar days from the assessment) and `warn_days` (advance
    warning). Both are whole days from 1 to 3650 — `0` is not "no deadline",
    it is a typo, and the script says so. Omitting them is the valid way to
    say "none", and a version 1 document stays readable. Two rules the script
    enforces because the matrix sorts by colour, not by days: a deadline must
    never grow as the band rises (a missing one counts as infinite and is
    therefore only allowed at the bottom), and `warn_days` needs a `due_days`
    to warn about and must not exceed it.
  - Escalation recipients and end statuses are NOT package content. They depend
    on the groups and statuses of the target installation and are set once in
    Ticket administration.
  - Ticket **statuses** do NOT belong in this document. They live in the shared
    status catalogue and ship as a `STATUS-*` package next to it
    (`STATUS-TICKETS-DAKKS`); the two READMEs point at each other.
  - `TICKET-CONFIG-DAKKS-3D` is **derived** from `TICKET-CONFIG-DAKKS` by
    `scripts/build_ticket_config_3d.py`. Never hand-edit it — change the
    two-method package or the delta in the script and regenerate (`--write`),
    verify with `--check`. CI runs that check.

### Manifest (MUST)

- NEVER edit `manifest.json` by hand and NEVER invent sha256 values.
  Regenerate: `python3 scripts/build_config_manifest.py --write <BUNDLE>`,
  then verify: `python3 scripts/build_config_manifest.py --check`.
  CI runs `--check` on every push/PR (validate-reports.yml) and fails on any
  drift: unlisted file, missing file, wrong checksum, disallowed entry,
  duplicate key, unresolvable `parent_key`, transition pointing at a status the
  package does not carry, deadline that grows with the risk band.
- Keep `created_at`, `name`, `description` and `locale` stable across `--write`
  runs (the script preserves them).

### Packaging & downloads page (MUST)

- `package-reports.yml`: add an `upload-artifact` step for the bundle folder
  and a `create_config_zip "<BUNDLE>" "<zip-name>" "<document>"` call (NOT
  `create_zip()` — that stages `main_reports/` and fails without a JRXML).
- `publish-downloads.yml`: add a `get_last_modified` line plus `README_MAP`
  and `TITLE_MAP` entries (`Kategorien: <Thema>` / `Status: <Thema>` /
  `Ticketmanagement: <Thema>`); no `SCHEMA_MAP`.
- Category on the downloads page is automatic: a ZIP name starting with
  `category-` lands in **"Kategorien"**, one starting with `status-` in
  **"Status"**, one starting with `ticket-config-` in **"Ticketmanagement"**
  (`downloads/index.html`, `getCategory()`). All three rules sit above the
  report rules on purpose — `status-…` would otherwise fall through to the
  legacy bucket.
- Downloads-page only: NO `/api/report/<uuid>` upload step, NO
  `release-reports.yml` entry.

### Verify locally

- `python3 scripts/build_config_manifest.py --check` is green
- for TICKET-CONFIG-*: `python3 scripts/build_ticket_config_3d.py --check` is
  green as well
- `cd <BUNDLE> && zip -r /tmp/<zip-name>.zip .` produces a ZIP that calServer
  V2 imports as-is (Administration → Kategorien, Statusverwaltung bzw.
  Ticket-Verwaltung → Paket; permissions `category_import` / `status_import` /
  `support_config_import`)

---

## 1) Required bundle structure (MUST)
For every report bundle folder (e.g. DAKKS-SAMPLE, DCC, ORDER-SAMPLE, STICKERS-*):
- `main_reports/`  → contains the entry-point JRXML(s) users execute
- `subreports/`    → contains included JRXMLs (may be empty, but MUST exist)

### Why `subreports/` must exist even if empty
The packaging workflow enforces a consistent ZIP layout.
If no subreports exist, it creates `subreports/.keep` so `subreports/` is always present in the ZIP.

Do NOT remove `subreports/` and do NOT remove `.keep` if it's used for an empty folder.

---

## 2) Packaging allowlist (CRITICAL)
ZIP creation is filtered by file patterns (create_zip in package-reports.yml).
Non-allowed file types are actively deleted before zipping.

Baseline allowed:
- `*.jrxml`

Special-case allowlists:
- For `DAKKS-SAMPLE`: allow additionally `*.properties`, `*.md`
- For `DCC`: allow additionally `*.xsd`, `*.md`, `*.json`

### Implication (MUST)
If you introduce a required non-JRXML file for any bundle:
- You MUST extend the allowlist in `create_zip()` for that bundle,
- otherwise the file will NOT end up in the ZIP.

Never assume "it is in the repo → it will be in the ZIP".

---

## 3) Build-breaking conditions (MUST avoid)
The packaging workflow fails if:
- no JRXML is found for a configured sample/report bundle
- expected paths for upload-artifact are missing (`if-no-files-found: error`)

Also note:
- debug listings and `unzip -l` checks are run; broken ZIP contents will be visible in logs.

---

## 4) Artifact logic (two levels)
### A) Build artifacts (package-reports.yml)
- per-bundle artifacts (e.g. DAKKS-SAMPLE, STICKERS-CAL, …)
- aggregated artifact: `report-zips` (contains ALL generated ZIPs)

### B) Downloads site generation (publish-downloads.yml)
- consumes `report-zips`
- copies ZIPs to `site/downloads/files/`
- generates:
  - `downloads/metadata.tsv`
  - `downloads/latest.json` (size, sha256, URL, build metadata)
  - `downloads/index.html` renders `latest.json`

### Consequence (MUST)
A report bundle is "properly available" only if its ZIP:
- is generated in packaging,
- is included in the aggregated `report-zips` artifact
→ then it appears automatically on the Downloads page.

---

## 5) Release packaging vs build packaging (IMPORTANT)
- `package-reports.yml` (push to main) builds ZIPs for configured reports + stickers (as listed there).
- `release-reports.yml` (tag/manual release) currently builds only **core reports**
  (DAKKS, DCC, FIELD-NAMES, ORDER, INVENTORY, DELIVERY) and may exclude stickers.

### Consequence
If the requirement is: "ALL report packages incl. stickers must be in GitHub Releases":
- You MUST extend `release-reports.yml` analogously to `package-reports.yml`.

Do NOT assume stickers will be released unless explicitly added.

---

## 6) API upload mapping (ONLY when required)
Some ZIPs are POSTed via `curl` to fixed report IDs using secrets:
- `DOMAIN`
- `HTTP_X_REST_USERNAME`
- `HTTP_X_REST_PASSWORD`
- `HTTP_X_REST_API_KEY`

### Rules
- Never commit secrets.
- ZIP names and REPORT_URL/ID mapping must remain consistent.
- New bundles usually require a new API upload step if auto-deploy is expected.

---

## 7) Practical checklist for adding/modifying a report bundle
When you introduce or change a bundle:

> **Prüfplan bundles (`PRUEFPLAN-*`) follow section 0.3 instead of this
> checklist** — no JRXML, no `main_reports/`/`subreports/`, packaging via
> `create_pruefplan_zip()`, manifest via
> `scripts/build_pruefplan_manifest.py --write`.

### Bundle content
- Create/keep: `<BUNDLE>/main_reports/` and `<BUNDLE>/subreports/`
- Ensure at least one `*.jrxml` exists in the bundle scope

### package-reports.yml (mandatory for distribution)
- Add/update `upload-artifact` step for the bundle
- Add/update `create_zip()` invocation for the bundle
- Ensure the bundle ZIP ends up in the aggregated `report-zips`
- If needed: extend allowlist patterns for additional file types
- (Optional but recommended) keep/extend debug `unzip -l` verification

### release-reports.yml (only if releases must include it)
- Add the bundle there, especially for stickers

### API upload (only if required)
- Add a mapping + upload step for the new ZIP to the correct report ID

---

## Reporting format (when you respond with changes)
Always include:
- affected paths
- what changed (1–3 bullets)
- packaging implications (allowlist / workflows touched)
- how to validate (ZIP content + artifact presence)
