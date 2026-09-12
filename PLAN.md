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

- No map on the museums index, exhibition pages, calendar, home, or about page unless the owner changes Q4.
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
- Existing countdown boundaries are day 0, days 1–6, 7–13, 14–20, and 21–30. Reuse the same integer-day calculation as `countdown.html` so color and label cannot disagree in this phase.
- The current homepage already does `sort $upcoming "start"` in `layouts/index.html`; the museum-page upcoming list also sorts by `start`. The reported end-date bug is not present at this branch tip. Phase 3c therefore adds a regression assertion, not a drive-by edit. If the implementation baseline regresses **and** Q2 makes `layouts/index.html` a touched file, correct it in that run; otherwise do not touch the file.
- After initializing the pinned Huguette submodule, local Hugo **v0.165.0 extended** built successfully: 496 NL pages, 494 EN pages, 0 WARN lines, and 0 HTML `<script>` tags. This machine is one minor version behind the authoritative **v0.166.0 extended** pin; the operator re-runs every build/visual gate on the pin.
- Scratch Hugo proof on local v0.165.0: a `.Type == "museum-page"` head condition emitted local Leaflet CSS + two deferred local scripts on the museum page (2 script tags), while an about page emitted 0; `data-lat` / `data-lon` rendered as numeric attributes. This proves the proposed plain-Hugo conditional mechanism, not the final implementation.
- Leaflet’s official download page still identifies **1.9.4** as stable and 2.0.0-alpha.1 as prerelease. The official `leaflet.zip` fetched from GitHub release `v1.9.4` had SHA-256 `aaec1d5c3239a613a53e996087629aca1483cb2f0438b11b8a335c6cede4c16b`.

## 3c.4 Proposed implementation

### Map exception surface

Use `layouts/partials/museum-map-ready.html` as the one shared Hugo predicate. It receives a dict containing the current page and curated info; use it from both the head and location markup:

- page type is exactly `museum-page`;
- head lookup is `index hugo.Data.museums_info .Params.slug` (frozen slug; no `urlize`); `museum-page.html` passes page + generated museum + curated info into `museum-info.html`, so the same predicate has the same inputs there;
- `lat` and `lon` both exist, are finite non-null numbers (not booleans/strings), form a complete pair, and are within the approved NL bounds.

When true:

- `head.html` emits CSS in the order classless → Leaflet → custom, then deferred same-origin Leaflet JS followed by deferred `museum-map.js`;
- `museum-info.html` emits escaped `data-lat`, `data-lon`, generated museum name, and curated address on a hidden `#map`, plus a hidden failure fallback;
- `museum-map.js` initializes exactly one map, one tile layer, one marker, and one popup. Build popup DOM with `textContent`, not untrusted `innerHTML`.

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

Keep the two layer-control images because unmodified upstream `leaflet.css` references them, even though phase 3c adds no layer control. Do not vendor `leaflet-src*.js`, source maps, npm metadata, or the full source tree. `LICENSE` is the BSD-2-Clause text from the `v1.9.4` tag. Add `static/js/museum-map.js` separately; it is project code, not vendor code.

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

Add `layouts/partials/calendar-exhibition.html` as the calendar-only wrapper that computes an urgency class and delegates unchanged content to `exhibition.html`. Call it only from `calendar.html` and `calendar-month.html`. This avoids changing cards on home/museum/exhibition pages.

Eligible: show has started, has a valid end date, and is not ended. Open-ended, upcoming, ended, and >30-day shows remain neutral. Proposed classes and exact backgrounds:

| Days until close | Existing label | Class | Background |
|---:|---|---|---|
| 21–30 | Last month | `closing-heat-1` | `#eff6ff` |
| 14–20 | Last 3 weeks | `closing-heat-2` | `#dbeafe` |
| 7–13 | Last 2 weeks | `closing-heat-3` | `#bfdbfe` |
| 1–6 | Last week | `closing-heat-4` | `#93c5fd` |
| 0 | Last day | `closing-heat-5` | `#60a5fa` |

Use foreground/link color `#172554` within all five classes (links remain underlined). Measured contrast against the five backgrounds ranges from 13.50:1 to 5.78:1, above WCAG AA normal-text contrast. Add a non-color cue by retaining the existing bold countdown label; no new legend/i18n is required.

Do not shade month jump-nav: a month can contain mixed urgencies, so one shade would be false precision. Do not shade “Binnenkort te zien / Opening soon”: pre-opening shows are ineligible for closing urgency.

## 3c.5 DECISIONS FOR OWNER

Answer every numbered question in chat before ST-3c-1 begins.

1. **Closing scale boundaries?**
   **Recommendation:** approve 21–30 / 14–20 / 7–13 / 1–6 / 0 days and the five hex values in §3c.4; they exactly mirror the existing countdown buckets and preserve a text cue.
   **Alternatives:** three bands (21–30 / 7–20 / 0–6); four bands with day 0 folded into 1–6; different owner-supplied blue palette.

2. **Heat scope?**
   **Recommendation:** calendar index plus every static month page, NL + EN; no jump-nav and no homepage upcoming cards. This is consistent and keeps pre-opening cards neutral.
   **Alternatives:** month pages only; also shade homepage “Bijna afgelopen” (cheap but broadens the visual surface); shade upcoming/jump-nav (not recommended because closing urgency is misleading/ambiguous there).

3. **Tile source and attribution?**
   **Recommendation:** OpenStreetMap Standard raster tiles at `https://tile.openstreetmap.org/{z}/{x}/{y}.png`, `maxZoom: 19`, with always-visible `© OpenStreetMap contributors` linked to `https://www.openstreetmap.org/copyright`. It needs no account and is proportionate to one small map per museum page, but is best-effort/no-SLA and sends the page referrer to OSM. Follow OSMF’s tile policy: browser-driven views only, normal caching, no prefetch/offline/bulk download, no referrer suppression. Keep the URL in one JS constant so it is replaceable.
   **Alternatives:** owner-supplied commercial OSM tile provider/API key and terms; self-hosted tiles (largest operational burden); no basemap, marker/address only.

4. **Map interaction and dimensions?**
   **Recommendation:** one responsive map, `height: 22rem` (`max-width: 100%`), initial zoom 16, `minZoom: 5`, `maxZoom: 19`, zoom buttons/drag/keyboard on, scroll-wheel zoom off, no auto-open popup. Marker click/keyboard opens it. This avoids scroll trapping while keeping normal map interaction.
   **Alternatives:** 18rem or 28rem height; scroll-wheel on; static/non-draggable map; popup open on load; owner-supplied zoom limits.

5. **Maps on other pages?**
   **Recommendation:** no — museum detail pages only. It is the smallest auditable exception and matches the reserved 3b interface.
   **Alternatives:** museums-index map; exhibition-page map; both. Either alternative needs separate UX/performance/privacy planning and expands the JS allowlist.

6. **Leaflet version?**
   **Recommendation:** stable 1.9.4 with the exact runtime asset list in §3c.4; 2.0 remains prerelease and changes module/global behavior.
   **Alternatives:** owner-approved 2.0 prerelease (higher migration/test risk); defer until 2.0 stable.

7. **Missing-coordinate wording?**
   **Recommendation:** key `map_unavailable`: NL `Kaart niet beschikbaar; gebruik het adres hierboven.` / EN `Map unavailable; use the address above.` It is direct and leaves the address as the fallback.
   **Alternatives:** shorter `Kaart niet beschikbaar.` / `Map unavailable.`; silently omit the map (least helpful and harder to QA).

8. **Museum MORE multi-venue behavior?**
   **Recommendation:** one marker at the primary Gorssel venue, matching phase-3b D13’s one museum page and current address; mention the primary venue in the popup only if already present in curated data.
   **Alternatives:** multiple pins (requires a coordinate-array schema and popup labels); split venue pages (reopens frozen routing/data design); no map for MORE.

If the owner selects an alternative that changes a surface or expected count (especially Q2 or Q8), update the affected scope and exact QA expectations in this plan before implementation; do not improvise around a stale acceptance command.

## 3c.6 Ordered one-run subtasks

All runs are serialized because ST-3c-1 through ST-3c-3 edit the same curated file. Stop on conflict with §3c.5. Never use a generated-data edit as a fixture.

### ST-3c-1 — Coordinates batch A (10)

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

- **Scope:** the exact `static/vendor/leaflet/1.9.4/` files listed in §3c.4 only. No template references yet; no theme edit.
- **Work:** fetch official release zip; verify archive hash; copy unmodified runtime distribution + tagged license; record version/source in the commit body.
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

- **Scope:** `layouts/_default/museum-page.html`, `layouts/partials/head.html`, `layouts/partials/museum-info.html`, new `layouts/partials/museum-map-ready.html`, `static/js/museum-map.js`, `static/css/custom.css`, `i18n/nl.toml`, `i18n/en.toml`. Never `baseof` unless the proven deferred-head approach fails on the pin.
- **Work:** implement Q3–Q8 and §3c.4. Change the current `museum-info.html` call to pass page + generated museum + curated info explicitly; popup = generated museum name + curated address. Keep address server-rendered; no external HTML injection.
- **Verify:**

```sh
set -o pipefail
hugo --minify 2>&1 | tee /tmp/phase3c-map-build.log
test "$(grep -ci '^WARN' /tmp/phase3c-map-build.log)" = 0
EXPECTED_MAP_PAGES=60 # Q8 recommendation; use 58 only if owner selects “no map for MORE”
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
  "$EXPECTED_MAP_PAGES"
test "$(grep -Roh '<script' public --include='*.html' | wc -l | tr -d ' ')" = "$EXPECTED_SCRIPT_TAGS"
! grep -RE '<script[^>]*src=.https?://' public --include='*.html'
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
grep -R 'closing-heat-5' /tmp/phase3c-day0/kalender \
  /tmp/phase3c-day0/en/calendar --include='*.html' >/dev/null
```

Day-0 also remains a browser gate using `hugo server --clock 2026-09-13T00:00:00+02:00`; synthetic fixture data, if refreshed data lacks a day-0 show, lives only in a disposable copy and is never committed.

- **Commit:** `feat(calendar): add closing urgency heat`

### ST-3c-7 — Docs + final audit

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
- [ ] Calendar index + month pages show approved blue bands for eligible running shows; day 0 is darkest; >30 days/upcoming/open-ended/ended are neutral; text still communicates status without color.
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
EXPECTED_MAP_PAGES=60 # Q8 recommendation; update per recorded owner answer
EXPECTED_SCRIPT_TAGS=$((EXPECTED_MAP_PAGES * 2))
grep -Rl '<script' public --include='*.html' | sort > /tmp/phase3c-script-pages
test "$(wc -l < /tmp/phase3c-script-pages | tr -d ' ')" = "$EXPECTED_MAP_PAGES"
test "$(grep -Ec '^public/(en/)?museums/[^/]+/index\.html$' /tmp/phase3c-script-pages)" = \
  "$EXPECTED_MAP_PAGES"
test "$(grep -Roh '<script' public --include='*.html' | wc -l | tr -d ' ')" = "$EXPECTED_SCRIPT_TAGS"
! grep -RE '<script[^>]*src=.https?://' public --include='*.html'
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
grep -R 'closing-heat-5' /tmp/phase3c-day0/kalender \
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

For a deliberate missing-coordinate proof, build a disposable copy with one pair removed. Assert that page contains the Q7 text, contains no `leaflet.css`, `leaflet.js`, or `museum-map.js`, and still prints its address. Never leave that fixture in this worktree.

### VISUAL — real browser on a locally served pinned build

Start:

```sh
hugo server --disableFastRender --clock 2026-09-12T12:00:00+02:00
```

The operator records pass/fail in the implementation log after checking actual rendered behavior (DOM/network inspection, not screenshot-only):

- NL `/museums/rijksmuseum/` and EN counterpart: map becomes visible at 22rem; standard tiles render; marker sits on Museumstraat 1/Rijksmuseum, not Amsterdam centroid; attribution remains visible.
- Click marker and activate it by keyboard: popup opens and contains the museum name + address; close/reopen works; language switch keeps the same venue.
- Scroll over the page: page scroll is not trapped; zoom buttons, drag, and keyboard work; responsive widths at narrow mobile and desktop do not overflow.
- Network panel: Leaflet CSS/JS and `museum-map.js` are same-origin; tile requests use only the approved host; home, calendar, museum index, exhibition, and about pages request no JS or map tiles.
- One museum in each coordinate spot-check region: pin plausibly overlays the official venue. Check Museum MORE according to Q8.
- Disposable missing-coordinate page: address + Q7 empty state render, map remains absent, and network shows no Leaflet/tile request.
- `/kalender/`, `/en/calendar/`, and one NL+EN month page: 21–30 is lightest and 0 is darkest; 14–20, 7–13, and 1–6 deepen monotonically; countdown text remains legible and card links work.
- Restart with `--clock 2026-09-13T00:00:00+02:00` to inspect a real day-0 card (`end: 2026-09-13`) as `closing-heat-5`. Use a disposable synthetic copy only if refreshed data no longer contains examples for every band.
- Confirm >30-day, upcoming, open-ended, and recently-ended/collapsed cards are unshaded; jump-nav is unshaded; homepage upcoming order is earliest start first.
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
5. Coordinate fields may remain harmless curated data, or revert the three coordinate commits if the owner wants the exact pre-3c schema instance.

No rollback touches `gh-pages` directly, generated feeds/data, frozen slugs, or pipeline scripts. Republish through the normal site pipeline after owner merge/revert.

## 3c.11 Risks & unknowns

| Risk / unknown | Mitigation / gate |
|---|---|
| JS leaks beyond museum pages | Shared readiness predicate; no inline JS; exact source/output allowlist and 60-page/120-tag gates |
| Tile provider availability, policy, or privacy | Q3 owner choice; visible attribution; no prefetch; one replaceable URL; address survives outage |
| Wrong venue / swapped coordinates | Numeric/bounds audit + source per record + all-venue plausibility review + six independent spot-checks |
| Museum MORE has multiple venues | Q8; default remains phase-3b primary Gorssel model |
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

*(Append during the build, one bullet per run.)*

Status: `draft`
