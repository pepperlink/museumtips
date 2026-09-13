# AGENTS.md — museumtips

> Canonical operating guide for AI agents working in this repo. Read before any task. Keep it fact-dense; verify commands before trusting. **Last verified: 2026-09-13.**

## What this is

Multilingual (NL default, English under `/en/`) Hugo static site — plus two weekly-refreshed iCalendar feeds — for temporary exhibitions at Dutch museums. Live at <https://museumtips.pepperlink.nl>, served by GitHub Pages from the **`gh-pages` branch** (built output; never edit it directly). The site renders `data/exhibitions.json`; the `.ics` feeds serve calendar subscribers. Hugo v0.166.0 (extended), **no Node.js**, classless-CSS theme. **JavaScript exception (phase 3c):** exactly two deferred same-origin files (`static/vendor/leaflet/1.9.4/leaflet.js`, `static/js/museum-map.js`) load only on map-ready museum detail pages and on the museums index when ≥1 museum is map-ready; all other pages stay no-JS.

## Layout

- `hugo.toml` — site config: `languages.nl` (default, no URL prefix) + `languages.en` (`/en/`); theme mounted from the `themes/huguette` submodule (layouts + archetypes only).
- `content/nl/`, `content/en/` — page copy: `_index.md`, `about.md`, `calendar.md`, `museums.md`. **Keep both languages in sync.**
- `layouts/` — site layouts extending the theme (`_default/`, `index.html`, `partials/`).
- `i18n/nl.toml`, `i18n/en.toml` — UI strings (add new strings to both).
- `data/exhibitions.json` — **generated** by the museum tracker pipeline (schema 1: `compiled` date, `museums[]` and `exhibitions[]` each with a pipeline-frozen `slug`; exhibitions also carry `title/museum/city/start/end/description/url`). Museum and exhibition pages depend on those slugs — the site never computes production slugs. Never hand-edit.
- `data/museums_info.json`, `data/exhibitions_info.json` — **curated by hand** (schema.org-aligned shape since phase 4). Keyed by frozen museum/exhibition `slug` (must match `exhibitions.json`; never rename). **`museums_info.json`:** root `@type: Museum`; `address_v2`/`address_display`, `geo`, `offers[]`, `_visitor`, `_meta`, plus top-level cadence fields (`refresh_group`, `last_refreshed_extras`, `next_due`) and file-level `_cadence`. **`exhibitions_info.json`:** sidecar (no root `@type`); `admission_v2`, `subjectOf[]`, `_meta` (incl. optional `orphaned_since`). Field contract: `docs/structured-data-schema.md`. Pipeline and agents must not clobber generated keys; **`lat`/`lon` → `geo.latitude`/`geo.longitude` are curated only** — never pipeline-written.
- `museumtips.ics`, `closing-soon.ics` (repo root) — **generated** weekly; these URLs are a public API for calendar subscribers. Never hand-edit.
- `static/` — classless.css (mirrors the theme copy; keep in sync), `custom.css` (site-level overrides, e.g. card heading numbering), `js/museum-map.js`, vendored Leaflet under `vendor/leaflet/1.9.4/`, CNAME, `.nojekyll`, and feed copies used by the Hugo build; the pipeline writes root + `static/` feed copies together in the same commit.
- `themes/huguette` — git submodule → <https://github.com/cathelijne/hugo-theme-huguette>. Clone with `--recurse-submodules`; do not vendor or edit it here.
- `docs/site-plan.md` — the site plan / roadmap (stack decision record, data flow, hosting sketch).
- `docs/structured-data-schema.md` — phase 4 curated/generated field contract (Tables 1–3).
- `scripts/reconcile-curated.py` — recurring curated-record reconciliation (stubs, group balance, orphan grace); `scripts/verify-losslessness.py` — pre-migration losslessness gate (ST-4-2).

## Commands (verified)

| Task | Command | Notes |
|---|---|---|
| clone | `git clone --recurse-submodules https://github.com/pepperlink/museumtips.git` | or `git submodule update --init --recursive` |
| preview | `hugo server` | live-reload at http://localhost:1313/ |
| build | `hugo --minify` | output `public/`; pipeline pins `hugo` v0.166.0 at `/opt/data/museum_tracker/bin/hugo` |
| Hugo pin (operator) | `HUGO="${HUGO:-/opt/data/museum_tracker/bin/hugo}"` | use in verify scripts; Mac lane may have v0.165 — operator re-runs on v0.166 before sign-off |
| reconcile curated | `python3 scripts/reconcile-curated.py --domain museums` then `--domain exhibitions` | run each cadence cycle before refresh batches; read-only against `exhibitions.json` |
| refresh feeds + data | `python3 /opt/data/museum_tracker/publish_feeds.py` *(pipeline host only)* | regenerates feeds + copies `data/exhibitions.json` into the clone, commits + pushes `main`, then triggers the site publish |
| publish site | `python3 /opt/data/museum_tracker/publish_site.py` *(pipeline host only)* | builds from `main` and pushes the result to `gh-pages` |

Weekly automation (Hermes cron): tracker + digest Thu 10:05 UTC; site rebuild → `gh-pages` Thu 17:00 UTC.

## Extras refresh cadence (phase 4)

Museum extras refresh in alternating halves: **15 group A**, then **15 group B** (~30 museums total). Cadence fields live on each museum record (never pipeline-written):

| Field | Role |
|---|---|
| `refresh_group` | `"A"` or `"B"` — seeded 15/15 alphabetical-by-slug; new museums via smaller-group-wins in `reconcile-curated.py` |
| `last_refreshed_extras` | ISO date of last actual extras re-verification for this record (nullable) |
| `next_due` | Operator schedule marker for the next check (nullable until assigned) |
| `_cadence.last_completed_a` / `last_completed_b` | File-level markers set when all 15 in that group finish a batch — orphan deletion reads these |

**Next refresh batch (ongoing hand-off):** (1) `python3 scripts/reconcile-curated.py --domain museums` and `--domain exhibitions`; (2) pick the group whose `next_due` is earliest (or alternate A→B if tied); (3) for each museum in that group, re-verify hours/pricing/cards/access/transit on the museum’s site — update `_visitor.*`/`offers[]` only for changed facts; stamp `_meta.sources[].checked` on rows actually rechecked; advance `_meta.verified` and `last_refreshed_extras`; set `next_due`; (4) when all 15 in the group are done, set `_cadence.last_completed_a` or `last_completed_b` to today. Never blanket-set `last_refreshed_extras` to today without a real per-record check. Exhibition orphans: `_meta.orphaned_since` stamped when a slug drops from generated data; record deleted only after both `_cadence` markers postdate that date (four fixtures in `reconcile-curated.py`).

## Press `subjectOf[]` rules (phase 4)

Every press article carries `verifiedAccess`, `accessNote`, `accessChecked`, and optionally `archiveUrl`. Bounded three-step ladder (PLAN.md §4.4.3): alternate URL discovery → rendered access check → Wayback. **Terminal state:** if all steps fail, keep the original `url` and record `verifiedAccess: false` + specific failure `accessNote` — never drop the link. **`archiveUrl` is metadata only** — never overwrite live `url`. Vocabulary: success `ok`/`archived`; failure `http_403`, `http_404`, `http_410`, `timeout`, `paywall`, `redirect_loop`. Consistency: `verifiedAccess == true` → `accessNote` is `ok` or `archived`; `archiveUrl` non-null iff `accessNote == "archived"`.

## Verification recipes

- Build: `hugo --minify` exits 0; `public/index.html`, `public/en/index.html`, `public/kalender/index.html` exist.
- Data sanity: `data/exhibitions.json` parses; `compiled` is recent; spot-check 2–3 exhibitions render on `/kalender/`.
- Live checks: `curl -I https://museumtips.pepperlink.nl/` → 200; feeds return recent `last-modified`; `/en/calendar/` renders.
- After a publish: confirm the new `gh-pages` commit exists on origin (GitHub / `git ls-remote`). Do not trust a script's exit code alone.
- **Missing-coordinate fixture** (`verify-missing-coordinate-fixture`) — re-run whenever `museum-map-ready.html` or map asset loading changes. Phase 4 moved coordinates under `geo.*`; all **four** cases (removed pair, null longitude, string longitude, out-of-bounds latitude). Disposable worktree only; never commit the fixture.

```sh
# verify-missing-coordinate-fixture — copy to /tmp, run all four cases, discard.
FIXTURE=/tmp/museumtips-missing-coord-fixture
rm -rf "$FIXTURE" && cp -a . "$FIXTURE" && cd "$FIXTURE"
python3 - <<'PY'
import json, copy
d = json.load(open("data/museums_info.json"))
slug = next(k for k in d if k != "_cadence")
a = copy.deepcopy(d); del a[slug]["geo"]
json.dump(a, open("data/museums_info.json.removed", "w"), indent=2, ensure_ascii=False)
b = copy.deepcopy(d); b[slug]["geo"]["longitude"] = None
json.dump(b, open("data/museums_info.json.null", "w"), indent=2, ensure_ascii=False)
c = copy.deepcopy(d); c[slug]["geo"]["longitude"] = "4.885219"
json.dump(c, open("data/museums_info.json.string", "w"), indent=2, ensure_ascii=False)
f = copy.deepcopy(d); f[slug]["geo"]["latitude"] = 90.0
json.dump(f, open("data/museums_info.json.outofbounds", "w"), indent=2, ensure_ascii=False)
print("fixture slug:", slug)
PY
for case in removed null string outofbounds; do
  cp "data/museums_info.json.$case" data/museums_info.json
  hugo --minify --destination "/tmp/mc-$case"
  page="/tmp/mc-$case/museums/$slug/index.html"
  grep -q 'Kaart niet beschikbaar\|Map unavailable' "$page"
  ! grep -q 'leaflet.css\|leaflet.js\|museum-map.js' "$page"
done
cd - >/dev/null && rm -rf "$FIXTURE" /tmp/mc-removed /tmp/mc-null /tmp/mc-string /tmp/mc-outofbounds
echo "verify-missing-coordinate-fixture: OK (all 4 cases)"
```

## Conventions

- Commits: Conventional Commits — `feat|fix|docs|chore(scope): summary`.
- Branches: `diane/...` or `cursor/...`. **Never merge** — the owner merges. Never push to `main` or `gh-pages` except via the publish scripts.
- PR body: plain-language What / Why / Verification.
- Site copy: every content change touches **both** NL and EN; UI strings go in `i18n/*.toml`, not inline.
- Copy punctuation: use the literal typographic apostrophe `’` (U+2019) in site copy (`content/`, `i18n/`). Hugo's Goldmark typographer (on by default in v0.166) rewrites markdown **bodies** (`'` → `&rsquo;`) but front-matter and i18n values render raw — a straight `'` there stays straight and looks inconsistent.
- Keep it a plain Hugo static build: no Node toolchain, no external services. JavaScript is limited to the phase-3c map exception (see below); the theme itself is classless CSS with no JS.

## JavaScript allowlist (phase 3c)

Source tree — exactly these tracked `.js` files (verify after any map work):

```sh
test "$(git ls-files '*.js' | sort | tr '\n' ' ')" = \
  "static/js/museum-map.js static/vendor/leaflet/1.9.4/leaflet.js "
```

Built HTML — scripts only on map-ready museum detail pages and on NL/EN museums index when ≥1 museum is map-ready. No CDN or inline JS:

```sh
! grep -RE '<script[^>]*src=["'\'']?https?://' public --include='*.html'
! grep -R 'javascript:\| on[a-zA-Z][a-zA-Z]*=' public --include='*.html'
```

Map CSS/JS (`leaflet.css`, `leaflet.js`, `museum-map.js`) must not appear on calendar, home, about, or exhibition pages. Shared readiness predicate: `layouts/partials/museum-map-ready.html`.

## Navigation and banner (phase 4)

- Nav visibility fix: `static/css/custom.css` kills the language-switcher bar’s box-shadow (`body > nav + nav`) and raises the main menu (`z-index: 43`) — theme untouched.
- Home is the first menu item with no distinct styling (Q2).
- Photo banner: repo override `layouts/partials/headerimage.html` + `static/images/banner.jpg`; license in `docs/banner-shortlist.md`. Hugo minify strips `class=` quotes — `data-header-band` marker keeps banner verify greps honest; **never weaken verify blocks** to match minified HTML.

## Constraints (do not)

- Never hand-edit `museumtips.ics`, `closing-soon.ics`, or `data/exhibitions.json` — the pipeline overwrites them. Never hand-edit root or `static/*.ics` feed copies except via the pipeline. `data/museums_info.json` and `data/exhibitions_info.json` are curated — don’t regenerate or clobber them (pipeline or agents). **Never add coordinates via the pipeline** — curated `geo.*` only.
- Never break the public feed URLs or change their paths.
- Never edit `themes/huguette` from this repo (changes belong in the theme repo).
- No secrets in the repo; deploy credentials live only on the pipeline host.
- Don't touch Pages/deploy plumbing (`.nojekyll`, `CNAME`, gh-pages flow) without checking the deploy impact.

## Agent workflow expectations

- This file outranks your defaults. On conflict, it wins.
- Work only within the assigned scope; no drive-by refactors, no repo restructuring.
- Run the verification commands and report exact commands + output. If something could not be verified, say so explicitly — "couldn't verify" is acceptable; silent guessing is not.
- **Never weaken verify blocks** (PLAN.md §4.8, coordinate fixtures, JS allowlist, banner checks) to pass on a different Hugo version or minified HTML — fix the site or use documented markers (`data-header-band`, `data-lat=`) instead.
- If blocked or ambiguous: STOP and report findings. Do not guess.
