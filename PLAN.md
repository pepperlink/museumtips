# PLAN — Phase 2: Calendar UX + polish

Status: **approved** (owner, 2026-09-12) — implementation in progress; runs append to §11 below.

Owner review of this document comes **before** any implementation. Do not start coding from this file until the owner signs off (especially the decisions in §4).

## 0. Agent ground rules

Follow `AGENTS.md` (present at repo root; owner-approved 2026-09-12). It outranks defaults.

In force for this phase: Conventional Commits; `diane/…` or `cursor/…` branches; **owner merges**; never push `main` or `gh-pages` except via the pipeline scripts; never hand-edit `data/exhibitions.json`, root `*.ics`, or `themes/huguette`; never change public feed URLs; NL + EN stay in sync; no Node.js; Hugo v0.166 extended (pipeline pin `/opt/data/museum_tracker/bin/hugo`); minimal JS (ideally zero); work only in assigned scope.

## 1. What & why

Phases 1–4 in `docs/site-plan.md` (stack, JSON, scaffold, publish) are done. This is **phase 2** of the live site = site-plan next-step 5: calendar UX, then polish.

`/kalender/` is a month-grouped list with four concrete bugs (null end dates → year 1 / “Afgelopen”; unsorted jump-nav; clumsy meta lines; ended shows still listed). The page should become a better way to browse what is on, by month and by place, without abandoning the no-JS Hugo build. Page copy still reads like scaffold/fixture text and needs an editorial pass (operator-drafted, not agent-invented).

## 2. Non-goals

- No stack change, no Node toolchain, no theme-submodule edits.
- No feed URL / path / filename changes; no hand-edits of generated `data/exhibitions.json` or root `*.ics`.
- No gh-pages / CNAME / `.nojekyll` / publish-script surgery.
- No visual day-cell calendar library (FullCalendar etc.).
- No per-exhibition pages, search API, images, or bilingual exhibition titles from the pipeline (schema 1 is unchanged).
- Do not draft final NL/EN marketing copy in implementation runs — land owner-approved copy only.
- Do not merge this branch or open work that the owner did not approve in §4.

## 3. Recon summary

Verified 2026-09-12 against this worktree + `https://museumtips.pepperlink.nl`.

- Live: NL default + `/en/`; pages home, `/kalender/`, `/musea/`, `/over/`. Data: `data/exhibitions.json` schema 1, compiled **2026-09-10**, **111** exhibitions, **30** museums. Zero JS; Huguette classless CSS (submodule). Hugo layouts in `layouts/` (`calendar.html`, `museums.html`, `index.html`, `partials/exhibition.html`, `format-date.html`, `countdown.html`).
- **(a) Null `end` (5):** Ayoung Kim (Dommelplein); john gerrard - Ghost Feed (Dommelplein); Ad Minoliti - Feminist School of Painting (Dommelplein); Hanuman reist de wereld over; Deshima Experience. `time.AsTime` on null → 0001-01-01 → “tot en met 1 januari 1” / “1 January 1”, countdown “Afgelopen”/“Ended”, junk jump-nav `#0001-01`. Same date call on `/musea/`.
- **(b) Jump-nav order (live):** `2026-09, 2026-10, 2028-06, 2030-05, 0001-01, 2026-11, 2026-12, 2027-01 … 2027-12, 2028-12, 2027-09, 2027-05, 2034-01`. Neither JSON order nor ISO order. Cause: `sort` on `end` with nulls is unreliable. Fix by sorting derived `YYYY-MM` keys, not raw `.end`.
- **(c) Meta line:** `exhibition.html` always prints start (or `open_ended` = “Startdatum onbekend”) + “tot en met” + full month name. **67** rows have `start: null`. Example: “Startdatum onbekend · tot en met 13 september 2026 · Laatste dag”.
- **(d) “Ended” (13 on live):** **8** really ended before 2026-09-12 (mostly 2026-09-06) + **the 5 null-end false positives**. Home already keeps `end >= today`, so it hides both groups (open-ended also vanish from “Bijna afgelopen” — correct for that list).
- Other awkwardness: `/musea/` groups by tracker `group` in file order (mix of cities, “The Hague”, catch-all “Noord/Oost/Zuid”); visitor-facing `quirks`; home/about/README still say the site is a **fixture**.
- Housekeeping: root `*.ics` DTSTAMP `20260912T081711Z` (98639 / 31821 bytes). `static/*.ics` is **2026-09-11** (2 bytes smaller). Live feed etags match **root** sizes — `publish_site.py` likely overlays root feeds on Hugo `public/`. Root `index.html` is the pre-Pages landing page (commit `0841858`); Hugo does not use it.

## 4. Decisions taken

**Already decided (constraints):** Hugo-only; no Node; feeds unchanged; no generated-file or theme edits; NL+EN together; deploy stays on the pod pipeline.

**D1 — calendar view — DECIDED: static month pages, 0 JS**

| | Static month pages (0 JS) | Vanilla-JS widget | Hybrid (static + small JS) |
|---|---|---|---|
| What | Keep the end-month **list** on `/kalender/`. Add build-time `/kalender/YYYY-MM/` (and `/en/calendar/YYYY-MM/`) listing shows **open that month** (date overlap; null-end included). Jump-nav links there. | One page; JS switches months / optional day grid; needs a baked JSON slice. | Static pages as the source of truth; JS only enhances in-page switching. |
| Fit | Matches date-**range** shows; SEO; no-JS; Hugo-native. | First JS on the site; no-JS users need a duplicate list anyway. | Extra moving parts for little gain over static links. |
| Cost | More URLs; overlap logic in templates. | New testing + a11y; contradicts no-JS lean. | Highest complexity. |

A day-cell grid is a poor fit (shows last weeks–years; cells empty or packed). **Decision (owner, 2026-09-12): static month pages + fixed list (column 1). No JS this phase.** If scope ever needs shrinking: list-only (fix §3 bugs, no new routes).

**D2 — city / museum grouping — DECIDED: static**

| | Static | Client-side |
|---|---|---|
| City (19) | New city sections or `/kalender/stad/…` pages, or regroup `/musea/` by `city`. | Filter chips; needs JS. |
| Museum (30) | Already on `/musea/`. Polish that page; link from calendar meta. Do not duplicate. | Same chips on `/kalender/`. |

**Decision (owner, 2026-09-12): static. Regroup `/musea/` by city; optional city jump-nav or city pages only if the month pages are not enough. No filter JS.**

**D3 — ended shows — DECIDED: hide >7 days, collapse the rest**

| Policy | Trade-off |
|---|---|
| Keep | Honest archive; page stays noisy (8 real ended now, more each Thursday). |
| Collapse | `<details>` “Afgelopen (N)” at the bottom. Scan stays clean; still findable. |
| Hide after N days | Matches weekly refresh. **N = 7** (one pipeline cycle). Older ended drop; just-ended remain briefly. |

**Decision (owner, 2026-09-12): hide `end < today − 7 days`; collapse the rest of ended in `<details>`. Null `end` is never ended — its own “Geen einddatum” bucket.**

**D4 / D5 — housekeeping — DECIDED**

- **D4 root `index.html` — decided: remove.** Pipeline is live; file is unused by Hugo; leftover risk if someone treats it as the site.
- **D5 `static/*.ics` — decided: the pipeline writes root + `static/` in the same commit.** (Pipeline-host change; do not hand-copy feeds in this repo. Do not touch feed URLs.)
- **D6 — museum `quirks` on `/musea/` — decided: hide** (operator notes, mixed EN, not visitor copy).

**Copy refresh:** operator draft v2 (informal tone) is ready; owner signs off at landing. Fast-track (owner-agreed 2026-09-12): content-file changes land right after ST1; i18n strings with ST5. Files: `content/{nl,en}/*.md` (incl. front matter) + `i18n/{nl,en}.toml`.

## 5. Approach & subtasks

Each item is **one Cursor run**. All §4 decisions are resolved (2026-09-12); if a run finds a conflict with them, stop and report.

### ST1 — Date correctness + meta line

- **Scope:** `layouts/_default/calendar.html`, `layouts/_default/museums.html`, `layouts/partials/{exhibition,format-date,countdown}.html`, `i18n/{nl,en}.toml`.
- **Steps:** Guard null `end`/`start`. Sort jump-nav + sections by real `YYYY-MM`. Open-ended section (not `#0001-01`, not “Afgelopen”). Hide missing start. Shorter dates (abbrev month; range `9 mei – 13 sep 2026` when both known; `t/m 13 sep 2026` when only end). Keep countdown labels. Same date helper on `/musea/` and home (shared partial).
- **Tests:** The five named shows never render year 1 or Ended. No `#0001-01`. Months ISO-sorted. 67 missing starts print no “Startdatum onbekend”.
- **Docs:** none beyond i18n keys.
- **Verify:** `hugo --minify`; grep `public/kalender/index.html` for `1 januari 1` / `#0001-01` (expect 0); spot three meta lines.
- **Model:** `grok-4.6`. **Depends:** none (D3 only affects whether ended still list).

### ST2 — Ended-exhibition policy

- **Scope:** `layouts/_default/calendar.html`, `layouts/index.html` (only if policy should change home), `i18n/{nl,en}.toml`.
- **Steps:** Implement D3 (hide older than 7 days; collapse the rest). Home “Bijna afgelopen” stays `end >= today`.
- **Tests:** A show with `end` last week vs eight weeks ago matches D3. Null-end unchanged from ST1.
- **Docs:** one line in README if the rule is visitor-visible.
- **Verify:** `hugo --minify`; count “Afgelopen”/“Ended” on NL+EN calendar.
- **Model:** `composer-2.5`. **Depends:** D3, ST1.

### ST3 — Calendar month view

- **Scope:** `layouts/_default/calendar.html`, new month layout + content/archetype as needed, `content/{nl,en}/calendar.md` front matter, `i18n/{nl,en}.toml`. No theme edits; no `data/exhibitions.json` edits.
- **Steps:** Implement D1. Overlap: open in month M if `end` is null or `end >= M-start`, and `start` is null or `start <= M-end`. Both languages, same slugs. List page keeps end-month grouping.
- **Tests:** A Sep-2026 page includes a May–Oct show and the five open-ended; excludes a show that ended Aug 2026. `/en/calendar/2026-09/` exists. `hugo --minify` exits 0.
- **Docs:** README route list.
- **Verify:** `hugo --minify`; `ls public/kalender/ public/en/calendar/`; open one month page.
- **Model:** `grok-4.6`. **Depends:** D1, ST1.

### ST4 — City / museum grouping

- **Scope:** `layouts/_default/museums.html`, optionally calendar layouts + `content/{nl,en}/museums.md` / calendar content, `i18n/{nl,en}.toml`.
- **Steps:** Implement D2 + D6. Default path: regroup `/musea/` by `city` (sorted); fix per-museum date lines (ST1 helper). Add city pages or calendar city nav only if D2 says so.
- **Tests:** 19 cities appear; no year-1 dates; quirks hidden or shown per D6; EN `/en/museums/` matches.
- **Docs:** README if new routes.
- **Verify:** `hugo --minify`; spot `public/musea/index.html` + EN.
- **Model:** `grok-4.6`. **Depends:** D2, D6, ST1.

### ST5 — Copy refresh (NL + EN)

- **Scope:** `content/nl/{_index,about,calendar,museums}.md`, `content/en/{_index,about,calendar,museums}.md`, `i18n/{nl,en}.toml`.
- **Steps:** Land **owner-approved** operator draft only. Keep translationKeys/urls/layouts. Drop fixture wording. Technical i18n from ST1–ST4 may be rewritten here — do both languages in one run. **Fast-track (owner-agreed):** the content-file part lands right after ST1; this run covers the i18n strings + any remainder.
- **Tests:** Every NL string has EN; no leftover “fixture”; subscribe URLs unchanged.
- **Docs:** n/a (this *is* the docs/copy).
- **Verify:** `hugo --minify`; read home + about in both langs.
- **Model:** `composer-2.5`. **Depends:** operator draft + owner approval; content files right after ST1 (fast-track); i18n strings after ST1–ST4.

### ST6 — Housekeeping

- **Scope:** `README.md`, `AGENTS.md` if routes/ICS policy change, `docs/site-plan.md` (pointer only), root `index.html` if D4 = remove. **Not** `data/exhibitions.json`, root `*.ics`, theme, CNAME, gh-pages.
- **Steps:** README: live dataset (not fixture); Hugo routes; ICS rule from D5. AGENTS: drop stale “fixture” implications if any; keep feed-URL warning. D4 delete root `index.html`. D5 is a **pipeline-host** change plus README — do not copy `.ics` by hand.
- **Tests:** README commands still match `AGENTS.md`. Site build unchanged if only docs + unused `index.html`.
- **Docs:** this subtask.
- **Verify:** `hugo --minify`; if D4 ran: `git ls-files index.html` is empty (root file gone), while `public/index.html` (the Hugo home) still builds.
- **Model:** `composer-2.5`. **Depends:** D4, D5; runs after ST3–ST4 so the README lists real routes.

## 6. Definition of done

- [x] Owner approved the plan (2026-09-12).
- [ ] No year-1 dates; no `#0001-01`; the five open-ended shows are not “Afgelopen”/“Ended”.
- [ ] Calendar jump-nav is chronological (`YYYY-MM`).
- [ ] Meta line: no “Startdatum onbekend”; shorter dates; countdown labels kept.
- [ ] D3 visible on `/kalender/` and `/en/calendar/`.
- [ ] D1 calendar UX live on NL + EN; no-JS usable.
- [ ] D2 grouping live; `/musea/` not showing year-1 dates.
- [ ] Owner-approved copy landed both languages; no fixture claims on pages.
- [ ] D4/D5 done or explicitly deferred to pipeline host.
- [ ] `hugo --minify` exits 0; feed paths `/museumtips.ics` and `/closing-soon.ics` unchanged.
- [ ] `themes/huguette` and generated data/feeds untouched.

## 7. QA / acceptance

```sh
hugo --minify
test -f public/index.html -a -f public/en/index.html -a -f public/kalender/index.html
# after D1 month pages:
# test -f public/kalender/2026-09/index.html -a -f public/en/calendar/2026-09/index.html
! grep -F '1 januari 1' public/kalender/index.html public/musea/index.html
! grep -F '1 January 1' public/en/calendar/index.html public/en/museums/index.html
! grep -F '0001-01' public/kalender/index.html public/en/calendar/index.html
```

Build authority: run the pinned Hugo **v0.166.0 extended** (pipeline host). Setup at build start: the same pinned darwin/arm64 build is installed on the Mac lane for agent self-checks; if a run cannot build locally it must say so explicitly, and the operator runs the pinned build pod-side before anything is marked done.

Spot-render: Ayoung Kim / Deshima Experience (open-ended); one “Laatste dag”/“Last day” row; one city on `/musea/`; home five closings.

**Owner checklist (live or `hugo server`):** both langs; jump-nav order; no junk month; meta lines readable; ended policy matches D3; subscribe links still `webcal://…/museumtips.ics` and `closing-soon.ics`; no JS required for the chosen D1/D2; feeds `curl -I` 200 + recent `last-modified`.

## 8. Documentation

- `README.md` — fixture lie; routes; ICS dual-write/overlay rule.
- `AGENTS.md` — only if layout/ICS policy changes; last-verified date.
- `docs/site-plan.md` — one line: phase 2 specified in `PLAN.md` (do not rewrite the old stack essay).
- Do not edit `docs/site-plan.md` deployment sketches or feed URLs.

## 9. Rollback

Nothing irreversible. Revert the implementation PR/branch (`git revert` or close unmerged). Feeds and `gh-pages` stay under pipeline control; this phase must not push them. If D4 removed root `index.html`, restore that blob from `0841858`. If D5 changed the pipeline host, revert that script on the host (out of repo).

## 10. Risks & unknowns

- Hugo `sort` on mixed null/date fields — do not rely on it; sort normalized keys.
- Build versions: the pin is Hugo **v0.166.0 extended** (pipeline host). The Mac lane currently has **no Hugo** — install the same pinned darwin/arm64 build at build start; runs that cannot build locally must say so (operator runs the pod-side pinned check).
- Month-page URL scheme must not collide with `/kalender/` or `/en/calendar/` indexes; keep feed paths free.
- Overlap vs end-month on the same site can confuse; copy (ST5) must say which page is which.
- `static/*.ics` vs root: live sizes match root — confirm overlay in `publish_site.py` before deleting static copies.
- `.nojekyll` (repo root and `static/.nojekyll`) and `static/CNAME` are tracked files — leave untouched; hosting plumbing is out of scope.
- Countdown uses integer day math (`Unix/86400`); timezone edge on “last day” already exists — don’t widen it.
- Copy run vs ST1–ST4 both touch `i18n/*.toml` — serialize or rebase.

## 11. Log

*(Append during the build, one bullet per run.)*

- 2026-09-12 · ST1 (grok-4.6) — commit `9e1d59b`. Null/zero-date guard: the five open-ended shows moved to their own “Geen einddatum” section (no “Afgelopen”, no countdown, no `#0001-01`); jump-nav + sections sorted on normalized `YYYY-MM`; meta line shortened (`t/m 13 sep 2026`, `9 mei – 13 sep 2026`; unknown start hidden); shared helper on `/musea/` and home. Operator-verified on pinned Hugo v0.166 (pod build): year-1 / `0001-01` / `Startdatum onbekend` greps all 0; nav ascending; five shows in the no-end section. Leftover: jump-nav keeps a “Geen einddatum” entry; `until`/`open_ended` keys now unused (left for ST5).

- 2026-09-12 · ST2 (composer-2.5) — commit `fca5fdf`. Ended policy (D3): recently-ended shows (≤ 7 days) now live in a collapsed `<details>` “Afgelopen (8)” / “Ended (8)” block below everything on /kalender/ + /en/calendar/; shows ended > 7 days are dropped entirely; empty months fall out of the nav and sections. Operator-verified on pinned Hugo: build OK; 8 ended items only inside the block; ST1 regression greps all 0; nav ascending. Leftover: the “hide” branch is not yet exercised — no item is > 7 days old in the current dataset (will show after future refreshes).

- 2026-09-12 · ST3 (grok-4.6) — commit `d3e487b`. Month pages: `/kalender/YYYY-MM/` + `/en/calendar/YYYY-MM/` (89 per language, current month → last `end`), generated build-time via content adapters + shared partials (month-keys, jump-nav, add-calendar-month-pages; new `calendar-month.html` layout). Each page lists shows open that month (overlap rule incl. null bounds), with H1, back link, prev/next, and the same ended handling as the list page. List jump-nav now links to month pages, year-grouped (89 + “Geen einddatum”). Operator-verified on pinned Hugo: build OK; spot pages exist (2026-09, 2027-05, 2030-05); Sep-2026 includes Kho Liang Ie + all five open-ended; no `<script>` anywhere; ST1/ST2 regression greps all 0. Leftovers: jump-nav lists all future months (16 end-month variant available on request); open-ended shows appear on every month page (per approved overlap rule).

- 2026-09-12 · ST4 (grok-4.6) — commit `e77f395`. City grouping (D2) + quirks hidden (D6): `/musea/` + `/en/museums/` now grouped by city (A→Z, museums A→Z within) — 20 city sections in the current dataset (PLAN said 19; data has 20), with a city jump list; tracker `quirks` no longer rendered; content subtitle/intro updated (“per stad” / “by city”). Date lines keep the ST1 short style; museums without current shows render name + site link only (same as before). Operator-verified on pinned Hugo: build OK; Rijksmuseum under Amsterdam; quirks greps 0; 20 sections both languages; ST1–ST3 regression greps all 0; no scripts.

- 2026-09-12 · ST5 (composer-2.5) — commit `06f626c`. i18n informal pass per approved table (subscribe buttons, “Alles bekijken”, jump labels incl. new jump_to_city, “Meer bij dit museum”, “Laatst bijgewerkt:”, empty-state texts) + tone sweep; NL/EN key parity 55/55. `until`, `open_ended`, `quirks` reported unused but left in place. Operator-verified on pinned Hugo: build OK; all changed strings render on the expected pages; ST1–ST4 regressions all 0; no scripts.

- 2026-09-12 · operator (D5) — `publish_feeds.py` now writes the root feed copies AND the `static/` copies in the same commit (static copies had been lagging one generation); change applied on the pipeline host; the next refresh (or post-merge rebuild) exercises it.

- 2026-09-12 · ST6 (composer-2.5) — commit `027a334`. Housekeeping: README brought current (live weekly dataset, month-view + city routes, root+`static` feed copies in one commit; fixture wording gone), root `index.html` removed (D4), AGENTS.md `static/` line updated + legacy index.html bullet dropped, site-plan pointer added. Operator-verified: build OK; diff scope exactly the four files; quick regression battery clean.

- 2026-09-12 · operator — tiny docs fix: `docs/site-plan.md` intro no longer claims “no site is built yet” (the site is live; pointer added by ST6).
- 2026-09-12 · operator (post-phase QA fix) — commit `b15a136`, PR #5. Live-review fixes: (a) stray “0.1.” card numbers — Huguette auto-numbers `h2/h3` inside `<article>` and every card is an `<article><h3>` (pre-existing; amplified by the month pages) → suppressed via new site-level `static/css/custom.css` (`classless.css` untouched); (b) copy typography unified to literal `’` in `content/{nl,en}` (Hugo v0.166 typographer rewrites markdown bodies only — front matter renders raw). AGENTS.md gained the punctuation convention; (c) subtitle + introduction ran together without a space (the theme renders them inline by design — `h6 + p { display: inline }`) — space restored via the same override file. Verified on pinned Hugo + local preview (computed styles + screenshots); live re-verify after publish.
