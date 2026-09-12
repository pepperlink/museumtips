# Independent review — Phase 3b (Museum & exhibition pages)
> **Post-review status (2026-09-12):** all HIGH findings and the medium/low items were folded into `PLAN.md` on this branch, with the mechanics re-verified on the pinned Hugo v0.166 (see PLAN.md §3b.13). This document is preserved as the review record.


Reviewer: independent agent pass, 2026-09-12. Scope: `PLAN.md` §"Phase 3b — Museum & exhibition pages (plan)" only (3b.0–3b.13). Verified against this worktree on pinned-adjacent **Hugo v0.165.0 extended** (local; pipeline pins v0.166.0 — see "Not verified" for the gap this leaves). All template/behaviour claims below marked "verified" were reproduced with real `hugo build`/`hugo list all` runs in a scratch experiment, then fully reverted (`git status` clean; no repo file other than this review was changed).

## Verdict: **rework**

Not because the overall shape is wrong — D7/D8/D12/D13/D15 and the page specs (3b.5) are sound and the non-goals (3b.2) correctly fence off 3c/3d. But **D9's core data-access mechanism as written does not work and will break the Hugo build**, not just render wrong — that's a launch-blocking defect in the plan's most load-bearing new decision, and it needs a rewrite of that one section before any ST-B run starts. Findings 1–2 are the reason for "rework" rather than "approve-with-fixes"; everything else is fixable in-flight.

## Strengths

- Reuses the month-page content-adapter mechanism instead of inventing a second page-generation path — verified this pattern (`AddPage` with `kind`/`path`/`url`/`layout`/`type`/`translationKey`/`params`) works identically for a new `museum`/`exhibition` type, mirroring `calendar-month` exactly.
- D8's tracker-frozen-slug design is the right call — build-time `urlize(title)` would genuinely misfire on real data (`H'ART Museum (ex-Hermitage Amsterdam)` urlizes to `hart-museum-ex-hermitage-amsterdam`, confirmed live in this dataset).
- Non-goals (3b.2) are disciplined: explicitly reserves the map slot without building toward it, explicitly excludes a CTA slot, explicitly keeps schema additive.
- D12/D13 (ended-show lifecycle, Museum MORE one-page) are pragmatic, minimum-surface answers that don't fight the existing D3/overlap logic.
- Owner-question list (3b.9) is mostly the right set and appropriately concrete (asks for a pasted VEVENT template, a pasted slug table — good instinct to offload ambiguous naming to the owner rather than guess).

## Numbered findings

### 1. [HIGH] D9's `hugo.Data.<file>.<slug>` access pattern fatally breaks the build for any hyphenated slug

**What:** D9 says: "Join at build: `hugo.Data.museums_info.<slug>`." D8's own slug charset is `[a-z0-9]+(?:-[a-z0-9]+)*` — hyphens are expected and will occur for real museums (e.g. a slug like `h-art-museum`). Go's `html/template`/`text/template` dot-chain syntax does not accept `-` inside a chained identifier.

**Verified:** built a scratch data file and template using `{{ hugo.Data.museums_info.h-art-museum }}`. Result:
```
ERROR error building site: "…/layouts/_default/baseof.html:2:1": apply base template failed:
template: museums.html:2: bad character U+002D '-'
```
This is a **template parse error**, which fails the *entire* build (Hugo parses templates before executing per-page), not a per-page render glitch. The very first museum or exhibition whose slug contains a hyphen (a near-certainty given D8's own slug list examples) takes down `hugo --minify` for the whole site.

**Why it matters:** This is the plan's core "join at build" mechanic for both museum and exhibition extras (D9), used throughout the museum/exhibition page specs (3b.5) and referenced directly in ST-B3/ST-B4's scope. If implemented as literally written, ST-B3 cannot pass its own verify step (`hugo --minify` exits 0) once a real hyphenated slug is in the extras file.

**Fix:** Always access by key, never by dot-chase: `{{ index hugo.Data.museums_info $slug }}` (or `{{ with index hugo.Data.museums_info $slug }}…{{ end }}` for the "missing key → omit" case D9 already wants). Add this as an explicit implementation note in D9, not left to be discovered by ST-B3.

### 2. [HIGH] D9's filenames (`museums-info.json`, `exhibitions-info.json`) don't match the claimed dot-access key, and the parenthetical "Hugo turns `museums-info.json` into `museums_info`" is factually wrong

**What:** D9's file table names the curated files with hyphens: `data/museums-info.json`, `data/exhibitions-info.json`. The text then claims "Hugo turns `museums-info.json` into `museums_info`" to justify the dot-access `hugo.Data.museums_info`.

**Verified:** created `data/extra-facts.json` and printed `hugo.Data` — the merged key is **`extra-facts`** (hyphen preserved), not `extra_facts`. Renaming the same file to `data/extra_facts.json` produced the key `extra_facts`, which *is* dot-accessible (`hugo.Data.extra_facts` renders correctly). Hugo does not perform hyphen→underscore normalization for `data/` files; the key is the literal file basename.

**Why it matters:** compounds finding 1. Even after fixing the per-slug lookup with `index` (finding 1), the *outer* key `hugo.Data.museums_info` used throughout the page specs and D16's "join partials" is simply the wrong name for a file called `museums-info.json` — it would need `{{ index hugo.Data "museums-info" }}` for the outer access too, or the file should be renamed.

**Fix:** rename the curated files to `data/museums_info.json` and `data/exhibitions_info.json` (underscore) so the *outer* key is dot-accessible as documented, and combine with finding 1's `index`-based *inner* per-slug lookup. Update ST-B1's scope (currently says `data/museums-info.json`, `data/exhibitions-info.json`) and AGENTS.md's future curated-file bullet (ST-B8) to match.

### 3. [HIGH] D11/ST-B6: scoping the ICS output format globally in `hugo.toml` leaks to every other `page`-kind template and produces per-build warnings

**What:** ST-B6's scope says "hugo.toml outputFormat + exhibition calendar layout." A natural reading is to flip Hugo's global `[outputs] page = [...]` to include the new format, since Hugo's `[outputs]` table is keyed by page **kind**, not by content `type`. Museum pages, the `about`/`calendar`/`museums` content pages, and *all* ~178 calendar-month adapter pages share `kind = "page"`.

**Verified:** with `[outputs] page = ['html', 'calendar']` set, the build still exits 0 but emits one warning per affected template that lacks a matching output template, e.g.:
```
WARN  found no layout file for "calendar" for layout "calendar-month" for kind "page": …
WARN  found no layout file for "calendar" for layout "museum" for kind "page": …
WARN  found no layout file for "calendar" for layout "museums" for kind "page": …
```
Removing the global `[outputs]` entry and instead setting `"outputs" (slice "html" "calendar")` **only inside the exhibition `AddPage` dict** produces the `event.ics` file for exhibition pages only, with zero warnings and no stray files anywhere else (verified: museum test page had only `index.html`, no `.ics`; no other page gained a spurious calendar output). This per-page `outputs` field has worked in content adapters since Hugo v0.147.2 (well before the pinned v0.166.0), so it's safely available.

**Why it matters:** the plan's own zero-JS/no-stray-output verification bar ("Build size … fine for Hugo") implicitly assumes a clean build; a global `[outputs]` change is the kind of thing that passes `hugo --minify` (exit 0) while quietly spamming warnings across every one of the ~90 month pages plus the three index pages, which could mask real errors in CI output and is easy for an implementing agent to reach for since it's the first result in most Hugo "add an ICS output format" tutorials.

**Fix:** state explicitly in D11/D16/ST-B6 that the `outputs` field must be set **per adapter page** in `add-exhibition-pages.html` (mirroring how the museum-adapter dict does *not* get an `outputs` key), and that the global `[outputs]` table in `hugo.toml` should not be touched.

### 4. [HIGH] D7's URL table gives the full public EN URL, but the `AddPage.url` value must omit the `/en/` prefix — copying the table literally double-nests the path with no build error

**What:** D7's table literally shows, e.g., `/en/exhibition/<slug>/` as "the EN [URL]" and `/en/museums/<slug>/` likewise. The existing (working) month-page partial does **not** include the `en/` prefix in the `url` value it passes to `AddPage` — it uses `printf "calendar/%s/" $key` for English, and Hugo's own per-language subdir routing (English is the only non-default language; `defaultContentLanguageInSubdir = false` only exempts the default `nl`) prepends `/en/` automatically.

**Verified:** setting the exhibition/museum adapter dict's `url` field to the literal table value (`"en/exhibition/test-show/"`) produced pages at **`public/en/en/exhibition/test-show/`** — a doubled, dead path — while `hugo --minify` still exited 0 and produced no error or warning. Fixing the dict to omit the prefix (`"exhibition/test-show/"`, matching the month-page convention) produced the correct `public/en/exhibition/test-show/`.

**Why it matters:** D7's table is the primary reference an implementing agent will copy from for ST-B3/ST-B4. Because the double-prefix bug is silent (no build failure), it would only surface via the exact `test -f public/en/…` commands in §3b.11 — which is good, *if* run — but it's an easy, costly-to-debug mistake to bake into the first draft. `hugo list all`'s `permalink` column (verified: correctly showed `.../en/museums/test-museum/` once fixed) is a fast way to catch it, but the plan doesn't mention checking permalinks, only `test -f`.

**Fix:** add one line to D7 clarifying that `AddPage.url` values are locale-relative and must never include the language subdir prefix — spell out the exact NL/EN pair the way `calendar-month-keys.html` does it (`"kalender/%s/"` vs `"calendar/%s/"`, no `en/`).

### 5. [MEDIUM] `countdown.html` "precise" mode calling convention is unspecified and the existing signature can't take a mode flag without touching 3 unrelated call sites

**What:** D14/D16 say detail pages call `countdown.html` in a new "precise" mode, reusing the same partial. Today `countdown.html` is called as `partial "countdown.html" .` — the exhibition row itself, no wrapper dict — from three places: the card partial (`exhibition.html`), `museums.html`, and the home layout. Its body reads `.end`/`.start` directly off that context.

**Why it matters:** to add a `precise` flag, either (a) the call sites all change to pass a wrapper dict (`dict "value" . "precise" true`), which means the three *existing, unrelated* call sites must be touched and re-verified even though ST-B4's stated scope is "this layout only," or (b) a parallel `countdown-precise.html` (or similar) is added instead, leaving the shared partial and its 3 call sites untouched. The plan doesn't choose between these, so it's easy to either regress the cards or scope-creep ST-B4.

**Fix:** pick (b) explicitly — a separate small partial (or a param that defaults false and is passed only from the new templates) — and say so in D16, so ST-B4's "no card changes yet" claim actually holds.

### 6. [MEDIUM] No i18n / display convention for `cards[].accepted == null` (unknown) state

**What:** D9's museum extras schema allows `"accepted": true|false|null` per entrance card. D14 defines `card_accepted` and `card_not_accepted` but nothing for the `null`/unknown case, and the museum page spec (3b.5 item 7) doesn't say what to render when `accepted` is null.

**Why it matters:** this is a real, expected data state per D9's own collection protocol ("if a fact is unclear … set unknown/omit — never guess"), not an edge case. Without a defined string, an implementer will either invent one inline (violating the "new UI strings go in i18n, never inline" rule in 3b.0) or silently drop the row.

**Fix:** add a key, e.g. `card_status_unknown` ("Onbekend of dit museum deze kaart accepteert" / similar), or explicitly decide the null case omits that card's status line and states only the label.

### 7. [MEDIUM] D11's optional mailto share references an i18n subject that's never defined

**What:** D11 says: "Optional `mailto:?subject=&body=` using i18n subject." D14's key table has no `share_mailto_subject` (or equivalent) key.

**Why it matters:** same class of gap as the explicit "parent-museum back link" example the review brief called out — a spec'd display string with no i18n key. Since D11 marks this "optional," the cheapest fix is to defer it, but the plan should say that explicitly rather than leave a dangling reference.

**Fix:** either drop the mailto option from 3b's scope (defer to a later phase, consistent with "do not draft visitor copy… land collected, cited facts only" spirit) or add the key to D14.

### 8. [MEDIUM] Parent-museum back link on the exhibition page has no i18n key (the exact gap class the review brief flagged)

**What:** Exhibition page spec item 1: "Back links: calendar index + parent museum page." `back_to_calendar` (existing) covers the first. `back_to_museums` (D14) is "Terug naar alle musea / Back to all museums" — that's the **index**, not "back to *this* museum." No key exists for "back to [museum name]" or a generic "back to the museum" label.

**Why it matters:** walking the page spec section-by-section (as the review brief asked), this is the one string with no defined text and no defined key. If the museum's own name is used as the link text with no label at all (e.g. `← Centraal Museum`), that needs no i18n key — but the plan doesn't say that's the intended treatment, so it's ambiguous rather than decided.

**Fix:** decide explicitly — either "link text = museum name, no i18n string needed" (cheapest, consistent with how month-page prev/next links use month names as link text), or add a `back_to_museum` key. Either is fine; leaving it undecided is the issue.

### 9. [MEDIUM] ST-B5 touches a shared partial exercised by every existing page; its verify step should explicitly re-run the phase-2 regression battery, not just phase-3b greps

**What:** ST-B5's scope is `layouts/partials/exhibition.html` (the card partial) and `layouts/_default/museums.html` — both used by home, `/kalender/`, every month page, and `/musea/`. Its verify step lists phase-3b-specific checks (card href retarget, hash-link fallback) plus a *subset* of phase-1 regressions (year-1, `0001-01`). It does not mention re-running the D3 ended-count check, the "Opening soon" section render, or the zero-`<script>` sweep — all of which are exercised by the same partial and are already-established regression baselines (§7/§11 log of the Phase-2 section above).

**Why it matters:** this is exactly the kind of change (small, mechanical, touches a widely-reused partial) that regresses something two layers away from the diff. The review brief specifically asked about "a regression baseline before templates change" — ST-B5 is the subtask most likely to need one and least likely to get one as scoped.

**Fix:** ST-B5's verify step should re-run the *full* Phase 2 QA block from §7 (the four greps + the ended-count spot check + the no-`<script>` sweep), not just the 3b-specific assertions.

### 10. [MEDIUM] Sequencing gap: cards can start linking to museum/exhibition pages before extras exist, and this isn't flagged as a decision

**What:** ST-B5 (card retarget) depends only on ST-B3 + ST-B4 (adapters + layout), not on C1/C2 (extras collection) landing. C1/C2 are both sized "L" and explicitly allowed to lag ("C1/C2 can interleave after ST-B1 + museum slugs; landing extras before ST-B3 only affects whether sections are empty").

**Why it matters:** this is a legitimate, reversible design choice (graceful-omit is well specified), but it means there's a real window — plausibly the bulk of the phase, given C1/C2 are the largest-effort subtasks — where every museum/exhibition page linked from every card and the `/musea/` index is missing most of hours/transport/parking/pricing/admission/press. That's a visible, public quality regression risk that should be an explicit owner sign-off, not an implicit side effect of subtask dependency ordering.

**Fix:** add to 3b.9 (owner questions) something like: "OK to publish museum/exhibition pages (and retarget cards to them) before C1/C2 extras are collected, accepting that most pages will show only the generated-JSON fields for a while — or should ST-B5 (card retarget) wait for a minimum extras threshold (e.g. all 30 museums, or top-N by traffic)?"

### 11. [MEDIUM] Owner questions (3b.9) don't ask the owner to sign off on the C1/C2 collection effort/timeline

**What:** C1 (30 museums, official-source hours/transport/parking/access/cards/pricing, cited) and C2 (up to 187 exhibitions' admission + press, cited) are both sized "L," explicitly hand-curated, and explicitly require live-URL verification per fact (3b.4 D9 collection protocol). This is very plausibly the single largest time cost in the whole phase, larger than all the template subtasks combined.

**Why it matters:** 3b.9 asks 12 questions about URLs, slugs, MORE/Ruurlo, card titles, ICS details, press policy, lat/lon, translation policy, and the build gate — all reasonable — but never asks the owner to confirm the collection effort is acceptable, staged, or should be descoped for a first cut (e.g., "ship with only hours + pricing for the 30 museums, defer press/admission-flag collection to a follow-up"). Without that, a run could spend an unbounded amount of effort on C1/C2 before the owner ever sees a page.

**Fix:** add an owner question along these lines to 3b.9, e.g.: "C1/C2 are the largest-effort subtasks in this phase (30 museums × ~7 facts, up to 187 exhibitions × admission+press, each cited to a live official source). Should a first cut ship with partial coverage (e.g. museum hours+pricing only, exhibition admission-flag only, no press) and backfill press/full extras later, or hold the whole phase for full coverage?"

### 12. [LOW] D7 says old hash links work "until ST5 retargets them" — should say ST-B5

**What:** D7's text: "keep `id="{{ urlize name }}"` so old card hash links still work until ST5 retargets them." There is no "ST5" in 3b.7's subtask list (ST-P, ST-B1…ST-B8). "ST5" is Phase 2's "Copy refresh" subtask (§5 above the phase-3b section) — an apparent copy-paste leftover. The subtask that actually retargets card/index links in phase 3b is **ST-B5**.

**Why it matters:** minor, but could send an implementing agent looking for the wrong subtask or wondering if a phase-2 rerun is implied.

**Fix:** s/ST5/ST-B5/.

### 13. [LOW] Naming collision risk (not a functional bug, but worth avoiding): `layouts/_default/exhibition.html` (new page layout) vs. `layouts/partials/exhibition.html` (existing card partial)

**What:** D16 proposes a new single-page layout at `layouts/_default/exhibition.html`. An existing, heavily-reused card partial already lives at `layouts/partials/exhibition.html`. These are different Hugo template namespaces (verified: both coexist and resolve correctly with no collision — confirmed via a working scratch build), so this is **not a functional defect**.

**Why it matters:** purely readability/maintenance — two same-named files with very different jobs, one calling the other indirectly, is the kind of thing that causes a future contributor (or a fast-moving agent) to edit the wrong file.

**Fix:** optional — consider `layouts/_default/exhibition-page.html` or similar if the naming collision bothers the owner; not blocking.

### 14. [LOW] New i18n keys with placeholders (`more_in_city`, `opens_in`, `closes_in`) don't state which of the repo's two existing i18n-argument conventions to use

**What:** the repo already has two different conventions for parameterized i18n strings: `dict`-style Go-template substitution (`exhibitions_in_month` = `"Tentoonstellingen in {{ .Month }} {{ .Year }}"`, called via `i18n "exhibitions_in_month" (dict "Month" … "Year" …)`), and `printf`-style (`ended_shows` = `"Afgelopen (%d)"`, called via `printf (i18n "ended_shows") (len $ended)`). D14's new keys use `%s`/`%d` placeholders (`more_in_city`, `opens_in`, `closes_in`), which matches the `printf` convention, but the plan never says so explicitly.

**Why it matters:** minor consistency risk; an implementer could reach for the `dict` pattern instead and it wouldn't be obviously wrong until reviewed.

**Fix:** one line in D14 or ST-B2: "call with `printf (i18n \"key\") arg` to match the existing `ended_shows` convention," since that's the pattern the `%s`/`%d` syntax implies.

### 15. Verified non-issue: sitemap inclusion needs no special handling

The review brief asked to check for a sitemap gap. **Verified**: this is a non-issue. Hugo auto-includes every page (including `AddPage`-created adapter pages) in `/nl/sitemap.xml` / `/en/sitemap.xml` with no extra code — confirmed the existing 89 calendar-month pages already appear there (93 `<url>` entries in `public/nl/sitemap.xml` from a stock build), and confirmed a scratch museum/exhibition test page appeared the same way. No plan change needed; noting this so it isn't re-litigated.

## Mechanics check (§1 of the review brief) — summary of verified results

- **AddPage dict fields, verified against the real `calendar-month` mechanism:** `kind`/`path`/`url`/`title`/`layout`/`type`/`translationKey`/`params` all behave as the plan assumes. A scratch `museum`/`exhibition` type+layout pair resolved cleanly against `layouts/_default/museum.html` / `layouts/_default/exhibition.html`, exactly mirroring `calendar-month`. **Confirmed feasible.**
- **`layout`/`type` resolution:** confirmed via `hugo list all`, which correctly reported `section=museum` / `section=exhibition` and the right permalinks for both languages once the URL prefix bug (finding 4) was fixed.
- **Per-page `event.ics` output (D11/ST-B6):** confirmed feasible **only** via the per-page `outputs` field on the exhibition `AddPage` dict (finding 3), not via a global `[outputs]` bump. The `text/calendar` media type and `.ics` suffix are Hugo built-ins; a custom `[outputFormats.calendar]` override (custom `baseName`/`protocol`) works as D11 describes.
- **`hugo.Data.museums_info.<slug>` (D9):** **does not work as written** — findings 1 and 2 are build-breaking, not stylistic.
- **Language switcher / `translationKey` pairing (D15):** confirmed working end-to-end in the scratch test — `partials/lang-switcher.html` correctly paired NL/EN museum and exhibition test pages via matching `translationKey`, no code change needed, matching the month-page precedent.

## Owner questions (3b.9) — technical-feasibility opinions

- **Q1 (URLs) / Q2 (slug freeze):** technically sound as scoped, contingent on fixing findings 1/2/4 before implementation.
- **Q4 (MORE one page):** confirmed via data (`data/exhibitions.json`) that the Ruurlo show's `city` field ("Ruurlo") doesn't match any `museums[].city` ("Gorssel") — D13's "no special handling, city links stay index-hash" is the right minimal answer; a museum page for MORE naturally includes the Ruurlo show already (join is by `museum` name, not `city`).
- **Q7 (ICS UID/DTEND):** verified the weekly feed's own convention from `museumtips.ics`: all-day `DTEND` is last-day-plus-one (e.g. a show ending `2026-09-13` emits `DTEND;VALUE=DATE:20260914`), and weekly UIDs are `museum-<hash>[-ld]@hermes.museumtracker` — confirmed no collision with the proposed `museumtips-<slug>@museumtips.pepperlink.nl` (different local-part scheme and domain). D11's "match the existing feeds" instruction is achievable; recommend the plan just paste this exact convention rather than asking the owner to paste a VEVENT template, since it's already fully visible in the tracked `museumtips.ics`.
- **Q11 (`/musea/` shrink vs keep in-list titles):** no strong technical driver either way; this is genuinely an owner call.
- **Missing question (see finding 11):** C1/C2 effort/timeline sign-off should be added.
- **Missing question (see finding 10):** whether ST-B5 (card retarget) should gate on a minimum extras threshold.

## Coverage check (§7 of the review brief)

Both page specs (3b.5) map completely onto the owner's stated requirements:

- **Museum page:** description, website, hours, transport, parking, accessibility, entrance cards, pricing (incl. supplements), current+upcoming shows, more-in-city, last-verified, and a location/map slot are all present as distinct, individually-omittable sections (3b.5 items 1–10, backed by D9's extras schema). **Fully covered**, nothing under-served.
- **Exhibition page:** dates+status, press links, admission + Museumkaart/supplement flag, description, museum link, one-event `.ics`, related shows, and share are all present (3b.5 items 1–10, D11). **Fully covered.**
- **Nothing appears over-built** relative to the ask, with one soft exception: D11's optional mailto share (finding 7) is a small scope add beyond a plain "share permalink," already marked optional by the plan itself — fine to keep optional or cut, not a real over-engineering risk.

## What I could NOT verify

- **Behaviour on the pipeline-pinned Hugo v0.166.0 extended specifically.** This review's local Hugo binary is v0.165.0 extended (the only one available in this environment); the pipeline pin is v0.166.0. All mechanics above (content-adapter `outputs` field, dot-vs-index template parsing, data-file key naming, URL prefix behaviour, sitemap auto-inclusion) are long-standing, version-stable Hugo behaviours, not v0.165/v0.166-specific features, so I have high confidence they carry over — but I could not run the literal pinned binary to confirm byte-for-byte.
- **Museum tracker / pipeline-side implementation (ST-P).** Out of scope for this repo and this review; I did not attempt to verify anything about the tracker's slug-freezing store, since it's explicitly pipeline-host work.
- **Actual content of any future `museums-info.json`/`exhibitions-info.json` data** (doesn't exist yet — C1/C2 haven't run), so I could not test the *real* per-museum slug set for hyphen frequency beyond the one confirmed real example (`H'ART Museum` → `hart-museum-ex-hermitage-amsterdam`, which itself demonstrates the hyphen problem in finding 1 would apply immediately).
- **Live-site behaviour** (GitHub Pages serving, MIME type for `.ics` on Pages, cert/CDN behaviour) — this review only ran local `hugo build`, consistent with the plan's own "if a run cannot build locally it must say so" convention; I *could* build locally (unlike some phase-2 runs), but did not publish or check `gh-pages`.
- **Whether `hugo list all` is available/enabled on the exact pipeline-host binary** — the plan's §3b.11 suggests it as a verification aid; I confirmed it works locally and is genuinely useful (it caught the URL-prefix bug immediately via the `permalink` column) but didn't check the pipeline host's Hugo build flags.
