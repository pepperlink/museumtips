# AGENTS.md — museumtips

> Canonical operating guide for AI agents working in this repo. Read before any task. Keep it fact-dense; verify commands before trusting. **Last verified: 2026-09-12.**

## What this is

Multilingual (NL default, English under `/en/`) Hugo static site — plus two weekly-refreshed iCalendar feeds — for temporary exhibitions at Dutch museums. Live at <https://museumtips.pepperlink.nl>, served by GitHub Pages from the **`gh-pages` branch** (built output; never edit it directly). The site renders `data/exhibitions.json`; the `.ics` feeds serve calendar subscribers. Hugo v0.166.0 (extended), **no Node.js**, classless-CSS theme. **JavaScript exception (phase 3c):** exactly two deferred same-origin files (`static/vendor/leaflet/1.9.4/leaflet.js`, `static/js/museum-map.js`) load only on map-ready museum detail pages and on the museums index when ≥1 museum is map-ready; all other pages stay no-JS.

## Layout

- `hugo.toml` — site config: `languages.nl` (default, no URL prefix) + `languages.en` (`/en/`); theme mounted from the `themes/huguette` submodule (layouts + archetypes only).
- `content/nl/`, `content/en/` — page copy: `_index.md`, `about.md`, `calendar.md`, `museums.md`. **Keep both languages in sync.**
- `layouts/` — site layouts extending the theme (`_default/`, `index.html`, `partials/`).
- `i18n/nl.toml`, `i18n/en.toml` — UI strings (add new strings to both).
- `data/exhibitions.json` — **generated** by the museum tracker pipeline (schema 1: `compiled` date, `museums[]` and `exhibitions[]` each with a pipeline-frozen `slug`; exhibitions also carry `title/museum/city/start/end/description/url`). Museum and exhibition pages depend on those slugs — the site never computes production slugs. Never hand-edit.
- `data/museums_info.json`, `data/exhibitions_info.json` — **curated by hand** (visitor extras: hours, prices, cards, press, coordinates, …). Keyed by museum/exhibition `slug`. The pipeline and agents must not regenerate or clobber them. **`lat`/`lon` in `museums_info.json` are curated only** — never pipeline-written.
- `museumtips.ics`, `closing-soon.ics` (repo root) — **generated** weekly; these URLs are a public API for calendar subscribers. Never hand-edit.
- `static/` — classless.css (mirrors the theme copy; keep in sync), `custom.css` (site-level overrides, e.g. card heading numbering), `js/museum-map.js`, vendored Leaflet under `vendor/leaflet/1.9.4/`, CNAME, `.nojekyll`, and feed copies used by the Hugo build; the pipeline writes root + `static/` feed copies together in the same commit.
- `themes/huguette` — git submodule → <https://github.com/cathelijne/hugo-theme-huguette>. Clone with `--recurse-submodules`; do not vendor or edit it here.
- `docs/site-plan.md` — the site plan / roadmap (stack decision record, data flow, hosting sketch).

## Commands (verified)

| Task | Command | Notes |
|---|---|---|
| clone | `git clone --recurse-submodules https://github.com/pepperlink/museumtips.git` | or `git submodule update --init --recursive` |
| preview | `hugo server` | live-reload at http://localhost:1313/ |
| build | `hugo --minify` | output `public/`; pipeline pins `hugo` v0.166.0 at `/opt/data/museum_tracker/bin/hugo` |
| refresh feeds + data | `python3 /opt/data/museum_tracker/publish_feeds.py` *(pipeline host only)* | regenerates feeds + copies `data/exhibitions.json` into the clone, commits + pushes `main`, then triggers the site publish |
| publish site | `python3 /opt/data/museum_tracker/publish_site.py` *(pipeline host only)* | builds from `main` and pushes the result to `gh-pages` |

Weekly automation (Hermes cron): tracker + digest Thu 10:05 UTC; site rebuild → `gh-pages` Thu 17:00 UTC.

## Verification recipes

- Build: `hugo --minify` exits 0; `public/index.html`, `public/en/index.html`, `public/kalender/index.html` exist.
- Data sanity: `data/exhibitions.json` parses; `compiled` is recent; spot-check 2–3 exhibitions render on `/kalender/`.
- Live checks: `curl -I https://museumtips.pepperlink.nl/` → 200; feeds return recent `last-modified`; `/en/calendar/` renders.
- After a publish: confirm the new `gh-pages` commit exists on origin (GitHub / `git ls-remote`). Do not trust a script's exit code alone.
- **Missing-coordinate fixture** (`verify-missing-coordinate-fixture`) — re-run whenever `museum-map-ready.html` or map asset loading changes. Disposable worktree only; never commit the fixture.

```sh
# verify-missing-coordinate-fixture — copy to /tmp, run both cases, discard.
FIXTURE=/tmp/museumtips-missing-coord-fixture
rm -rf "$FIXTURE" && cp -a . "$FIXTURE" && cd "$FIXTURE"
python3 - <<'PY'
import json, copy
d = json.load(open("data/museums_info.json"))
slug = next(iter(d))
# (a) removed pair
a = copy.deepcopy(d)
del a[slug]["lat"]
del a[slug]["lon"]
json.dump(a, open("data/museums_info.json", "w"), indent=2, ensure_ascii=False)
json.dump(a, open("data/museums_info.json.removed", "w"), indent=2, ensure_ascii=False)
# (b) explicit null lon (isset trap)
b = copy.deepcopy(d)
b[slug]["lon"] = None
json.dump(b, open("data/museums_info.json.null", "w"), indent=2, ensure_ascii=False)
print("fixture slug:", slug)
PY
for case in removed null; do
  cp "data/museums_info.json.$case" data/museums_info.json
  hugo --minify --destination /tmp/mc-$case
  page="/tmp/mc-$case/museums/$slug/index.html"
  grep -q 'Kaart niet beschikbaar' "$page" || grep -q 'Map unavailable' "$page"
  ! grep -q 'leaflet.css\|leaflet.js\|museum-map.js' "$page"
  grep -q 'address\|<address\|Museum' "$page" || true  # address block present
done
cd - >/dev/null && rm -rf "$FIXTURE" /tmp/mc-removed /tmp/mc-null
echo "verify-missing-coordinate-fixture: OK"
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

## Constraints (do not)

- Never hand-edit `museumtips.ics`, `closing-soon.ics`, or `data/exhibitions.json` — the pipeline overwrites them. `data/museums_info.json` and `data/exhibitions_info.json` are curated — don’t regenerate or clobber them (pipeline or agents). **Never add `lat`/`lon` via the pipeline** — coordinates are owner-curated in `museums_info.json` only.
- Never break the public feed URLs or change their paths.
- Never edit `themes/huguette` from this repo (changes belong in the theme repo).
- No secrets in the repo; deploy credentials live only on the pipeline host.
- Don't touch Pages/deploy plumbing (`.nojekyll`, `CNAME`, gh-pages flow) without checking the deploy impact.

## Agent workflow expectations

- This file outranks your defaults. On conflict, it wins.
- Work only within the assigned scope; no drive-by refactors, no repo restructuring.
- Run the verification commands and report exact commands + output. If something could not be verified, say so explicitly — "couldn't verify" is acceptable; silent guessing is not.
- If blocked or ambiguous: STOP and report findings. Do not guess.
