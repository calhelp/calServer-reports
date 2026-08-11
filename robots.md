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
- **Downloads page:** V2 bundles appear in their own category **"APEX · V2 (JSON-Datenquelle)"** (matched on `-json-sample` in `downloads/index.html` `getCategory()`), separate from the V1 (BASE) reports. Add a `get_last_modified` line + `README_MAP`/`TITLE_MAP` entry in `publish-downloads.yml` for each new V2 bundle.
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
