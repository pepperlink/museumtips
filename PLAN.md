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

- Live: NL default + `/en/`; pages home, `/kalender/`, `/museums/`, `/over/`. Data: `data/exhibitions.json` schema 1, compiled **2026-09-10**, **111** exhibitions, **30** museums. Zero JS; Huguette classless CSS (submodule). Hugo layouts in `layouts/` (`calendar.html`, `museums.html`, `index.html`, `partials/exhibition.html`, `format-date.html`, `countdown.html`).
- **(a) Null `end` (5):** Ayoung Kim (Dommelplein); john gerrard - Ghost Feed (Dommelplein); Ad Minoliti - Feminist School of Painting (Dommelplein); Hanuman reist de wereld over; Deshima Experience. `time.AsTime` on null → 0001-01-01 → “tot en met 1 januari 1” / “1 January 1”, countdown “Afgelopen”/“Ended”, junk jump-nav `#0001-01`. Same date call on `/museums/`.
- **(b) Jump-nav order (live):** `2026-09, 2026-10, 2028-06, 2030-05, 0001-01, 2026-11, 2026-12, 2027-01 … 2027-12, 2028-12, 2027-09, 2027-05, 2034-01`. Neither JSON order nor ISO order. Cause: `sort` on `end` with nulls is unreliable. Fix by sorting derived `YYYY-MM` keys, not raw `.end`.
- **(c) Meta line:** `exhibition.html` always prints start (or `open_ended` = “Startdatum onbekend”) + “tot en met” + full month name. **67** rows have `start: null`. Example: “Startdatum onbekend · tot en met 13 september 2026 · Laatste dag”.
- **(d) “Ended” (13 on live):** **8** really ended before 2026-09-12 (mostly 2026-09-06) + **the 5 null-end false positives**. Home already keeps `end >= today`, so it hides both groups (open-ended also vanish from “Bijna afgelopen” — correct for that list).
- Other awkwardness: `/museums/` groups by tracker `group` in file order (mix of cities, “The Hague”, catch-all “Noord/Oost/Zuid”); visitor-facing `quirks`; home/about/README still say the site is a **fixture**.
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
| City (19) | New city sections or `/kalender/stad/…` pages, or regroup `/museums/` by `city`. | Filter chips; needs JS. |
| Museum (30) | Already on `/museums/`. Polish that page; link from calendar meta. Do not duplicate. | Same chips on `/kalender/`. |

**Decision (owner, 2026-09-12): static. Regroup `/museums/` by city; optional city jump-nav or city pages only if the month pages are not enough. No filter JS.**

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
- **D6 — museum `quirks` on `/museums/` — decided: hide** (operator notes, mixed EN, not visitor copy).

**Copy refresh:** operator draft v2 (informal tone) is ready; owner signs off at landing. Fast-track (owner-agreed 2026-09-12): content-file changes land right after ST1; i18n strings with ST5. Files: `content/{nl,en}/*.md` (incl. front matter) + `i18n/{nl,en}.toml`.

## 5. Approach & subtasks

Each item is **one Cursor run**. All §4 decisions are resolved (2026-09-12); if a run finds a conflict with them, stop and report.

### ST1 — Date correctness + meta line

- **Scope:** `layouts/_default/calendar.html`, `layouts/_default/museums.html`, `layouts/partials/{exhibition,format-date,countdown}.html`, `i18n/{nl,en}.toml`.
- **Steps:** Guard null `end`/`start`. Sort jump-nav + sections by real `YYYY-MM`. Open-ended section (not `#0001-01`, not “Afgelopen”). Hide missing start. Shorter dates (abbrev month; range `9 mei – 13 sep 2026` when both known; `t/m 13 sep 2026` when only end). Keep countdown labels. Same date helper on `/museums/` and home (shared partial).
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
- **Steps:** Implement D2 + D6. Default path: regroup `/museums/` by `city` (sorted); fix per-museum date lines (ST1 helper). Add city pages or calendar city nav only if D2 says so.
- **Tests:** 19 cities appear; no year-1 dates; quirks hidden or shown per D6; EN `/en/museums/` matches.
- **Docs:** README if new routes.
- **Verify:** `hugo --minify`; spot `public/museums/index.html` + EN.
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
- [ ] D2 grouping live; `/museums/` not showing year-1 dates.
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
! grep -F '1 januari 1' public/kalender/index.html public/museums/index.html
! grep -F '1 January 1' public/en/calendar/index.html public/en/museums/index.html
! grep -F '0001-01' public/kalender/index.html public/en/calendar/index.html
```

Build authority: run the pinned Hugo **v0.166.0 extended** (pipeline host). Setup at build start: the same pinned darwin/arm64 build is installed on the Mac lane for agent self-checks; if a run cannot build locally it must say so explicitly, and the operator runs the pinned build pod-side before anything is marked done.

Spot-render: Ayoung Kim / Deshima Experience (open-ended); one “Laatste dag”/“Last day” row; one city on `/museums/`; home five closings.

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

- 2026-09-12 · ST1 (grok-4.6) — commit `9e1d59b`. Null/zero-date guard: the five open-ended shows moved to their own “Geen einddatum” section (no “Afgelopen”, no countdown, no `#0001-01`); jump-nav + sections sorted on normalized `YYYY-MM`; meta line shortened (`t/m 13 sep 2026`, `9 mei – 13 sep 2026`; unknown start hidden); shared helper on `/museums/` and home. Operator-verified on pinned Hugo v0.166 (pod build): year-1 / `0001-01` / `Startdatum onbekend` greps all 0; nav ascending; five shows in the no-end section. Leftover: jump-nav keeps a “Geen einddatum” entry; `until`/`open_ended` keys now unused (left for ST5).

- 2026-09-12 · ST2 (composer-2.5) — commit `fca5fdf`. Ended policy (D3): recently-ended shows (≤ 7 days) now live in a collapsed `<details>` “Afgelopen (8)” / “Ended (8)” block below everything on /kalender/ + /en/calendar/; shows ended > 7 days are dropped entirely; empty months fall out of the nav and sections. Operator-verified on pinned Hugo: build OK; 8 ended items only inside the block; ST1 regression greps all 0; nav ascending. Leftover: the “hide” branch is not yet exercised — no item is > 7 days old in the current dataset (will show after future refreshes).

- 2026-09-12 · ST3 (grok-4.6) — commit `d3e487b`. Month pages: `/kalender/YYYY-MM/` + `/en/calendar/YYYY-MM/` (89 per language, current month → last `end`), generated build-time via content adapters + shared partials (month-keys, jump-nav, add-calendar-month-pages; new `calendar-month.html` layout). Each page lists shows open that month (overlap rule incl. null bounds), with H1, back link, prev/next, and the same ended handling as the list page. List jump-nav now links to month pages, year-grouped (89 + “Geen einddatum”). Operator-verified on pinned Hugo: build OK; spot pages exist (2026-09, 2027-05, 2030-05); Sep-2026 includes Kho Liang Ie + all five open-ended; no `<script>` anywhere; ST1/ST2 regression greps all 0. Leftovers: jump-nav lists all future months (16 end-month variant available on request); open-ended shows appear on every month page (per approved overlap rule).

- 2026-09-12 · ST4 (grok-4.6) — commit `e77f395`. City grouping (D2) + quirks hidden (D6): `/museums/` + `/en/museums/` now grouped by city (A→Z, museums A→Z within) — 20 city sections in the current dataset (PLAN said 19; data has 20), with a city jump list; tracker `quirks` no longer rendered; content subtitle/intro updated (“per stad” / “by city”). Date lines keep the ST1 short style; museums without current shows render name + site link only (same as before). Operator-verified on pinned Hugo: build OK; Rijksmuseum under Amsterdam; quirks greps 0; 20 sections both languages; ST1–ST3 regression greps all 0; no scripts.

- 2026-09-12 · ST5 (composer-2.5) — commit `06f626c`. i18n informal pass per approved table (subscribe buttons, “Alles bekijken”, jump labels incl. new jump_to_city, “Meer bij dit museum”, “Laatst bijgewerkt:”, empty-state texts) + tone sweep; NL/EN key parity 55/55. `until`, `open_ended`, `quirks` reported unused but left in place. Operator-verified on pinned Hugo: build OK; all changed strings render on the expected pages; ST1–ST4 regressions all 0; no scripts.

- 2026-09-12 · operator (D5) — `publish_feeds.py` now writes the root feed copies AND the `static/` copies in the same commit (static copies had been lagging one generation); change applied on the pipeline host; the next refresh (or post-merge rebuild) exercises it.

- 2026-09-12 · ST6 (composer-2.5) — commit `027a334`. Housekeeping: README brought current (live weekly dataset, month-view + city routes, root+`static` feed copies in one commit; fixture wording gone), root `index.html` removed (D4), AGENTS.md `static/` line updated + legacy index.html bullet dropped, site-plan pointer added. Operator-verified: build OK; diff scope exactly the four files; quick regression battery clean.

- 2026-09-12 · operator — tiny docs fix: `docs/site-plan.md` intro no longer claims “no site is built yet” (the site is live; pointer added by ST6).
- 2026-09-12 · operator (post-phase QA fix) — commit `b15a136`, PR #5. Live-review fixes: (a) stray “0.1.” card numbers — Huguette auto-numbers `h2/h3` inside `<article>` and every card is an `<article><h3>` (pre-existing; amplified by the month pages) → suppressed via new site-level `static/css/custom.css` (`classless.css` untouched); (b) copy typography unified to literal `’` in `content/{nl,en}` (Hugo v0.166 typographer rewrites markdown bodies only — front matter renders raw). AGENTS.md gained the punctuation convention; (c) subtitle + introduction ran together without a space (the theme renders them inline by design — `h6 + p { display: inline }`) — space restored via the same override file. Verified on pinned Hugo + local preview (computed styles + screenshots); live re-verify after publish.
- 2026-09-12 · operator (navigation fan-out) — commit `eac55ae`, PR #6. Cities + museums linkable from every card (home, kalender, month pages; NL+EN) → deep links to their anchors on the museums page; museums page gained per-museum anchors; homepage gained “Bekijk alle musea per stad” / “See all museums by city” (i18n `view_museums`) next to “Alles bekijken”. Links render only when the target section exists (Museum MORE’s Ruurlo venue stays plain — no dead links). Operator-verified on pinned Hugo + local preview (slug audit + real-browser click-through); live re-verify after publish.
- 2026-09-12 · operator (post-publish layout fix) — commit `fc28e26`, PR #8. In-content navs (museums city jump list, calendar month jump nav, month prev/next) were absolutely positioned over the top of the page — the theme's `body>nav, header nav` navbar rule caught them because Huguette renders content directly under `<body>`. Effect: /museums/ hid its title, intro and first ~3 museums; /kalender/ hid title/intro and ~3,500px of content. Fix: `class="contentnav"` + `position: static` override in custom.css. Operator-verified on pinned Hugo + local preview (positions, click-through, screenshots). Awaiting owner merge → republish.

- 2026-09-12 · operator (upcoming section) — commit `ef91176`, PR #9. Homepage gains “Binnenkort te zien” / “Opening soon”: ALL future-start shows, sorted by opening date (hidden while empty). Countdown partial is start-aware (“Opent deze week/maand” before opening; closing countdowns only for running shows). “Bijna afgelopen”/closing-soon excludes not-yet-opened shows (site guard; feeds + digest guarded tracker-side same day). Tracker-side (same day): digest gains “Opening soon — next 5”; upcoming capture becomes part of every refresh — this subsumes the Kusama-class gap fix (shows are stored before they open; Sep 2026 incident documented in the skill). Operator-verified on pinned Hugo + local preview (synthetic future entries: order, countdowns, NL/EN parity, closing section unchanged, graceful empty state). Awaiting owner merge → data lands via pipeline refresh.

---

# PLAN — Phase 3b: Museum & exhibition pages (plan)

Status: **draft** (2026-09-12) — owner + independent reviewer before any implementation. Do not start feature code from this section until the owner signs off (especially §3b.4).

Phase 2 (§0–§11 above) stays the record of calendar UX. This section is the next site-plan slice: one page per museum and one page per exhibition, NL + EN.

## 3b.0 Agent ground rules

Follow `AGENTS.md` (outranks defaults). Same in-force list as §0: Conventional Commits; `diane/…` or `cursor/…`; **owner merges**; never push `main` / `gh-pages` except via pipeline scripts; never hand-edit `data/exhibitions.json`, root `*.ics`, or `themes/huguette`; never change public feed URLs (`/museumtips.ics`, `/closing-soon.ics`); NL + EN stay in sync; no Node.js; Hugo v0.166.0 extended; **zero JavaScript in this phase** (Leaflet is 3c, not here); work only in assigned scope.

Site-copy punctuation: literal `’` (U+2019) in `content/` and `i18n/`. New UI strings go in `i18n/{nl,en}.toml`, never inline.

Reuse the month-page mechanism: `content/{nl,en}/_content.gotmpl` → shared `AddPage` partials → layouts + `translationKey`. Do not invent a second page-generation path.

## 3b.1 Goals

Ship two new page types, both languages, classless HTML, no JS:

1. **Museum page** (one per tracker museum, currently 30): description + official website; opening hours; how to get there (public transport + parking); accessibility; entrance cards; pricing (incl. supplements); current + upcoming exhibitions (reuse card / date / countdown partials); “more museums in this city”; per-page last-verified date; a **location** section that can hold an address now and a map later.
2. **Exhibition page** (one per row in `exhibitions[]`): title, museum, city; start/end + status line; description; link to the museum’s own show URL; admission with an explicit Museumkaart / supplement flag when known; press links (quality outlets); “add to agenda” (one-event `.ics`); related shows (same museum / same city); shareable permalink.
3. **Cross-links:** cards and the `/museums/` overview point at these pages. The museum’s own URL remains available, not as the card title target.

## 3b.2 Non-goals

- No stack change, no Node, no theme-submodule edits, no feed path/filename changes, no hand-edits of generated JSON/ICS.
- **No Leaflet / no map UI** (phase **3c**). Reserve a location section + lat/lon fields only. Do not design tiles, markers, popups, or a JS loader.
- **No marketing CTA** (tickets, newsletter, donate) — phase **3d**. Do not occupy a `cta` slot or add booking buttons.
- No bilingual exhibition titles from the pipeline (schema still has one `title` / `description` string).
- No search, no images, no client-side filters, no clipboard JS, no third-party share widgets.
- Do not rewrite month-page overlap logic, D3 ended policy, or city jump-nav except where card links must change.
- Do not draft visitor copy for hours/prices in implementation runs — land collected, cited facts only.
- Do not implement the tracker pipeline in this repo; this plan **specs the JSON fields** the operator adds on the host.

## 3b.3 Recon (what we reuse)

Verified 2026-09-12 in this worktree.

- Live routes: `/`, `/kalender/`, `/kalender/YYYY-MM/`, `/museums/`, `/over/` (+ `/en/…`). Data: `data/exhibitions.json` schema 1, `compiled` 2026-09-12, **30** museums, **187** exhibitions. Cards: `layouts/partials/exhibition.html` — **title `<a href="{{ .url }}">` is the museum’s own site**; museum/city names deep-link to `/museums/#urlize`.
- Month pages: `content/{nl,en}/_content.gotmpl` → `partials/add-calendar-month-pages.html` → `$.AddPage` (`kind/path/url/title/layout/type/translationKey/params`). Language switcher uses `.AllTranslations` (needs matching `translationKey`). NL vs EN URLs already diverge (`/kalender/` vs `/en/calendar/`) with a shared key `calendar-month-YYYY-MM`.
- `/museums/` is an index (`layout: museums`, NL `url: /museums/` + alias redirect for the old path, EN at `/en/museums/`), grouped by city, quirks hidden. Museum MORE is one tracker museum; some shows use city `Ruurlo` (no museum-row city match → no city hash link today).
- Countdown partial is **bucket** labels (`Opent deze week`, `Laatste week`, …), not “opent over N dagen”. Date helper already shared.
- Zero `<script>` by policy. Custom CSS only for theme collisions (`contentnav`, card numbering).
- Adapter-created pages are auto-included in the sitemaps (verified on the pin — no extra config); no sitemap work needed in this phase.
- Generated files are overwritten weekly. Anything the site must not lose (hours, press, slugs) cannot live only in `exhibitions.json` unless the **tracker** persists it.

## 3b.4 Decisions (recommendations)

Owner signs these off before build runs. Defaults below are the proposal.

**Owner status (2026-09-12):** D7 approved **with one change** — exhibition pages **nest under their museum**: `/museums/<museum-slug>/tentoonstelling/<slug>/` (EN `/en/museums/<museum-slug>/exhibition/<slug>/`), one-event ICS as a sibling file `<slug>.ics` at the same level (shape owner-confirmed after review; mechanics verified on the pin, see D11). D8–D14 approved as recommended (D8: "stability, of course"). D15–D16: implementation detail, proceed.

**Rename note (2026-09-12):** the NL museums section path is `/museums/` (was the `musea` spelling) — owner: the Dutch plural is "museums" and `/en/` prevents overlap with the English section. All paths in this plan already reflect it; the live site keeps the old path as a redirect alias (site PR #11).

### D7 — URL scheme — RECOMMEND: locale-specific section + frozen slug

| Page | NL | EN | `AddPage.path` (both langs) | `translationKey` |
|---|---|---|---|---|
| Museum | `/museums/<slug>/` | `/en/museums/<slug>/` | `museum/<slug>` | `museum-<slug>` |
| Exhibition | `/museums/<museum-slug>/tentoonstelling/<slug>/` | `/en/museums/<museum-slug>/exhibition/<slug>/` | `exhibition/<slug>` | `exhibition-<slug>` |
| One-event ICS | `/museums/<museum-slug>/tentoonstelling/<slug>.ics` | `/en/museums/<museum-slug>/exhibition/<slug>.ics` | companion ICS page (D11) | n/a |

**Why this shape (owner-confirmed 2026-09-12):** the museums section uses the word `museums` in **both** languages — Dutch and English share it and never collide because the English site lives under `/en/` (owner: "Dutch plural of museum is museums"; the NL path was renamed from `/musea/`). Each exhibition **nests under its own museum** — `/museums/<museum-slug>/tentoonstelling/<slug>/` (EN `/en/museums/<museum-slug>/exhibition/<slug>/`) — so the URL itself expresses the parent relationship (breadcrumb clarity, nothing new at the top level). `tentoonstelling` is the visitor-facing NL noun; `exhibition` matches the EN section vocabulary already in i18n (`nav` stays Musea/Museums — these URLs are not new menu items).

**Do not** put pages at `/<slug>/` (collides with `over`, `kalender`, future sections) or reuse month `path = YYYY-MM` (un-namespaced). Keep `/museumtips.ics` and `/closing-soon.ics` free.

**Locale-relative `url` values (implementation-critical):** the `url` passed to `AddPage` must NOT include the language subdir — Hugo prepends `/en/` for the English site itself. Pass `"museums/<slug>/"` / `"museums/<slug>/"` and `"museums/<museum-slug>/tentoonstelling/<slug>/"` / `"museums/<museum-slug>/exhibition/<slug>/"` (Hugo adds the locale prefix), exactly like `calendar-month-keys.html` does (`"kalender/%s/"` vs `"calendar/%s/"`). A literal `/en/…` value silently double-nests to `/en/en/…` with the build still exiting 0 (verified on the pin) — check `hugo list all` permalinks, not just `test -f`.

**Nesting input:** an exhibition page needs its **museum's frozen slug as well as its own** — skip the page when either is missing (this extends the no-pages-without-slug gate until both slug shipments land).

Index pages stay. Museum **name headings** on `/museums/` become links to `/museums/<slug>/`; keep `id="{{ urlize name }}"` so old card hash links still work until ST-B5 retargets them.

### D8 — Slug stability — RECOMMEND: tracker-persisted `slug` (operator host), freeze-once

This is the crux. Pages are public URLs; titles and sort order are not stable.

**Interface (pipeline emits; this repo never invents production slugs):**

On each `museums[]` object, additive field:

```text
slug: string  // [a-z0-9]+(?:-[a-z0-9]+)*  no leading/trailing hyphen
```

On each `exhibitions[]` object, additive field:

```text
slug: string  // same charset
```

Optional but useful (not required for 3b pages): opaque tracker `id` for the operator’s store. The **site** joins on `slug` only.

**Museum slug rule**

1. Operator seeds a **frozen table of the current 30** (human-chosen, URL-safe). This avoids ugly urlize of names like `H'ART Museum (ex-Hermitage Amsterdam)` and `Museum Boijmans Van Beuningen (Depot)`.
2. New museums: `base = urlize(name)` in the **Hugo 0.166 sense** (Unicode fold, lower case, non-alphanumerics → `-`, collapse/strip hyphens). If `base` collides with any slug ever issued for a museum, append `-2`, `-3`, …
3. **Freeze on first write.** A later rename of `name` does not change `slug`. Do not recycle a slug for a different museum.

**Exhibition slug rule**

1. On first persist of a show in the tracker store: `base = urlize(title)`; if `base` is empty (`…` only, etc.), use `urlize(museum) + "-show"`.
2. Collision check against **all exhibition slugs ever issued** (not only the current weekly JSON). If taken, `base-2`, `base-3`, …
3. **Freeze on first write.** Title edits, description edits, and JSON array reorder must not change `slug`.
4. Identity for “first write”: the tracker’s internal exhibition key (the same identity used to update dates/URLs today). If a show drops out of the weekly export and returns, reuse the stored slug.
5. Dedup is **global**, not per-museum — keeps slugs unique (the nested URL inherits its museum's slug for the parent segment).

**Site behaviour until slugs exist:** do not generate museum/exhibition pages from `urlize(title)` in Hugo. Missing `slug` → skip that page (and skip internal card links for that row). After the pipeline ships slugs, a later ST can `fail the build` if any row lacks one.

**Why build-time slugs are weaker**

| Failure | Build-time `urlize(title)` | Tracker freeze |
|---|---|---|
| Title tweak at source | URL changes → 404 / broken shares | Stable |
| Two shows, same title | Suffix depends on JSON order that week | Assigned once |
| Show leaves and returns | New suffix or clash | Same slug |
| Hugo vs Python `urlize` | Drift if only the site computes | One writer (tracker) |
| Card links before pages exist | Can ship the wrong permalink | No permalink until freeze |

Build-time slugs are acceptable only for throwaway local mocks, not for `gh-pages`.

**Schema:** keep `schema: 1` and **add** `slug` (do not wait on bilingual titles). Document in README/AGENTS as required for 3b routes. Pipeline still owns `data/exhibitions.json`; this repo still never hand-edits it.

### D9 — Extras data location — RECOMMEND: hand-curated repo JSON, pipeline-untouched

| File | Key | Owner | Pipeline |
|---|---|---|---|
| `data/exhibitions.json` | generated | tracker | **writes** |
| `data/museums_info.json` | museum `slug` | editors / collection runs in this repo | **must not touch** |
| `data/exhibitions_info.json` | exhibition `slug` | same | **must not touch** |

**Join at build (verified on pinned Hugo v0.166):** use the file **basename verbatim** — Hugo does *not* normalize hyphens: `data/museums_info.json` is dot-accessible as `hugo.Data.museums_info` (underscore filename, no hyphen → valid; a file named `museums-info.json` keeps the hyphen key and can never be dot-chased). **Slug keys are hyphenated by design, so never dot-chase them** — always `index`:

```gotemplate
{{ with index hugo.Data.museums_info $slug }} … {{ end }}
{{ with index hugo.Data.exhibitions_info $slug }} … {{ end }}
```

(`hugo.Data.museums_info.h-art-museum` is a **template parse error** — `bad character U+002D '-'` — that fails the whole build; verified on the pin.) Missing key → omit extras sections, still render name/shows from generated JSON. Never merge extras *into* `exhibitions.json` (weekly overwrite).

**Museum extras (per slug)** — all visitor strings in NL + EN pairs; facts carry `source` URL + `verified` (YYYY-MM-DD):

- `name` (debug; display name still comes from generated JSON)
- `description_nl` / `description_en`
- `address` (one line; venue note allowed, e.g. MORE Gorssel)
- `lat` / `lon` (numbers or `null` — **3c only**; unused in 3b templates except unused data)
- `hours_nl` / `hours_en`
- `transit_nl` / `transit_en`
- `parking_nl` / `parking_en`
- `access_nl` / `access_en`
- `cards` — list of `{ "id": "museumkaart"|"vriendenloterij"|"icom"|"stadspas"|"other", "label": "…", "accepted": true|false|null, "note_nl", "note_en" }`
- `pricing_nl` / `pricing_en` (standard ticket + known supplements; free text, cited)
- `verified` — page-level last-checked date (max of fact dates, or explicit)
- `sources` — `{ "fact": "hours"|"pricing"|…, "url": "https://…" }`

**Exhibition extras (per slug):**

- `admission`: `{ "museumkaart": "included"|"supplement"|"not_covered"|"unknown", "note_nl", "note_en", "source", "verified" }`
- `press`: list of `{ "title", "outlet", "url", "lang": "nl"|"en", "date"? }` — quality outlets only (see protocol)
- `verified`

No press / unknown admission → skip those blocks (do not invent). Tracker `description` + `url` + dates remain the exhibition body defaults.

**Collection protocol (same spirit as the 2026-09-12 exhibition sweep):**

1. **Official sources only** for hours, prices, cards, access, transport, admission flags: the museum’s own website (or PDF linked from it). One cited URL per fact.
2. Do not use Wikipedia, blogs, or Google knowledge panels as primary. Visitor-review sites are out.
3. Press: national/quality arts coverage (e.g. NRC, de Volkskrant, Trouw, Het Parool, Museumtijdschrift, well-known international arts press). Museum “press release” pages are discovery, not the listed article. Skip listicles and uncredited copies.
4. Record `verified` as the date the agent/operator actually opened the URL. Stale (> ~90 days) facts get a re-check, not silent reuse.
5. NL + EN: translate hours/prices **faithfully**; do not add claims absent from the source. Product names (Museumkaart, Vriendenloterij) stay in Dutch in both languages.
6. Batch via subagents (e.g. 5–6 museums per run; exhibitions grouped by museum). Human operator spot-checks a sample before merge.
7. If a fact is unclear (exhibition-only supplement buried in FAQ), set `unknown` / omit — never guess.

### D10 — Card link behaviour — RECOMMEND: title → our exhibition page; museum site as secondary

| Element | Today | 3b |
|---|---|---|
| Card title | `.url` (museum site) | our nested exhibition page (`/museums/<museum-slug>/tentoonstelling/<slug>/`; if slug present; else keep `.url` so we never ship a dead title link) |
| Museum name | `/museums/#urlize` | `/museums/<museum.slug>/` when slug exists; hash fallback otherwise |
| City name | `/museums/#urlize(city)` | unchanged (index anchors) |
| New line / link | — | `museum_show_page` → `.url` (“Bekijk op de museumsite”) when `.url` is set |
| `/museums/` show titles | `.url` | exhibition page, same fallback |

Do **not** put Museumkaart badges on cards in the first pass (keeps lists scannable). Flag lives on the exhibition page.

### D11 — One-event `.ics` — **owner spec: sibling `<slug>.ics`** — mechanics verified on pinned Hugo v0.166

Zero JS. Owner spec (2026-09-12): the ICS is a **sibling file** of the exhibition page — `/museums/<museum-slug>/tentoonstelling/<slug>.ics` (EN `/en/museums/<museum-slug>/exhibition/<slug>.ics`). “Zet in je agenda” links it (relative `../<slug>.ics` from the page — verify the href in ST-B6).

**Mechanics (verified on pinned Hugo v0.166, scratch site):** add a **companion `AddPage`** per exhibition per language with `url` ending `.ics` (`"museums/<museum-slug>/tentoonstelling/<slug>.ics"` / `"museums/<museum-slug>/exhibition/<slug>.ics"`), `outputs` = the ICS format only, using a custom output format `icsfile` (`mediaType = "text/calendar"`, `isPlainText`, `baseName = "index"`) and template `layouts/_default/exhibition-ics.icsfile.ics`. Verified output (mechanism re-confirmed with the nested shape on the pin): exactly `public/museums/<museum-slug>/tentoonstelling/<slug>.ics` + the EN twin. **Do NOT touch the global `[outputs]` table in `hugo.toml`** (kind-keyed; museum/calendar-month/about pages share `kind = "page"` and a global bump leaks WARNs, verified).

- UID: `museumtips-<slug>@museumtips.pepperlink.nl` — distinct local-part scheme from the weekly feeds' `museum-<hash>[-ld]@hermes.museumtracker` (verified, no collision).
- All-day `DTSTART`/`DTEND` from `start`/`end`; **the weekly feeds' convention, verified from `museumtips.ics`: `DTEND;VALUE=DATE` = last day + 1** (a show ending 2026-09-13 emits `DTEND;VALUE=DATE:20260914`). Match it — do not invent a second all-day rule.
- `SUMMARY` = title; `LOCATION` = museum + city; `DESCRIPTION` + `URL` = museum show URL.
- Skip the Calendar output if both dates missing.
- **Do not** write these files into repo-root or `static/*.ics`; they are Hugo build output only. Public weekly feeds stay the only hand-off to subscribers of the *full* set.

Share: print the permalink (`rel=canonical` already via Hugo) plus short hint to copy the URL. **No mailto/Web Share in 3b** — mailto would need its own i18n subject string; explicitly deferred, keep scope tight.

### D12 — Ended shows on new pages — RECOMMEND: same window as the JSON export

Generate an exhibition page for every JSON row with a `slug`. When the Thursday pipeline drops a show, the page disappears. Do not build a separate archive. Aligns with D3 without duplicating hide/collapse on the detail URL.

Museum pages always exist for every `museums[]` row (even with zero current shows).

### D13 — Museum MORE / multi-venue — RECOMMEND: one museum page

One tracker name → one `/museums/museum-more/`. Address/hours may note Gorssel as default; exhibition cards still show the per-show `city`. “More museums in this city” uses the exhibition’s `city` on **exhibition** pages and the museum row’s `city` on **museum** pages. Do not split venue microsites in 3b (open Q3 if the owner wants Ruurlo/Twickel later).

### D14 — i18n: all new keys (add to both `nl.toml` and `en.toml`)

Existing keys stay (`website`, `compiled`, `exhibitions_here`, countdown buckets, `back_to_calendar`, `no_exhibitions`, `no_museums`, …). Cards keep bucket countdown; **detail pages** call the countdown partial in `precise` mode.

| Key | NL | EN |
|---|---|---|
| `back_to_museums` | Terug naar alle musea | Back to all museums |
| `museum_website` | Museumwebsite | Museum website |
| `last_verified` | Gecontroleerd op | Checked on |
| `location` | Locatie | Location |
| `opening_hours` | Openingstijden | Opening hours |
| `getting_there` | Bereikbaarheid | Getting there |
| `public_transport` | Openbaar vervoer | Public transport |
| `parking` | Parkeren | Parking |
| `accessibility` | Toegankelijkheid | Accessibility |
| `entrance_cards` | Toegangskaarten | Entrance cards |
| `card_accepted` | Geldt | Accepted |
| `card_not_accepted` | Geldt niet | Not accepted |
| `card_status_unknown` | Status onbekend | Status unknown |
| `pricing` | Prijzen | Prices |
| `current_exhibitions` | Nu te zien | On now |
| `upcoming_exhibitions` | Binnenkort | Coming up |
| `no_current_exhibitions` | Geen lopende tentoonstellingen. | No exhibitions on now. |
| `more_in_city` | Meer musea in %s | More museums in %s |
| `museum_show_page` | Bekijk op de museumsite | View on the museum site |
| `official_page` | Pagina van het museum | Museum’s own page |
| `admission` | Toegang | Admission |
| `museumkaart_included` | Museumkaart geldt | Covered by Museumkaart |
| `museumkaart_supplement` | Museumkaart geldt, met toeslag | Museumkaart valid; supplement applies |
| `museumkaart_not_covered` | Museumkaart geldt niet voor deze tentoonstelling | Museumkaart does not cover this exhibition |
| `museumkaart_unknown` | Museumkaart: zie de museumsite | Museumkaart: see the museum site |
| `press` | Pers | Press |
| `add_to_calendar` | Zet in je agenda | Add to calendar |
| `share` | Delen | Share |
| `share_hint` | Kopieer de link van deze pagina | Copy this page’s link |
| `related_same_museum` | Meer in dit museum | More at this museum |
| `related_same_city` | Meer in deze stad | More in this city |
| `opens_in` | Opent over %d dagen | Opens in %d days |
| `opens_today` | Opent vandaag | Opens today |
| `closes_in` | Sluit over %d dagen | Closes in %d days |
| `closes_today` | Laatste dag | Last day |

`closes_today` may reuse `last_day` instead of a new key — implementation should not duplicate if the wording matches. Product names Museumkaart / Vriendenloterij are **not** i18n keys (data labels).

**Argument style:** keys with `%s`/`%d` placeholders (`more_in_city`, `opens_in`, `closes_in`) are called with `printf (i18n "key") arg` — matching the existing `ended_shows` (`"Afgelopen (%d)"`) convention; `dict`-style stays for existing keys only.

**Back-link to the parent museum:** link text **is the museum name** (like month prev/next links use month names) — no i18n key needed.

Do **not** add `map_coming_soon` (no teaser copy for 3c).

### D15 — `translationKey` pairing

Same as month pages: identical key in both `AddPage` dicts; different `url`. Language switcher stays `partials/lang-switcher.html` with no code change if keys match.

- Museums: `museum-<slug>`
- Exhibitions: `exhibition-<slug>`
- Do not reuse `museums` / `calendar` (those are the indexes).

### D16 — Consistency / partials

| Reuse | New |
|---|---|
| `exhibition.html` (card), `format-date.html`, `countdown.html` | `countdown-precise.html` — **separate partial** so the three existing bucket call sites (card, museums, home) stay untouched; no wrapper-dict refactor |
| `_content.gotmpl` (call the new partials next to month pages) | `add-museum-pages.html`, `add-exhibition-pages.html` |
| `contentnav` class on any in-page nav | `layouts/_default/museum-page.html`, `layouts/_default/exhibition-page.html` (the `-page` suffix avoids confusion with the existing card partial `partials/exhibition.html`; name resolution verified on the pin) |
| Ended/upcoming split already used on home | `layouts/_default/exhibition-page.calendar.ics` — the ICS output template (verified to produce `…/event.ics` on the pin) |
| — | small join partials: `museum-info.html`, `exhibition-info.html` (**index-based** extras lookup; no extra HTTP) |

Month layouts: **untouched** except they inherit card-link changes from `exhibition.html`. Custom CSS: only if new `<nav>` hits the Huguette `body>nav` trap — then reuse `contentnav`, do not restyle the theme.

## 3b.5 Page specs

### Museum page (`layout: museum-page`)

Order:

1. H1 = generated `name`. Back link: `back_to_museums` → museums index.
2. City (link to `/museums/#city`).
3. Description (extras); omit if empty.
4. `museum_website` → generated `site`.
5. **Location** `section#location`: address if known. **Map slot for 3c:** empty `<div id="map" hidden></div>` (or equivalent inert container), no script, no iframe, no copy. `lat`/`lon` not rendered.
6. Opening hours; getting there (transit then parking); accessibility — each a `<section>` omitted if that extras field is empty.
7. Entrance cards (list; `accepted: null` renders the label with `card_status_unknown`); pricing.
8. Current exhibitions (`end >= today` or null-end; `start` empty or `<= today`), then upcoming (`start > today`). Reuse `exhibition.html`. Empty current → `no_current_exhibitions`.
9. More museums in this city (name + link to their museum pages; exclude self).
10. Footer line: `last_verified` + extras `verified` if set; else omit (do not print `compiled` as if it verified hours).

NL + EN: one `AddPage` per language per museum; titles = museum name (proper name, not translated).

### Exhibition page (`layout: exhibition-page`)

Order:

1. H1 = `title`. Back links: calendar index + parent museum page (link text = museum name).
2. Museum + city (links as D10).
3. Dates via `format-date.html`; status via `countdown-precise.html` (`opens_in` / `closes_in` / existing `ended`). Null end: no closing countdown (same as cards).
4. Description from generated JSON.
5. `official_page` → `.url`.
6. Admission block from extras; always show `museumkaart_*` variant (unknown if extras missing).
7. Press list; omit section if empty.
8. Add to agenda (if ICS output exists) + share permalink.
9. Related: up to 5 other shows same museum (exclude self; prefer current/upcoming); up to 5 same city excluding that museum. Reuse cards.
10. `last_verified` if extras `verified` set.

### 3c / 3d interface notes (only)

- **3c:** `section#location` + `#map` + `lat`/`lon` in `museums_info.json`. No Leaflet CSS/JS in 3b. Do not pre-vend a map library.
- **3d:** no button, no `params.cta`, no third-party booking URL field in extras yet.

## 3b.6 Data-collection subtasks

These are content runs, not template runs. They may proceed in parallel with adapters once **museum slugs are seeded** (exhibitions extras wait on exhibition slugs).

### C1 — Museum info × 30

- **Scope:** fill `data/museums_info.json` for every `museums[].slug`.
- **Sources:** official site of that museum (hours/visit/plan-your-visit/accessibility pages). Cite `sources[]`.
- **Verify:** 30 keys match 30 slugs; every non-empty fact has a URL; NL/EN pairs both present or both absent; `lat`/`lon` may stay null; no text in `exhibitions.json`.
- **Size:** L (batch 5–6 museums / subagent). **Model:** capable mid-tier for extraction; operator spot-check.

### C2 — Exhibition extras (admission + press)

- **Scope:** `data/exhibitions_info.json` keyed by exhibition slug. Admission from the **show** page or ticketing FAQ on the official site. Press: 0–3 links, quality outlets, no stuffing.
- **Priority:** running + upcoming first; do not block templates on 100% coverage (`unknown` / omit is valid).
- **Verify:** no key without a live slug; every admission `source` is official; press URLs 200; no duplicate outlet+URL; language parity of `note_*`.
- **Size:** L. **Model:** capable mid-tier in museum-grouped batches.

## 3b.7 Build subtasks (ordered)

Each item is **one Cursor run**. If a run conflicts with D7–D16, stop and report. Pipeline slug work is **ST-P** on the operator host (not this repo).

### ST-P — Tracker: emit `slug` (operator host)

- **Scope:** museum tracker store + the weekly **compile step** that regenerates `data/exhibitions.json` (the scripts the Thursday refresh runs — `publish_feeds.py` only copies the file into the repo). Seed 30 museum slugs; persist exhibition slugs freeze-once; emit `slug` fields into the JSON. Still never edited by site agents.
- **Verify:** every museum and exhibition row in the next published JSON has a unique `slug`; a title-edit fixture keeps the same slug; weekly job does not rewrite `museums_info.json` / `exhibitions_info.json`.
- **Model:** operator / pipeline. **Size:** M. **Depends:** D8 sign-off. **Blocks:** production permalinks (ST-B3+ still mockable locally only if owner allows fixtures — default: wait).

### ST-B1 — Curated file scaffolds + docs note

- **Scope:** add empty-object or `{}` skeletons `data/museums_info.json`, `data/exhibitions_info.json`; README/AGENTS one-liners: pipeline must not touch them; never hand-edit `exhibitions.json`.
- **Verify:** `hugo --minify` exits 0; files parse; no layout change yet; **record the pre-change baseline** (build exit 0, page count, `grep -c '<script'` = 0, WARN-count = 0) for later regression diffs.
- **Model:** composer-2.5. **Size:** S. **Depends:** none.

### ST-B2 — i18n keys (table D14)

- **Scope:** `i18n/nl.toml` + `i18n/en.toml` only. Key parity. Typographic `’`.
- **Verify:** equal key counts; `hugo --minify` 0. Unused until layouts land is OK.
- **Model:** composer-2.5. **Size:** S. **Depends:** D14.

### ST-B3 — Museum content adapters + layout

- **Scope:** `add-museum-pages.html`; call from both `_content.gotmpl`; `layouts/_default/museum-page.html`; join extras partial (**index-based lookup**, D9). No card changes yet. Skip museums without `slug`.
- **Verify:** `hugo --minify` 0; `test -f public/museums/<one-slug>/index.html` and `public/en/museums/<same-slug>/index.html`; `hugo list all` permalinks correct (catches silent `/en/en/` doubling); language switcher pair (grep `translationKey` / click locally); 30×2 pages once slugs ship; no `<script>`; `/museums/` index still builds; month pages unchanged; extras render for a fixture slug and are omitted cleanly otherwise.
- **Model:** capable mid-tier (grok-4.6-class). **Size:** M. **Depends:** ST-P (or owner-approved fixture slugs), ST-B1, ST-B2.

### ST-B4 — Exhibition adapters + layout (HTML)

- **Scope:** `add-exhibition-pages.html`; `layouts/_default/exhibition-page.html`; `countdown-precise.html` called from this layout only (cards keep the bucket partial untouched); admission/press/related/share **without** ICS yet if that keeps the diff reviewable (ICS = ST-B6). Skip rows without `slug`.
- **Verify:** build 0; spot 3 NL + 3 EN pages (shape `public/museums/<museum-slug>/tentoonstelling/<slug>/index.html`); **card bucket labels unchanged** after the new partial exists (diff one known card render before/after); open-ended show has no fake “Afgelopen”; related lists exclude self; extras missing → admission unknown, no press heading; no `<script>`.
- **Model:** capable mid-tier. **Size:** L. **Depends:** ST-B3, D8.

### ST-B5 — Card + index link retarget (D10)

- **Scope:** `layouts/partials/exhibition.html`, `layouts/_default/museums.html` only (home/calendar/month inherit the card partial). Title → exhibition page; museum name → museum page; secondary `museum_show_page` → `.url`.
- **Verify:** build 0; grep a known `.url` is no longer the card `<h3>` href; museum index titles match; hash city links still work; fallback: a synthetic row without slug still titles to `.url`; **re-run the full Phase-2 QA battery (§7): the four greps (year-1, `0001-01`, …), the D3 ended-count spot check, the “Binnenkort” section render, and the zero-`<script>` sweep** — this subtask touches a partial every page uses.
- **Model:** composer-2.5. **Size:** S. **Depends:** ST-B3, ST-B4.

### ST-B6 — One-event ICS output (D11)

- **Scope:** `[outputFormats.icsfile]` (`mediaType` `text/calendar`, `baseName` `index`, `isPlainText`) + companion `.ics` `AddPage`s (NL `museums/<museum-slug>/tentoonstelling/<slug>.ics`, EN mirrored) + `layouts/_default/exhibition-ics.icsfile.ics` (per D11; never global `[outputs]` — verified leak); agenda link on exhibition page; exclude companion pages from sitemaps if they render there. Do not touch root/`static` weekly ICS.
- **Verify:** build 0; `public/museums/<museum-slug>/tentoonstelling/<slug>.ics` + `public/en/museums/<museum-slug>/exhibition/<slug>.ics` exist as **sibling files** (not inside the page directory); **zero new WARN lines**; each starts `BEGIN:VCALENDAR`; UID pattern; DTEND = end+1; the agenda href on the page resolves to the sibling; no museum/other page gains an `.ics`; `public/museumtips.ics` still the weekly file from static; no new JS.
- **Model:** capable mid-tier. **Size:** M. **Depends:** ST-B4.

### ST-B7 — `/museums/` + calendar copy touch-up

- **Scope:** `content/{nl,en}/museums.md` (and calendar/home only if a sentence must mention exhibition pages). Owner-tone, both langs. Point readers at per-museum pages without claiming a map or tickets.
- **Verify:** build 0; NL/EN parity; subscribe URLs unchanged.
- **Model:** composer-2.5. **Size:** S. **Depends:** operator wording if the owner wants a draft; else keep to one factual sentence.

### ST-B8 — Docs

- **Scope:** README route list; AGENTS.md last-verified + curated-file rule + slug fields; one pointer line in `docs/site-plan.md` (do not rewrite the stack essay).
- **Verify:** commands still match; feed URLs listed unchanged.
- **Model:** composer-2.5. **Size:** S. **Depends:** ST-B3–B6 so routes are real.

C1/C2 can interleave after ST-B1 + museum slugs; landing extras before ST-B3 only affects whether sections are empty.

## 3b.8 Risks & mitigations

| Risk | Mitigation |
|---|---|
| Slug churn / 404s | D8 freeze-once in tracker; site never computes production slugs |
| Pipeline overwrites extras | Separate files; AGENTS + publish script must not `cp` them; ST-P verify |
| Pipeline overwrites slugs | Persist in tracker DB, not derived each Thursday |
| Language switcher 404 | Shared `translationKey`; equal AddPage sets NL/EN |
| Card regressions / dead links | Fallback to `.url` and hash links when slug missing; ST-B5 grep |
| Huguette `body>nav` overlay | `class="contentnav"` on new in-page navs |
| Card heading numbers | Existing `custom.css` already suppresses `article h3::before` |
| ICS MIME / GH Pages | `text/calendar` via Hugo; **serving `.ics` from GitHub Pages confirm after first publish** (not verifiable pre-deploy); do not rename weekly feeds |
| Hyphen dot-access / `/en/en/` doubling | D9/D7 fix notes: `index`-only slug lookups + locale-relative URLs; `hugo list all` permalink check; WARN-count gate |
| All-day DTEND off-by-one | Copy the weekly feed convention in ST-B6 |
| Zero-JS leak | `! grep -R '<script' public/` (allow none); 3c is the first allowed exception |
| MORE / Ruurlo city mismatch | D13; city links stay index-hash; don’t require a museum row per venue |
| Stale prices | `verified` + 90-day recheck in C1/C2; unknown > guess |
| Build size (~187×2 HTML + ICS) | Fine for Hugo; still no Node |
| Month-page `path` collision | Namespace `museum/` and `exhibition/` |

## 3b.9 Open questions for the owner

1. Approve D7 URLs (`/museums/<slug>/`, `/en/museums/<slug>/`, `/museums/<museum-slug>/tentoonstelling/<slug>/`, `/en/museums/<museum-slug>/exhibition/<slug>/`; ICS sibling `<slug>.ics`)? 
   → **Owner 2026-09-12: yes — approved** (with one modification — exhibitions nest under their museum: `/museums/<museum>/tentoonstelling/<slug>/`; owner-confirmed; see 3b.4 owner status).
2. Approve D8 (pipeline-frozen slugs; operator-seeded 30 museum slugs) and the “no pages without slug” gate?
   → **Owner 2026-09-12: yes — approved (answered together with Q1).**
3. Any preferred slugs for awkward names (H’ART, Boijmans Depot, De Buitenplaats vs Drents)? Default: operator table, pasted in the PR for a skim.
4. Museum MORE: confirm one page (D13) vs split Gorssel / Ruurlo / Twickel now?
   → **Owner 2026-09-12: covered by D13 approval (one page).**
5. Exhibition pages for shows already ended but still in JSON (D12) — OK that they vanish next drop?
6. Card titles: confirm D10 (internal page first, museum site secondary). Any need for a Museumkaart badge on cards in 3b?
7. ICS: **superseded by owner spec (D7/D11, 2026-09-12) — sibling `<slug>.ics`**; UID `museumtips-<slug>@museumtips.pepperlink.nl`; DTEND = weekly feeds' last-day+1 (verified).
8. Press: is the outlet list in D9 enough, or add/ban specific names? Max links per show (recommend 3)?
9. May C1 fill `lat`/`lon` now (unused) to save a 3c pass, or leave null until 3c?
10. English museum descriptions: human translation of the official NL visit blurb vs short original EN from the museum’s EN site when it exists (recommend: prefer the museum’s own EN page when present)?
11. Should `/museums/` shrink to city + name + one-liner (detail lives on museum pages) or keep today’s in-list exhibition titles?
12. Build gate: fail `hugo` when a row lacks `slug` once ST-P has shipped, or keep skip-and-warn?
13. Publish museum/exhibition pages (and retarget cards to them) **before** C1/C2 extras are collected — most pages show only generated-JSON fields for a while — or gate ST-B5 (card retarget) on a minimum extras threshold (e.g. all 30 museums)?
   → **Owner 2026-09-12: confirmed** — ship pages + card retarget as soon as the code is ready; extras land incrementally (missing sections stay hidden by design). (Q14 governs data scope; this one governs launch timing.)
14. C1/C2 are the largest-effort subtasks (30 museums × ~7 cited facts; up to 187 exhibitions × admission + press). First cut with partial coverage (museum hours+pricing + admission flags; press backfilled later), or hold the phase for full coverage?
   → **Owner 2026-09-12: full coverage.** Refresh cadence for this data becomes a phase-4 design item (owner: “we need to think about how often to refresh this in phase 4”).

## 3b.10 Definition of done

- [ ] Owner approved D7–D16 (and answered §3b.9).
- [ ] Pipeline emits unique frozen `slug` on every museum and exhibition row.
- [ ] Museum pages NL+EN for all 30; exhibition pages NL+EN for every slugged show.
- [ ] Language switcher lands on the counterpart page.
- [ ] Cards + `/museums/` titles link internally; museum `.url` still reachable.
- [ ] Per-show sibling `.ics` downloads (`/museums/<museum-slug>/tentoonstelling/<slug>.ics`, companion pages only, zero build WARNs); weekly feed URLs unchanged.
- [ ] Extras files exist, cited, pipeline-untouched; missing extras do not break the build.
- [ ] Location section reserved; **no** map JS; **no** 3d CTA.
- [ ] i18n key parity; copy uses `’`.
- [ ] `hugo --minify` exits 0; month pages / D3 / home upcoming unchanged in behaviour; `themes/huguette` untouched.

## 3b.11 Verification plan

```sh
hugo --minify
test -f public/index.html -a -f public/en/index.html
test -f public/kalender/index.html -a -f public/en/calendar/index.html
test -d public/kalender/2026-09 -a -d public/en/calendar/2026-09
# museum + exhibition (replace slugs after ST-P):
test -f public/museums/<museum-slug>/index.html
test -f public/en/museums/<museum-slug>/index.html
test -f public/museums/<museum-slug>/tentoonstelling/<show-slug>/index.html
test -f public/en/museums/<museum-slug>/exhibition/<show-slug>/index.html
test -f public/museums/<museum-slug>/tentoonstelling/<show-slug>.ics
test -f public/museumtips.ics -a -f public/closing-soon.ics
! grep -F '1 januari 1' public/kalender/index.html public/museums/index.html
! grep -F '0001-01' public/kalender/index.html
# no JS in this phase:
! grep -R '<script' public/ --include='*.html'
# zero build warnings (proves no global [outputs] leak):
[ "$(hugo --minify 2>&1 | grep -ci '^WARN')" = "0" ]
```

Content-adapter check: `hugo list all` (verified available on the pin) includes `museum/<slug>` and `exhibition/<slug>` for both languages with **correct permalinks** (`/museums/…` + `/en/museums/…`; nested exhibition permalinks `/museums/<museum>/tentoonstelling/…` + `/en/museums/<museum>/exhibition/…` — catches the silent `/en/en/` doubling); `translationKey` pairs visible via language switcher on `hugo server`.

Link check (local preview, real browser — not screenshot-only):

- Home card title → exhibition page → “Bekijk op de museumsite” → official URL; museum name → museum page; city → `/museums/#city`.
- `/museums/` name → museum page; in-list show title → exhibition page; “more in this city” → sibling museum.
- Exhibition: precise countdown; agenda link downloads ICS; EN switch keeps the same slug.
- Month page still lists shows; jump-nav and `contentnav` not covering the title (regression of PR #8).
- Spot one museum with full extras and one with empty extras (graceful omit).
- Visual: classless article layout; no restored `0.1.` numbers on cards; location section has address and no map tiles.

Pinned Hugo **v0.166.0 extended** remains build authority. If a run cannot build locally, say so; operator runs the pod pin before done.

## 3b.12 Rollback

Revert the implementation PR/branch. Curated JSON reverts with git. Tracker slug columns stay (harmless if unused) or operator drops them. Weekly feeds and `gh-pages` stay pipeline-controlled; this phase must not push them.

## 3b.13 Log

- 2026-09-12 · plan cycle: draft `a01d087`; independent review `29671cd`; operator review + fix pass (28 items folded, verified on pinned Hugo v0.166).
- 2026-09-12 · owner answers: Q1/Q2 approved · Q14 = full coverage (refresh cadence → phase-4 item) · Q13 confirmed: ship-when-ready; extras land incrementally.
- 2026-09-12 · owner decisions D7–D14 (D7 amended — final shape: exhibitions **nest under their museum**, `/museums/<museum-slug>/tentoonstelling/<slug>/` + ICS sibling `<slug>.ics`; the intermediate top-level `/museum/` stem idea was retired on owner review; mechanics verified on the pin; D8 "stability, of course"; D9–D14 agreed). Phase-4 backlog: extras-data refresh cadence; upcoming-section sort key → **start date** (owner observation).
- 2026-09-12 · owner request: NL museums section renamed to `/museums/` (Dutch plural; disambiguated by `/en/`); live site keeps the old `musea` path as a redirect (site PR #11, one front-matter edit — links resolve via `GetPage`); all plan paths updated.
- 2026-09-12 · **ST-P done (operator)** — freeze-once slugs live: store `store_slugs.json` (30 museum seeds + 187 exhibition slugs; key `museum|url`, plus `|title` for shared series URLs; ASCII kebab; global dedup with `-2` suffixes). Emitted into `exhibitions.json`. Fixture proofs: second run byte-identical (idempotent), title edit keeps slug, exact-duplicate title gets `-2`. `publish_feeds.py` now executes the emit as a guard before every publish (refuses to publish slugless). Data + store on the operator host; slugged data on `main`.
- 2026-09-12 · **ST-B1 done** (composer-2.5, run 1) — scaffolds `data/museums_info.json` + `data/exhibitions_info.json` (`{}`), README/AGENTS pipeline-vs-curated rules, baseline recorded (`docs/baseline-phase3b.txt`: 192 pages, 0 `<script`, 0 WARN); commit `8d70e680` on `cursor/phase3b-build`, verified on origin.
- 2026-09-12 · **ST-B3 done** (grok-4.6-tier, run 2) — museum pages live on the branch: `add-museum-pages.html` + `layouts/_default/museum-page.html` + `museum-info.html` partial, called from both `_content.gotmpl`; commit `88aa8aa`. Operator verified **on the pin v0.166**: exit 0, **252 pages (127 NL + 125 EN)**, 0 WARN, 0 `<script>`, 0 `/en/en/`, 30+30 museum pages with switcher/hreflang pairs, extras omission + fixture proofs (agent built locally with 0.165 — pin re-verification done by operator).
- 2026-09-12 · **C1 landed** — curated museum extras (30 museums) now `data/museums_info.json` keyed by frozen slug (30/30 validated, 6/6 spot-checks earlier today); commit `ef41301` on main; merged into the build branch (add/add conflict resolved toward the curated data, `8203f71`). Pin build with real extras renders all six sections NL + EN on `/museums/rijksmuseum/`. Notes: RMO `site` URL fix + rebrand observations queued in FINDINGS.md; card-block wording review (owner) still applies to final copy.
- 2026-09-12 · **ST-B4 done** (grok-4.6-tier, run 3) — exhibition pages nest under their museums: countdown-precise states proven (“Opent over 3 dagen”; open-ended clean, no fake end; ended page per D12); related lists self-excluded; extras `{}` → unknown admission, no press heading; fixture NL+EN reverted; cards untouched (B5 next). Operator pin verification: exit 0, **626 pages (314 NL + 312 EN)**, 187+187 exhibition + 30+30 museum pages, 0 WARN/`<script>`/`/en/en/`. Found: singular day-count (“Sluit over 1 dagen”) — fix folded into ST-B7. Commit `f071e0e`.
- 2026-09-12 · **ST-B5 done** (composer-2.5, run 4) — cards retargeted: exhibition titles → exhibition pages, museum names → museum pages, “Bekijk op de museumsite” keeps the external `.url`; no-slug fallback proven; full Phase-2 QA battery green. Operator pin verification: 626 pages, 0 WARN/`<script>`/`/en/en/`. Commit `c777f94`.
- 2026-09-12 · **ST-B6 done** (grok-4.6-tier, run 5) — per-show `.ics`: `[outputFormats.icsfile]` (per-page only), companion pages, `exhibition-ics.icsfile.ics` template, agenda link on detail pages. Operator pin verification: **990 pages (496+494)**, 364 companions, **weekly feeds md5 byte-identical**, open-ended shows DTSTART-only, 5 no-date shows skipped per D11, sitemap clean. Commit `d348129`.
- 2026-09-12 · **ST-B7 done** (composer-2.5, run 6) — museums-intro copy NL+EN + singular day-count fix (`opens_tomorrow`/`closes_tomorrow`; “Sluit morgen” proven on real data, i18n 95/95 parity); calendar/home untouched per scope. Operator pin verification: 990 pages, feeds unchanged. Commit `48f8a3d` (rebased cleanly over ST-B6 after a Mac-lane push outage — see token note below).
- 2026-09-12 · **C2 landed** — `data/exhibitions_info.json`: admission + press for **187/187 shows** (172 included / 13 supplement / 1 not_covered / 1 unknown; 92 press links on 54 shows); all press URLs resolve, admission sources re-checked; LC/DVHN 403-walled cases recorded honestly in failures. Commit `ae3128b` on main; merged into the build branch. Milestone log for tonight: ST-B5…B7 + C1/C2 landed; B8 (docs) in flight; GitHub token rotation handled (org + personal tokens wired; pod pushes restored mid-run; Mac-lane push creds repaired same evening).

- 2026-09-12 · **ST-B8 done + phase 3b build COMPLETE** (composer-2.5, run 7) — docs: routes + agent rules refreshed (README/AGENTS/site-plan); recovered via the Mac lane after credential repair, rebased cleanly. **Endgame battery green on the pin**: 990 pages (496/494), 0 WARN/`<script>`, weekly feeds byte-identical, §3b.11 greps zero, permalink audit exactly 800 rows (436 pages + 364 ICS); real-browser link check NL+EN (countdown “Sluit morgen”, surcharge line, press links, agenda `.ics`). Commit `b264404`. **PR #12 opened** for owner review/merge. Commit `ba16976` chain.

- 2026-09-12 · **PR #12 MERGED → PHASE 3B LIVE** — main `4628f8d`; site published (`deploy: site build from main @4628f8d`); live-verified: home / museums index / museum page (C1 extras) / exhibition NL+EN / surcharge show (“Sluit morgen”, toeslag, Pers) / per-show `.ics` (VCALENDAR, UID ok) / `/musea/` — all 200; weekly feeds byte-identical (md5 match). Phase 3b ships: museum + exhibition detail pages, per-show calendar files, curated data for 30 museums + 187 shows.*(Append during the build, one bullet per run.)*

---

# PLAN — Phase 3c: Museum maps + calendar heatmap (plan)

Status: **draft** (2026-09-12) — owner answers §3c.5 before any build run. This section is a plan only; it authorizes no implementation.

Phase 2 and phase 3b above remain the implementation record. Phase 3c activates the location interface reserved by 3b and adds a closing-urgency treatment to the static calendars.

## 3c.0 Agent ground rules

Follow `AGENTS.md` (outranks defaults). In force: Conventional Commits; `diane/…` or `cursor/…` branches; **owner merges**; never push `main` or `gh-pages` except through the publish scripts; never change `/museumtips.ics` or `/closing-soon.ics`; never hand-edit generated `data/exhibitions.json` or any generated ICS; never let the pipeline write curated `data/museums_info.json` / `data/exhibitions_info.json`; use pipeline-frozen slugs; keep NL + EN in sync; no Node or asset build step; Hugo **v0.166.0 extended** is authoritative; never edit `themes/huguette`.

Leaflet is the owner-approved **only deliberate JavaScript exception**. The exception is restricted to map-ready museum detail pages. Calendar heat is build-time HTML + CSS and must add no JavaScript. Site-copy punctuation remains literal `’` in `content/` and `i18n/`.

Planning-cycle boundary: this branch commits and pushes **only `PLAN.md`**. No phase-3c implementation file is authorized until the owner answers §3c.5.

## 3c.1 Goals

1. Turn the inert `section#location > #map` slot on each museum detail page into a Leaflet map with one venue marker and a name/address popup.
2. Vendor a pinned stable Leaflet release under repo `static/`; load its CSS, JS, and the one small site initializer only on museum pages that have a complete coordinate pair.
3. Add numeric `lat` / `lon` plus a coordinate source to all **30** curated museum records, without changing generated-data ownership.
4. Give running shows on the NL + EN calendar index and static month pages a light→dark blue closing-urgency heat treatment.
5. Preserve the homepage “Binnenkort te zien” / “Opening soon” order by **start date**.

## 3c.2 Non-goals

- Maps appear on museum detail pages and the museums index only (owner Q5, 2026-09-13). No maps on exhibition pages, calendar, home, or about page.
- No geolocation, directions API, route planning, clustering, multi-layer control, search, tracking code, analytics, service worker, map iframe, or JavaScript framework.
- No CDN-loaded library. The Leaflet runtime is same-origin and vendored; only map tiles are requested from the owner-approved tile provider.
- No Node/npm, bundling, transpiling, minifying, package lock, Hugo Pipes JS build, or theme-submodule edit.
- No heatmap day-grid library and no JS heat calculation. “Heatmap” here means server-rendered urgency classes on exhibition cards, not a geographic heat layer.
- No change to countdown wording, ended-show policy, month-overlap logic, frozen URLs/slugs, feeds, deployment plumbing, or curated exhibition extras.
- No copy rename from “Musea” to “Museums” or any other wording change; the parked display-copy request remains parked.
- No speculative coordinate for a secondary venue. Museum MORE follows the owner’s Q8 answer.

## 3c.3 Recon and mechanically verified baseline

Verified 2026-09-12 in this checkout:

- `layouts/partials/museum-info.html` already renders address inside `section#location` and an inert `<div id="map" hidden></div>`. `layouts/_default/museum-page.html` receives the frozen museum slug in `.Params.slug`; generated pages have `type = "museum-page"`.
- `data/museums_info.json` has exactly 30 frozen-slug keys and 30 addresses, but currently has **zero** `lat` keys, zero `lon` keys, and zero complete coordinate pairs. The phase-3b schema reserved the fields; they were not populated.
- `layouts/partials/head.html` is the one site-owned head partial. It currently emits CSS only. `layouts/_default/baseof.html` has no script block or page-specific asset hook.
- Calendars are `layouts/_default/calendar.html` and `calendar-month.html`; both render cards through `layouts/partials/exhibition.html`. The card partial is also shared by home, museum, and exhibition pages, so heat scope must not be implemented as an unconditional card style.
- Existing countdown boundaries are day 0, days 1–6, 7–13, 14–20, and 21–30. The owner approved a **four-band heat step (2026-09-13): 0–10 / 11–25 / 26–50 / 50+ days to close**, applied on top of the same integer-day calculation as `countdown.html` so color and label cannot disagree in this phase.
- The current homepage already does `sort $upcoming "start"` in `layouts/index.html`; the museum-page upcoming list also sorts by `start`. The reported end-date bug is not present at this branch tip. Phase 3c therefore adds a regression assertion, not a drive-by edit. If the implementation baseline regresses **and** Q2 makes `layouts/index.html` a touched file, correct it in that run; otherwise do not touch the file.
- After initializing the pinned Huguette submodule, local Hugo **v0.165.0 extended** built successfully: 496 NL pages, 494 EN pages, 0 WARN lines, and 0 HTML `<script>` tags. This machine is one minor version behind the authoritative **v0.166.0 extended** pin; the operator re-runs every build/visual gate on the pin.
- Scratch Hugo proof on local v0.165.0: a `.Type == "museum-page"` head condition emitted local Leaflet CSS + two deferred local scripts on the museum page (2 script tags), while an about page emitted 0; `data-lat` / `data-lon` rendered as numeric attributes. This proves the proposed plain-Hugo conditional mechanism, not the final implementation.
- Leaflet’s official download page still identifies **1.9.4** as stable and 2.0.0-alpha.1 as prerelease. The official `leaflet.zip` fetched from GitHub release `v1.9.4` had SHA-256 `aaec1d5c3239a613a53e996087629aca1483cb2f0438b11b8a335c6cede4c16b`.

## 3c.4 Proposed implementation

### Map exception surface

Use `layouts/partials/museum-map-ready.html` as the one shared Hugo predicate. It receives a dict containing the current page and curated info; use it from both the head and location markup:

- page type is exactly `museum-page`;
- head lookup is `index hugo.Data.museums_info .Params.slug` (frozen slug; no `urlize`); `museum-page.html` passes page + generated museum + curated info into `museum-info.html`, so the same predicate has the same inputs there;
- `lat` and `lon` both exist and are genuine non-null numbers (explicit JSON `null` rejected, strings rejected, booleans rejected), form a complete pair, and are within the approved NL bounds. **Verified idiom (scratch fixture, pin v0.166.0, 2026-09-13):** `isset` returns true for an explicit JSON `null` and must NOT be used — use the nested guard below. Fixture verdicts on v0.166.0: a float pair is ready; `"lon": null`, a missing key, and string values are all not-ready, with the build staying green:

~~~go-html-template
{{ $ready := false }}
{{ if and (ne $lat nil) (ne $lon nil) }}{{ if and (eq (printf "%T" $lat) "float64") (eq (printf "%T" $lon) "float64") }}{{ if and (ge $lat 50.7) (le $lat 53.65) (ge $lon 3.2) (le $lon 7.25) }}{{ $ready = true }}{{ end }}{{ end }}{{ end }}
~~~

When true:

- `head.html` emits CSS in the order classless → Leaflet → custom, then deferred same-origin Leaflet JS followed by deferred `museum-map.js`;
- `museum-info.html` emits escaped `data-lat`, `data-lon`, generated museum name, and curated address on a hidden `#map`, plus a hidden failure fallback;
- `museum-map.js` initializes exactly one map, one tile layer, one marker, and one popup. Build popup DOM with `textContent`, not untrusted `innerHTML`; set `referrerPolicy: 'strict-origin-when-cross-origin'` in the `L.tileLayer` options so the OSMF referrer requirement holds even if site headers are ever hardened.
- **Museums index overview map (owner Q5, 2026-09-13):** one map on `/museums/` and `/en/museums/` when at least one museum is map-ready — every ready museum as a marker, popups built from DOM nodes (`textContent`) with the museum name + an internal link to its detail page in the current language, `fitBounds` over the ready set, no clustering at this scale. When zero museums are ready, the index renders no map and no scripts. `museum-map.js` handles both modes — the vendored-file allowlist stays at exactly two JS files.

When false: no Leaflet CSS, no script tags, no tile request; the address remains visible and the localized empty-state text replaces the hidden map. For a ready map, JS must unhide the container immediately before `L.map` so Leaflet receives real dimensions; wrap initialization in `try`/`catch`, and on failure re-hide the map and reveal the same empty-state text. Without JS, the address still remains.

No inline script and no event-handler attribute are allowed. `static/js/museum-map.js` is the only site-written JS. `static/vendor/leaflet/1.9.4/leaflet.js` is the only third-party JS.

### Exact vendored Leaflet surface

Recommend Leaflet **1.9.4**, copied from the official release archive without rebuilding:

```text
static/vendor/leaflet/1.9.4/
├── LICENSE
├── leaflet.css
├── leaflet.js
└── images/
    ├── layers.png
    ├── layers-2x.png
    ├── marker-icon.png
    ├── marker-icon-2x.png
    └── marker-shadow.png
```

Keep the two layer-control images because unmodified upstream `leaflet.css` references them, even though phase 3c adds no layer control. Do not vendor `leaflet-src*.js`, source maps, npm metadata, or the full source tree. `LICENSE` is the BSD-2-Clause text from the `v1.9.4` tag — it is **not part of `leaflet.zip`**; fetch it separately: `curl -fsSL https://raw.githubusercontent.com/Leaflet/Leaflet/v1.9.4/LICENSE -o static/vendor/leaflet/1.9.4/LICENSE` (verified 2026-09-13: HTTP 200, BSD-2-Clause, 1,395 bytes). The distributed `leaflet.js` keeps a `//# sourceMappingURL=leaflet.js.map` comment; since `.map` files are deliberately not vendored, devtools may log a benign same-origin 404 — expected, not a defect. Add `static/js/museum-map.js` separately; it is project code, not vendor code.

### Coordinate collection and validation

For every curated museum slug:

1. Prefer coordinates explicitly published by the museum on its official visit/contact page or an official embedded map.
2. Otherwise use the OpenStreetMap venue object/entrance and verify its name and position against the existing official street address. Store a durable OSM object URL, not a transient search-result URL.
3. Pin the visitor venue/main entrance, not the city centroid, municipality, back office, or a similarly named institution. Visually inspect the point over the venue footprint/entrance.
4. Add numeric `lat` and `lon` (not quoted strings; recommend 6 decimal places) and one `sources[]` entry with `"fact": "coordinates"` and the official or OSM URL. Update `verified` to the actual collection date. Do not rewrite unrelated curated prose.
5. Validate the broad Netherlands guardrails `50.70 ≤ lat ≤ 53.65`, `3.20 ≤ lon ≤ 7.25`; bounds catch swaps/typos but do not prove venue plausibility.
6. Operator independently spot-checks at least six geographically distributed records against official addresses: Amsterdam, Rotterdam, Den Haag/Wassenaar, north, east/central, and south. All 30 still receive the collector’s venue-level visual check.

Missing/invalid one-sided pairs are treated as missing, never coerced to `0`, and never produce a map.

### Calendar heat rendering

Add `layouts/partials/calendar-exhibition.html` as the calendar-only wrapper that computes an urgency class and wraps the unchanged output of `exhibition.html` in a `<div class="closing-heat-N">` (its `<article>` has no class hook; the wrapper therefore carries its own padding/box styling — `<article>` has no card box to inherit). Call it only from `calendar.html` and `calendar-month.html`. This avoids changing cards on home/museum/exhibition pages.

Eligible: show has started, has a valid end date, and is not ended. Open-ended, upcoming, and ended shows remain neutral. Proposed classes and exact backgrounds:

| Days until close | Existing label | Class | Background |
|---:|---|---|---|
| 50+ | months away | `closing-heat-1` | `#eff6ff` |
| 26–50 | 4–7 weeks | `closing-heat-2` | `#dbeafe` |
| 11–25 | 2–4 weeks | `closing-heat-3` | `#bfdbfe` |
| 0–10 | last 10 days (day 0 included) | `closing-heat-4` | `#60a5fa` |

Use foreground/link color `#172554` within all four classes (links remain underlined). Owner-approved four bands; measured `#172554` contrast across the four backgrounds ranges 13.50:1 to 5.78:1 (all above WCAG AA normal text). The site-default body text color `#433` on the darkest band measures 4.67:1 — an AA pass with a thin margin; re-check if the palette or text color ever changes. Add a non-color cue by retaining the existing bold countdown label; no new legend/i18n is required.

Do not shade month jump-nav: a month can contain mixed urgencies, so one shade would be false precision. Do not shade “Binnenkort te zien / Opening soon”: pre-opening shows are ineligible for closing urgency.

## 3c.5 DECISIONS FOR OWNER

Answer every numbered question in chat before ST-3c-1 begins.

1. **Closing scale boundaries?**
   **Owner answer (2026-09-13): four custom bands — 0–10 / 11–25 / 26–50 / 50+ days to close** (closer = darker; day 0 inside the darkest band). Palette updated in §3c.4 with recomputed contrast.
   *(Original recommendation: 21–30 / 14–20 / 7–13 / 1–6 / 0 mirroring the countdown buckets — superseded.)*

2. **Heat scope?**
   **Owner answer (2026-09-13): calendar index + all month pages, NL + EN** (= recommendation). No jump-nav, no homepage cards.

3. **Tile source and attribution?** *(Owner answer 2026-09-13: OSM Standard — recommendation accepted; alternatives not chosen.)*
   **Recommendation:** OpenStreetMap Standard raster tiles at `https://tile.openstreetmap.org/{z}/{x}/{y}.png`, `maxZoom: 19`, with always-visible `© OpenStreetMap contributors` linked to `https://www.openstreetmap.org/copyright`. It needs no account and is proportionate to one small map per museum page, but is best-effort/no-SLA and sends the page referrer to OSM. Follow OSMF’s tile policy: browser-driven views only, normal caching, no prefetch/offline/bulk download, no referrer suppression. Keep the URL in one JS constant so it is replaceable.
   **Alternatives:** owner-supplied commercial OSM tile provider/API key and terms; self-hosted tiles (largest operational burden); no basemap, marker/address only.

4. **Map interaction and dimensions?**
   **Owner answer (2026-09-13): as proposed, with `scrollWheelZoom` ON** (overrode the recommendation). Overview: height `22rem` (`max-width: 100%`), initial zoom 16, `minZoom: 5`, `maxZoom: 19`, buttons/drag/keyboard + wheel zoom on; no auto-open popup; wheel over the map zooms it (accepted), page scroll unaffected elsewhere.

5. **Maps on other pages?**
   **Owner answer (2026-09-13): museum detail pages + a museums-index overview map** (NL + EN; see the new bullet in §3c.4). Exhibition pages, calendar, home, about: no maps. The JS allowlist and expected counts below are updated accordingly.

6. **Leaflet version?**
   **Recommendation:** stable 1.9.4 with the exact runtime asset list in §3c.4; 2.0 remains prerelease and changes module/global behavior.
   **Alternatives:** owner-approved 2.0 prerelease (higher migration/test risk); defer until 2.0 stable.

7. **Missing-coordinate wording?**
   **Recommendation:** key `map_unavailable`: NL `Kaart niet beschikbaar; gebruik het adres hierboven.` / EN `Map unavailable; use the address above.` It is direct and leaves the address as the fallback.
   **Alternatives:** shorter `Kaart niet beschikbaar.` / `Map unavailable.`; silently omit the map (least helpful and harder to QA).

8. **Museum MORE multi-venue behavior?**
   **Recommendation:** one marker at the primary Gorssel venue, matching phase-3b D13’s one museum page and current address; mention the primary venue in the popup only if already present in curated data.
   **Alternatives:** multiple pins (requires a coordinate-array schema and popup labels); split venue pages (reopens frozen routing/data design); no map for MORE.

If the owner selects an alternative that changes a surface or expected count (especially Q2 or Q8), update the affected scope and exact QA expectations in this plan before implementation; do not improvise around a stale acceptance command. *(Executed for Q1/Q4/Q5 — owner answers folded 2026-09-13; scope + counts updated.)*

## 3c.6 Ordered one-run subtasks

All runs are serialized because ST-3c-1 through ST-3c-3 edit the same curated file. Stop on conflict with §3c.5. Never use a generated-data edit as a fixture. ST-3c-6 is file-disjoint from ST-3c-4/5 and may run before or in parallel with them if useful; keep the numeric order otherwise.

### ST-3c-1 — Coordinates batch A (10)

- **Model:** `composer-2.5` · **Size:** S · **Depends:** —
- **Scope:** only `data/museums_info.json`: `rijksmuseum`, `van-gogh-museum`, `stedelijk-museum`, `h-art-museum`, `huis-marseille`, `foam`, `museum-boijmans-van-beuningen`, `kunsthal`, `nederlands-fotomuseum`, `museum-more`.
- **Work:** collect/verify per §3c.4; add pairs + coordinate source; Q8 governs MORE.
- **Verify:**

```sh
python3 - <<'PY'
import json
import math
d=json.load(open("data/museums_info.json"))
batch="""rijksmuseum van-gogh-museum stedelijk-museum h-art-museum huis-marseille foam museum-boijmans-van-beuningen kunsthal nederlands-fotomuseum museum-more""".split()
for slug in batch:
    v=d[slug]; lat=v.get("lat"); lon=v.get("lon")
    assert type(lat) in (int,float) and type(lon) in (int,float), slug
    assert math.isfinite(lat) and math.isfinite(lon), slug
    assert 50.70 <= lat <= 53.65 and 3.20 <= lon <= 7.25, slug
    assert any(s.get("fact")=="coordinates" and s.get("url","").startswith("https://") for s in v["sources"]), slug
print("batch A coordinate pairs:", len(batch))
PY
hugo --minify
git diff --name-only
# expect only data/museums_info.json
```

- **Human gate:** open all ten source points; compare names/footprints to official addresses.
- **Commit:** `feat(data): add first museum coordinate batch`

### ST-3c-2 — Coordinates batch B (10)

- **Model:** `composer-2.5` · **Size:** S · **Depends:** ST-3c-1
- **Scope:** only `data/museums_info.json`: `kunstmuseum-den-haag`, `fotomuseum-den-haag`, `voorlinden`, `singer-laren`, `teylers-museum`, `centraal-museum`, `museum-de-fundatie`, `museum-arnhem`, `kroller-muller-museum`, `museum-kranenburgh`.
- **Work:** same protocol; do not touch batch A except a documented correction.
- **Verify:**

```sh
python3 - <<'PY'
import json, math
d=json.load(open("data/museums_info.json"))
batch="""kunstmuseum-den-haag fotomuseum-den-haag voorlinden singer-laren teylers-museum centraal-museum museum-de-fundatie museum-arnhem kroller-muller-museum museum-kranenburgh""".split()
for slug in batch:
    v=d[slug]; lat=v.get("lat"); lon=v.get("lon")
    assert type(lat) in (int,float) and type(lon) in (int,float), slug
    assert math.isfinite(lat) and math.isfinite(lon), slug
    assert 50.70 <= lat <= 53.65 and 3.20 <= lon <= 7.25, slug
    assert any(s.get("fact")=="coordinates" and s.get("url","").startswith("https://") for s in v["sources"]), slug
print("batch B coordinate pairs:", len(batch))
PY
hugo --minify
git diff --name-only
# expect only data/museums_info.json
```

- **Human gate:** source/official-address check for all ten.
- **Commit:** `feat(data): add second museum coordinate batch`

### ST-3c-3 — Coordinates batch C + complete audit (10)

- **Model:** `composer-2.5` · **Size:** S · **Depends:** ST-3c-2
- **Scope:** only `data/museums_info.json`: `drents-museum`, `groninger-museum`, `fries-museum`, `de-buitenplaats`, `museum-volkenkunde`, `rijksmuseum-van-oudheden`, `frans-hals-museum`, `de-pont-museum`, `van-abbemuseum`, `bonnefantenmuseum`.
- **Work:** fill batch C, then audit all 30 pairs/sources and six geographically distributed records.
- **Verify:**

```sh
python3 - <<'PY'
import json
import math
generated=json.load(open("data/exhibitions.json"))
info=json.load(open("data/museums_info.json"))
slugs={m["slug"] for m in generated["museums"]}
assert len(slugs)==30 and set(info)==slugs
for slug,v in info.items():
    lat=v.get("lat"); lon=v.get("lon")
    assert type(lat) in (int,float) and type(lon) in (int,float), slug
    assert math.isfinite(lat) and math.isfinite(lon), slug
    assert 50.70 <= lat <= 53.65 and 3.20 <= lon <= 7.25, slug
    sources=[s for s in v.get("sources",[]) if s.get("fact")=="coordinates"]
    assert sources and all(s.get("url","").startswith("https://") for s in sources), slug
print("validated coordinate pairs:", len(info))
PY
hugo --minify
git diff --name-only
# expect only data/museums_info.json
```

- **Commit:** `feat(data): complete museum coordinates`

### ST-3c-4 — Vendor Leaflet 1.9.4

- **Model:** `composer-2.5` · **Size:** S · **Depends:** —
- **Scope:** the exact `static/vendor/leaflet/1.9.4/` files listed in §3c.4 only. No template references yet; no theme edit.
- **Work:** fetch official release zip; verify archive hash; copy unmodified runtime distribution + tagged license (`curl -fsSL https://raw.githubusercontent.com/Leaflet/Leaflet/v1.9.4/LICENSE -o static/vendor/leaflet/1.9.4/LICENSE` — the zip contains no LICENSE; verified 2026-09-13); record version/source in the commit body.
- **Verify:**

```sh
curl -fsSL https://github.com/Leaflet/Leaflet/releases/download/v1.9.4/leaflet.zip \
  -o /tmp/leaflet-1.9.4.zip
test "$(shasum -a 256 /tmp/leaflet-1.9.4.zip | awk '{print $1}')" = \
  aaec1d5c3239a613a53e996087629aca1483cb2f0438b11b8a335c6cede4c16b
test -f static/vendor/leaflet/1.9.4/leaflet.css
test -f static/vendor/leaflet/1.9.4/leaflet.js
test -f static/vendor/leaflet/1.9.4/LICENSE
test "$(find static/vendor/leaflet/1.9.4/images -type f | wc -l | tr -d ' ')" = 5
test "$(find static/vendor/leaflet/1.9.4 -type f | wc -l | tr -d ' ')" = 8
! find static/vendor/leaflet/1.9.4 -type f \( -name '*src*' -o -name '*.map' \) | grep .
hugo --minify
! grep -R '<script' public --include='*.html'
```

- **Commit:** `chore(vendor): add Leaflet 1.9.4`

### ST-3c-5 — Conditional museum maps

- **Model:** capable mid-tier (`cursor-grok-4.6-medium`-class) · **Size:** M · **Depends:** ST-3c-4
- **Scope:** `layouts/_default/museum-page.html`, `layouts/partials/head.html`, `layouts/partials/museum-info.html`, the museums-index template (overview map; exact path identified during implementation), new `layouts/partials/museum-map-ready.html`, `static/js/museum-map.js`, `static/css/custom.css`, `i18n/nl.toml`, `i18n/en.toml`. Never `baseof` unless the proven deferred-head approach fails on the pin.
- **Work:** implement Q3–Q8 and §3c.4. Change the current `museum-info.html` call to pass page + generated museum + curated info explicitly; popup = generated museum name + curated address. Keep address server-rendered; no external HTML injection.
- **Verify:**

```sh
set -o pipefail
hugo --minify 2>&1 | tee /tmp/phase3c-map-build.log
test "$(grep -ci '^WARN' /tmp/phase3c-map-build.log)" = 0
M=$(python3 -c "import json;d=json.load(open('data/museums_info.json'));print(sum(1 for v in d.values() if v.get('lat') is not None and v.get('lon') is not None))")
if [ "$M" -ge 1 ]; then EXPECTED_MAP_PAGES=$(( M*2 + 2 )); INDEX_MAP_PAGES=2; else EXPECTED_MAP_PAGES=0; INDEX_MAP_PAGES=0; fi
# Owner Q5: M ready museums x 2 languages + 2 museums-index pages when M >= 1.
EXPECTED_SCRIPT_TAGS=$((EXPECTED_MAP_PAGES * 2))
museum_pages="$(
  find public/museums -mindepth 2 -maxdepth 2 -type f -name index.html
  find public/en/museums -mindepth 2 -maxdepth 2 -type f -name index.html
)"
# There are always 30×2 museum detail pages; Q8 changes map readiness, not routes.
test "$(printf '%s\n' "$museum_pages" | grep -c .)" = 60
grep -Rl '<script' public --include='*.html' | sort > /tmp/phase3c-script-pages
test "$(wc -l < /tmp/phase3c-script-pages | tr -d ' ')" = "$EXPECTED_MAP_PAGES"
test "$(grep -Ec '^public/(en/)?museums/[^/]+/index\.html$' /tmp/phase3c-script-pages)" = \
  "$(( M*2 ))"
test "$(grep -Ec '^public/(en/)?museums/index\.html$' /tmp/phase3c-script-pages)" = \
  "$INDEX_MAP_PAGES"
test "$(grep -Roh '<script' public --include='*.html' | wc -l | tr -d ' ')" = "$EXPECTED_SCRIPT_TAGS"
! grep -RE "<script[^>]*src=[\"']?https?://" public --include='*.html'
! grep -R 'javascript:\| on[a-zA-Z][a-zA-Z]*=' public --include='*.html'
test "$(git ls-files '*.js' | sort | tr '\n' ' ')" = \
  "static/js/museum-map.js static/vendor/leaflet/1.9.4/leaflet.js "
python3 - <<'PY'
import re
def keys(path):
    return set(re.findall(r"^\[([^]]+)\]\s*$", open(path).read(), re.M))
nl=keys("i18n/nl.toml"); en=keys("i18n/en.toml")
assert nl==en, (sorted(nl-en), sorted(en-nl))
print("i18n key parity:", len(nl))
PY
test -f public/museumtips.ics -a -f public/closing-soon.ics
```

- **Browser gate:** §3c.8 map checks in both languages, including marker placement and popup activation.
- **Commit:** `feat(map): add museum detail maps`

### ST-3c-6 — Calendar closing heat

- **Model:** `composer-2.5` · **Size:** M · **Depends:** —
- **Scope:** new `layouts/partials/calendar-exhibition.html`, `layouts/_default/calendar.html`, `layouts/_default/calendar-month.html`, `static/css/custom.css`. `layouts/index.html` only if Q2 explicitly includes a homepage surface; copy/i18n should remain untouched.
- **Work:** implement Q1/Q2. Keep `exhibition.html` output unchanged and preserve D3 ended collapse/month overlap.
- **Verify:**

```sh
set -o pipefail
hugo --clock 2026-09-12T12:00:00+02:00 --minify 2>&1 | tee /tmp/phase3c-heat-build.log
test "$(grep -ci '^WARN' /tmp/phase3c-heat-build.log)" = 0
for class in closing-heat-1 closing-heat-2 closing-heat-3 closing-heat-4; do
  grep -R "$class" public/kalender public/en/calendar --include='*.html' >/dev/null
done
grep -Rl 'closing-heat-' public --include='*.html' | sort > /tmp/phase3c-heat-pages
test "$(grep -Ec '^public/(kalender|en/calendar)/' /tmp/phase3c-heat-pages)" = \
  "$(grep -c . /tmp/phase3c-heat-pages)"
! grep -R '<script' public/kalender public/en/calendar --include='*.html'
grep -F '{{ $upcoming = sort $upcoming "start" }}' layouts/index.html
! grep -F 'sort $upcoming "end"' layouts/index.html
! grep -F '1 januari 1' public/kalender/index.html public/museums/index.html
! grep -F '1 January 1' public/en/calendar/index.html public/en/museums/index.html
! grep -F '0001-01' public/kalender/index.html public/en/calendar/index.html
test -f public/museumtips.ics -a -f public/closing-soon.ics
hugo --clock 2026-09-13T00:00:00+02:00 --minify \
  --destination /tmp/phase3c-day0
grep -R 'closing-heat-4' /tmp/phase3c-day0/kalender \
  /tmp/phase3c-day0/en/calendar --include='*.html' >/dev/null
```

Day-0 also remains a browser gate using `hugo server --clock 2026-09-13T00:00:00+02:00`; synthetic fixture data, if refreshed data lacks a day-0 show, lives only in a disposable copy and is never committed.

- **Commit:** `feat(calendar): add closing urgency heat`

### ST-3c-7 — Docs + final audit

- **Model:** `composer-2.5` · **Size:** S · **Depends:** ST-3c-1…6
- **Scope:** `README.md`, `AGENTS.md`, `docs/site-plan.md`; update both-language route descriptions only if necessary. Do not change visitor display copy.
- **Work:** document the exception, vendor pin/provenance, external tile/attribution dependency, conditional page scope, coordinate ownership, and phase pointer. Run full QA.
- **Verify:** §3c.8 mechanical battery + real-browser checklist; set `PHASE_START=$(git merge-base HEAD origin/main)`, then `git diff --name-only "$PHASE_START"...HEAD` must match approved 3c files; generated data/feeds/theme absent.
- **Commit:** `docs(map): document phase 3c exception`

## 3c.7 Acceptance checklist

- [ ] Owner answered Q1–Q8 before implementation.
- [ ] All 30 curated museum records have plausible numeric coordinate pairs, coordinate sources, and current verification dates; generated JSON and curated exhibition info remain untouched.
- [ ] NL + EN museum detail pages show the same venue point, visible attribution, one marker, and a usable popup.
- [ ] Missing or invalid coordinates produce localized text + address, no map assets, and no tile request.
- [ ] Leaflet 1.9.4 runtime is vendored exactly; no CDN library, Node tooling, source maps, or theme edit.
- [ ] Only map-ready museum detail HTML contains scripts: exactly Leaflet + `museum-map.js`, both same-origin/deferred; no inline JS/event handlers/`javascript:` URLs.
- [ ] Calendar index + month pages show the four owner-approved bands for eligible running shows (0–10 darkest, 50+ lightest; day 0 inside the darkest band); upcoming/open-ended/ended are neutral; text still communicates status without color.
- [ ] Museums index (NL+EN) shows the overview map with every ready museum as a marker; popups carry name + internal link; the zero-ready state renders no map and no scripts.
- [ ] “Binnenkort te zien” / “Opening soon” remains sorted ascending by `start`; display copy stays “Musea”.
- [ ] NL + EN calendar behavior matches; month navigation, D3 ended policy, phase-3b detail links/ICS, and frozen slugs regress cleanly.
- [ ] `hugo --minify` on pinned v0.166.0 exits 0 with 0 WARN; weekly feed files/URLs and deployment plumbing are unchanged.

## 3c.8 QA battery

### Mechanical (run on pinned Hugo v0.166.0 extended)

```sh
set -o pipefail
hugo version
# must report v0.166.0+extended
hugo --minify 2>&1 | tee /tmp/phase3c-final-build.log
test "$(grep -ci '^WARN' /tmp/phase3c-final-build.log)" = 0
test -f public/index.html -a -f public/en/index.html
test -f public/kalender/index.html -a -f public/en/calendar/index.html
test -f public/museums/rijksmuseum/index.html
test -f public/en/museums/rijksmuseum/index.html
test -f public/museumtips.ics -a -f public/closing-soon.ics

# Complete coordinate/schema audit: run the Python block from ST-3c-3.

# Auditable JS allowlist.
M=$(python3 -c "import json;d=json.load(open('data/museums_info.json'));print(sum(1 for v in d.values() if v.get('lat') is not None and v.get('lon') is not None))")
if [ "$M" -ge 1 ]; then EXPECTED_MAP_PAGES=$(( M*2 + 2 )); INDEX_MAP_PAGES=2; else EXPECTED_MAP_PAGES=0; INDEX_MAP_PAGES=0; fi
EXPECTED_SCRIPT_TAGS=$((EXPECTED_MAP_PAGES * 2))
grep -Rl '<script' public --include='*.html' | sort > /tmp/phase3c-script-pages
test "$(wc -l < /tmp/phase3c-script-pages | tr -d ' ')" = "$EXPECTED_MAP_PAGES"
test "$(grep -Ec '^public/(en/)?museums/[^/]+/index\.html$' /tmp/phase3c-script-pages)" = \
  "$(( M*2 ))"
test "$(grep -Ec '^public/(en/)?museums/index\.html$' /tmp/phase3c-script-pages)" = \
  "$INDEX_MAP_PAGES"
test "$(grep -Roh '<script' public --include='*.html' | wc -l | tr -d ' ')" = "$EXPECTED_SCRIPT_TAGS"
! grep -RE "<script[^>]*src=[\"']?https?://" public --include='*.html'
! grep -R 'javascript:\| on[a-zA-Z][a-zA-Z]*=' public --include='*.html'
test "$(git ls-files '*.js' | sort | tr '\n' ' ')" = \
  "static/js/museum-map.js static/vendor/leaflet/1.9.4/leaflet.js "

# Heat + phase-2 regressions.
for class in closing-heat-1 closing-heat-2 closing-heat-3 closing-heat-4; do
  grep -R "$class" public/kalender public/en/calendar --include='*.html' >/dev/null
done
grep -Rl 'closing-heat-' public --include='*.html' | sort > /tmp/phase3c-heat-pages
test "$(grep -Ec '^public/(kalender|en/calendar)/' /tmp/phase3c-heat-pages)" = \
  "$(grep -c . /tmp/phase3c-heat-pages)"
grep -F '{{ $upcoming = sort $upcoming "start" }}' layouts/index.html
! grep -F 'sort $upcoming "end"' layouts/index.html
! grep -F '1 januari 1' public/kalender/index.html public/museums/index.html
! grep -F '1 January 1' public/en/calendar/index.html public/en/museums/index.html
! grep -F '0001-01' public/kalender/index.html public/en/calendar/index.html
hugo --clock 2026-09-13T00:00:00+02:00 --minify \
  --destination /tmp/phase3c-day0
grep -R 'closing-heat-4' /tmp/phase3c-day0/kalender \
  /tmp/phase3c-day0/en/calendar --include='*.html' >/dev/null

# NL/EN i18n key parity.
python3 - <<'PY'
import re
def keys(path):
    return set(re.findall(r"^\[([^]]+)\]\s*$", open(path).read(), re.M))
nl=keys("i18n/nl.toml"); en=keys("i18n/en.toml")
assert nl==en, (sorted(nl-en), sorted(en-nl))
print("i18n key parity:", len(nl))
PY

# Protected artifacts and paths.
PHASE_START=$(git merge-base HEAD origin/main)
git diff --exit-code "$PHASE_START" -- data/exhibitions.json data/exhibitions_info.json \
  museumtips.ics closing-soon.ics static/museumtips.ics static/closing-soon.ics \
  themes/huguette CNAME static/CNAME
```

For a deliberate missing-coordinate proof, build a disposable copy with BOTH cases: (a) one pair removed; (b) one record with an explicit `"lon": null` — the exact case a natural `isset` implementation gets wrong (see the verified idiom in §3c.4). For each: assert the page contains the Q7 text, no `leaflet.css`, `leaflet.js`, or `museum-map.js`, and still prints its address. Never leave the fixture in this worktree; keep the recipe as a named script documented in `AGENTS.md` so future edits to the readiness predicate re-run it.

### VISUAL — real browser on a locally served pinned build

Start:

```sh
hugo server --disableFastRender --clock 2026-09-12T12:00:00+02:00
```

The operator records pass/fail in the implementation log after checking actual rendered behavior (DOM/network inspection, not screenshot-only):

- NL `/museums/rijksmuseum/` and EN counterpart: map becomes visible at 22rem; standard tiles render; marker sits on Museumstraat 1/Rijksmuseum, not Amsterdam centroid; attribution remains visible.
- Click marker and activate it by keyboard: popup opens and contains the museum name + address; close/reopen works; language switch keeps the same venue.
- Wheel over the map zooms the map (owner-approved Q4); page scrolling works normally everywhere outside the map; zoom buttons, drag, and keyboard work; responsive widths at narrow mobile and desktop do not overflow.
- Network panel: Leaflet CSS/JS and `museum-map.js` are same-origin; tile requests use only the approved host; home, calendar, exhibition, and about pages request no JS or map tiles (the museums index requests them only in its map-ready state). Click a `tile.openstreetmap.org` request → Headers → confirm a `Referer` value is present (OSMF tile policy; Finding 5 of the independent review).
- One museum in each coordinate spot-check region: pin plausibly overlays the official venue. Check Museum MORE according to Q8.
- Museums index NL + EN: overview map shows exactly the ready museums as markers; popup opens with name + working internal link; zero-ready disposable copy shows no map/scripts.
- Disposable missing-coordinate page: address + Q7 empty state render, map remains absent, and network shows no Leaflet/tile request.
- `/kalender/`, `/en/calendar/`, and one NL+EN month page: 50+ is lightest; 26–50, 11–25, and 0–10 deepen monotonically; countdown text remains legible and card links work.
- Restart with `--clock 2026-09-13T00:00:00+02:00` to inspect a real day-0 card (`end: 2026-09-13`) in the darkest band (`closing-heat-4`). Use a disposable synthetic copy only if refreshed data no longer contains examples for every band.
- Confirm 50+ shows carry only the lightest band; upcoming, open-ended, and recently-ended/collapsed cards are unshaded; jump-nav is unshaded; homepage upcoming order is earliest start first.
- Recheck the prior `contentnav` regression: calendar title/nav are not overlaid; no `0.1.` card numbering returns.

## 3c.9 Documentation

- `README.md` — museum maps, Leaflet 1.9.4 vendor/source, OSM tile dependency + attribution/privacy/no-SLA note, and no-JS-everywhere-else statement.
- `AGENTS.md` — exact JS allowlist and output-path grep; map assets must remain museum-detail-only; curated coordinate ownership/pipeline prohibition; pinned Hugo unchanged.
- `docs/site-plan.md` — one pointer to this §3c plan; do not rewrite the historical stack/deployment essay.
- `static/vendor/leaflet/1.9.4/LICENSE` — upstream license shipped with the vendored runtime.
- No content-copy docs, feed docs, or deploy docs need edits.

## 3c.10 Rollback

Nothing is irreversible. Before merge, close the branch. After merge, revert phase-3c commits in reverse order:

1. Revert docs.
2. Revert heat wrapper/classes to restore unchanged calendar cards.
3. Revert map template/initializer/CSS/i18n; this restores the inert hidden `#map`, removes every script tag, and stops all tile requests.
4. Remove the vendored Leaflet directory in the same revert that removes its references.
5. Coordinate fields may remain harmless curated data, or revert the three coordinate commits if the owner wants the exact pre-3c schema instance. Any cross-batch correction must land in its own labeled commit (`fix(data): correct <slug> coordinates`) so the three batch-add commits stay independently revertible.

No rollback touches `gh-pages` directly, generated feeds/data, frozen slugs, or pipeline scripts. Republish through the normal site pipeline after owner merge/revert.

## 3c.11 Risks & unknowns

| Risk / unknown | Mitigation / gate |
|---|---|
| JS leaks beyond museum pages | Shared readiness predicate; no inline JS; exact source/output allowlist and derived page/tag gates (computed from the curated data, not hardcoded) |
| Tile provider availability, policy, or privacy | Q3 owner choice; visible attribution; no prefetch; one replaceable URL; address survives outage |
| Wrong venue / swapped coordinates | Numeric/bounds audit + source per record + all-venue plausibility review + six independent spot-checks |
| Museum MORE has multiple venues | Q8; default remains phase-3b primary Gorssel model |
| Museums-index overview map weight (Q5) | One map, ≤30 markers, no clustering at this scale; loads only when ≥1 museum is ready; same two vendored files; visual QA covers popups + link targets |
| Marker images break after minification/base URL | Keep upstream CSS/image relative layout; test NL root + `/en/` nested paths in browser |
| Hidden map initialized at zero dimensions or init throws | Unhide immediately before `L.map`; on exception re-hide + reveal empty state; browser-resize/mobile gate; call `invalidateSize` only if evidence requires it |
| Popup injects curated text as HTML | Build DOM nodes and assign `textContent`; no `innerHTML` |
| Color alone communicates urgency | Existing bold countdown remains; contrast gate; no status removed |
| Heat/day label diverges near midnight | Reuse existing countdown integer-day calculation in this phase; timezone/countdown redesign remains out of scope |
| Shared card partial causes global color | Calendar-only wrapper; explicit negative greps outside calendars |
| Local toolchain differs | Local proof is v0.165.0 only; operator must repeat all gates and browser serve on v0.166.0 extended |
| Upstream Leaflet 1.x is maintenance-only / 2.0 changes API | Pin 1.9.4 now; future upgrade is an explicit reviewed phase, never an implicit CDN change |
| Vendor licensing/provenance lost | Exact path, tagged license, release URL/hash, no rebuilt/minified derivative |
| “Binnenkort” premise differs from checkout | Current evidence is start-sort; retain regression gate and obey touched-file-only constraint |

## 3c.12 Log

- 2026-09-13 · Owner answers folded: **Q1 four custom bands (0–10/11–25/26–50/50+)**, Q2 calendar index + months, Q3 OSM Standard, **Q4 scroll-wheel zoom ON**, **Q5 + museums-index overview map**. Palette table + contrast recomputed for four bands; index-map spec added (§3c.4 + ST-3c-5); expected script-page counts now `M×2 + 2 index`; heat/day-0 checks updated. Q6–Q8 stand at their recommendations unless the owner flags otherwise.

- 2026-09-13 · Independent review folded (0 blockers / 5 major / 7 minor; doc `docs/plan-review-phase3c.md`). Pin-verified on v0.166.0: nested `ne X nil` + type/bounds guard → float pair ready; explicit `null`, missing key, and string values all not-ready with a green build (scratch fixture); quote-tolerant CDN regex catches all three `src=` forms; `v1.9.4` LICENSE fetch OK (BSD-2-Clause, 1,395 B). Status: awaiting owner Q1–Q8 answers.

*(Append during the build, one bullet per run.)*

Status: `draft`
- 2026-09-13 · **PHASE 3C BUILD COMPLETE** — ST-3c-1…7 via composer-2.5 (1–4, 6, 7) + cursor-grok-4.6-medium (5). Coordinates 30/30 with operator gates after each batch (`9f31cf7`, `5cb99d8`, `1a0b41d`; correction `e2345b5`); Leaflet 1.9.4 vendored byte-identical (`1ac44bf`); conditional maps → 62 script pages / 124 tags exact (`c6cb822`); four-band calendar heat (`6a68d9b`); docs (`21f9809`). Pinned battery v0.166.0: 990 pages / 0 WARN; fixtures (pair-removed + explicit-null) render the empty state with no map assets; regression greps clean; weekly feeds md5 byte-identical; browser gate passed (marker/popup/index-30/zero-script-home/wheel-zoom/referrer/empty-state). PR #14 → owner review.
- 2026-09-13 · **PHASE 3C LIVE** — PR #14 merged by owner (main `16cfc33`); published @16cfc33 to gh-pages; live sweep green: map scripts + coordinate attrs on museum pages, Leaflet on the museums index, heat classes on both calendars served from the CDN, home still 0 `<script>`, weekly feeds byte-identical (`370a9643…` / `456f8abd…`), route spot-checks 200 (incl. the corrected `singer-laren` page).

---

## Phase 4 — structured data, refresh cadence, navigation & polish

Status: **approved (owner decisions 2026-09-13)** — independent review (`docs/plan-review-phase4.md`, findings F1–F21) fully incorporated below; the owner has now answered every §4.5 question (Q1–Q16, recorded 2026-09-13, each decision folded into the relevant subsection and subtask below). Planning-cycle boundary: this branch commits and pushes **only `PLAN.md`**; the first ST-4 build/implementation commit belongs to a separate, later branch/run, not this one.

### 4.0 Agent ground rules

Follow `AGENTS.md` (outranks defaults). In force: Conventional Commits; `diane/…` or `cursor/…` branches; **owner merges**; never push `main` or `gh-pages` except through the publish scripts; never change `/museumtips.ics` or `/closing-soon.ics` paths; never hand-edit generated `data/exhibitions.json` or any generated ICS; keep NL + EN in sync; no Node or asset build step; Hugo **v0.166.0 extended** is authoritative (Mac lane currently has **v0.165.0 extended** only — every run states which pin it built on; the operator re-verifies on v0.166.0 before anything is marked done); never edit `themes/huguette`; no JavaScript beyond the phase-3c allowlist (`static/js/museum-map.js`, `static/vendor/leaflet/1.9.4/leaflet.js`) — phase 4 adds **zero** new JS.

**Repo/pipeline boundary (load-bearing for this phase — verify before any run starts):** the weekly discovery/scrape pipeline (`/opt/data/museum_tracker/…`) lives entirely **outside this git repo**, on a host this repo's agents cannot reach. `data/exhibitions.json` and root/`static/*.ics` are that pipeline's output and stay hand-edit-forbidden here. `data/museums_info.json` and `data/exhibitions_info.json` are **curated but agent-editable inside this repo** — phase 3b's C1/C2 and phase 3c's coordinate batches (ST-3c-1…3) already established the pattern: agent runs add/update curated fields in dated, human-gated batches, committed here, and the pipeline never touches them. Phase 4 extends that same pattern to structured-data migration, cadence bookkeeping, and press-link fallbacks — **it does not add pipeline-host code**, because this repo's agents have no access to write it. Any work item that is genuinely pipeline-host-only (item 1(b)'s JSON-LD-consuming scraper; the weekly discovery scrape itself) is scoped in this plan as a **documented handoff** the operator implements on the pipeline host, exactly like phase 2's D5.

### 4.1 Goals

1. Give the internal curated data store (`data/museums_info.json`, `data/exhibitions_info.json`) a schema.org-aligned internal shape for both museums (`Museum`) and exhibitions (`ExhibitionEvent`-shaped), migrating current flat fields (dates, address, pricing/cards, venue) into the mapped structure in §4.4.1, **without** changing frozen slugs, file identity, or curated-data ownership.
2. Document the equivalent target shape for the pipeline-generated `data/exhibitions.json` and hand it to the operator for the pipeline host — **not** implemented in this repo.
3. Document the target contract for scrapers to additionally consume museum-site JSON-LD (`ExhibitionEvent`) as an extra discovery source — again a pipeline-host handoff, not repo code.
4. Explicitly defer serving our own JSON-LD on site pages; leave a clean upgrade note pointing at the schema.org-shaped store this phase creates.
5. Halve the museum-extras refresh cadence: ~15 museums refreshed one week, the other ~15 the next, on top of the unchanged weekly discovery cadence; press links keep collecting weekly and drop when their show ends.
6. Improve press-link fallback for hard-403 outlets (retry alternate paths; fall back to link-only, recorded honestly).
7. Fix the invisible main navigation and ship an unmistakable "Home" affordance on every page.
8. Run a light copy pass (display/URL consistency nits, informal-tone cleanup) **after** the functional workstreams land.
9. Decide and record the fate of the phase-3d leftovers (share/CTA/Telegram hooks): fold a defined slice into phase 4, or re-defer explicitly.

### 4.2 Non-goals

- **International section** — parked; no new content, routes, or data for it in this phase.
- **Serving our own JSON-LD** on museum/exhibition/calendar pages — deferred; §4.4.1 notes the upgrade path the schema.org-shaped store leaves open, but no `<script type="application/ld+json">` ships in this phase.
- **Full copy rewrite** — §4.4.5 is a light pass (consistency + tone nits) on top of the phase-2 operator draft, not a rewrite.
- **Any theme edit** (`themes/huguette`) — every navigation/banner change lands in this repo's own `layouts/`/`static/css/custom.css`, never the submodule.
- No pipeline-host code changes from this repo (see §4.0 boundary) — this repo produces target-contract docs for items 1(b)/1(c)'s pipeline-side pieces, not scraper code.
- No new JavaScript, no CDN assets, no map/heat changes (3c is closed) beyond what's already shipped.
- No frozen-slug, feed-path/filename, or `/musea/` → `/museums/` redirect changes.
- No decomposition of free-text opening hours into structured `OpeningHoursSpecification` — 30 free-text variants with holiday exceptions is out of scope for one phase; hours/transit/parking/access stay bilingual free text (§4.4.1).
- No booking/ticketing integration, CTA button, or Telegram bot code beyond whatever §4.5 Q6 explicitly approves folding in.

### 4.3 Recon and verified baseline

Verified 2026-09-12 in this checkout (Mac lane Hugo **v0.165.0-…+extended**; pin is v0.166.0):

- **Data shapes today.** `data/exhibitions.json` (pipeline-generated, schema 1): `museums[]` = `{name, city, group, site, quirks, slug}` (30 rows); `exhibitions[]` = `{title, museum, city, start, end, description, url, slug}` (187 rows). `data/museums_info.json` (curated, 30 keys by frozen slug): flat fields `name, description_nl/en, address` (single string), `lat, lon` (numeric, phase 3c), `hours_nl/en, transit_nl/en, parking_nl/en, access_nl/en, cards[] ({id,label,accepted,note_nl,note_en}), pricing_nl/en, verified, sources[] ({fact,url}), notes[]`. `data/exhibitions_info.json` (curated, 187 keys by frozen slug): `admission {museumkaart: included|supplement|not_covered|unknown, note_nl, note_en, source, verified}`, `press[] ({title,outlet,url,lang,date})`, `verified`. None of the three files carries any `@type`/schema.org marker today. i18n key parity is **96/96** (grown from 55 at phase-2 ST5 via 3b/3c additions).
- **Ownership precedent.** Curated-file edits already happen via agent runs in this repo, human-gated, in dated batches: phase 3b's C1 (30 museums) / C2 (187 shows admission+press) and phase 3c's ST-3c-1…3 (10-museum coordinate batches). This is the template phase 4 reuses for the cadence and press-fallback workstreams — no new mechanism needed, just a schedule.
- **Press fallback today.** `exhibitions_info.json` currently has 92 press entries across 54 shows; two confirmed DVHN entries carry working URLs already (`beauty-of-the-beast-dieren-in-de-art-nouveau`, `into-nature-haunted-by-waters`); no `verified_access` or equivalent field exists yet to record a hard-403/fallback outcome — this phase adds one.
- **Navigation bug (operator-reproduced 2026-09-13, encode as given).** `layouts/_default/baseof.html` renders `headerimage.html` → `navigation.html` → (inside it) `lang-switcher.html`, each of the latter two emitting a top-level `<nav>` directly under `<body>`. `static/css/classless.css:217-222`: `body>nav, header nav { position: var(--navpos) /* absolute */; top:0; left:0; right:0; z-index:41; box-shadow: 0vw -50vw 0 50vw var(--clight), 0 calc(-50vw + 2px) 4px 50vw var(--cdark); }`. Both bars float, full-bleed, same z-index; the second (`lang-switcher`'s `<nav>`, later in source order) paints its own full-bleed shadow sheet over the first bar's link text — hit-testing still finds the links (that's why nobody filed this as "links don't work"), but the paint hides them, on **every page, both languages**. Operator's proven one-line fix: `body > nav + nav { box-shadow: none !important; }` (+ optional `body > nav:first-of-type { z-index: 43 }`), with before/after screenshots captured live.
- **Existing `.contentnav` precedent** (PR #8, phase-2 log): in-page navs (museums city list, calendar month jump nav) hit the *same* `body>nav` rule and were pulled out of flow via `body>nav.contentnav, header nav.contentnav { position: static; z-index: auto; box-shadow: none; }` in `static/css/custom.css:26-32`. The main menu bar and the language switcher currently keep the float design; §4.5 Q1 asks whether to extend the same static-in-flow treatment to them too, instead of (or in addition to) the operator's shadow-kill patch.
- **Existing "Home" menu item.** `content/{nl,en}/_index.md` front matter already sets `menu: { main: { name: Home, weight: 1 } }` — "Home" is already the first (leftmost) menu link in both languages. It has been invisible along with the rest of the bar; §4.5 Q2 is about making it visually unmistakable once visible, not about adding a new link.
- **Banner/header state.** `layouts/_default/baseof.html:4` unconditionally calls `partial "headerimage.html"`; per the task brief that theme partial only renders a banner when page front matter sets `header:`, and `grep -rn 'header:' content/` in this checkout returns zero hits — the theme's banner slot has always been dormant here. No `layouts/partials/headerimage.html` override exists in this repo (theme-owned, submodule not initialized in this checkout).
- **3d leftovers, checked against the actual plan text.** `PLAN.md` §3b.2/§3b.4 (D11) already parked, verbatim: "No marketing CTA (tickets, newsletter, donate) — phase 3d. Do not occupy a `cta` slot or add booking buttons," and "no mailto/Web Share in 3b — mailto would need its own i18n subject string; explicitly deferred." §3b.5 item 8 lists "Add to agenda … + share permalink" as already shipped (the per-exhibition `.ics` + canonical URL). So the concrete 3d leftover set is: (a) an optional `mailto:?subject=&body=` share action (needs a new i18n `share_mailto_subject`/body key, D11), (b) a `cta`/booking-button slot (fully unbuilt, no schema field reserved), (c) Telegram hooks — **no pre-Phase-4 repo specification or implementation**: zero hits for "Telegram" anywhere in `PLAN.md`, `AGENTS.md`, or `README.md` *before* this phase's own brief introduced it (Phase 4 itself now contains this recon paragraph, so a bare "zero hits anywhere in PLAN.md" claim would be self-contradicting the moment this sentence is written). Before assigning Telegram to a future phase, record the owner's actual intent/source for the request (what it's meant to do, why now) rather than treating "no prior spec" as license to guess a scope. Fold-in vs defer is §4.5 Q6.
- **Cadence/press today have no schema hook.** No `refresh_group`, `last_refreshed`, or similar field exists on any of the 30 `museums_info.json` records; nothing marks which half was last touched. 30 museums ÷ 2 = 15/15 exactly.

### 4.4 Proposed implementation

#### 4.4.1 Structured data (schema.org) — authoritative field-by-field contract [F1]

**Status:** this subsection is now the transcribed, owner-approvable contract itself, censused against the live data on 2026-09-12 (30 museum records / 146 cards / 398 sources / 102 notes / 187 exhibition records / 92 press entries, matching `docs/plan-review-phase4.md`'s verified counts). ST-4-1 (§4.6) transcribes and validates this contract into `docs/structured-data-schema.md` — it does **not** design it; any field found in the live data but missing from the tables below is a bug in this section, not something ST-4-1 may invent a mapping for.

**Scope split (repeat of §4.0's boundary, now applied field-by-field):** this repo migrates the **curated** stores (`museums_info.json`, `exhibitions_info.json`) directly, in-repo, agent-run, human-gated. The **generated** store (`exhibitions.json`) keeps schema 1 unchanged in this phase; phase 4 only writes the target "schema 2" contract (Table 1 below) for the operator to implement on the pipeline host later (§4.6 ST-4-5). Site templates therefore change only where they read curated fields — they keep reading generated `exhibitions.json` exactly as today until the operator switches producers (§4.4.1.7).

**Cross-cutting design choices (apply to every table below; don't relitigate per field):**

- Bilingual leaf values stay an internal `{ "nl": …, "en": … }` sub-object wherever literal schema.org/JSON-LD expects one string per node (owner Q8, §4.5) — a deliberate, documented deviation from JSON-LD validity, acceptable because serving our own JSON-LD is deferred (non-goal #2).
- Two named extension subtrees hold everything schema.org has no literal node for, always at the object's top level next to the schema.org-shaped keys: **`_visitor`** — bilingual free-text visitor information (hours/transit/parking/access/pricing) — and **`_meta`** — provenance and bookkeeping (`sources[]`, `notes[]`, `verified`, per-field `source`/`verified` pairs). This is the exact split the recon's "unnamed `_meta`/`_visitor` buckets" needed named: nothing else is a placeholder bucket.
- Every migrated record gets exactly one new top-level `"@type"` key (`"Museum"` or, for the sidecar shape §4.4.1.6(a), no root `@type` — see below); no existing key is renamed — legacy flat keys are **removed in the same big-bang commit(s)** that add the new shape (owner Q4: big-bang migration, no parallel-fields window; §4.4.7).
- Card acceptance is a **three-state string enum**, never a boolean and never `InStock`/`OutOfStock` (schema.org `availability` is a stock-keeping vocabulary for physical/e-commerce goods, not admission-card acceptance — using it would misrepresent the fact and silently coerces `null` into a false binary): `"accepted"` | `"not_accepted"` | `"unknown"`, mapped 1:1 from legacy `true`/`false`/`null`.
- `note_*` and `notes_*` are two live spellings of the same fact (never both present on one card) and both normalize into the same target leaf; see Table 2b.

##### Table 1 — `data/exhibitions.json` (pipeline-generated, schema 1 → schema 2 target)

All 16 existing fields (2 root + 6 per museum row × 30 rows + 8 per exhibition row × 187 rows) keep their **exact current key, path, and type** — schema 2 is additive-only (§4.4.1.7); the only new content is one `@type` key per row. This table is the complete generated-store mapping the recon found entirely absent.

| Existing field | Path | Type / nullability | Schema-2 target | Notes |
|---|---|---|---|---|
| `schema` | root | int, constant | same key; value bumps `1`→`2` once `@type` rows are emitted | version marker; consumers must treat `schema>=1` fields as always present and only gate `@type` reads on `schema==2` |
| `compiled` | root | ISO date string | unchanged | pipeline-run timestamp |
| `museums[].name` | museum row | string, required | unchanged | join key used by `exhibitions[].museum` (by value, not slug — existing design, unchanged) |
| `museums[].city` | museum row | string, required | unchanged | canonical venue city |
| `museums[].group` | museum row | string, required | unchanged | display-only region label; no schema.org target, passed through verbatim |
| `museums[].site` | museum row | URL string, required | unchanged | conceptually `Museum.url`, but the flat key name stays `site` — renaming it would not be additive (F4) |
| `museums[].quirks` | museum row | string, required | unchanged | operator/pipeline-only annotation; never rendered |
| `museums[].slug` | museum row | string, required, frozen identity | unchanged | join key to `museums_info.json` keys; never renamed |
| *(new, schema 2 only)* | museum row | constant | `"@type": "Museum"` | additive; absent under schema 1, present under schema 2 |
| `exhibitions[].title` | exhibition row | string, required | unchanged | source-language string, single value (no NL/EN variant — see Q16, §4.5) |
| `exhibitions[].museum` | exhibition row | string, required | unchanged | joins to `museums[].name` by value |
| `exhibitions[].city` | exhibition row | string, required | unchanged | may duplicate `museums[].city`; generated store's own existing join, unchanged |
| `exhibitions[].start` | exhibition row | ISO date string or `null` | unchanged | nullable — open-ended/unannounced start |
| `exhibitions[].end` | exhibition row | ISO date string or `null` | unchanged | nullable — open-ended run |
| `exhibitions[].description` | exhibition row | string, required | unchanged | single value, same `inLanguage` caveat as `title` |
| `exhibitions[].url` | exhibition row | URL string, required | unchanged | official page |
| `exhibitions[].slug` | exhibition row | string, required, frozen identity | unchanged | join key to `exhibitions_info.json` keys; never renamed |
| *(new, schema 2 only)* | exhibition row | constant | `"@type": "ExhibitionEvent"` | additive; see §4.4.1.6 for what this marker does/doesn't imply about the curated sidecar's own `@type` |

**Reverse/equality checks for Table 1 (run whenever the operator emits a schema-2 fixture, §4.6 ST-4-5):** every schema-1 key/value pair present in a pre-cutover fixture is byte-identical in the schema-2 fixture; the only diff is the 30+187 new `@type` keys; `schema` is the only value that changes.

##### Table 2 — `data/museums_info.json` (curated, 30 records) — scalar and address fields

| Existing field | Occurrences | Type / nullability | Target path | Notes |
|---|---:|---|---|---|
| record key (slug) | 30 | string, frozen identity | unchanged (same key) | must equal `exhibitions.json museums[].slug` for the same museum — reverse check |
| `name` | 30 | string, required | `name` (unchanged) | must equal `exhibitions.json museums[].name` for the same slug — reverse check (duplicate-data ownership: generated store owns identity/name; this is a mirror, not authoritative) |
| `description_nl` | 30 | string, required | `description.nl` | bilingual leaf sub-object |
| `description_en` | 30 | string, required | `description.en` | bilingual leaf sub-object |
| `address` | 30 | string, required | **both** `address_display` (verbatim copy, canonical raw/display string — F2) **and** `address_v2.{@type:"PostalAddress", streetAddress, postalCode, addressLocality, addressCountry:"NL", venueNote}` (parsed) — legacy `address` is **removed in the same big-bang commit** that adds these two (owner Q4; the pre-commit losslessness proof, §4.4.1.5, is what makes this safe to do in one step) | see §4.4.1.4 for the parse rule, `venueNote`, and the 6 non-reversible records |
| `lat` | 30 | float, required | `geo.latitude` — legacy `lat` removed in the same big-bang commit (Q4) | `geo.latitude == lat` bit-exact — reverse check, run **before** the commit as part of the losslessness proof |
| `lon` | 30 | float, required | `geo.longitude` — legacy `lon` removed in the same big-bang commit (Q4) | `geo.longitude == lon` bit-exact — reverse check, run **before** the commit as part of the losslessness proof |
| `hours_nl` | 30 | string, required | `_visitor.hours.nl` | free text, unchanged value |
| `hours_en` | 30 | string, required | `_visitor.hours.en` | free text, unchanged value |
| `transit_nl` | 30 | string, required | `_visitor.transit.nl` | free text, unchanged value |
| `transit_en` | 30 | string, required | `_visitor.transit.en` | free text, unchanged value |
| `parking_nl` | 30 | string, required | `_visitor.parking.nl` | free text, unchanged value |
| `parking_en` | 30 | string, required | `_visitor.parking.en` | free text, unchanged value |
| `access_nl` | 30 | string, required | `_visitor.access.nl` | free text, unchanged value |
| `access_en` | 30 | string, required | `_visitor.access.en` | free text, unchanged value |
| `pricing_nl` | 30 | string, required | `_visitor.pricing.nl` | free text, unchanged value |
| `pricing_en` | 30 | string, required | `_visitor.pricing.en` | free text, unchanged value |
| `sources[].fact` | 398 | string, required (enum: `description\|address\|hours\|pricing\|cards\|transit\|parking\|access\|coordinates`) | `_meta.sources[].fact` | provenance, unchanged shape |
| `sources[].url` | 398 | URL string, required | `_meta.sources[].url` | provenance, unchanged shape |
| `notes[]` | 102 strings total | string list | `_meta.notes[]` | unchanged shape, verbatim |
| `verified` | 30 | ISO date string, required | `_meta.verified` | unchanged value; the big-bang commit (ST-4-2, owner Q4) moves the "last verified" read from top-level `verified` to `_meta.verified` in the same step it removes the legacy key |
| *(new)* | 30 | constant | `"@type": "Museum"` | additive |
| *(new, cadence — §4.4.2)* | 30 | see §4.4.2 | `refresh_group`, `last_refreshed_extras`, `next_due` | not part of the schema.org migration; added by ST-4-6, documented in §4.4.2 |

##### Table 2b — `museums_info.json` `cards[]` → `offers[]` (146 cards across 30 museums)

| Existing field | Occurrences | Type / nullability | Target path | Notes |
|---|---:|---|---|---|
| `cards[].id` | 146 | string, required | `offers[].identifier` | **retained** — the recon found this dropped; F2 requires it kept |
| `cards[].label` | 146 | string, required | `offers[].name` | unchanged value; template's existing "fall back to id if label falsy" logic is preserved unchanged |
| `cards[].accepted` | 146 (144 bool, 2 `null`: `huis-marseille`/`vriendenloterij`, `museum-kranenburgh`/`vriendenloterij`) | `true\|false\|null` | `offers[].acceptance` | three-state enum per the cross-cutting rule above: `true→"accepted"`, `false→"not_accepted"`, `null→"unknown"` — **no null collapse, no `InStock`/`OutOfStock`** |
| `cards[].note_nl` | 119 (mutually exclusive with `notes_nl` on the same card) | string | `offers[].description.nl` | normalize: `description.nl = note_nl` when `note_nl` is present |
| `cards[].note_en` | 119 | string | `offers[].description.en` | normalize: `description.en = note_en` when `note_en` is present |
| `cards[].notes_nl` | 27 (mutually exclusive with `note_nl`; museums: Foam, Museum Boijmans Van Beuningen, Kunsthal, Nederlands Fotomuseum, Museum MORE) | string | `offers[].description.nl` | normalize: `description.nl = notes_nl` when `note_nl` is absent and `notes_nl` is present — same target leaf, other spelling |
| `cards[].notes_en` | 27 | string | `offers[].description.en` | same rule, `.en` |
| *(new)* | 146 | constant | `"@type": "Offer"` | additive |
| *(new)* | 146 | constant | `"category": "discount-card"` | additive |

**Pre-existing display bug, fixed in the same big-bang commit (F2):** `layouts/partials/museum-info.html` (current lines ~76–78) reads only `.note_nl`/`.note_en` per card and has never rendered the 27 `notes_nl`/`notes_en` values for Foam, Museum Boijmans Van Beuningen, Kunsthal, Nederlands Fotomuseum, or Museum MORE — those five museums' plural-note cards have displayed with no note text since C1. ST-4-2 (§4.6, owner Q4's big-bang migration) fixes this as a named part of the combined data-reshape + template-cutover commit: once templates read `offers[].description.{nl,en}` (which the normalization above already merges from whichever spelling exists), the bug disappears as a side effect — ST-4-2's verify step must explicitly assert the previously-blank notes now render for those five museums (§4.4.1.5).

##### Table 3 — `data/exhibitions_info.json` (curated, 187 records)

| Existing field | Occurrences | Type / nullability | Target path | Notes |
|---|---:|---|---|---|
| record key (slug) | 187 | string, frozen identity | unchanged (same key) | must equal `exhibitions.json exhibitions[].slug` — reverse check |
| `admission.museumkaart` | 187 | string enum `included\|supplement\|not_covered\|unknown` | `admission_v2.admissionStatus` | value unchanged; explicitly a **custom, non-schema.org property** (stated, not implied) |
| `admission.note_nl` | 187 | string, may be `""` | `admission_v2.description.nl` | bilingual leaf; empty string is a valid value, not absent |
| `admission.note_en` | 187 | string, may be `""` | `admission_v2.description.en` | bilingual leaf |
| `admission.source` | 187 | URL string, required | `_meta.admission.source` | provenance |
| `admission.verified` | 187 | ISO date string, required | `_meta.admission.verified` | provenance; distinct from record-level `_meta.verified` |
| `press[].title` | 92 | string, required | `subjectOf[].headline` | unchanged value |
| `press[].outlet` | 92 | string, required | `subjectOf[].publisher.name` (`publisher.@type: "Organization"` constant) | unchanged value |
| `press[].url` | 92 | URL string, required | `subjectOf[].url` | unchanged value |
| `press[].lang` | 92 | string enum `nl\|en` | `subjectOf[].inLanguage` | unchanged value |
| `press[].date` | 92 | ISO date string, required | `subjectOf[].datePublished` | unchanged value |
| record `verified` | 187 | ISO date string, required | `_meta.verified` | unchanged value |
| *(new)* | 187 | constant | `admission_v2.@type: "Offer"` | additive |
| *(new)* | 92, `subjectOf[]` only — §4.4.3/ST-4-9 | bool | `subjectOf[].verifiedAccess` | additive, from the press-fallback pass; **legacy `press[]` no longer exists to mirror onto** — ST-4-2's big-bang commit (owner Q4) already removed it, so ST-4-9 (which runs after ST-4-2) writes these fields to `subjectOf[]` only |
| *(new)* | 92, `subjectOf[]` only | string, controlled vocabulary (§4.4.3) | `subjectOf[].accessNote` | additive |
| *(new)* | 92, `subjectOf[]` only | ISO date string | `subjectOf[].accessChecked` | additive |
| *(new)* | 92 | constant | `subjectOf[].@type: "NewsArticle"` | additive |

**Reverse/equality checks for Tables 2/2b/3 (the 30-record/146-card semantic-equality script, F2/F9 — new fixture-backed check, §4.6 ST-4-2's verify step):**

- `geo.latitude == lat` and `geo.longitude == lon`, bit-exact, all 30.
- `address_display` equals the original `address` string verbatim, all 30 (independent of how well the `PostalAddress` split worked — this is the true losslessness gate, not the parse quality).
- `{o.identifier for o in offers}` == `{c.id for c in cards}` per museum, all 30 (146 total).
- `offers[i].acceptance` == three-state mapping of `cards[i].accepted`, all 146, **including both `null` cases** (`huis-marseille`, `museum-kranenburgh`).
- `offers[i].description.{nl,en}` == the note text from whichever of `note_*`/`notes_*` was present on `cards[i]`, all 146, **including all 27 plural-note cards** across Foam / Museum Boijmans Van Beuningen / Kunsthal / Nederlands Fotomuseum / Museum MORE.
- `admission_v2.admissionStatus` == `admission.museumkaart`, all 187.
- `len(subjectOf) == len(press)` per exhibition and `sum(len(subjectOf)) == 92`, all 187.
- **Fixtures (checked into ST-4-2's verify step, both domain commits, not committed as separate files):** a small Python literal table covering the two null-accepted cards and the five plural-notes museums, asserting the exact expected `acceptance`/`description` output for each — regression-proof against a future accidental re-collapse.

##### 4.4.1.4 Address / multi-venue handling rule

The single `address` string is not always a clean `street, postcode city` triple. Six of the 30 records carry venue/access annotations the naive split would either mangle or silently drop: `h-art-museum` (former-building name + taxi drop-off note), `museum-boijmans-van-beuningen` and `kunsthal` (venue qualifier prefix — "Depot Boijmans Van Beuningen," / "Museumpark,"), `museum-more` (names a second location, Kasteel Ruurlo), `kroller-muller-museum` (park annotation), `museum-volkenkunde` (goods-entrance annotation). Rule (owner Q11, §4.5): `address_v2.streetAddress`/`postalCode`/`addressLocality`/`addressCountry` capture only the parseable postal triple; **any remaining text that isn't part of the postal triple is preserved verbatim in `address_v2.venueNote`** (single string, not bilingual — the source text has no language split today, matching the original field), never dropped and never force-fit into a `PostalAddress` sub-property that doesn't semantically fit (e.g. "Depot Boijmans Van Beuningen" is not a `streetAddress`). `address_display` (verbatim original string, top-level sibling of `address_v2`) is the backstop losslessness check regardless of how the split or `venueNote` assignment turned out.

##### 4.4.1.5 Losslessness proof (F9) — mandatory pre-commit gate (owner Q4, Q16a)

Because Q4 chose **big-bang** migration (data reshape + template cutover land in the same commit(s), no parallel-fields window to fall back on), this proof is not a post-hoc check — it is a **hard pre-commit gate**: it must pass on the working tree **before** ST-4-2's big-bang commit(s) are made, since there is no intermediate parallel-fields state left to diff against afterward. Three gates, all mandatory, none of which may be skipped or sampled:

1. **Full-population before/after fact diff.** Generate a canonical **before-facts** set and, after the transform (staged, not yet committed), a canonical **after-facts** set, both as flat `(record, field-path, value)` tuples, and diff them: every before-fact must have exactly one after-fact with an equal value at its mapped target path (per Tables 2/2b/3), and the after-set must contain **no fact absent from the before-set** (catches accidental duplication as well as loss). Scope: all 30 museums, 146 cards, 398 sources, 102 notes, 187 admissions, 92 press articles — not a sample (owner Q16a: hard gate, no reduced-sample substitute). Fail the run on any unconsumed source field or any extra/unexplained target field.
2. **Named fixtures.** The two null-accepted cards (`huis-marseille`, `museum-kranenburgh`) and the five plural-notes museums (Foam, Museum Boijmans Van Beuningen, Kunsthal, Nederlands Fotomuseum, Museum MORE) get an explicit, named assertion of their exact expected output — not swept in by the generic diff alone.
3. **Scratch render-equality check.** Because template cutover and data reshape land together with no separately-revertible intermediate step, build the **staged** (uncommitted) working tree with `hugo --minify` into a scratch destination and diff it against a build of the **pre-migration** tree (same pin), page-for-page, with the 5 plural-notes museum pages and the 13 targeted snapshots (item 4 below) as the only allowed differences. A staged tree that fails this build-and-diff check must not be committed — this is what stands in for the parallel-fields window's own byte-identical gate now that there's no separate cutover commit to run it against.
4. In addition to the flat diff, render and manually eyeball a snapshot of the built HTML for every anomalous shape: the 6 non-reversible addresses (§4.4.1.4), the 5 plural-notes museums, and the 2 null-accepted cards — 13 targeted museum-detail-page snapshots, not just `rijksmuseum`.

All three gates run against the **staged, uncommitted** tree; a failure at any gate blocks the commit — there is no "commit now, fix in a follow-up" option under big-bang.

##### 4.4.1.6 `ExhibitionEvent` — both shapes specified (F3)

The phrase "ExhibitionEvent-shaped curated store" in earlier drafts overstated what the `exhibitions_info.json` migration (folded into ST-4-2, §4.6, under the Q4 big-bang restructure) builds. Both real options were specified here; **§4.5 Q13 answered: sidecar, option (a)** — the fork below is settled, kept only as the record of what was decided against.

**(a) Extras/provenance sidecar — chosen (Q13).** `exhibitions_info.json[slug]` stays a slug-keyed extras record: `admission_v2`, `subjectOf[]`, `_meta.*`. It carries **no** title, dates, museum, city, or `url` — those remain solely in generated `exhibitions.json`, joined by slug at render time exactly as today (`exhibition-page.html` already does this join). Nothing is duplicated on disk, so there is no drift risk between the two stores, and no cross-file join logic needs to change. **This is the only shape ST-4-2 implements.**

**(b) Complete `ExhibitionEvent` — not chosen.** The rejected alternative: add `"@type": "ExhibitionEvent"` at the record root; `name`, `startDate`, `endDate`, `location.{@type:"Place", name, address}`, and `url` computed at render time (joined from generated `exhibitions.json` + the museum's `museums_info.json` row) rather than stored a second time; `offers` becomes `[admission_v2]` (array). More schema.org-literal, useful only once JSON-LD is actually served (non-goal #2 this phase); would have cost a render-time cross-file join with no current visible benefit — not built.

The exhibitions-side migration (sidecar shape only) is part of ST-4-2's big-bang commit — **Depends: ST-4-1, owner Q4, Q13** (§4.6, §4.5).

##### 4.4.1.7 Pipeline schema-2 rollout safety (F4)

Schema 2 (Table 1) is additive/backward-compatible by construction — every schema-1 key/path/type is unchanged; the only addition is a per-row `@type`. That constraint alone is not a rollout plan; the atomic operator sequence for the *actual* future producer switch (pipeline-host, out of this repo, documented for the operator in ST-4-5) is:

1. **Dual-write:** pipeline emits both `schema:1` (legacy, unchanged) and a `schema:2` fixture file side by side for at least one full weekly cycle, without switching the file the site build reads.
2. **Fixture-validate:** run this repo's `hugo --minify` against the `schema:2` fixture in a scratch destination; assert zero WARN and the same page count as the `schema:1` build (990 pages, current baseline).
3. **Deploy compatible templates:** merge and publish (via the normal `gh-pages` flow) any repo template change that can read either schema (there should be none needed, since schema 2 only adds a key nothing reads yet).
4. **Switch producer:** pipeline starts writing `schema:2` as the live `data/exhibitions.json`.
5. **Verify live:** re-run the §4.8 battery against the live site after the next publish; confirm page count, feed byte-equality, and zero regressions.
6. **Remove schema 1 emission later:** only after step 5 is clean for at least one full cycle, the pipeline stops dual-writing.

**Rollback, both sides:** *pipeline* — revert the producer to `schema:1`-only emission (step 4 in reverse); the dual-write fixture from step 1 is disposable. *site* — if a site-side template change shipped in step 3 turns out to depend on `@type` being present, revert that template commit before the pipeline rolls back its producer (same ordering constraint as §4.10 item 6): a template expecting `@type` must never be live while the producer is back to schema 1.

**Migration ownership rules (stated explicitly):**

| Store | Who writes the new shape | How |
|---|---|---|
| `data/museums_info.json` | This repo's agents | Big-bang structural migration (§4.6 ST-4-2, museums-domain commit), same file, same 30 keys, human-gated diff review |
| `data/exhibitions_info.json` | This repo's agents | Big-bang structural migration (§4.6 ST-4-2, exhibitions-domain commit), same file, same 187 keys |
| `data/exhibitions.json` | Pipeline (operator, out-of-repo) | This repo only ships the Table 1 target-contract doc (§4.6 ST-4-5); no code change here; pipeline emits schema 2 per §4.4.1.7's sequence, unchanged until then |
| Museum-site JSON-LD consumption (item 1(b)) | Pipeline (operator, out-of-repo) | Target-contract doc only (§4.6 ST-4-5); additive discovery source, never a replacement for existing scraping |
| Serving our own JSON-LD (item 1(c)) | Deferred entirely | No work this phase; this section leaves the upgrade path documented (the store is already schema.org-shaped) |

NL is absent from Google's event-rich-result region list, so even once JSON-LD is served (future phase), rich-result coverage will be patchy — this only affects the deferred surface, not this phase's store migration.

#### 4.4.2 Extras refresh cadence [F6, F12]

Weekly discovery (pipeline-host, unchanged) keeps finding new/ended exhibitions every week. Museum **extras** (hours/prices/cards/access/transit — the curated, agent-refreshed half of `museums_info.json`) move to a halved cadence: ~15 museums refreshed in week A, the other ~15 in week B, alternating.

**Curated-record lifecycle — a recurring repo-side reconciliation run, not "drops naturally" (F6).** `AGENTS.md` states the pipeline never writes curated files, so an ended exhibition slug disappearing from generated `exhibitions.json` cannot by itself remove its `exhibitions_info.json` record or press links — there is no automatic mechanism for that today, even though parity happens to hold now. Fix: add a recurring, repo-side, human-gated **reconciliation run** (own subtask, ST-4-6a, §4.6) that, every cycle:

1. **Adds missing curated keys** — any generated slug (museum or exhibition) with no curated record gets a stub record created (empty/`unknown` fields, flagged for the next refresh batch) — never silently absent from the curated file.
2. **Resolves orphaned curated keys** (curated records whose generated slug no longer exists) per the **owner-approved retention rule (§4.5 Q15, answered 2026-09-13): one full cadence cycle of grace, then delete.** Concretely: on each reconciliation run, an orphaned `exhibitions_info.json` record (press links, admission facts intact) is left untouched if its generated slug disappeared less than one full A+B cadence cycle ago; once a run finds the same orphaned record still absent from generated `exhibitions.json` after a full cycle has elapsed, that run deletes it. This gives the copy/press work a grace window instead of an instant hard delete, without accumulating stale records forever, and is wired into ST-4-6a's own verify step (§4.6) as an explicit age check, not just an orphan count.
3. **Collects press weekly** — press-link discovery still runs every week (tied to weekly exhibition discovery, not the museum-extras halves); this is unchanged from before.

The pipeline stays strictly read-only with respect to curated files throughout — the reconciliation run is a repo-agent job, exactly like C1/C2/ST-3c-1…3.

**Cadence bookkeeping (F12) — mechanism (see §4.5 Q5 for the state-location choice):** a stored `refresh_group: "A"|"B"` field per museum record, computed once (deterministic, alphabetical-by-slug alternation, 15/15 exact on the current 30); `last_refreshed_extras: "YYYY-MM-DD"` (nullable); `next_due: "YYYY-MM-DD"` (the operator's schedule marker for that record). No new file, no pipeline-host state.

- **No "today for all" initialization.** `last_refreshed_extras` is seeded per record from the best available evidence — `_meta.verified` (Table 2) if that date reflects an actual source check, else `null` — never blanket-set to the run date for records that weren't actually reverified. A `null` seed is an honest "never tracked" state, not a false freshness claim.
- **Verification compares changed records + source dates**, not just field presence: a refresh batch's acceptance check must show the specific facts that changed (diff against the pre-batch value) and that `_meta.sources[].url` / `admission.source` dates advanced — a no-op batch that only bumps `last_refreshed_extras` without touching any fact must fail its own acceptance check.
- **New-museum group assignment never reshuffles existing groups.** When a museum is added, it is assigned to whichever group currently has fewer members (ties broken alphabetically); every existing museum's `refresh_group` is left untouched. This trades perfect alphabetical determinism for stability — the review's flagged failure mode (inserting one slug flips every later alphabetical assignment) cannot happen.
- **31+ balance rule.** The two groups are never required to be exactly equal once the set grows past 30 — acceptance only requires `abs(len(A) - len(B)) <= 1` after any addition/removal, checked by the same reconciliation run (item 2 above).

#### 4.4.3 Press fallback [F13]

Three distinct activities were previously conflated into one step; they're now separated so each has its own success/failure definition:

1. **Alternate-URL discovery** — for a press entry whose stored `url` is known or suspected hard-403 (currently-known outlets: DVHN, Leeuwarder Courant, ~5 shows total across both), search the outlet's own site/search for a different URL to the same article (same headline/date/outlet) **before** touching rendering or Wayback. This is genuinely a different URL, not a retry of the same one — a headless re-fetch of the identical link is not "an alternate path."
2. **Rendered access check** — for whichever URL is currently on file (original or the alternate from step 1), attempt a rendered/headless fetch if available tooling supports it. Success statuses: HTTP 200 with article content present after JS execution, or a same-outlet redirect (3xx) that lands on 200 content — record the **final** URL after redirect, not the pre-redirect one. Explicit failure statuses, each with its own `accessNote` vocabulary term: `http_403` (hard block), `http_404`/`http_410` (removed), `timeout` (no response within the tool's limit), `paywall` (200 but content gated — detect via outlet-known paywall markers, not a guess), `redirect_loop`.
3. **Archive fallback** — only after step 2 fails: retry via the Wayback Machine (`web.archive.org`) for an archived snapshot URL of whichever URL is currently on file. Record the **archive URL** separately from the live URL — never overwrite the live `url` field with an archive URL; `accessNote` gets `archived` and a new field records which URL is the archive vs the original (see Table 3, §4.4.1: `subjectOf[].archiveUrl`, nullable — the only shape, since ST-4-2's big-bang commit already removed legacy `press[]`, owner Q4).
4. **Terminal state** — if both step 2 and step 3 fail, keep the original link **as-is** (never drop it) and record `verifiedAccess: false` + the specific failure `accessNote` from step 2's vocabulary. Successes (step 2 or step 3) record `verifiedAccess: true` and, for step-3 successes, `accessNote: "archived"`.

**Original-vs-archive display rule:** the site always links to the **original** `url` (unchanged visitor-facing behavior); `archiveUrl` is metadata only, not rendered as a second visible link this phase (a future phase could surface "view archived copy" — out of scope here).

This is a bounded, one-alternate-URL-attempt + one-rendered-check + one-Wayback-check-per-outlet-per-show effort (§4.5 Q9) — not an open-ended scrape-around-403 project, but auditing and recording an honest outcome for all 92 entries (batched, not sampled) is real work: sized **L** (§4.6 ST-4-9, F14), not S.

#### 4.4.4 Navigation fix + Home button + banner [F5, F16]

Three coupled decisions (§4.5 Q1–Q3, **all answered by the owner 2026-09-13**), one shared file scope (`static/css/custom.css`, `layouts/partials/navigation.html`; never `themes/huguette`):

1. **Kill the paint bug — decided (Q1): shadow-kill now.** The operator's reproduced-live one-liner is the plan's approach for ST-4-10: `body > nav + nav { box-shadow: none !important; }` + optional `body > nav:first-of-type { z-index: 43 }` — the only variant actually confirmed against the pinned stylesheet with before/after screenshots (`docs/plan-review-phase4.md`); ST-4-13's full browser/keyboard QA gate (F11) is the acceptance evidence for this fix, not an open decision. **Deferred, logged for a later phase:** the `.contentnav`-style static-in-flow alternative (removes the float-stacking bug class entirely, but needs a `body` top-padding reset and overrides for **both** `nav+*` margin instances, per the spec below) is not built this phase — revisit it once the owner has seen the shadow-kill fix live; see also the §4.4.4 item 3 note on its interaction with the Q3 banner decision, and the residual-option row in §4.11. Its spec, kept for that future revisit: extending `body>nav.contentnav, header nav.contentnav { position: static; z-index: auto; box-shadow: none; }` (`static/css/custom.css:26-32`) to both header bars requires **two resets**: (a) `body`'s existing top padding (from the theme, sized for the floated/absolute nav) reset to whatever the static-in-flow bars now actually occupy, and (b) **both** `nav+*` margin instances — the theme's `nav+* { margin-top: 3rem; }` rule fires between nav 1/nav 2 and again between nav 2/content once both bars are in normal flow, so that future CSS block must explicitly override `margin-top` on the relevant `nav+*` matches, not just `position`/`z-index`/`box-shadow`. Either way: **no theme edit**, `static/css/custom.css` only.
2. **Home button — decided (Q2): visibility fix only, no extra styling.** The already-first "Home" menu link becomes visible via item 1's nav fix; no chip, border, or background treatment ships this phase. ST-4-11 is a no-op closeout (§4.6) — removed from the critical path. One line kept for later: a chip can be requested once the owner sees the visible menu live.
3. **Top bar vs banner — decided (Q3): photo banner.** The owner picked a licensed photo banner over the plain-top-bar status quo — the "subtle CSS-only band, no photo" alternative text below is now dead (owner did not pick it; a real photograph ships, not a color/gradient band). `headerimage.html` (theme-owned) only activates on `header:` front matter, which no page sets today, and most routes (`/museums/<slug>/`, `/museums/<slug>/exhibition/<slug>/`, `/kalender/<month>/`) are generated by content **adapters**, not `content/{nl,en}/*.md` front matter — editing markdown front matter alone covers only the hand-authored pages (`_index.md`, `about.md`, `calendar.md`, `museums.md`). The full banner rollout (ST-4-12, §4.6) therefore needs: (i) the adapter code that creates museum/exhibition/month pages to set an equivalent `header:`-style parameter itself (not front matter, since those pages have none) — full adapter-generated page coverage, not just the hand-authored four; (ii) a `layouts/partials/headerimage.html` **override in this repo** (never editing the theme copy), since the theme's own partial's hard-coded `50vh` inline image treatment (`themes/huguette/layouts/partials/headerimage.html:3-16`) is being kept or adapted, not replaced by a CSS-only band; (iii) responsive dimensions specified for desktop and the 375px mobile width (no fixed-height image that overflows or crops badly at mobile width); (iv) a recorded license/attribution for the chosen photo. **Hard dependency, blocking:** the banner subtask cannot start until the owner has picked a licensed image from an operator-prepared shortlist (new subtask ST-4-12a, §4.6) — until that pick happens, **no banner renders** (status quo, plain top bar, exactly as today); this is not a soft "nice to have first," it is a blocking `Depends:` on ST-4-12 itself. **Interaction with Q1:** both the banner rollout and the deferred static-in-flow nav revisit (item 1) touch header layout — if the static-in-flow option is picked up in a later phase, re-verify the banner's responsive dimensions and the `nav+*` margin resets together, since the banner partial override and the nav's own vertical spacing both sit in the same header region.

Every combination must pass the full-page QA gate in §4.6 ST-4-13: every page type (home, calendar index + one month page, museums index, one museum detail, one exhibition detail, about) × both languages × a mobile width, confirming the menu text (including "Home") is actually visible/paints correctly, not just present in the DOM.

#### 4.4.5 Copy pass (light) — after the functional work

Runs only after §4.4.1–4.4.4 land (nav labels, any new i18n strings, and the schema migration's visible surface, if any, need to be stable first). Scope: (a) display "Musea"/"Museums" wording vs the `/museums/` URL — confirm the phase-3b D7 rename (NL label "Musea", URL word "museums" in both languages) is still the intended visitor-facing pairing, and fix any surrounding copy that reads oddly against it; (b) informal-tone nits left over from the ST5 pass; (c) no full rewrite, no new pages, no URL changes.

**Known gap (F19):** ST-4-14's `Depends:` line names "owner-approved copy nits list," but that list does not exist yet anywhere in this repo — it is not a stale reference to a prior artifact, it is a to-be-created input. ST-4-14 cannot start until the owner supplies or approves that list; §4.6's dependency line states this explicitly rather than implying the list already exists.

#### 4.4.6 3d leftovers

Per §4.3's recon: (a) optional mailto share (needs `share_mailto_subject`/body i18n keys — small, well-scoped); (b) CTA/booking slot (unbuilt, no schema reservation exists); (c) Telegram hooks (no prior spec anywhere in this repo — owner-introduced fresh in this brief). §4.5 Q6 asks whether to fold slice (a) into phase 4 (small, additive, no new external dependency) while leaving (b)/(c) explicitly deferred (both need their own scoping — a booking-button design and a Telegram integration are each their own decision set, not a phase-4-sized add-on), or to leave all three deferred as a block.

#### 4.4.7 Legacy-field removal — folded into the big-bang commit (superseded by owner Q4) [F7]

**Superseded, kept as the historical record of what F7 originally flagged and how the plan closed it.** Q4/§4.11 previously promised "a follow-up commit" removing the legacy flat fields once templates were cut over, but no subtask ever did it, and the acceptance checklist explicitly allowed either state — leaving a permanent two-source-of-truth window with no promise ever enforced. The review's own proposed fix (build below, superseded 2026-09-13) was a **parallel-fields** staging with two dedicated post-cutover removal subtasks, `ST-4-4b`/`ST-4-4c`, one per curated file, each gated on one clean §4.8 run after template cutover and independently revertible.

**Owner Q4 (2026-09-13) overrode that recommendation and chose big-bang instead:** data reshape and template cutover for each curated file now land in the **same** commit, and legacy-field removal is not a separate step at all — it happens in that same big-bang commit, proven safe beforehand by the mandatory pre-commit losslessness gates (§4.4.1.5). There is no parallel-fields window to leave open and therefore nothing for a follow-up subtask to close: **`ST-4-4b` and `ST-4-4c` do not exist in this plan** (dropped, along with the parallel-fields staging they depended on); their removal work is subsumed into ST-4-2 (§4.6). F7's original concern — a promised removal step that never got wired into a real subtask — is resolved by construction rather than by scheduling a follow-up: there is no window during which legacy and schema.org-shaped keys coexist, so there is nothing left to schedule.

### 4.5 DECISIONS FOR OWNER

**All questions answered 2026-09-13** (owner) — every `Answer (owner, 2026-09-13):` line below is authoritative and is folded into the relevant subsection (§4.4.x) and subtask (§4.6) elsewhere in this plan; no ST-4 build run may start from an unresolved question, and none remain. Renumbered Q1–Q16 (was Q1–Q10) to fold in the six missing decisions the review found (F15) without losing track of the originals — every cross-reference elsewhere in this plan uses these numbers.

1. **Navigation CSS treatment?**
   **Recommendation (was the alternative):** the operator's exact one-line kill, reproduced live against the pinned stylesheet with before/after screenshots — `body > nav + nav { box-shadow: none !important; }` + optional `body > nav:first-of-type { z-index: 43 }`. This is the only variant actually proven on this repo's CSS; smallest diff; keeps the float design.
   **Alternative (was the recommendation):** extend the `.contentnav` static-in-flow treatment (PR #8 precedent) to both header bars — removes the float-stacking bug class entirely, but is a **larger, not-yet-visually-proven** change: per §4.4.4 item 1 it additionally needs an explicit `body` top-padding reset and overrides for **both** `nav+*` margin instances (nav1→nav2 and nav2→content), or it introduces three oversized vertical gaps instead of fixing the overlap.
   **Answer (owner, 2026-09-13):** shadow-kill now (ST-4-10, with the ST-4-13 browser/keyboard QA gate as acceptance evidence). The static-in-flow alternative is not built this phase — logged as a future note to revisit once the owner has seen the shadow-kill fix live (§4.4.4 item 1, §4.11).

2. **Home-button treatment?**
   **Recommendation:** a visually distinct chip (border/background) on the existing first "Home" `<li>`, via a class hook in `navigation.html` — no new markup logic, no JS.
   **Alternatives:** (a) bold/larger/differently-colored plain text, least "buttony" but zero layout risk; (b) a persistent fixed-position corner button independent of the nav bar — most unmistakable, but reopens fixed-position/mobile-overlap complexity the site doesn't have today; (c) rely on the visibility fix alone (no extra styling) — risks not meeting "unmistakable."
   **Answer (owner, 2026-09-13):** visibility fix only (alternative c) — no extra styling. ST-4-11 is closed-by-design as a no-op closeout, removed from the critical path; a chip can be requested later once the owner sees the visible menu live (§4.4.4 item 2).

3. **Top-bar / banner treatment?**
   **Recommendation:** plain light top bar (status quo, no `header:` front matter anywhere) — zero image sourcing/licensing work, matches the site's existing no-stock-photo minimalism.
   **Alternative — two sub-options, one chosen, one now dead:** a header treatment applied consistently across **every** page, both languages, either (i) an owner-supplied/approved **photo** — **chosen, see the Answer below** — or (ii) a CSS-only color/gradient band with no photo — **dead; the owner did not pick this, a real photograph ships instead.** Per §4.4.4 item 3, most routes are adapter-generated (not `content/*.md` front matter), so either sub-option requires adapter changes + a `layouts/partials/headerimage.html` override in this repo (theme's own partial hard-codes a `50vh` image treatment) + specified responsive dimensions; the chosen photo sub-option additionally needs licensed asset sourcing — materially bigger than "add `header:` to markdown files."
   **Answer (owner, 2026-09-13):** photo banner ("we'd pick and license an image together") — the CSS-only band sub-option is dead; a real licensed photograph ships. ST-4-12 is expanded to full banner scope (adapter-generated page coverage, `headerimage.html` override, responsive dimensions, license record) and is **blocked** on a new operator dependency, ST-4-12a (banner asset shortlist, 3–5 licensed candidates, for the owner to pick from) — until that pick happens, no banner renders (status quo). Interacts with Q1's deferred static-in-flow revisit — see §4.4.4 item 3's note.

4. **Structured-data migration staging — big-bang vs parallel fields?**
   **Recommendation (not chosen):** parallel fields — add the schema.org-aligned nested keys alongside the legacy flat keys in one commit per curated file (ST-4-2/ST-4-3), cut templates over to read only the new keys (ST-4-4), then **remove** the legacy keys in dedicated follow-up commits (ST-4-4b/ST-4-4c, §4.4.7) once templates are proven on the pin for one verification cycle. Every commit stays independently revertible (mirrors the 3c coordinate-batch discipline); the removal step is no longer optional/unscheduled.
   **Alternative (chosen):** big-bang — one commit (or a small, domain-split set of commits) rewrites shape + templates together; fewer/no intermediate states, but a template bug and a data-shape bug become indistinguishable in the diff, and rollback must revert both together.
   **Answer (owner, 2026-09-13):** big-bang — the owner overrode the parallel-fields recommendation. `ST-4-2`, the old `ST-4-3`, and the old `ST-4-4` are merged into one big-bang migration path (data reshape + template cutover together); `ST-4-4b`/`ST-4-4c` (legacy-removal machinery) are dropped entirely — there is no legacy-field window to close. `ST-4-1` (the docs-only schema contract) is unaffected and stays a separate, earlier subtask. **Mandatory pre-commit gates (no exceptions):** the full-population losslessness proof (all 30/146/398/102/187/92, §4.4.1.5), the named fixtures (2 null-accepted cards, 5 plural-notes museums), and a scratch render-equality check (staged tree vs. pre-migration build, byte-identical except the 5 plural-notes pages and the 13 targeted snapshot pages) — all three must pass on the **staged, uncommitted** tree before any big-bang commit lands. **Rollback:** revert the big-bang commit(s) atomically — see the rewritten §4.10 commit table. **Commit split (justified):** two commits, split by data domain, not by data-vs-template — (1) `data/museums_info.json` reshape + every museum-only template reader (`museum-info.html`, `museum-page.html`, `museums.html`, `museum-map-ready.html`, `head.html`), (2) `data/exhibitions_info.json` reshape + every exhibition-only template reader (`exhibition-info.html`, `exhibition-page.html`) — justified because the two curated files and their template readers are already file-disjoint (confirmed by `grep -rn 'museums_info\|exhibitions_info' layouts/`, §4.3), so splitting along that existing seam keeps each commit's revert scoped to one curated file and its exclusive templates without reopening a cross-file two-source-of-truth window within either domain. **Residual risk, recorded honestly (§4.11):** losing the parallel-fields window means a template bug and a data-shape bug are no longer separable in the diff for whichever domain's commit introduces one — this is a real, accepted cost of the owner's override, mitigated (not eliminated) by the three mandatory pre-commit gates above, not by a post-commit safety net.

5. **Cadence implementation — week-A/B state file vs deterministic half-split?**
   **Recommendation:** a stored `refresh_group: "A"|"B"` field per museum in `museums_info.json` itself, seeded once (alphabetical-by-slug alternation on the current 30) and thereafter maintained by the smaller-group-wins rule for additions (§4.4.2, F12) — self-documenting, survives clones, no drift risk, never reshuffles existing assignments.
   **Alternative:** a separate week-A/B state file (e.g. `data/refresh_state.json`) tracking "next due" group — decouples the rotation pointer from the museum records, but can silently drift if museums are added/removed without updating the state file too.
   **Answer (owner, 2026-09-13):** `refresh_group` field in `museums_info.json` (recommendation) — keep.

6. **3d fold — fold slice (a) in, or keep all three leftovers deferred?**
   **Recommendation:** keep all three deferred — phase 4 already carries six workstreams; the structured-data migration is the load-bearing piece and shouldn't compete with new share/CTA/Telegram scope this phase.
   **Alternative:** fold in only the smallest leftover — the already-spec'd mailto share (D11, needs one new i18n key pair) — as a single extra subtask (§4.6 ST-4-15a), leaving CTA/booking and Telegram fully deferred (each needs its own future scoping pass).
   **Answer (owner, 2026-09-13):** all three 3d leftovers deferred (recommendation) — ST-4-15 runs its defer branch; mailto, CTA/booking, and Telegram all stay explicitly out of phase 4.

7. **Curated filenames — keep `museums_info.json`/`exhibitions_info.json`, or rename to signal the new contract?**
   **Recommendation:** keep the current names — a rename touches every `.Site.Data.*` template reference and this repo's docs for no visitor-facing benefit; only the internal shape changes.
   **Alternative:** rename (e.g. a `_v2` suffix, as would have marked a staged migration under the non-chosen parallel-fields option, §4.5 Q4) — clearer at a glance that the shape changed, but adds churn independent of the actual migration risk.
   **Answer (owner, 2026-09-13):** keep filenames (recommendation).

8. **Bilingual leaf fields inside a schema.org-shaped store?**
   **Recommendation:** keep bilingual values as an internal `{ "nl": …, "en": … }` sub-object wherever schema.org expects one string (as stated in §4.4.1) — deliberate, documented deviation from literal JSON-LD, acceptable because serving our own JSON-LD is deferred (non-goal #2).
   **Alternative:** pick one authoritative language per schema.org node and keep the other as a documented sibling key outside the schema-shaped subtree — more literally correct, but fragments the file and complicates every template lookup for no near-term benefit (nothing serves JSON-LD yet).
   **Answer (owner, 2026-09-13):** bilingual `{nl, en}` sub-objects (recommendation).

9. **Press-link fallback: effort budget and outcome contract?** (expanded per F13)
   **Recommendation:** the three-step ladder in §4.4.3 (alternate-URL discovery → rendered access check → Wayback archive check), one attempt per step per outlet per show; the explicit success-status/failure-vocabulary/redirect/paywall/archive-URL rules in §4.4.3 are the contract, not a placeholder; keep link-only with `verifiedAccess: false` + a specific failure `accessNote` if all three fail; never overwrite the live `url` with an archive URL. Sized **L** (§4.6 ST-4-9, F14) to reflect auditing all 92 entries honestly, not S.
   **Alternative:** skip discovery/retries entirely and mark link-only immediately for every hard-403 outlet — faster, but skips the owner's explicit ask to attempt alternates first.
   **Answer (owner, 2026-09-13):** the three-step ladder (recommendation), applied to `subjectOf[]` only — since ST-4-2's big-bang commit (Q4) already removed legacy `press[]`, ST-4-9 has a single field shape to write, not a mirrored pair.

10. **Pipeline-host scope boundary (item 1(b), JSON-LD-consuming scraper) — docs-only handoff, or does the owner want to grant pipeline-host access for a repo agent run?**
    **Recommendation:** docs-only handoff (§4.6 ST-4-5) — this repo's agents have no access to `/opt/data/museum_tracker/`; the operator implements the scraper change there, on their own schedule, exactly like phase 2's D5.
    **Alternative:** the owner arranges pipeline-host access for an agent session so a phase-4 (or phase-5) run implements it directly — a bigger access/scope change, not assumed by this plan.
    **Answer (owner, 2026-09-13):** docs-only pipeline handoff (recommendation).

11. **Address / multi-venue handling — `venueNote` sidecar, or reject non-conforming records from the `PostalAddress` split?** *(new, F2/F15)*
    **Recommendation:** the `address_v2.venueNote` rule in §4.4.1.4 — parse the postal triple where it exists, preserve everything else verbatim in `venueNote`, and keep `address_display` as the unconditional verbatim backstop. Handles all 6 flagged records (H'ART, Boijmans, Kunsthal, MORE, Kröller-Müller, Volkenkunde) without a record-by-record special case.
    **Alternative:** leave `address_v2.streetAddress` etc. unset (null) for any record the parser can't confidently split, relying only on `address_display` — simpler rule, but loses the structured `PostalAddress` benefit for 6 of 30 museums (20%) instead of just the non-postal remainder.
    **Answer (owner, 2026-09-13):** `venueNote` sidecar + `address_display` display backstop (recommendation).

12. **Nullable card acceptance + plural-note normalization — three-state enum and note-field merge, or something else?** *(new, F2/F15)*
    **Recommendation:** the rule already baked into Tables 2b (§4.4.1): three-state `acceptance` enum (`accepted`/`not_accepted`/`unknown`) replacing boolean/null, and `note_*`/`notes_*` merged into one `description.{nl,en}` leaf per card regardless of which spelling the source record used. Losslessly covers the 2 null-accepted cards and 27 plural-note cards; also fixes the pre-existing `museum-info.html` plural-notes display bug as a side effect of the template cutover.
    **Alternative:** keep `accepted` boolean-only and force the 2 null cases to `false` (matches current template's ternary fallback exactly) — simpler enum, but is the exact "null collapse" the review flagged as a fact-loss bug; not recommended.
    **Answer (owner, 2026-09-13):** three-state acceptance enum + note-field merge (recommendation).

13. **Sidecar vs full `ExhibitionEvent`?** *(new, F3/F15 — blocked the old ST-4-3, now the exhibitions-domain commit inside ST-4-2)*
    **Recommendation:** keep `exhibitions_info.json` as the extras/provenance **sidecar** (§4.4.1.6(a)) — no root `@type`, no duplicated title/dates/museum/city/url; the existing render-time join to generated `exhibitions.json` is unchanged. Zero drift risk because nothing is duplicated.
    **Alternative:** promote it to a complete `ExhibitionEvent` (§4.4.1.6(b)) with `@type`, joined `name`/`startDate`/`endDate`/`location`/`url` computed at render time (never stored twice) — more schema.org-literal, useful only once JSON-LD is actually served (non-goal #2 this phase); adds a cross-file render-time join for no current visible benefit.
    **Answer (owner, 2026-09-13):** sidecar, not full `ExhibitionEvent` (recommendation) — the exhibitions-domain commit in ST-4-2 (§4.6) implements only the sidecar shape (§4.4.1.6(a)); the full-`ExhibitionEvent` fork (§4.4.1.6(b)) is explicitly not built this phase.

14. **Schema-2 release order / rollout safety?** *(new, F4/F15 — pipeline-host handoff content, ST-4-5)*
    **Recommendation:** the additive-only Table 1 shape plus the 6-step dual-write → fixture-validate → deploy-compatible-templates → switch-producer → verify-live → remove-schema-1-later sequence in §4.4.1.7. No repo template needs to change to tolerate schema 2 (it adds a key nothing reads yet), so steps 3 stays a no-op until a future phase actually consumes `@type`.
    **Alternative:** a hard cutover (pipeline switches producer the same week a repo template starts requiring `@type`) — faster to land, but removes the dual-write safety window and makes a pipeline-side mistake immediately break the live site with no fixture-validated fallback.
    **Answer (owner, 2026-09-13):** additive schema-2 + the 6-step rollout sequence (recommendation) — this is the literal content ST-4-5's pipeline-host handoff doc transcribes.

15. **Orphaned curated-record retention rule?** *(new, F6/F15 — feeds the reconciliation run, §4.4.2)*
    **Recommendation:** retain an orphaned `exhibitions_info.json` record (press links, admission facts) for one full cadence cycle after its generated slug disappears, then delete — gives press/copy work a grace window instead of instant loss, without unbounded accumulation.
    **Alternative:** delete immediately on the next reconciliation run once the generated slug is gone — simplest rule, matches today's *accidental* parity exactly, but a show that briefly drops and reappears (schedule correction) loses its curated facts and has to be re-collected from scratch.
    **Answer (owner, 2026-09-13):** one-cadence-cycle grace for orphans (recommendation) — wired explicitly into the §4.4.2 reconciliation run and ST-4-6a below: an orphaned `exhibitions_info.json` record is retained through exactly one full A+B cadence cycle after its generated slug disappears, then deleted on the reconciliation run that finds it still orphaned past that window.

16. **Full-population migration proof requirement, and the generated-copy `inLanguage` gap?** *(new, F9/F15, grouped)*
    **Recommendation, proof requirement:** the full-population losslessness proof in §4.4.1.5 (all 30/146/398/102/187/92, not a sample) is mandatory before ST-4-2's commits may be committed — no reduced-sample "spot check only" substitute.
    **Recommendation, `inLanguage`:** generated `exhibitions.json`'s `title`/`description` are single-value strings authored once and rendered verbatim on **both** the NL and EN site (confirmed: `exhibition-page.html` renders `$ex.description` unconditionally, no per-language branch) — there is no `inLanguage` this phase can honestly assign per site-language page. Record this as a known, accepted limitation of the generated store (out of scope to fix — would require a pipeline-host authoring change, item 1(b)/1(c) territory) rather than silently defaulting `inLanguage` to the current page's language, which would be a false claim once JSON-LD is ever served.
    **Alternative (proof):** sample-based verification (e.g. 5 representative museums) — faster, but is exactly the "a few types/counts, not note text/identifiers/nullable states" gap the review flagged; not recommended.
    **Alternative (`inLanguage`):** have the pipeline mark every generated title/description with the language it was actually authored in (adds one field, item 1(b)/1(c)-adjacent pipeline-host work) — solves the gap properly, but is out of this phase's boundary (§4.0) without an explicit owner ask to add pipeline-host scope.
    **Answer (owner, 2026-09-13):** **Q16a** (proof requirement) — full-population losslessness proof is a hard gate (recommendation); no sample-based substitute, ever, and it now runs pre-commit under the Q4 big-bang restructure (§4.4.1.5). **Q16b** (`inLanguage`) — record the generated-copy language gap as an accepted limitation (recommendation); no pipeline-side fix scoped this phase.

If an owner answer changes a surface, file scope, or expected count in any subtask below (especially Q4/Q5/Q6/Q13/Q14/Q15), update the affected subtask before that run starts; do not improvise around a stale acceptance command.

### 4.6 Ordered one-run subtasks

Workstream A (structured data) is serialized (ST-4-1, then ST-4-2's big-bang migration, then ST-4-5 — owner Q4 dropped the old ST-4-3/ST-4-4/ST-4-4b/ST-4-4c staging entirely; see §4.4.7). Workstream B (cadence, ST-4-6, 6a…8) depends on A's shape landing first so cadence bookkeeping isn't added twice. Workstream C (press fallback, ST-4-9) and Workstream D (navigation, ST-4-10, 11 (no-op), 12a, 12, 13) are file-disjoint from A/B and from each other and may run in parallel once their own owner questions are answered — ST-4-12 additionally blocks on ST-4-12a's owner-pick gate. Workstream E (copy, ST-4-14) and F (3d, ST-4-15) run last per §4.4.5/§4.4.6. ST-4-16 closes the phase.

**Operator tool pin (F21) — applies to every verify script below:** every `hugo` invocation in this section uses the pinned binary, never a bare `hugo` that might resolve to whatever's on `PATH`:

```sh
HUGO="${HUGO:-/opt/data/museum_tracker/bin/hugo}"
command -v "$HUGO" >/dev/null 2>&1 || HUGO=hugo   # local-dev fallback; the run log must still say which one was used
"$HUGO" version   # print once per run; must report v0.166.0+extended on the operator's own re-run
```

Every `hugo --minify`/`hugo server` below is shorthand for `"$HUGO" --minify`/`"$HUGO" server` with the two lines above already run. Verification stays Python/shell only — no `jq` (a clean `PATH` doesn't have it; nothing here needs it).

#### ST-4-1 — Structured-data target schema spec (docs only) — transcribe and validate, not design [F1, F14]

- **Model:** `composer-2.5` · **Size:** L *(resized from M — F14: this is now a full transcription of Tables 1–3 plus five owner-decision branches, not a short illustrative doc)* · **Depends:** owner Q4, Q7, Q8, Q11, Q12, Q13, Q14, Q16
- **Scope:** new `docs/structured-data-schema.md` only. No data or template changes.
- **Work:** **transcribe and validate** §4.4.1's Tables 1, 2, 2b, 3 (already the authoritative, owner-approvable mapping — this subtask does not invent target keys) into `docs/structured-data-schema.md`, verbatim field-for-field, plus: the address/venueNote rule (§4.4.1.4) per the Q11 answer; the card-acceptance/note-normalization rule (§4.4.1.5-adjacent Table 2b) per Q12; the sidecar `ExhibitionEvent` shape Q13 picked (§4.4.1.6(a) only — the full-`ExhibitionEvent` fork is not built); the schema-2 rollout sequence (§4.4.1.7) per Q14; the `inLanguage` limitation note per Q16. State the **big-bang** migration plan (Q4 answer) as the literal commit sequence ST-4-2 (two domain-split commits: museums, then exhibitions, each reshape + template cutover together) will follow — no parallel-fields staging, no separate legacy-removal step.
- **Verify:**

```sh
test -f docs/structured-data-schema.md
grep -q '"@type": "Museum"' docs/structured-data-schema.md
grep -q '"@type": "Offer"' docs/structured-data-schema.md
grep -q '"@type": "NewsArticle"' docs/structured-data-schema.md
grep -q 'schema.*2' docs/structured-data-schema.md
grep -q 'address_v2' docs/structured-data-schema.md
grep -q 'venueNote' docs/structured-data-schema.md
grep -q 'acceptance' docs/structured-data-schema.md
grep -qi 'not_accepted' docs/structured-data-schema.md
grep -qi 'unknown' docs/structured-data-schema.md
# no placeholder text carried over from the pre-review draft:
! grep -n 'or the exact\|exact selector\|TODO' docs/structured-data-schema.md
git diff --name-only  # expect only docs/structured-data-schema.md
```

- **Commit:** `docs(data): add structured-data target schema spec`

#### ST-4-2 — Big-bang structured-data migration (data reshape + template cutover, owner Q4) [F2, F7, F8, F9]

**Merged subtask (owner Q4, 2026-09-13):** the old `ST-4-2` (museums data), `ST-4-3` (exhibitions data), and `ST-4-4` (template cutover) are folded into this single migration path — data reshape and template cutover for each curated file now land **in the same commit**, and legacy-field removal is not a separate step (`ST-4-4b`/`ST-4-4c` are dropped, §4.4.7). **Commit split, justified:** two commits, split by data domain (not by data-vs-template), because the two curated files and their template readers are already file-disjoint (`grep -rn 'museums_info\|exhibitions_info' layouts/`, §4.3) — splitting along that existing seam keeps each commit's revert scoped to one curated file and its exclusive templates, with no cross-file two-source-of-truth window opened within either domain. **Every pre-commit gate in §4.4.1.5 (full-population losslessness proof, named fixtures, scratch render-equality check) must pass on the staged tree before either commit lands** — there is no post-commit follow-up subtask to catch a miss.

##### Commit 1 — museums domain (data + templates together)

- **Model:** capable mid-tier (`cursor-grok-4.6-medium`-class) · **Size:** L · **Depends:** ST-4-1, owner Q4, Q11, Q12
- **Scope:** `data/museums_info.json` **and** every museum-only template reader — `layouts/partials/museum-info.html`, `layouts/_default/museum-page.html`, `layouts/_default/museums.html`, `layouts/partials/museum-map-ready.html`, `layouts/partials/head.html` (confirmed exhaustive for this domain by the grep above). Never `data/exhibitions.json` (unchanged schema 1). Never `themes/huguette`.
- **Work:** for all 30 records, replace the flat legacy fields with the schema.org-shaped subtree per Tables 2/2b (§4.4.1) **in the same commit**: `address_display` + `address_v2` (`PostalAddress` + `venueNote` per §4.4.1.4), `geo`, `offers[]` (from `cards[]`, three-state `acceptance`, merged `note_*`/`notes_*` → `description.{nl,en}`, retained `identifier`), `_visitor.{hours,transit,parking,access,pricing}.{nl,en}`, `_meta.{sources[],notes[],verified}` — and delete `address`, `lat`, `lon`, `hours_nl/en`, `transit_nl/en`, `parking_nl/en`, `access_nl/en`, `pricing_nl/en`, `description_nl/en`, `cards[]`, `sources[]`, `notes[]`, `verified` (grep-verified no template still reads them before deleting). Point every museum-domain template read at the new keys, including `museum-map-ready.html`'s `lat`/`lon` reads → `geo.latitude`/`geo.longitude`. **Fix the pre-existing plural-notes display bug as part of this same commit** (§4.4.1, Table 2b note): once `museum-info.html` reads `offers[].description.{nl,en}`, Foam/Boijmans/Kunsthal/Nederlands Fotomuseum/Museum MORE's previously-blank card notes must now render. Rendered HTML output must be **pixel/text-identical** to pre-migration for every other card/page; the five plural-notes museums are the one **intentional** rendering change, excluded from the byte-identical diff and checked separately.
- **Pre-commit gate (run on the staged tree, before this commit):** the full §4.4.1.5 losslessness proof (before/after fact diff, named fixtures, scratch render-equality build-and-diff) — all three, full population, no sample.
- **Verify:**

```sh
python3 - <<'PY'
import json
d = json.load(open("data/museums_info.json"))
assert len(d) == 30
card_total = offer_total = 0
null_accept_seen = set()
legacy = {"address","lat","lon","hours_nl","hours_en","transit_nl","transit_en","parking_nl","parking_en",
          "access_nl","access_en","pricing_nl","pricing_en","description_nl","description_en",
          "cards","sources","notes","verified"}
for slug, v in d.items():
    assert v.get("@type") == "Museum", slug
    assert not (legacy & set(v)), (slug, legacy & set(v))  # big-bang: legacy keys gone in this same commit
    addr = v["address_v2"]
    assert addr["@type"] == "PostalAddress" and addr.get("addressCountry") == "NL", slug
    assert v["address_display"], slug  # verbatim losslessness backstop (checked against the pre-commit snapshot)
    geo = v["geo"]
    assert geo["@type"] == "GeoCoordinates", slug
    offers = v["offers"]
    assert offers, slug
    for o in offers:
        assert o["@type"] == "Offer" and o["category"] == "discount-card", slug
        assert o["acceptance"] in ("accepted", "not_accepted", "unknown"), (slug, o["identifier"])
        if o["acceptance"] == "unknown":
            null_accept_seen.add(slug)
    card_total += len(offers); offer_total += len(offers)
    for lang in ("nl", "en"):
        assert v["_visitor"]["hours"][lang], slug
    assert v["_meta"]["verified"], slug
assert card_total == offer_total == 146, card_total
assert null_accept_seen == {"huis-marseille", "museum-kranenburgh"}, null_accept_seen
print("museums_info.json big-bang migration: 30/30, offers: 146, legacy keys gone, null-accept fixtures OK")
PY
set -o pipefail
hugo --minify --destination /tmp/phase4-before  # run BEFORE this commit on the pre-migration tree, keep it
# after staging this commit's changes:
hugo --minify 2>&1 | tee /tmp/phase4-st2-build.log
test "$(grep -ci '^WARN' /tmp/phase4-st2-build.log)" = 0
diff -rq /tmp/phase4-before public \
  -x 'foam' -x 'museum-boijmans-van-beuningen' -x 'kunsthal' \
  -x 'nederlands-fotomuseum' -x 'museum-more'
for slug in foam museum-boijmans-van-beuningen kunsthal nederlands-fotomuseum museum-more; do
  grep -q 'entrance_cards\|kortingskaarten' "public/museums/$slug/index.html"
  diff -q "/tmp/phase4-before/museums/$slug/index.html" "public/museums/$slug/index.html" >/dev/null && \
    { echo "FAIL: $slug note text unchanged, plural-notes bug not fixed"; exit 1; }
done
test -f public/museumtips.ics -a -f public/closing-soon.ics

# AGENTS.md missing-coordinate fixture (removed / explicit null / string / out-of-bounds) — re-run mandatory,
# readiness inputs moved from flat lat/lon to geo.latitude/geo.longitude:
FIXTURE=/tmp/museumtips-phase4-coord-fixture
rm -rf "$FIXTURE" && cp -a . "$FIXTURE" && cd "$FIXTURE"
python3 - <<'PY'
import json, copy
d = json.load(open("data/museums_info.json"))
slug = next(iter(d))
cases = {}
a = copy.deepcopy(d); del a[slug]["geo"]; cases["removed"] = a
b = copy.deepcopy(d); b[slug]["geo"]["longitude"] = None; cases["null"] = b
c = copy.deepcopy(d); c[slug]["geo"]["longitude"] = "4.885219"; cases["string"] = c
e = copy.deepcopy(d); e[slug]["geo"]["latitude"] = 90.0; cases["outofbounds"] = e
for name, data in cases.items():
    json.dump(data, open(f"data/museums_info.json.{name}", "w"), indent=2, ensure_ascii=False)
print("fixture slug:", slug)
PY
for case in removed null string outofbounds; do
  cp "data/museums_info.json.$case" data/museums_info.json
  hugo --minify --destination "/tmp/mc-$case"
  page="/tmp/mc-$case/museums/$(python3 -c "import json;print(next(iter(json.load(open('data/museums_info.json.$case')))))")/index.html"
  grep -q 'Kaart niet beschikbaar\|Map unavailable' "$page"
  ! grep -q 'leaflet.css\|leaflet.js\|museum-map.js' "$page"
done
cd - >/dev/null && rm -rf "$FIXTURE" /tmp/mc-removed /tmp/mc-null /tmp/mc-string /tmp/mc-outofbounds

MAP_PAGES=$(grep -rl 'data-lat=' public --include='*.html' | wc -l | tr -d ' ')
echo "map-ready pages: $MAP_PAGES"  # record in §4.12; compare to pre-migration count, must be equal
for p in public/index.html public/en/index.html public/kalender/index.html public/en/calendar/index.html \
         public/over/index.html public/en/about/index.html; do
  ! grep -q 'leaflet.css\|leaflet.js\|museum-map.js' "$p"
done
git diff --name-only  # expect only data/museums_info.json + the museum-domain template files listed above
```

- **Human gate:** spot-check every `PostalAddress`/`venueNote` split against the original address string (30 records, from the pre-commit before-facts snapshot) — the 6 flagged non-conforming addresses (H'ART, Boijmans, Kunsthal, MORE, Kröller-Müller, Volkenkunde) get an explicit second look.
- **Commit:** `feat(data+templates): big-bang migrate museums_info.json + museum templates to schema.org shape`

##### Commit 2 — exhibitions domain (data + templates together)

- **Model:** capable mid-tier (`cursor-grok-4.6-medium`-class) · **Size:** M · **Depends:** ST-4-1, Commit 1 above (sequential, per the domain-split justification), owner Q4, Q13
- **Scope:** `data/exhibitions_info.json` **and** the exhibition-only template readers — `layouts/partials/exhibition-info.html`, `layouts/_default/exhibition-page.html`. Never `data/exhibitions.json`. Never `themes/huguette`.
- **Work:** for all 187 records, replace the flat legacy fields with `admission_v2` (`Offer`-shaped, `admissionStatus` unchanged enum, bilingual `description`) and `subjectOf: NewsArticle[]` mirroring each `press[]` entry, per Table 3 (§4.4.1) — **sidecar shape only** (§4.4.1.6(a), owner Q13; no root `@type`, no duplicated title/dates/museum/city/url) — and delete legacy `admission`/`press[]` in the same commit. Point `exhibition-info.html`/`exhibition-page.html` at the new keys.
- **Pre-commit gate (run on the staged tree, before this commit):** the full §4.4.1.5 losslessness proof, scoped to the exhibitions-domain facts (admissions, press/`subjectOf`).
- **Verify:**

```sh
python3 - <<'PY'
import json
d = json.load(open("data/exhibitions_info.json"))
assert len(d) == 187
press_total = 0
for slug, v in d.items():
    assert "admission" not in v and "press" not in v, slug  # big-bang: legacy keys gone in this same commit
    assert "@type" not in v, slug  # sidecar shape (Q13) — no root @type
    off = v["admission_v2"]
    assert off["@type"] == "Offer" and off["admissionStatus"] in ("included", "supplement", "not_covered", "unknown"), slug
    articles = v.get("subjectOf", [])
    press_total += len(articles)
    for a in articles:
        assert a["@type"] == "NewsArticle" and a["headline"] and a["url"], slug
assert press_total == 92, press_total
print("exhibitions_info.json big-bang migration: 187/187, press mirrored:", press_total, "— sidecar shape, no legacy keys")
PY
set -o pipefail
hugo --minify --destination /tmp/phase4-before-ex  # pre-migration tree, exhibitions domain
hugo --minify 2>&1 | tee /tmp/phase4-st2b-build.log
test "$(grep -ci '^WARN' /tmp/phase4-st2b-build.log)" = 0
diff -rq /tmp/phase4-before-ex public  # exhibition-domain output must be fully byte-identical (no intentional change here)
git diff --name-only  # expect only data/exhibitions_info.json + the exhibition-domain template files listed above
```

- **Commit:** `feat(data+templates): big-bang migrate exhibitions_info.json + exhibition templates to schema.org shape`

#### ST-4-5 — Generated-data target-schema + JSON-LD-consumption handoff (docs only) [F4]

- **Model:** `composer-2.5` · **Size:** S · **Depends:** ST-4-1, owner Q14
- **Scope:** `docs/structured-data-schema.md` (append a clearly-labeled "pipeline-host handoff" section) + one `AGENTS.md` pointer line. No pipeline-host access, no code.
- **Work:** state, explicitly, that `data/exhibitions.json`'s schema-2 target shape (Table 1, §4.4.1) and the JSON-LD-consuming scraper addition are pipeline-host changes the operator implements outside this repo (§4.0 boundary, §4.5 Q10), with the exact additive-only target shape and the full 6-step rollout sequence (dual-write → fixture-validate → deploy-compatible-templates → switch-producer → verify-live → remove-schema-1-later, §4.4.1.7) plus both pipeline-side and site-side rollback steps, so the operator has a ready-to-implement, ready-to-roll-back spec.
- **Verify:**

```sh
grep -q 'pipeline-host handoff' docs/structured-data-schema.md
grep -q 'additive' docs/structured-data-schema.md
grep -q 'dual-write' docs/structured-data-schema.md
grep -qi 'rollback' docs/structured-data-schema.md
git diff --name-only  # expect only docs/structured-data-schema.md and AGENTS.md
```

- **Commit:** `docs(data): hand off generated-schema + JSON-LD scraper spec to pipeline host`

#### ST-4-6 — Add cadence bookkeeping fields [F12]

- **Model:** `composer-2.5` · **Size:** S · **Depends:** ST-4-2, owner Q5
- **Scope:** `data/museums_info.json` only.
- **Work:** compute and store `refresh_group: "A"|"B"` (deterministic, alphabetical-by-slug alternation on the current 30) on every record. Seed `last_refreshed_extras` from `_meta.verified` (ST-4-2's migrated provenance date) **only where that date reflects an actual source check** — do **not** blanket-set it to today for records that weren't actually reverified this run (F12: no "today for all" initialization). Add `next_due` (nullable ISO date; the operator's next-scheduled-check marker, left `null` until an actual schedule is assigned).
- **Verify:**

```sh
python3 - <<'PY'
import json
d = json.load(open("data/museums_info.json"))
groups = {}
for slug, v in d.items():
    g = v["refresh_group"]
    assert g in ("A", "B"), slug
    assert "last_refreshed_extras" in v, slug  # present, but null is an honest allowed value
    assert "next_due" in v, slug
    groups[g] = groups.get(g, 0) + 1
assert groups == {"A": 15, "B": 15}, groups
# explicitly assert this run did NOT fabricate a blanket "today" freshness claim:
import datetime
today = datetime.date.today().isoformat()
blanket_today = sum(1 for v in d.values() if v.get("last_refreshed_extras") == today)
assert blanket_today < 30, f"{blanket_today}/30 records claim today — looks like a blanket init, not evidence-seeded"
print("refresh_group split:", groups, "— last_refreshed_extras seeded from evidence/null, not blanket today")
PY
hugo --minify
git diff --name-only  # expect only data/museums_info.json
```

- **Commit:** `feat(data): add museum extras refresh_group bookkeeping`

#### ST-4-6a — Curated-record reconciliation run (recurring) [F6]

- **Model:** `composer-2.5` · **Size:** S · **Depends:** ST-4-6, owner Q15 (answered 2026-09-13: one-cadence-cycle grace)
- **Scope:** `data/museums_info.json`, `data/exhibitions_info.json` only. Read-only against `data/exhibitions.json` (join source, never written).
- **Work:** implement and run once (repeatable every cadence cycle thereafter, per §4.4.2): (1) create a stub curated record for any generated slug missing one; (2) apply the **Q15 one-cadence-cycle grace rule** to orphaned `exhibitions_info.json` records — on the run that first finds a curated slug absent from generated `exhibitions.json`, stamp `_meta.orphaned_since` with that run's date (do not delete yet); on any later run, if `_meta.orphaned_since` is set, the slug is still absent from generated data, **and** one full A+B cadence cycle has elapsed since `orphaned_since`, delete the record; if the slug reappears in generated data before that, clear `orphaned_since` (the grace resets — no partial credit toward a future drop); (3) recompute `refresh_group` for any newly-added museum via the smaller-group-wins rule (§4.4.2), never touching existing assignments; (4) assert `abs(len(A) - len(B)) <= 1`.
- **Verify:**

```sh
python3 - <<'PY'
import json, datetime
g = json.load(open("data/exhibitions.json"))
m = json.load(open("data/museums_info.json"))
e = json.load(open("data/exhibitions_info.json"))
gen_museum_slugs = {row["slug"] for row in g["museums"]}
gen_ex_slugs = {row["slug"] for row in g["exhibitions"]}
assert gen_museum_slugs <= set(m), sorted(gen_museum_slugs - set(m))  # no missing curated museum keys
groups = {}
for v in m.values():
    groups[v["refresh_group"]] = groups.get(v["refresh_group"], 0) + 1
assert abs(groups.get("A", 0) - groups.get("B", 0)) <= 1, groups
CADENCE_CYCLE_DAYS = 14  # one full A+B cycle
today = datetime.date.today()
newly_orphaned = stale_but_kept = 0
for slug, v in e.items():
    orphaned_since = v.get("_meta", {}).get("orphaned_since")
    if slug not in gen_ex_slugs:
        assert orphaned_since, (slug, "orphaned with no orphaned_since stamp — Q15 grace rule not applied")
        age_days = (today - datetime.date.fromisoformat(orphaned_since)).days
        assert age_days < CADENCE_CYCLE_DAYS, (slug, age_days, "past grace window, should have been deleted")
        newly_orphaned += (age_days == 0)
        stale_but_kept += (age_days > 0)
    else:
        assert not orphaned_since, (slug, "slug reappeared in generated data but orphaned_since was never cleared")
print("museum keys:", len(m), "orphaned (within Q15 grace):", newly_orphaned + stale_but_kept, "groups:", groups)
PY
hugo --minify
git diff --name-only  # expect only data/museums_info.json and/or data/exhibitions_info.json
```

- **Commit:** `chore(data): curated-record reconciliation (add missing, resolve orphans per Q15 grace rule)`

#### ST-4-7 — Week-A extras refresh batch (15 museums)

- **Model:** `composer-2.5` · **Size:** L *(resized from M, or split into 3×5-museum batches — F14)* · **Depends:** ST-4-6
- **Scope:** `data/museums_info.json`, only the 15 records with `refresh_group: "A"`.
- **Work:** re-verify hours/pricing/cards/access/transit against each museum's own site; update `_visitor.*`/`offers[]`/`_meta.sources[]`/`_meta.verified`/`last_refreshed_extras`/`next_due` for changed facts only (do not touch unrelated prose, per the phase-3c precedent).
- **Verify:** must show the specific facts that changed, not just that bookkeeping fields advanced (F12) — a batch that only bumps `last_refreshed_extras` without any source date advancing fails this check:

```sh
python3 - <<'PY'
import json
before = json.load(open("/tmp/phase4-st7-before.json"))  # snapshot taken before this ST's edits
after = json.load(open("data/museums_info.json"))
today = __import__("datetime").date.today().isoformat()
group_a = [s for s, v in after.items() if v["refresh_group"] == "A"]
assert len(group_a) == 15
changed = 0
for slug in group_a:
    b, a = before[slug], after[slug]
    fact_changed = any(b.get("_visitor", {}).get(k) != a.get("_visitor", {}).get(k)
                        for k in ("hours", "transit", "parking", "access", "pricing")) \
                    or b.get("offers") != a.get("offers")
    source_advanced = a["_meta"]["verified"] > b["_meta"]["verified"] or \
                       any(s["url"] for s in a["_meta"]["sources"])
    assert a["last_refreshed_extras"] == today, slug
    if fact_changed or source_advanced:
        changed += 1
print("Week-A refresh: 15 museums touched,", changed, "with an actual fact/source-date change")
PY
hugo --minify
git diff --name-only  # expect only data/museums_info.json
```

- **Human gate:** spot-check a few updated facts against each museum's own current page.
- **Commit:** `chore(data): refresh museum extras — week A (15)`

#### ST-4-8 — Week-B extras refresh batch (15 museums)

- **Model:** `composer-2.5` · **Size:** L *(resized from M, or 3×5-museum batches — F14)* · **Depends:** ST-4-6a (reconciliation run has landed); **independent of wall-clock** (F14) — this ST is scheduled/run whenever the operator's own cadence calendar next calls for group B, not gated on "the calendar week after ST-4-7"
- **Scope:** `data/museums_info.json`, only the 15 records with `refresh_group: "B"`.
- **Work:** same protocol as ST-4-7, group B. This run proves the alternating cadence for a second cycle; document the ongoing weekly hand-off (which group is due next, via `next_due`) for the operator to repeat indefinitely — phase 4 does not "finish" the cadence, it establishes and proves it for two cycles.
- **Verify (full literal command — F10, not "same as ST-4-7"):**

```sh
python3 - <<'PY'
import json
before = json.load(open("/tmp/phase4-st8-before.json"))  # snapshot taken before this ST's edits
after = json.load(open("data/museums_info.json"))
today = __import__("datetime").date.today().isoformat()
group_b = [s for s, v in after.items() if v["refresh_group"] == "B"]
assert len(group_b) == 15
changed = 0
for slug in group_b:
    b, a = before[slug], after[slug]
    fact_changed = any(b.get("_visitor", {}).get(k) != a.get("_visitor", {}).get(k)
                        for k in ("hours", "transit", "parking", "access", "pricing")) \
                    or b.get("offers") != a.get("offers")
    source_advanced = a["_meta"]["verified"] > b["_meta"]["verified"] or \
                       any(s["url"] for s in a["_meta"]["sources"])
    assert a["last_refreshed_extras"] == today, slug
    if fact_changed or source_advanced:
        changed += 1
print("Week-B refresh: 15 museums touched,", changed, "with an actual fact/source-date change")
PY
hugo --minify
git diff --name-only  # expect only data/museums_info.json
```

- **Commit:** `chore(data): refresh museum extras — week B (15)`

#### ST-4-9 — Press-link fallback pass [F13]

- **Model:** `composer-2.5` · **Size:** L *(resized from S — F14: 92 links, batched, 3-step ladder, per §4.4.3)* · **Depends:** ST-4-2 (exhibitions-domain commit — legacy `press[]` is already gone, big-bang, owner Q4), owner Q9
- **Scope:** `data/exhibitions_info.json` only, `subjectOf[]` entries lacking a `verifiedAccess` field (currently all 92). **No legacy `press[]` side to mirror onto** — ST-4-2's big-bang commit already removed it, so this subtask writes a single field shape, not a mirrored pair. Batched (e.g. ~20 entries per sub-run), not one giant unreviewed pass.
- **Work:** apply the §4.4.3 three-step ladder (alternate-URL discovery → rendered access check → Wayback archive check) to every `subjectOf[]` article, prioritizing known hard-403 outlets (DVHN, Leeuwarder Courant, ~5 shows); record `verifiedAccess` + `accessNote` (from the §4.4.3 vocabulary: `http_403`/`http_404`/`http_410`/`timeout`/`paywall`/`redirect_loop`/`archived`/`ok`) + `accessChecked` + (when archived) `archiveUrl` on every article.
- **Verify:**

```sh
python3 - <<'PY'
import json
d = json.load(open("data/exhibitions_info.json"))
VOCAB = {"ok", "http_403", "http_404", "http_410", "timeout", "paywall", "redirect_loop", "archived"}
total = checked = 0
for slug, v in d.items():
    articles = v.get("subjectOf", [])
    for a in articles:
        total += 1
        assert "verifiedAccess" in a, (slug, a.get("url"))
        assert a["accessNote"] in VOCAB, (slug, a.get("url"))
        if a["accessNote"] == "archived":
            assert a.get("archiveUrl"), (slug, a.get("url"))
            assert a["url"] != a["archiveUrl"], "live url must not be overwritten by an archive url"
        checked += 1
assert total == checked and total >= 92
print("subjectOf entries with verifiedAccess + accessNote vocabulary:", checked, "/", total)
PY
hugo --minify
git diff --name-only  # expect only data/exhibitions_info.json
```

- **Commit:** `chore(data): press-link fallback verification pass`

#### ST-4-10 — Navigation visibility fix [F5, F10]

- **Model:** `composer-2.5` · **Size:** S · **Depends:** owner Q1
- **Scope:** `static/css/custom.css` only (plus a class-hook edit in `layouts/partials/navigation.html` and/or `layouts/partials/lang-switcher.html` if Q1 picks the `.contentnav`-style alternative — see §4.4.4 item 1 for the full CSS that alternative requires, including both `nav+*` margin resets and the `body` padding reset). Never `themes/huguette`.
- **Work:** implement the Q1 answer (recommended: the reproduced-live one-liner). Verify against a **built HTML page**, not just the CSS rule text — the bug is about computed paint order, and a passing grep on the CSS source proves nothing about actual visibility.
- **Verify:**

```sh
set -euo pipefail
hugo --minify
"$HUGO" server --disableFastRender &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
sleep 2
# Browser gate (see §4.6 ST-4-13) confirms the second bar no longer paints over the first bar's text;
# this script only confirms the server serves valid, script-free HTML.
grep -RE "<script[^>]*src=[\"']?https?://" public --include='*.html' && exit 1
test -f public/index.html -a -f public/en/index.html
```

- **Browser gate:** load home NL+EN; confirm "Home / Kalender / Musea / Over" (and EN equivalents) are visibly painted, not just present in the DOM, by **both mouse click and keyboard Tab+Enter activation** of every main-nav link and the language switcher (F11) — folded into ST-4-13's full sweep.
- **Commit:** `fix(nav): stop the language-switcher bar painting over the main menu`

#### ST-4-11 — Home button: closed-by-design no-op (owner Q2)

- **Status:** **closed by design, not built** — owner Q2 answer is "visibility fix only, no extra styling." No chip/border/background treatment ships this phase; the already-first "Home" menu link becomes visibly unmistakable purely because ST-4-10 makes the whole menu paint correctly. Removed from the critical path — no other subtask depends on this one.
- **Model:** n/a · **Size:** n/a (no-op) · **Depends:** ST-4-10 (evidence only — this subtask makes no changes of its own)
- **Scope:** none — no file changes.
- **Work:** none. Closeout evidence only: confirm "Home" is present and painted as part of ST-4-13's browser sweep; record the closure explicitly in §4.12 rather than silently dropping the subtask number.
- **Verify (closeout evidence, not silence):**

```sh
hugo --minify
grep -q '>Home<' public/index.html
grep -q '>Home<' public/en/index.html
echo "ST-4-11: closed by design (owner Q2, 2026-09-13) — visibility fix only, no chip; confirmed on $(date -u +%F)"
```

- **Note for later:** a distinct chip/border/background treatment can be requested by the owner after seeing the plain visible menu live — not scoped or scheduled this phase.
- **Commit:** none (no-op; closure recorded in §4.12).

#### ST-4-12a — Banner asset shortlist (operator task, blocks ST-4-12) [F16, Q3]

- **Model:** `composer-2.5` · **Size:** S · **Depends:** owner Q3 (photo banner chosen, 2026-09-13)
- **Scope:** new `docs/banner-shortlist.md` only. No template/CSS/content changes — this subtask never renders anything on the site.
- **Work:** owner directive (2026-09-13): use **Lorem Picsum** for the banner photo — no separate licensing hunt. Select **3–5 candidate photos** from Lorem Picsum (fixed image IDs; deterministic; Unsplash-derived, free to use — record each ID + terms and the resolved image URL), each with a one-line fit note (subject matter, aspect ratio, palette vs. the classless theme) and desktop + 375px crop suitability; mark a **default pick** (`OPERATOR PICK: <picsum-id>`) with a swap note. Owner review is optional — the default stands unless the owner swaps it. No candidate is wired into any template yet; ST-4-12 vendors the picked image into `static/images/` when it builds.
- **Verify:**

```sh
test -f docs/banner-shortlist.md
CANDIDATES=$(grep -c '^## Candidate' docs/banner-shortlist.md)
test "$CANDIDATES" -ge 3 -a "$CANDIDATES" -le 5
grep -qi 'license' docs/banner-shortlist.md
grep -qE 'OPERATOR PICK: ' docs/banner-shortlist.md
git diff --name-only  # expect only docs/banner-shortlist.md
```

- **Blocking gate:** ST-4-12 (the actual banner build) may not start until this doc records a default pick (`OPERATOR PICK` present; owner swap optional at any time — a one-line change). **Until then, no banner renders** — status quo, plain top bar, exactly as today; this is the enforced default state, not a soft preference.
- **Commit:** `docs(header): prepare banner photo shortlist (Lorem Picsum, owner directive)`

#### ST-4-12 — Top-bar / banner treatment (photo banner build) [F16]

- **Model:** `composer-2.5` · **Size:** L *(per §4.4.4 item 3's expanded scope — owner Q3 picked the photo banner, not the plain-bar status quo)* · **Depends:** ST-4-10, ST-4-12a (banner photo recorded)
- **Scope:** `content/{nl,en}/*.md` front matter (`header:` field, the four hand-authored pages) **and** the adapter code generating museum/exhibition/month pages (`layouts/partials/add-museum-pages.html`, `add-exhibition-pages.html`, `add-calendar-month-pages.html` — set the equivalent parameter on pages that have no front matter of their own, so **every** adapter-generated page gets the same banner, not just the four hand-authored ones) **and** a `layouts/partials/headerimage.html` **override in this repo** (never `themes/huguette`) sized for the picked photo **and** `static/css/custom.css` for the responsive dimensions (desktop and 375px mobile width — no fixed-height image that overflows or crops badly) **and** the picked image asset itself (vendored locally under `static/images/` — no runtime hotlink to picsum.photos) plus its source/license record (carried over from ST-4-12a's shortlist pick into this override's doc comment or a dedicated line in `docs/structured-data-schema.md`'s neighbor doc — kept adjacent to the shortlist, not scattered).
- **Work:** implement the owner-picked banner consistently across **every** page type (home, calendar index + month pages, museums index, every museum detail, every exhibition detail, about) × both languages; specify and verify the responsive dimensions at both widths; record the final license/attribution line.
- **Verify (asserts the exact expected file set, F10, not just markdown-authored pages, plus the license record):**

```sh
hugo --minify
python3 - <<'PY'
import json, os
g = json.load(open("data/exhibitions.json"))
expected = set()
for row in g["museums"]:
    expected.add(f"public/museums/{row['slug']}/index.html")
    expected.add(f"public/en/museums/{row['slug']}/index.html")
for row in g["exhibitions"]:
    for m in g["museums"]:
        if m["name"] == row["museum"] and m.get("slug") and row.get("slug"):
            expected.add(f"public/museums/{m['slug']}/tentoonstelling/{row['slug']}/index.html")
            expected.add(f"public/en/museums/{m['slug']}/exhibition/{row['slug']}/index.html")
for p in ("public/index.html", "public/en/index.html", "public/over/index.html", "public/en/about/index.html",
          "public/kalender/index.html", "public/en/calendar/index.html",
          "public/museums/index.html", "public/en/museums/index.html"):
    expected.add(p)
missing = [p for p in sorted(expected) if not os.path.exists(p)]
assert not missing, missing
with_header = {p for p in sorted(expected) if 'class="header-band"' in open(p, encoding="utf-8").read()}
missing_header = sorted(expected - with_header)
assert not missing_header, ("pages missing the header band:", missing_header)
print("header treatment present on the exact expected file set:", len(expected), "pages")
PY
grep -qi 'license' docs/banner-shortlist.md  # attribution/license record carried through, not dropped
! grep -RE "<script[^>]*src=[\"']?https?://" public --include='*.html'
```

- **Commit:** `feat(header): add licensed photo banner treatment`

#### ST-4-13 — Full top-bar visual QA (browser gate) [F11]

- **Model:** `composer-2.5` · **Size:** M *(resized from S — F14: screenshot artifacts + computed-style capture + keyboard activation across 6 page types × 2 languages × 2 widths is materially more than a checklist pass)* · **Depends:** ST-4-10, ST-4-12 (ST-4-11 is a no-op closeout, §4.6 — nothing to wait on)
- **Scope:** no template/CSS file changes — QA-only run; screenshots + computed-style dumps are saved as review artifacts (e.g. `/tmp/phase4-nav-qa/`, referenced by name in §4.12, not committed to the repo).
- **Work:** `"$HUGO" server --disableFastRender` (start under `set -euo pipefail` with an `EXIT` trap that kills the server, per ST-4-10's pattern). For every page type (home, `/kalender/` + one month page, `/museums/`, one museum detail, one exhibition detail, `/over/`) × both languages × desktop **and** 375px width:
  - Capture a **named before/after screenshot** (e.g. `home-nl-desktop-before.png`/`-after.png`) — kept as artifacts, not just a pass/fail line.
  - Activate every main-nav link and the language-switcher link by **both real mouse click and keyboard Tab+Enter**; confirm each lands on the expected page.
  - Read and record the **computed** `position`, `margin-top`, `z-index`, `box-shadow`, and bounding-box (`getBoundingClientRect`) for **both** top-level `<nav>` elements and for **each** `.contentnav` on that page (museums city-jump nav, calendar month-jump nav where present) — a DOM-presence grep cannot catch a paint-over or an invisible overlay intercepting clicks, only computed style + hit-test evidence can.
  - Confirm the "Home" menu link is visibly painted like the other three items (Q2: visibility fix only, no distinct chip — nothing further to check here); no `0.1.`-style card-numbering regression (PR #6 precedent); no overlap between the now-visible header bars and in-content `.contentnav` bars (PR #8 precedent); no console errors.
- **Verify:** one row per page/language/width combination in a results table (§4.12), each row citing its screenshot filenames and computed-style values, not a bare pass/fail word.
- **Commit:** none (or `docs(plan): log phase-4 nav visual QA` if the log entry needs its own commit).

#### ST-4-14 — Copy pass (light)

- **Model:** `composer-2.5` · **Size:** S · **Depends:** ST-4-10…13 (nav labels stable); **owner-approved copy nits list — does not exist yet, must be supplied/approved before this ST starts** (F19)
- **Scope:** `content/{nl,en}/*.md`, `i18n/{nl,en}.toml`. No new pages, no URL changes.
- **Work:** per §4.4.5 — confirm/tidy the "Musea"/"Museums" vs `/museums/` pairing, sweep remaining informal-tone nits, keep NL/EN parity.
- **Verify:**

```sh
hugo --minify
python3 - <<'PY'
import re
def keys(path):
    return set(re.findall(r"^\[([^]]+)\]\s*$", open(path).read(), re.M))
nl = keys("i18n/nl.toml"); en = keys("i18n/en.toml")
missing_in_en = sorted(nl - en)
missing_in_nl = sorted(en - nl)
assert not missing_in_en, ("keys only in nl.toml:", missing_in_en)
assert not missing_in_nl, ("keys only in en.toml:", missing_in_nl)
print("i18n key parity:", len(nl))
PY
```

- **Commit:** `docs(copy): light consistency + tone pass (phase 4)`

#### ST-4-15 — 3d leftovers (conditional on owner Q6)

- **Model:** `composer-2.5` · **Size:** S (fold-in branch) · **Depends:** ST-4-14, owner Q6
- **Scope (fold-in branch only):** `layouts/_default/exhibition-page.html`, `i18n/{nl,en}.toml` (new `share_mailto_subject`/body keys, D11). **Defer branch:** no file changes — update §4.2 non-goals wording only if the owner wants the re-defer stated more explicitly for phase 5.
- **Work:** implement the smallest leftover (mailto share) only if Q6 says fold-in; otherwise no-op this subtask and record the re-defer decision **and explicit closeout evidence** in §4.12 (F14) — not silently skipped.
- **Verify (fold-in branch):**

```sh
hugo --minify
grep -q 'share_mailto_subject' i18n/nl.toml
grep -q 'share_mailto_subject' i18n/en.toml
! grep -R 'javascript:' public --include='*.html'
```

- **Verify (defer branch):** `echo "ST-4-15: Q6 = defer all three; no file changes, confirmed on $(date -u +%F)"` recorded in §4.12.
- **Commit:** `feat(share): add mailto share action` (fold-in) or no commit (defer, closeout evidence still recorded).

#### ST-4-16 — Docs + final audit

- **Model:** `composer-2.5` · **Size:** M *(resized from S — F14: runs the full expanded §4.8 battery, not a short doc-only pass)* · **Depends:** ST-4-1, 2 (both commits), 5, 6, 6a…9, 10, 11 (no-op), 12a, 12, 13…15 *(ST-4-3/4/4b/4c no longer exist — folded into ST-4-2, owner Q4)*
- **Scope:** `README.md`, `AGENTS.md`, `docs/site-plan.md` (pointer only). No visitor display-copy changes beyond what ST-4-14 already landed.
- **Work:** document the schema.org-shaped curated store, the cadence mechanism (`refresh_group`/`next_due`/reconciliation), the press `verified_access`/`access_note` fields, and the navigation fix. Run the full §4.8 QA battery.
- **Verify:** §4.8 battery in full; `PHASE_START=$(git merge-base HEAD origin/main)`; `git diff --name-only "$PHASE_START"...HEAD` matches the approved phase-4 file set; generated data/feeds/theme absent from the diff.
- **Commit:** `docs(plan): document phase 4 (structured data, cadence, navigation)`

### 4.7 Acceptance checklist

- [ ] Owner answered Q1–Q16 before implementation.
- [ ] `museums_info.json` (30/30) and `exhibitions_info.json` (187/187) carry schema.org-shaped fields **instead of** the legacy flat fields — replaced atomically in ST-4-2's two big-bang commits (owner Q4: no parallel-fields window, no separate removal step); frozen slugs and file identity unchanged; pipeline-host `exhibitions.json` schema untouched in this phase; the full losslessness proof (§4.4.1.5, all 30/146/398/102/187/92) passed **on the staged tree before each commit**, not a sample and not a post-commit check.
- [ ] The 30-record/146-card semantic-equality script passes, **including** the 2 null-accepted-card fixtures and the 5 plural-notes-museum fixtures (F2/F9).
- [ ] `cards[].id`/`offers[].identifier` retained for all 146; no card uses `InStock`/`OutOfStock` for acceptance anywhere.
- [ ] Templates read the migrated curated shape (ST-4-2's combined commits cover `museum-info.html`, `exhibition-info.html`, `museum-map-ready.html`, `museum-page.html`, `museums.html`, `exhibition-page.html`, `head.html` — every direct reader — F8); rendered HTML is unchanged from pre-migration except the five plural-notes museum pages, whose previously-blank card notes now render (ST-4-2's byte-identical-minus-five-exceptions diff); the AGENTS.md missing-coordinate fixture (removed/null/string/out-of-bounds) re-run passed.
- [ ] Legacy museum/exhibition fields are gone the instant ST-4-2's two big-bang commits land — no separate removal subtask, no indefinite two-source-of-truth state (F7 resolved by construction under owner Q4, not by scheduling a follow-up; §4.4.7).
- [ ] `refresh_group` (15 A / 15 B) exists on every museum record, seeded from evidence or `null` (never a blanket "today"); `next_due` exists; at least one full A+B cycle (ST-4-7 + ST-4-8) has run and shows actual changed facts/source dates, not just bookkeeping-field bumps; the reconciliation run (ST-4-6a) has added any missing curated keys and resolved orphans per the Q15 rule; group balance stays within 1 of even as the museum set changes.
- [ ] Every `subjectOf[]` press article carries `verifiedAccess` + an `accessNote` from the defined vocabulary (§4.4.3); known hard-403 cases (DVHN, Leeuwarder Courant) show an honest fallback outcome, never a dropped link; archive URLs are recorded separately and never overwrite the live URL. (Legacy `press[]` no longer exists — removed by ST-4-2's big-bang commit, owner Q4.)
- [ ] The main menu (all four items, both languages) is visibly painted on every page type and both a desktop and 375px width — not just present in the DOM; real mouse **and** keyboard activation confirmed for every main-nav + language-switcher link (F11); named before/after screenshots and computed-style dumps exist as artifacts for every route/width combination.
- [ ] Home is visibly unmistakable purely via the nav visibility fix (Q2: no chip built this phase; ST-4-11 closed by design) on every page.
- [ ] Top-bar/banner treatment (Q3: photo banner) matches the owner-picked image consistently across every page (including adapter-generated museum/exhibition/month pages, not just `content/*.md`) and both languages; the banner asset shortlist (ST-4-12a) and owner pick landed before ST-4-12 started; until the pick happened, no banner rendered (status quo).
- [ ] Copy pass landed after the functional work, NL/EN parity intact (tested per-file, not a single cross-file grep), no fixture/inconsistent "Musea"/`/museums/` wording left unexplained; the owner-approved copy nits list existed before ST-4-14 started.
- [ ] 3d leftovers explicitly resolved (folded per Q6 with a landed subtask, or re-deferred with explicit closeout evidence recorded) — no silent scope creep; Telegram's disposition records the owner's actual intent, not just a re-defer.
- [ ] `"$HUGO" --minify` on pinned v0.166.0 exits 0 with 0 WARN, same page count (990) as the pre-phase-4 baseline; weekly feed files/URLs (root + `static/` + `public/`, byte-equal to each other and to the live site), frozen slugs, `/musea/`→`/museums/` redirect, and the phase-3c JS allowlist all regress clean.
- [ ] `themes/huguette` untouched; no pipeline-host code added from this repo (only target-contract docs, including the additive/backward-compatible rollout sequence and its rollback steps).
- [ ] Traceability matrix (§4.7.1 below) complete: every scope item → decision → subtask → acceptance check → rollback step is filled in, no blank cells.

#### 4.7.1 Traceability matrix [F19]

Six workstreams (§4.1), six rows — owner scope item → decision → subtask → acceptance check → rollback step. Preserves the non-goals (§4.2) verbatim; this table only traces the six things phase 4 actually does.

| Scope item | Decision(s) | Subtask(s) | Acceptance check | Rollback |
|---|---|---|---|---|
| Structured data (curated + generated + JSON-LD-consumption handoff) | Q4, Q7, Q8, Q11, Q12, Q13, Q14, Q16 | ST-4-1, 2 (two big-bang commits), 5 *(ST-4-3/4/4b/4c dropped — folded into ST-4-2, Q4)* | §4.7 rows 2–5; §4.8's structured-data schema audit | §4.10 items 1, 6 |
| Extras refresh cadence + curated lifecycle | Q5, Q15 | ST-4-6, 6a, 7, 8 | §4.7 row 6 | §4.10 item 5 |
| Press-link fallback | Q9 | ST-4-9 | §4.7 row 7 | §4.10 item 4 |
| Navigation / Home button / banner | Q1, Q2, Q3 | ST-4-10, 11 (no-op), 12a, 12, 13 | §4.7 rows 8–9; §4.8 visual section | §4.10 item 3 |
| Copy pass (light) | *(owner-approved copy nits list, not yet a formal Q — see F19's noted gap below)* | ST-4-14 | §4.7 row 10 | §4.10 item 2 |
| 3d leftovers disposition | Q6 | ST-4-15 | §4.7 row 11 | §4.10 item 2 |

**Known gap, stated explicitly (F19):** the copy-pass row's input — an "owner-approved copy nits list" — does not exist anywhere in this repo yet (§4.4.5, §4.6 ST-4-14's `Depends:` line already states this). It is not covered by a numbered §4.5 decision because it isn't a design choice with a recommendation/alternative — it's a content artifact the owner must produce or approve before ST-4-14 can start. Listed here so the gap is traceable, not silently assumed away.

### 4.8 QA battery [F18]

Run on pinned Hugo **v0.166.0 extended**; Mac-lane runs restate they built on v0.165.0 and flag for operator re-verification.

```sh
HUGO="${HUGO:-/opt/data/museum_tracker/bin/hugo}"
command -v "$HUGO" >/dev/null 2>&1 || HUGO=hugo
set -o pipefail
"$HUGO" version   # must report v0.166.0+extended on the operator's re-run
"$HUGO" --minify 2>&1 | tee /tmp/phase4-final-build.log
test "$(grep -ci '^WARN' /tmp/phase4-final-build.log)" = 0
test -f public/index.html -a -f public/en/index.html
test -f public/kalender/index.html -a -f public/en/calendar/index.html
test -f public/museums/rijksmuseum/index.html -a -f public/en/museums/rijksmuseum/index.html
test -f public/museumtips.ics -a -f public/closing-soon.ics
# 990 pages (496 NL + 494 EN) is this repo's established baseline (phase-3b/3c logs, §4.12) — read it from
# Hugo's own build summary, the same metric every prior phase-close log cites, not a raw HTML file count
# (which includes per-exhibition .ics companions and aliases and is a different, larger number):
grep -A2 '^ Pages ' /tmp/phase4-final-build.log | grep -oE '[0-9]+' | { read -r nl; read -r en; \
  test "$nl" = 496 -a "$en" = 494; }

# Structured-data schema audit (30 museums / 187 exhibitions, both curated files) — full counts, not samples.
python3 - <<'PY'
import json
m = json.load(open("data/museums_info.json"))
e = json.load(open("data/exhibitions_info.json"))
assert len(m) == 30 and len(e) == 187
assert all(v.get("@type") == "Museum" for v in m.values())
groups = {}
for v in m.values():
    groups[v["refresh_group"]] = groups.get(v["refresh_group"], 0) + 1
assert abs(groups.get("A", 0) - groups.get("B", 0)) <= 1, groups
offers_total = sum(len(v.get("offers", [])) for v in m.values())
assert offers_total == 146, offers_total
sources_total = sum(len(v.get("_meta", {}).get("sources", [])) for v in m.values())
assert sources_total == 398, sources_total
notes_total = sum(len(v.get("_meta", {}).get("notes", [])) for v in m.values())
assert notes_total == 102, notes_total
admission_total = sum(1 for v in e.values() if "admission_v2" in v)
assert admission_total == 187, admission_total
press_total = sum(len(v.get("subjectOf", [])) for v in e.values())
verified = sum(1 for v in e.values() for a in v.get("subjectOf", []) if "verifiedAccess" in a)
assert press_total == verified == 92, (press_total, verified)
print("museums:", len(m), "offers:", offers_total, "sources:", sources_total, "notes:", notes_total,
      "exhibitions:", len(e), "admissions:", admission_total, "press verified:", verified, "/", press_total,
      "refresh_group:", groups)
PY

# Missing-coordinate fixture (AGENTS.md) — mandatory re-run, this phase moved lat/lon under geo.*.
FIXTURE=/tmp/museumtips-p4-final-coord-fixture
rm -rf "$FIXTURE" && cp -a . "$FIXTURE" && cd "$FIXTURE"
python3 - <<'PY'
import json, copy
d = json.load(open("data/museums_info.json"))
slug = next(iter(d))
a = copy.deepcopy(d); del a[slug]["geo"]
json.dump(a, open("data/museums_info.json.removed", "w"), indent=2, ensure_ascii=False)
b = copy.deepcopy(d); b[slug]["geo"]["longitude"] = None
json.dump(b, open("data/museums_info.json.null", "w"), indent=2, ensure_ascii=False)
print("fixture slug:", slug)
PY
for case in removed null; do
  cp "data/museums_info.json.$case" data/museums_info.json
  "$HUGO" --minify --destination "/tmp/mc-final-$case"
  page="/tmp/mc-final-$case/museums/$(python3 -c "import json;print(next(iter(json.load(open('data/museums_info.json.$case')))))")/index.html"
  grep -q 'Kaart niet beschikbaar\|Map unavailable' "$page"
  ! grep -q 'leaflet.css\|leaflet.js\|museum-map.js' "$page"
done
cd - >/dev/null && rm -rf "$FIXTURE" /tmp/mc-final-removed /tmp/mc-final-null
echo "verify-missing-coordinate-fixture: OK"

# Phase-3c regressions unchanged (JS allowlist, exact script-page/tag counts, heat classes, negative asset checks).
test "$(git ls-files '*.js' | sort | tr '\n' ' ')" = \
  "static/js/museum-map.js static/vendor/leaflet/1.9.4/leaflet.js "
! grep -RE "<script[^>]*src=[\"']?https?://" public --include='*.html'
! grep -R 'javascript:\| on[a-zA-Z][a-zA-Z]*=' public --include='*.html'
MAP_PAGES=$(grep -rl 'data-lat=' public --include='*.html' | wc -l | tr -d ' ')  # minify strips quotes from id="map"; data-lat= survives
SCRIPT_TAGS=$(grep -oRE '<script[^>]*src=' public --include='*.html' | wc -l | tr -d ' ')  # tag count, not line count (phase-3c convention: 62 pages / 124 tags)
echo "map-ready pages: $MAP_PAGES ; museum-map script tags: $SCRIPT_TAGS"  # record both counts in §4.12; must equal pre-phase-4 baseline
for p in public/index.html public/en/index.html public/kalender/index.html public/en/calendar/index.html \
         public/over/index.html public/en/about/index.html; do
  ! grep -q 'leaflet.css\|leaflet.js\|museum-map.js' "$p"   # negative asset check: home/calendar/about/(non-map) exhibition
done
for class in closing-heat-1 closing-heat-2 closing-heat-3 closing-heat-4; do
  grep -R "$class" public/kalender public/en/calendar --include='*.html' >/dev/null
done

# Phase-2 date/nav regressions unchanged.
! grep -F '1 januari 1' public/kalender/index.html public/museums/index.html
! grep -F '1 January 1' public/en/calendar/index.html public/en/museums/index.html
! grep -F '0001-01' public/kalender/index.html public/en/calendar/index.html

# Representative route + language-switch checks (F18) — not just file-existence.
for route in "" "kalender/" "en/calendar/" "museums/" "en/museums/" "museums/rijksmuseum/" "en/museums/rijksmuseum/" "over/" "en/about/"; do
  test -f "public/${route}index.html"
done
grep -q 'hreflang="en"' public/index.html
grep -q 'hreflang="nl"' public/en/index.html

# /musea/ -> /museums/ alias still resolves (frozen route, D7).
"$HUGO" --minify --destination /tmp/phase4-alias-check >/dev/null 2>&1
test -f /tmp/phase4-alias-check/musea/index.html

# NL/EN i18n key parity — tested per file, not a single cross-file grep (F10).
python3 - <<'PY'
import re
def keys(path):
    return set(re.findall(r"^\[([^]]+)\]\s*$", open(path).read(), re.M))
nl = keys("i18n/nl.toml"); en = keys("i18n/en.toml")
assert not (nl - en), sorted(nl - en)
assert not (en - nl), sorted(en - nl)
print("i18n key parity:", len(nl))
PY

# Feed byte-equality — root / static/ / public/ copies, not just "files exist" (F18).
diff -q museumtips.ics static/museumtips.ics
diff -q closing-soon.ics static/closing-soon.ics
diff -q museumtips.ics public/museumtips.ics
diff -q closing-soon.ics public/closing-soon.ics
# operator re-run additionally diffs these against the live URLs:
#   curl -sf https://museumtips.pepperlink.nl/museumtips.ics | diff - museumtips.ics
#   curl -sf https://museumtips.pepperlink.nl/closing-soon.ics | diff - closing-soon.ics

# Protected artifacts and paths untouched.
PHASE_START=$(git merge-base HEAD origin/main)
git diff --exit-code "$PHASE_START" -- data/exhibitions.json \
  museumtips.ics closing-soon.ics static/museumtips.ics static/closing-soon.ics \
  themes/huguette CNAME static/CNAME
```

**VISUAL — real browser on a locally served pinned build** (`"$HUGO" server --disableFastRender`), artifacts from ST-4-13 (F11):

- Main menu (all four items) and language switcher are both visibly painted on every page type × both languages × desktop **and** 375px — cite the ST-4-13 named screenshot files and computed-style values here, not just a pass/fail summary.
- Real mouse click **and** keyboard Tab+Enter activation confirmed for every main-nav link and the language switcher, on every page type.
- Home affordance is visually distinct from the other three items everywhere.
- Museum detail page: address still renders from the migrated `PostalAddress`/`address_display`; map (phase 3c) still shows the correct marker (regression, not new scope).
- One exhibition detail page: admission line and press links still render correctly from the migrated `Offer`/`NewsArticle` shape.
- Top-bar/banner treatment (Q3) is applied consistently, no layout shift or overflow at mobile width.
- Re-check the PR #6/#8 precedents: no stray `0.1.` card numbering; in-content `.contentnav` bars (museums city list, calendar month jump nav) still sit in flow and don't collide with the now-visible header bars; computed `position`/`z-index`/`box-shadow` recorded for both top navs and each `.contentnav`.

### 4.9 Documentation

- `README.md` — schema.org-shaped curated store (one paragraph, no full data-format rewrite); cadence mechanism (`refresh_group`/`next_due`/reconciliation); press `subjectOf[].verifiedAccess`/`accessNote` note; navigation fix; the photo banner (Q3) and its license record.
- `AGENTS.md` — curated-file ownership note extended to name the schema.org-shaped subtree explicitly (`address_v2`, `geo`, `offers[]`, `_visitor`, `_meta`); `refresh_group`/`next_due` as curated (agent-editable) fields, never pipeline-written; JS allowlist unchanged; the `HUGO=${HUGO:-/opt/data/museum_tracker/bin/hugo}` pin pointer (F21); last-verified date bump.
- `docs/site-plan.md` — one pointer line to this §Phase 4 plan; do not rewrite the historical stack/deployment essay.
- `docs/structured-data-schema.md` — new: the authoritative field-by-field mapping (Tables 1–3, §4.4.1) + the pipeline-host handoff section with the full rollout/rollback sequence (ST-4-1, ST-4-5).
- `docs/banner-shortlist.md` — new (ST-4-12a): the licensed candidate shortlist and the owner's recorded pick + license/attribution for the Q3 photo banner.
- No content-copy docs beyond what ST-4-14 already covers.

### 4.10 Rollback [F17]

**Owner Q4 (2026-09-13) chose big-bang migration** — there is no parallel-fields window, so rollback for the structured-data workstream is simpler in kind but coarser in grain than the (not-chosen) parallel-fields alternative would have been: **revert the big-bang commit(s) atomically.** Every other phase-4 commit stays independently revertible exactly as before. **General principle (F17): prefer forward-fixing a stale fact over reverting it** — if ST-4-7/8 corrected a museum's hours/pricing and a later rollback is needed for an unrelated reason, do not let that rollback silently republish the old, known-stale value; the commit matrix below keeps factual-correction commits separable from structural commits so this is always possible.

**Exact commit matrix (big-bang, owner Q4 — supersedes the non-chosen parallel-add/cutover/remove staging):**

| Stage | What landed | Revert action | Effect |
|---|---|---|---|
| Big-bang commit 1 — museums domain (ST-4-2) | `museums_info.json` reshaped to schema.org-shaped keys **and** every museum-domain template (`museum-info.html`, `museum-page.html`, `museums.html`, `museum-map-ready.html`, `head.html`) cut over, legacy keys removed — all in this one commit | Revert this single commit directly — data and templates move together, so there is no intermediate state to coordinate | Museum data and templates both return to their pre-phase-4 shape simultaneously; build stays green; no separate template-revert step, because there was never a separate template-cutover commit |
| Big-bang commit 2 — exhibitions domain (ST-4-2) | `exhibitions_info.json` reshaped (sidecar shape, Q13) **and** `exhibition-info.html`/`exhibition-page.html` cut over, legacy `admission`/`press[]` removed — all in this one commit | Revert this single commit directly, same property as commit 1 | Exhibitions data and templates both return to their pre-phase-4 shape simultaneously |
| A rollback is needed for one domain only | — | Revert only that domain's commit (they are file-disjoint, §4.4.1.7's ownership table) — the other domain's migration is unaffected | Partial rollback is safe and independent; this is the practical benefit the domain-split commit justification (§4.5 Q4) buys back under big-bang |
| A structural rollback is needed **after** cadence (ST-4-6/6a/7/8) or press-fallback (ST-4-9) commits have already landed on top of the new shape | — | Revert those dependent commits first (they read fields the big-bang commit introduced), then revert the big-bang commit itself — same dependency-ordering principle as reverting any commit its later commits build on | Full pre-phase-4 schema instance restored once all dependents are reverted; re-run ST-4-2 (both commits) from scratch to re-migrate, then re-run the dependents |

**Residual risk, recorded honestly (owner Q4, §4.11):** because data reshape and template cutover now land together with no separately-revertible intermediate step, a template bug and a data-shape bug introduced in the same big-bang commit are no longer separable in the diff — reverting the commit fixes both, but a targeted "just the template part" or "just the data part" revert is not possible the way it would have been under the (not-chosen) parallel-fields staging. This is mitigated, not eliminated, by the three mandatory pre-commit gates in §4.4.1.5 (full-population losslessness proof, named fixtures, scratch render-equality check) — they are what stand in for the parallel-fields window's own safety margin.

1. Revert docs (ST-4-16, ST-4-1/5) — including the pipeline-host handoff doc; if the operator already started the schema-2 rollout (§4.4.1.7) off that doc, coordinate the pipeline-side rollback (item 7 below) first.
2. Revert copy pass (ST-4-14) and any folded-in 3d leftover (ST-4-15) — restores prior visitor copy/i18n.
3. Revert navigation/banner commits (ST-4-10, ST-4-12a, ST-4-12; ST-4-11 is a no-op, nothing to revert) — restores the pre-fix (invisible-menu) CSS state and/or the pre-banner plain-bar state; not desirable long-term, but mechanically clean.
4. Revert press-fallback (ST-4-9) — `subjectOf[].verifiedAccess`/`accessNote`/`archiveUrl` fields drop; original `subjectOf[].url` values untouched either way (never dropped by this phase). **Archive/original URL restoration:** since the live `url` field is never overwritten by an archive URL (§4.4.3), reverting ST-4-9 cannot lose the original link — it only drops the recorded fallback outcome, which can be re-run later without re-doing any original-URL recovery.
5. Revert cadence batches (ST-4-7, ST-4-8) — restores pre-refresh museum-extras content. **Preserve refreshed factual corrections during a structural rollback:** if a structural rollback elsewhere (item 6) also touches `museums_info.json`, cherry-pick or re-apply ST-4-7/8's factual diffs on top of the restored structure rather than letting the structural revert silently re-publish stale hours/pricing — the two kinds of change are separable in the commit history precisely so this is possible. Revert bookkeeping (ST-4-6, ST-4-6a) separately if the owner wants the exact pre-phase-4 schema instance.
6. **Data-migration rollback:** see the commit matrix above.
7. **Pipeline schema-2 rollback (F4, §4.4.1.7):** if the operator's pipeline-host rollout reached "switch producer" (step 4) before a rollback is needed, the operator reverts the producer to schema-1-only emission; any site-side template that started depending on `@type` must be reverted first (same ordering constraint as item 6) so a template expecting `@type` is never live against a schema-1-only feed.

No rollback touches `gh-pages`, `data/exhibitions.json`, frozen slugs, or pipeline-host scripts/state directly (except via the operator's own schema-2 rollback, item 7, which is pipeline-host-executed, not repo-executed). Republish through the normal site pipeline after owner merge/revert.

### 4.11 Risks & unknowns

| Risk / unknown | Mitigation / gate |
|---|---|
| Pipeline-host items (1(b)/1(c)) get implemented as repo code by mistake | §4.0 boundary stated up front; ST-4-5's scope is docs-only; verify step checks `git diff --name-only` has no pipeline-host paths (none exist in this repo) |
| Address-string → `PostalAddress` decomposition mis-splits a record, or a non-postal annotation gets force-fit into a `PostalAddress` sub-property | Human spot-check on all 30 in ST-4-2, not a sample; the 6 flagged non-conforming records get an explicit second look; `address_v2.venueNote` + verbatim `address_display` backstop (§4.4.1.4) |
| Big-bang data reshape + template cutover (ST-4-2) silently changes rendered output | Byte-identical `diff -rq` gate against a pre-migration build, run as one of the three mandatory pre-commit gates (§4.4.1.5) on the staged tree **before** the commit, not after (with the 5 plural-notes-museum pages deliberately excluded and separately asserted to have *changed*) — not just "build succeeds" |
Big-bang migration (owner Q4 override) means a template bug and a data-shape bug in the same domain commit are no longer separable in the diff — the parallel-fields window's own safety margin (F7) is not available | The three mandatory pre-commit gates (§4.4.1.5: full-population losslessness proof, named fixtures, scratch render-equality check) run on the staged tree **before** either big-bang commit lands, standing in for the parallel-fields window; the domain split (museums vs exhibitions, §4.5 Q4) keeps a rollback in one domain from forcing a rollback in the other |
| `refresh_group` drifts if museums are added/removed later | Smaller-group-wins assignment for new museums, never reshuffling existing ones; the reconciliation run (ST-4-6a) checks the `abs(A−B)<=1` balance rule every cycle |
| Cadence bookkeeping is initialized dishonestly (blanket "today") and hides that no real refresh happened | ST-4-6 explicitly forbids blanket-seeding `last_refreshed_extras`; verification asserts fewer than 30/30 records claim the run date unless all 30 were actually reverified |
| Curated records for ended exhibitions accumulate forever, or get deleted the instant a slug drops (losing in-flight press/copy work) | Owner-approved retention rule (Q15) + the recurring reconciliation run (ST-4-6a) — no more "drops naturally" with no mechanism |
| Press fallback effort balloons beyond ~5 known hard-403 shows, or "alternate path" quietly becomes "retry the same URL" | Explicit 3-step ladder with named success/failure vocabulary (§4.4.3, Q9); sized L (F14) to reflect the real 92-entry audit; archive URLs never overwrite the live URL |
| Nav CSS fix regresses the PR #8 `.contentnav` in-page navs | ST-4-13's browser gate explicitly re-checks that precedent with computed styles, not just a DOM grep; both header bars and in-content navs get visual QA, screenshots, and mouse+keyboard activation checks in the same pass |
| Home-button styling looks like a call-to-action / booking button | Keep it a plain internal navigation affordance (link, not a `<button>`/form); Q2's recommendation avoids CTA-like framing; cross-check against §4.2's no-CTA non-goal |
| Owner's picked photo banner (Q3) ships without covering adapter-generated routes, or without a licensed image source ready | §4.4.4 item 3/ST-4-12 spell out the full adapter + partial-override + licensing + responsive-dimension scope; ST-4-12a's shortlist-and-pick gate blocks ST-4-12 from starting without a recorded, licensed choice — no banner renders until then (status quo) |
| Deferred nav alternative (Q1's static-in-flow option) gets picked up in a later phase without re-checking its interaction with the now-shipped photo banner (Q3) | §4.4.4 item 1/item 3 cross-reference this explicitly; a future revisit must re-verify the `body` padding reset, both `nav+*` margin overrides, and the banner's responsive dimensions together, not as two independent changes |
| Copy pass (ST-4-14) runs before nav/cadence text stabilizes, or before an owner-approved copy nits list exists | Explicit `Depends: ST-4-10…13` **and** the copy-nits-list gap stated as a precondition, not implied (F19) |
| 3d leftover scope creep (Telegram, CTA) despite Q6 | Q6's recommendation keeps both deferred; ST-4-15's fold-in branch is scoped to the single smallest leftover only; Telegram's disposition records the owner's actual intent (F20), not just "no prior spec" |
| Mac lane (v0.165.0) vs pin (v0.166.0) behavior differs on any new template construct | Every ST states which pin it built on; every verify script resolves `$HUGO` from the `AGENTS.md`-documented pin (F21); operator repeats the full §4.8 battery on v0.166.0 before sign-off |
| Schema-2 pipeline rollout breaks the live site if it's not actually additive | §4.4.1.7's 6-step dual-write/fixture-validate/verify-live sequence with both pipeline- and site-side rollback steps (F4) |

### 4.12 Log

*(Append during the build, one bullet per run.)*

- **2026-09-13 — Owner decisions recorded (Q1–Q16).** Owner answered all 16 §4.5 questions in chat; every answer is folded into the plan next to its question and into the affected subsections/subtasks. Headline changes from the recommendations: **Q1** shadow-kill CSS one-liner now, static-in-flow nav alternative deferred (future-note, §4.4.4 item 1/§4.11); **Q2** Home button is visibility-fix-only, ST-4-11 closed by design as a no-op; **Q3** photo banner chosen (not the plain-bar status quo) — ST-4-12 expanded to full adapter/partial-override/licensing scope, gated on a new ST-4-12a (owner picks from an operator-prepared licensed shortlist); **Q4** big-bang migration chosen over the parallel-fields recommendation — old ST-4-2/ST-4-3/ST-4-4 merged into one two-commit (museums, then exhibitions) big-bang path in ST-4-2, ST-4-4b/ST-4-4c dropped entirely, three pre-commit gates (losslessness proof, named fixtures, scratch render-equality check) made mandatory, §4.10 rollback and §4.11 risks rewritten for atomic-commit revert with the residual template/data-bug-conflation risk recorded honestly. Q5–Q16 all matched their stated recommendations (refresh_group field; all 3d leftovers deferred; keep filenames; bilingual sub-objects; 3-step press ladder — now `subjectOf[]`-only since legacy `press[]` is gone post-ST-4-2; docs-only pipeline handoff; `venueNote` sidecar; three-state acceptance enum; sidecar `ExhibitionEvent` shape; additive schema-2 rollout; one-cadence-cycle orphan grace, now wired into ST-4-6a via an `orphaned_since` stamp; full-population losslessness proof as a hard gate + the `inLanguage` gap recorded as an accepted limitation). Plan status line updated to `approved (owner decisions 2026-09-13)`. No implementation file touched — this run is `PLAN.md` only, per the planning-cycle boundary.

