# PLAN — Phase 2: Calendar UX + polish

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

**Recommend — calendar view (owner: pick D1)**

| | Static month pages (0 JS) | Vanilla-JS widget | Hybrid (static + small JS) |
|---|---|---|---|
| What | Keep the end-month **list** on `/kalender/`. Add build-time `/kalender/YYYY-MM/` (and `/en/calendar/YYYY-MM/`) listing shows **open that month** (date overlap; null-end included). Jump-nav links there. | One page; JS switches months / optional day grid; needs a baked JSON slice. | Static pages as the source of truth; JS only enhances in-page switching. |
| Fit | Matches date-**range** shows; SEO; no-JS; Hugo-native. | First JS on the site; no-JS users need a duplicate list anyway. | Extra moving parts for little gain over static links. |
| Cost | More URLs; overlap logic in templates. | New testing + a11y; contradicts no-JS lean. | Highest complexity. |

A day-cell grid is a poor fit (shows last weeks–years; cells empty or packed). **Recommendation: static month pages + fixed list (column 1). No JS this phase.** Fallback if the owner wants less surface: list-only (fix §3 bugs, no new routes).

**Recommend — city / museum filter (owner: pick D2)**

| | Static | Client-side |
|---|---|---|
| City (19) | New city sections or `/kalender/stad/…` pages, or regroup `/musea/` by `city`. | Filter chips; needs JS. |
| Museum (30) | Already on `/musea/`. Polish that page; link from calendar meta. Do not duplicate. | Same chips on `/kalender/`. |

**Recommendation: static. Regroup `/musea/` by city; optional city jump-nav or city pages only if D1 month pages are not enough. No filter JS.**

**Recommend — ended shows (owner: pick D3)**

| Policy | Trade-off |
|---|---|
| Keep | Honest archive; page stays noisy (8 real ended now, more each Thursday). |
| Collapse | `<details>` “Afgelopen (N)” at the bottom. Scan stays clean; still findable. |
| Hide after N days | Matches weekly refresh. **N = 7** (one pipeline cycle). Older ended drop; just-ended remain briefly. |

**Recommendation: hide `end < today − 7 days`; collapse the rest of ended in `<details>`. Null `end` is never ended — own “Geen einddatum” bucket.**

**Recommend — housekeeping (owner: pick D4, D5)**

- **D4 root `index.html`:** **Remove.** Pipeline is live; file is unused by Hugo; leftover risk if someone treats it as the site.
- **D5 `static/*.ics`:** **Pipeline writes root + `static/` in the same commit** (README already assumed this). Alternative: stop shipping `static/*.ics` if publish always overlays root → `public/` (confirm on the pipeline host first). Do not hand-copy feeds in this repo. Do not touch feed URLs.
- **D6 (found in recon):** Show tracker `quirks` on public `/musea/`? **Recommend hide** (operator notes, mixed EN, not visitor copy). Owner can keep.

**Copy refresh:** not designed here. Operator drafts; owner approves; then one landing run. Files: `content/{nl,en}/*.md` (incl. front matter) + `i18n/{nl,en}.toml`.

## 5. Approach & subtasks

Each item is **one Cursor run**. Stop if a §4 decision is still open.

### 2.1 Date correctness + meta line

- **Scope:** `layouts/_default/calendar.html`, `layouts/_default/museums.html`, `layouts/partials/{exhibition,format-date,countdown}.html`, `i18n/{nl,en}.toml`.
- **Steps:** Guard null `end`/`start`. Sort jump-nav + sections by real `YYYY-MM`. Open-ended section (not `#0001-01`, not “Afgelopen”). Hide missing start. Shorter dates (abbrev month; range `9 mei – 13 sep 2026` when both known; `t/m 13 sep 2026` when only end). Keep countdown labels. Same date helper on `/musea/` and home (shared partial).
- **Tests:** The five named shows never render year 1 or Ended. No `#0001-01`. Months ISO-sorted. 67 missing starts print no “Startdatum onbekend”.
- **Docs:** none beyond i18n keys.
- **Verify:** `hugo --minify`; grep `public/kalender/index.html` for `1 januari 1` / `#0001-01` (expect 0); spot three meta lines.
- **Model:** `grok-4.6`. **Depends:** none (D3 only affects whether ended still list).

### 2.2 Ended-exhibition policy

- **Scope:** `layouts/_default/calendar.html`, `layouts/index.html` (only if policy should change home), `i18n/{nl,en}.toml`.
- **Steps:** Implement the chosen D3 rule. Home “Bijna afgelopen” stays `end >= today`.
- **Tests:** A show with `end` last week vs eight weeks ago matches D3. Null-end unchanged from 2.1.
- **Docs:** one line in README if the rule is visitor-visible.
- **Verify:** `hugo --minify`; count “Afgelopen”/“Ended” on NL+EN calendar.
- **Model:** `composer-2.5`. **Depends:** D3, 2.1.

### 2.3 Calendar month view

- **Scope:** `layouts/_default/calendar.html`, new month layout + content/archetype as needed, `content/{nl,en}/calendar.md` front matter, `i18n/{nl,en}.toml`. No theme edits; no `data/exhibitions.json` edits.
- **Steps:** Implement D1. Overlap: open in month M if `end` is null or `end >= M-start`, and `start` is null or `start <= M-end`. Both languages, same slugs. List page keeps end-month grouping.
- **Tests:** A Sep-2026 page includes a May–Oct show and the five open-ended; excludes a show that ended Aug 2026. `/en/calendar/2026-09/` exists. `hugo --minify` exits 0.
- **Docs:** README route list.
- **Verify:** `hugo --minify`; `ls public/kalender/ public/en/calendar/`; open one month page.
- **Model:** `grok-4.6`. **Depends:** D1, 2.1.

### 2.4 City / museum grouping

- **Scope:** `layouts/_default/museums.html`, optionally calendar layouts + `content/{nl,en}/museums.md` / calendar content, `i18n/{nl,en}.toml`.
- **Steps:** Implement D2 + D6. Default path: regroup `/musea/` by `city` (sorted); fix per-museum date lines (2.1 helper). Add city pages or calendar city nav only if D2 says so.
- **Tests:** 19 cities appear; no year-1 dates; quirks hidden or shown per D6; EN `/en/museums/` matches.
- **Docs:** README if new routes.
- **Verify:** `hugo --minify`; spot `public/musea/index.html` + EN.
- **Model:** `grok-4.6`. **Depends:** D2, D6, 2.1.

### 2.5 Copy refresh (NL + EN)

- **Scope:** `content/nl/{_index,about,calendar,museums}.md`, `content/en/{_index,about,calendar,museums}.md`, `i18n/{nl,en}.toml`.
- **Steps:** Land **owner-approved** operator draft only. Keep translationKeys/urls/layouts. Drop fixture wording. Technical i18n from 2.1–2.4 may be rewritten here — do both languages in one run.
- **Tests:** Every NL string has EN; no leftover “fixture”; subscribe URLs unchanged.
- **Docs:** n/a (this *is* the docs/copy).
- **Verify:** `hugo --minify`; read home + about in both langs.
- **Model:** `composer-2.5`. **Depends:** operator draft + owner approval; preferably after 2.1–2.4 so new keys are in the draft.

### 2.6 Housekeeping

- **Scope:** `README.md`, `AGENTS.md` if routes/ICS policy change, `docs/site-plan.md` (pointer only), root `index.html` if D4 = remove. **Not** `data/exhibitions.json`, root `*.ics`, theme, CNAME, gh-pages.
- **Steps:** README: live dataset (not fixture); Hugo routes; ICS rule from D5. AGENTS: drop stale “fixture” implications if any; keep feed-URL warning. D4 delete root `index.html`. D5 is a **pipeline-host** change plus README — do not copy `.ics` by hand.
- **Tests:** README commands still match `AGENTS.md`. Site build unchanged if only docs + unused `index.html`.
- **Docs:** this subtask.
- **Verify:** `hugo --minify`; `test ! -f public/index.html` is wrong (Hugo still emits home) — instead: root `index.html` absent from git if D4; `public/index.html` is the Hugo home.
- **Model:** `composer-2.5`. **Depends:** D4, D5; can run after 2.3–2.4 so README lists real routes.

## 6. Definition of done

- [ ] Owner signed §4 (D1–D6) on this plan.
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
- Local Hugo here is **0.165**; pipeline is **0.166**. Prefer the pin for final check; note if only 0.165 was used.
- Month-page URL scheme must not collide with `/kalender/` or `/en/calendar/` indexes; keep feed paths free.
- Overlap vs end-month on the same site can confuse; copy (2.5) must say which page is which.
- `static/*.ics` vs root: live sizes match root — confirm overlay in `publish_site.py` before deleting static copies.
- `.nojekyll` is cited in `AGENTS.md` under `static/` but is **not** in this worktree (likely gh-pages only). Do not add it here.
- Countdown uses integer day math (`Unix/86400`); timezone edge on “last day” already exists — don’t widen it.
- Copy run vs 2.1–2.4 both touch `i18n/*.toml` — serialize or rebase.

## 11. Log

*(Empty on purpose. Append dated notes during the build, one bullet per run: what landed, verify command + result, leftover decisions.)*
