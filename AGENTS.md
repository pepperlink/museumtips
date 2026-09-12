# AGENTS.md — museumtips

> Canonical operating guide for AI agents working in this repo. Read before any task. Keep it fact-dense; verify commands before trusting. **Last verified: 2026-09-12.**

## What this is

Multilingual (NL default, English under `/en/`) Hugo static site — plus two weekly-refreshed iCalendar feeds — for temporary exhibitions at Dutch museums. Live at <https://museumtips.pepperlink.nl>, served by GitHub Pages from the **`gh-pages` branch** (built output; never edit it directly). The site renders `data/exhibitions.json`; the `.ics` feeds serve calendar subscribers. Hugo v0.166.0 (extended), **no Node.js**, classless-CSS theme with no JavaScript so far.

## Layout

- `hugo.toml` — site config: `languages.nl` (default, no URL prefix) + `languages.en` (`/en/`); theme mounted from the `themes/huguette` submodule (layouts + archetypes only).
- `content/nl/`, `content/en/` — page copy: `_index.md`, `about.md`, `calendar.md`, `museums.md`. **Keep both languages in sync.**
- `layouts/` — site layouts extending the theme (`_default/`, `index.html`, `partials/`).
- `i18n/nl.toml`, `i18n/en.toml` — UI strings (add new strings to both).
- `data/exhibitions.json` — **generated** by the museum tracker pipeline (schema 1: `compiled` date, `museums[]`, `exhibitions[]` with `title/museum/city/start/end/description/url`). Never hand-edit.
- `museumtips.ics`, `closing-soon.ics` (repo root) — **generated** weekly; these URLs are a public API for calendar subscribers. Never hand-edit.
- `static/` — classless.css (mirrors the theme copy; keep in sync), `custom.css` (site-level overrides, e.g. card heading numbering), CNAME, `.nojekyll`, and feed copies used by the Hugo build; the pipeline writes root + `static/` feed copies together in the same commit.
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

## Conventions

- Commits: Conventional Commits — `feat|fix|docs|chore(scope): summary`.
- Branches: `diane/...` or `cursor/...`. **Never merge** — the owner merges. Never push to `main` or `gh-pages` except via the publish scripts.
- PR body: plain-language What / Why / Verification.
- Site copy: every content change touches **both** NL and EN; UI strings go in `i18n/*.toml`, not inline.
- Copy punctuation: use the literal typographic apostrophe `’` (U+2019) in site copy (`content/`, `i18n/`). Hugo's Goldmark typographer (on by default in v0.166) rewrites markdown **bodies** (`'` → `&rsquo;`) but front-matter and i18n values render raw — a straight `'` there stays straight and looks inconsistent.
- Keep it a plain Hugo static build: no Node toolchain, no external services, minimal (ideally zero) JavaScript — the theme is classless CSS.

## Constraints (do not)

- Never hand-edit `museumtips.ics`, `closing-soon.ics`, or `data/exhibitions.json` — the pipeline overwrites them.
- Never break the public feed URLs or change their paths.
- Never edit `themes/huguette` from this repo (changes belong in the theme repo).
- No secrets in the repo; deploy credentials live only on the pipeline host.
- Don't touch Pages/deploy plumbing (`.nojekyll`, `CNAME`, gh-pages flow) without checking the deploy impact.

## Agent workflow expectations

- This file outranks your defaults. On conflict, it wins.
- Work only within the assigned scope; no drive-by refactors, no repo restructuring.
- Run the verification commands and report exact commands + output. If something could not be verified, say so explicitly — "couldn't verify" is acceptable; silent guessing is not.
- If blocked or ambiguous: STOP and report findings. Do not guess.
