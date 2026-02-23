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
- For `DAKKS-SAMPLE`: allow additionally `*.properties`, `*.md`, `*.json`, `*.xsd`
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
