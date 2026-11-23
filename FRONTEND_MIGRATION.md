# Frontend migration guardrails

`index.html` remains the production entry point. It is intentionally not a
disposable duplicate: the FastAPI routes `/app`, `/consult`, and `/index.html`
serve it, and it loads the styles and scripts under `static/`.

The files in `static/css` and `static/js` are the destination of the
modularization, not a standalone replacement page yet. Some modules currently
overlap with inline code in `index.html`; they must be migrated feature by
feature and compared before the inline implementation is removed.

## Rules for every migration

1. Keep the same DOM IDs and public `window` functions used by inline handlers.
2. Keep request paths, request payloads, local-storage keys, and server-side
   data unchanged.
3. Add the external module before removing the matching inline implementation.
4. Run `python -m pytest tests/test_frontend_contract.py -q` and the relevant
   browser smoke checks before moving to the next feature.
5. Do not delete `index.html`, `static/`, or a legacy implementation until the
   browser checks prove equivalent behavior.

### Data compatibility contract

Refactoring the frontend must not rename or delete existing browser storage
keys. In particular, active consultations, saved prescriptions, adherence,
symptom logs, profile/auth state, modality selection, and voice choice remain
under their current `herbalist_*` keys. The backend database is untouched by
this frontend-only migration.

## Current dependency order

The production page loads shared styles first, then the module scripts, then
its remaining inline application code, followed by component scripts. This
order is intentional during the transition because the inline page still owns
most application behavior.

## Browser smoke-test setup

Run `powershell -ExecutionPolicy Bypass -File tools/install-playwright-trusted.ps1`
to install the isolated Chromium test runner. The script builds a temporary
certificate bundle from the Windows trusted-root stores and sets
`NODE_EXTRA_CA_CERTS` only for that installation; it does not disable TLS
verification or change npm's global configuration.

After installation, run the local browser smoke checks with:

```powershell
node tools/frontend-smoke.mjs
```

The script discovers Playwright from the local npm cache automatically. Set
`PLAYWRIGHT_ENTRY` only if you need to override that discovery.

The smoke check opens only a local server and verifies the modular toast,
sidebar, modality, and account-scoped chat-history storage handoffs.

## First migration targets

- Toast/dialog behavior — module is the sole owner; validated legacy code removed.
- Chat session title derivation and stale transient-message cleanup are module-owned
  pure helpers. Active-session selection, local-storage writes, remote sync, and
  replay remain inline, preserving all existing session data and boot behavior.
- Sidebar controls — module is the sole owner; validated legacy code removed.
- Geolocation and clinical-modality selection — module is the sole owner; the
  `herbalist_modality` storage key and `/api/geo/detect` flow are unchanged.
- Account-scoped chat-history storage is module-owned; existing
  `herbalist_chat_sessions_<user>` and guest storage keys are retained.
- Canvas prescription controls are module-owned; the browser smoke check covers
  prescription rendering, batch scaling, checklist/dose state, fullscreen, and
  close cleanup. The duplicate inline implementation has been removed.
- Chat markdown, doctor-bubble, and evidence citation formatting are
  module-owned; the evidence drawer continues to use the existing shared
  citation map.
- Safety Checker modal and tab presentation are module-owned; the herb-drug
  and botanical-substitute request flows remain inline.
- Clinical Profile and Help Guide modal presentation controls are module-owned;
  profile saving and help-guide content remain inline.
- Adherence modal presentation is module-owned; dose records, reminders, and
  the `herbalist_adherence` storage key remain inline.
- Attachment-popover presentation and outside-click dismissal are module-owned;
  file uploads, Lab OCR, drug scanning, and Vision AI remain inline.
- Custom confirm, prompt, and alert behavior is module-owned. The page retains
  tiny compatibility forwards while its legacy encoded implementation awaits a
  byte-safe cleanup pass.
- Authentication/vault controls

New-chat stays in the inline page for now: its active implementation contains
the more complete session-history and persistence behavior. It will move only
after the module has that same behavior and the saved-consultation flow passes
browser testing.

Cook Mode is module-owned. Its Care Suite flow, voice narration, flexible
ingredient parsing, and kitchen timer were moved intact from the page; the
existing public handler names and timer controls are retained.

The authentication UI shell (modal visibility, form reset, tab selection, and
password visibility) is module-owned and covered by the browser smoke check.
All account submissions, validation, Firebase/API calls, verification, and
account writes remain inline. The Health Vault and prescription-saving paths
also remain inline because their production variants are richer and data-facing.
The read-only token and stored-user helpers are module-owned as well.

Each target must be extracted as a single source of truth. The other copy is
removed only after parity testing.
