# Independent review — PLAN.md §3c (Museum maps + calendar heatmap)

Reviewer: independent model (this document's author), reviewing a plan drafted by a different model (gpt-5.6-sol-high). Scope per the review brief: adversarial review of §3c.0–3c.12 only. **No PLAN.md edits, no site-code changes committed** — this document is the only file added.

## Claims reproduced on this lane

- Hugo on this machine: `hugo v0.165.0-76a5e1880ab46688155b02e99bab9be2a6134492+extended darwin/arm64` — **one minor version behind the pinned v0.166.0 extended**. Every result below is only as strong as that gap allows; the operator must re-run the same commands on the v0.166.0 pin before treating any of this as final sign-off.
- **Submodule gotcha (process, not a plan defect):** this checkout's `themes/huguette` submodule was *not* initialized (`git submodule status` showed a `-` prefix, directory empty). `hugo --minify` failed outright (`partial "headerimage.html" not found`) until `git submodule update --init --recursive` was run. §3c.3 says the recon build succeeded "after initializing the pinned Huguette submodule" — that's consistent with what I found, but it's worth restating loudly because it's exactly the kind of thing that burns a run before any §3c code is touched.
- **Baseline build, reproduced exactly:** after submodule init, `hugo --minify` → exit 0, **496 NL / 494 EN pages**, **0 WARN**, **0 `<script>` tags**. Matches §3c.3 verbatim.
- **Conditional per-page asset loading (§3c.4 mechanism), reproduced:** added a scratch `.Type == "museum-page"` + `index hugo.Data.museums_info .Params.slug` + lat/lon-presence predicate to `head.html`, gave `rijksmuseum` scratch `lat`/`lon`, added 3 placeholder vendor/JS files. Build: only `public/museums/rijksmuseum/index.html` and its EN counterpart gained script tags (`grep -Roh '<script' public | wc -l` = 4 = 2 pages × 2 tags); `van-gogh-museum` and `over`/`about` emitted 0. This is the same shape as the §3c.3 recon note and the ST-3c-5/§3c.8 `EXPECTED_MAP_PAGES`/`EXPECTED_SCRIPT_TAGS` gates. All scratch edits reverted; `git status --short` is clean.
- **Leaflet 1.9.4 vendor set, reproduced:** `curl -fsSL https://github.com/Leaflet/Leaflet/releases/download/v1.9.4/leaflet.zip` → SHA-256 `aaec1d5c3239a613a53e996087629aca1483cb2f0438b11b8a335c6cede4c16b`, **exact match** to §3c.3's recorded hash. Archive contains `dist/{leaflet.css,leaflet.js,leaflet-src.js,leaflet-src.esm.js,*.map,images/{layers.png,layers-2x.png,marker-icon.png,marker-icon-2x.png,marker-shadow.png}}` — exactly 5 images, confirmed all 5 are actually referenced (2 by `leaflet.css` `url(...)`, 3 by string literals inside `leaflet.js`'s runtime `Icon.Default` path logic), so the plan's "keep all 5" instruction is correct. No `leaflet.zip` LICENSE file exists in the archive (see Finding 2). `leafletjs.com/download.html` confirms 1.9.4 is still "Stable" and 2.0.0-alpha.1 still "Prerelease" (released 2025-08-16), matching §3c.3.
- **JS-exception auditability, reproduced:** the scratch build above proves a repo-wide `grep -Roh '<script'` / `grep -Rl '<script'` sweep can mechanically prove the JS exception stayed confined to ready museum pages, and `git ls-files '*.js'` on this checkout currently returns nothing extra to pollute the exact-match check in ST-3c-5/§3c.8 (the theme submodule doesn't leak `.js` files into `git ls-files` from the parent repo).
- **Coordinate-validation snippet, reproduced:** ran the exact ST-3c-1 Python block against the real (coordinate-less) `data/museums_info.json` — it correctly raised `AssertionError` identifying the first slug (`rijksmuseum`) once I gave it `lat`/`lon` but no `sources[]` entry, then passed once sources were added. `data/museums_info.json` currently has 30/30 keys and 0/30 coordinate pairs, confirmed via `jq`.
- **Heat/CSS contrast claims, reproduced exactly:** computed WCAG relative-luminance contrast for `#172554` against all five backgrounds — `13.5, 12.04, 10.34, 8.15, 5.78` — matches §3c.4's "13.50:1 to 5.78:1" to the stated precision. Also confirmed *why* the link-color override is necessary and not just cosmetic: the site's default link color `--clink: #07c` only reaches `4.28 → 1.83`:1 against the five backgrounds (fails AA on four of five), so replacing it with `#172554` inside heat cards is load-bearing, not decorative.
- **Day-0 fixture, reproduced:** the live dataset (`compiled: 2026-09-12`) has 7 exhibitions with `end: 2026-09-13`, so `hugo --clock 2026-09-13T00:00:00+02:00 --minify` genuinely exercises "Laatste dag"/day‑0 today, with **no synthetic fixture needed right now** (confirmed via a real build with that clock override — 2 pages under `/kalender/` render "Laatste dag").
- **i18n key-parity script, reproduced:** the exact regex from ST-3c-5/§3c.8 correctly reports `nl==en` (95/95) on the real `i18n/*.toml` files.
- **`data/exhibitions.json`/`museums_info.json` shape, reproduced:** 30 museum slugs in both files match; `sources[]` already uses `{"fact": ..., "url": ...}` shape elsewhere (e.g. `rijksmuseum`), consistent with what the coordinate audit expects.

Everything above that could be mechanically tried, was tried, on real repo state, with no lasting changes (verified via `git status --short` / `git diff --stat` after each experiment).

## Findings

### 1. MAJOR — the Hugo-side "non-null" coordinate check has no specified correct implementation, and the QA never tests the exact failure mode the spec calls out

§3c.4 requires the readiness predicate to treat `lat`/`lon` as ready only if they "exist, are finite non-null numbers... form a complete pair," and separately promises "missing/invalid one-sided pairs are treated as missing, never coerced to `0`, and never produce a map." I tested the obvious Hugo idiom for "exists" — `isset $info "lat"` — against a scratch record with `"lat": 52.358, "lon": null` (an explicit JSON `null`, not an absent key):

```
TYPECHECK lat=52.358 type=float64 lon= lontype=<nil> isset_lon=YES isfloat_lon=NO
```

`isset` returns `YES` for an explicit `null` value. A predicate built the natural way ("lat/lon both **exist**" → `isset`) would treat this one-sided-null record as ready, load Leaflet CSS/JS/tile requests on that page, and rely entirely on the JS `try`/`catch` fallback to hide the mess after the fact — directly contradicting the "no Leaflet CSS, no script tags, no tile request" guarantee for the not-ready case. The correct idiom (`ne $info.lon nil`, confirmed to correctly return `NO` for this case) is not mentioned anywhere in §3c.4.

Compounding this: §3c.8's own missing-coordinate QA step says to build "a disposable copy with **one pair removed**" — i.e. it only tests the *absent-key* case, never the *explicit-null* case that the spec's prose explicitly worries about. So the one code path most likely to be implemented wrong is also the one path the plan's own QA battery never exercises.

**Fix:** name the exact Hugo check in §3c.4 (`ne .lat nil` / `ne .lon nil`, not `isset`), and add a second disposable-fixture case to §3c.8: one museum record with `"lon": null` (not removed), asserting the same "no map assets, no tile request, Q7 text renders" outcome as the removed-key case.

### 2. MAJOR — ST-3c-4's own verify script cannot pass as literally written: the release zip has no `LICENSE` file

Downloaded the exact URL in ST-3c-4 (`leaflet.zip` from the `v1.9.4` GitHub release) and unzipped it: it contains only `dist/{leaflet.css,leaflet.js,leaflet-src.js,leaflet-src.esm.js,*.map,images/*}` — **no `LICENSE` file at any level**. ST-3c-4's verify block includes `test -f static/vendor/leaflet/1.9.4/LICENSE`, but the only fetch command given (the `curl ... leaflet.zip` line) cannot produce that file. The "Work" line says "copy... + tagged license" (correctly implying a second, separate fetch), but no command for it appears anywhere in §3c.4 or ST-3c-4.

I confirmed the license text exists at the tag itself: `curl -fsSL https://raw.githubusercontent.com/Leaflet/Leaflet/v1.9.4/LICENSE` → HTTP 200, BSD-2-Clause, "Copyright (c) 2010-2023, Volodymyr Agafonkin... Copyright (c) 2010-2011, CloudMade," matching §3c.4's claim about the license type.

**Fix:** add the explicit `curl -fsSL https://raw.githubusercontent.com/Leaflet/Leaflet/v1.9.4/LICENSE -o static/vendor/leaflet/1.9.4/LICENSE` line to ST-3c-4's "Work"/verify block so the subtask is actually self-contained and reproducible as written.

### 3. MAJOR — the "no CDN script" audit regex has a confirmed false-negative on unquoted `src=` attributes

ST-3c-4 and §3c.8 both gate on `! grep -RE '<script[^>]*src=.https?://' public --include='*.html'`. I built three variants of an externally-sourced script tag and ran that exact pattern:

```
<script defer src=https://cdn.example.com/x.js></script>      → NOT matched
<script defer src="https://cdn.example.com/y.js"></script>    → matched
<script src='https://cdn.example.com/z.js' defer></script>    → matched
```

The `.` in `src=.https?://` requires exactly one character between `=` and `https` (a quote); an **unquoted** attribute value — valid HTML5, and something a careless template edit like `<script defer src={{ $url }}>` would silently produce — has zero characters there and slips through undetected. This is precisely the audit meant to prove "no CDN-loaded library," and it has a real, demonstrated blind spot.

**Fix:** change the pattern to tolerate zero-or-one quote character, e.g. `<script[^>]*src=["']?https?://`, and re-verify against the three cases above.

### 4. MAJOR — every §3c subtask (ST-3c-1…7) omits the Model/Size/Depends annotations used throughout phases 2 and 3b

Every subtask in Phase 2 (§ lines ~93–138) and Phase 3b (ST-B1…B8, C1/C2 at lines ~546–611) carries explicit `**Model:**`, `**Size:**`, and (usually) `**Depends:**` lines — e.g. ST-B3/ST-B4 (comparable in complexity to the proposed ST-3c-5) are marked "capable mid-tier (grok-4.6-class)" / "Size: M" / "Size: L". None of ST-3c-1 through ST-3c-7 carry any of these three fields. ST-3c-5 in particular — new Hugo predicate partial, head-injection logic, new JS file, CSS, i18n keys, and the exact JS-allowlist audit the whole phase's safety rests on — is the single highest-risk run in the plan and has *no* stated model recommendation, unlike its phase-3b analogues.

This isn't cosmetic: the task's own framing is "before it costs build money" — sizing/model annotations are exactly the lever that prevents both under-provisioning (a weak model attempting ST-3c-5 and shipping the Finding-1/3 style bugs) and over-provisioning (a strong model on a coordinate-lookup subtask that composer-2.5 handled fine in phase 3b).

**Fix:** add Model/Size/Depends to all seven subtasks, following the phase-3b convention (e.g. ST-3c-5 ≈ ST-B3/B4's tier; ST-3c-1/2/3 ≈ ST-B1's tier: composer-class, S/M size, data-entry heavy).

### 5. MAJOR — Q3's own stated OSM referrer-policy risk is never turned into a QA check

Confirmed against the official [OSMF tile usage policy](https://operations.osmfoundation.org/policies/tiles/): web pages using `tile.openstreetmap.org` must "ensure a valid HTTP Referer header is sent," and OSMF actively enforces this (their own writeup: ~10% of current tile.openstreetmap.org traffic is non-compliant on this exact point, and they are moving to reject it). §3c.4/Q3 already *names* this risk correctly ("Follow OSMF's tile policy: browser-driven views only, normal caching, no prefetch/offline/bulk download, **no referrer suppression**"), which is good — but nothing in ST-3c-5's verify block, §3c.8's mechanical battery, or the VISUAL/browser-gate checklist actually checks it. The browser-gate network-panel bullet says only "tile requests use only the approved host" — it never says to open a tile request's headers and confirm `Referer` is present.

Right now this happens to work by omission (no `<meta name="referrer">` and no `Referrer-Policy` response header exist anywhere in this repo today, confirmed by reading `layouts/partials/head.html`), so the browser default (`strict-origin-when-cross-origin`) already complies. But that's incidental, not verified, and a future unrelated "harden headers" change could silently break every map on the site with zero test coverage catching it.

**Fix:** add one line to the VISUAL QA checklist: "DevTools → Network → click a `tile.openstreetmap.org` request → Headers → confirm a `Referer` value is present," and/or set `referrerPolicy: 'strict-origin-when-cross-origin'` explicitly in the `L.tileLayer(...)` call in `museum-map.js` so correctness doesn't depend on the rest of the site never adding a stricter policy.

### 6. MINOR — `EXPECTED_MAP_PAGES=60` / `EXPECTED_SCRIPT_TAGS` are hardcoded in three separate places and rely on a human remembering to edit them

ST-3c-5's verify block, and §3c.8's mechanical battery, both hardcode `EXPECTED_MAP_PAGES=60` with an inline comment ("use 58 only if owner selects 'no map for MORE'"). The comment shows the author is aware of the fragility, but the number itself is duplicated in two places and must be hand-edited consistently if Q8's alternative is chosen — an easy thing to miss, and a script that then either false-passes or false-fails.

**Fix:** derive the expected count at run time, e.g. `EXPECTED_MAP_PAGES=$(( $(jq '[.[] | select(.lat != null and .lon != null)] | length' data/museums_info.json) * 2 ))`, instead of a literal `60`.

### 7. MINOR — the "missing coordinate" fallback path has zero real-data regression coverage after ST-3c-3 lands

By design, ST-3c-1→3 land coordinates for all 30 curated museums before ST-3c-5 (maps) is built, and §3c.7's acceptance checklist requires "all 30... have plausible numeric coordinate pairs." Once that's true, there is no real museum left in production data to exercise the Q7 "map unavailable" empty state — the *only* test of that path, ever, is the disposable, never-committed fixture run once during ST-3c-5's QA. Any later change to `museum-map-ready.html`/`head.html` (e.g. the Finding-1 fix above) has no standing regression test for the "not ready" branch unless someone remembers to recreate that disposable fixture by hand.

**Fix:** keep the disposable-fixture recipe as a copy-pasteable, named script (e.g. documented in `AGENTS.md`'s verification recipes) that future agents are told to re-run whenever they touch the readiness predicate — not just a one-time step buried in ST-3c-5's log entry.

### 8. MINOR — rollback step 5 assumes clean per-commit revertibility that ST-3c-2's own instructions undermine

§3c.10's rollback step 5 says coordinate fields can be reverted via "the three coordinate commits" (one per batch). But ST-3c-2's own scope note says batch B work may include "a documented correction" folded into batch A's data, in the *same* commit as batch B's new records. If that happens, `git revert` of the batch-B commit alone would also undo the batch-A correction, and reverting "the three commits" cleanly is no longer guaranteed.

**Fix:** require any cross-batch correction to land as its own separate, clearly labeled commit (e.g. `fix(data): correct <slug> coordinates`), so the three "batch-add" commits stay independently revertible.

### 9. MINOR — the calendar-heat wrapper's CSS attachment point is unspecified

§3c.4 says the new `calendar-exhibition.html` partial "delegates unchanged content to `exhibition.html`," which renders a bare `<article>...</article>` with no class hook (confirmed: `layouts/partials/exhibition.html` never emits a `class` attribute, and `static/css/classless.css`/`custom.css` give `<article>` no border/box styling beyond heading-numbering resets). Since the wrapper can't add a class to `exhibition.html`'s own `<article>` tag without touching that partial, it must wrap the output in an outer `<div class="closing-heat-N">`. That's a reasonable, low-risk choice — but the plan should say so explicitly, and the implementer will need to add padding/box CSS on the wrapper div (there's currently no article "card" box at all to inherit from), rather than assuming the five hex backgrounds alone will look like a shaded card.

**Fix:** state explicitly in §3c.4 that `calendar-exhibition.html` wraps `exhibition.html`'s output in a `<div class="closing-heat-N">` (not a class on `<article>`), and that the wrapper's CSS needs its own padding since `<article>` has none today.

### 10. MINOR — the stated contrast numbers cover the link-color override only, not the untouched body/heading text color

I computed WCAG contrast for the site's default text color `--cfg: #433` against the darkest heat background (`closing-heat-5`, `#60a5fa`): **4.67:1** — technically a pass (AA normal-text minimum is 4.5:1) but with very little headroom, and never stated in §3c.4 (which only measures the `#172554` link-color override). Worth a one-line note so nobody "cleans up" the palette later without re-checking this margin.

### 11. MINOR — vendored `leaflet.js` retains a dangling sourcemap comment

The distributed `leaflet.js` ends with `//# sourceMappingURL=leaflet.js.map`. Since the plan (correctly) excludes `.map` files from the vendor set, any contributor auditing the browser Network panel with source maps enabled will see a same-origin 404 for `leaflet.js.map` on every museum-map page. Harmless (doesn't affect function, doesn't leak off-site), but worth a one-line callout in §3c.9/QA so a future reviewer doesn't mistake it for a real defect during the "no unexpected requests" visual gate.

### 12. MINOR — ST-3c-6 (calendar heat) is ordered after ST-3c-4/5 (maps) with no stated dependency, though the two features are file-disjoint

ST-3c-6 touches `calendar.html`, `calendar-month.html`, `custom.css` — none of which overlap with ST-3c-4/5's `museum-page.html`, `head.html`, `museum-info.html`, the vendor tree, or `museum-map.js`. The plan's only stated serialization reason ("ST-3c-1 through ST-3c-3 edit the same curated file") doesn't apply to ST-3c-6 vs ST-3c-4/5. This isn't wrong — serial execution is always safe — just an unexplained, possibly unnecessary lengthening of the phase; the heat work could run in parallel with (or even before) the map work.

## Traceability to the 8 owner decisions (§3c.5 Q1–Q8)

| Q | Traced to subtask(s)/QA | Gap noted here |
|---|---|---|
| Q1 boundaries/hex | ST-3c-6, contrast reproduced exactly | — |
| Q2 heat scope | ST-3c-6 scope line, conditional `layouts/index.html` inclusion | — |
| Q3 tile/attribution | ST-3c-5 ("implement Q3–Q8"), Q3 risk row | Finding 5 (referrer policy never tested) |
| Q4 interaction/dimensions | museum-map.js/custom.css, VISUAL gate (scroll/zoom/drag/responsive) | — |
| Q5 museum-pages-only | JS allowlist audit (page/tag counts, path regex) | Finding 3 (audit regex gap) |
| Q6 Leaflet 1.9.4 | ST-3c-4, hash-verified | Finding 2 (LICENSE fetch missing) |
| Q7 missing-coordinate copy | i18n key, disposable-fixture QA | Finding 1 & 7 (null case + no lasting coverage) |
| Q8 MORE multi-venue | ST-3c-1 batch A scope, `EXPECTED_MAP_PAGES` | Finding 6 (hardcoded count) |

All 8 are traced to at least one concrete subtask or QA line — traceability itself is solid. The gaps are in *how completely* each is enforced, not *whether* it's referenced at all.

## Not testable pre-implementation

`static/js/museum-map.js` and the final `museum-map-ready.html`/`museum-info.html` template bodies don't exist yet, so the following §3c.4 promises could only be checked for plausibility, not run: `textContent`-only popup construction, the unhide-before-`L.map`/`try`-`catch`/re-hide-on-failure sequence, and `invalidateSize` avoidance. Nothing found in the surrounding mechanics contradicts these; they should be spot-checked again once ST-3c-5 actually lands code.

## Summary

0 blockers, 5 major findings, 7 minor findings. The plan's factual/provenance claims (Leaflet hash and version status, baseline page/WARN/script counts, contrast math, day-0 fixture availability, i18n parity mechanism) all reproduced exactly on this lane. The weaker spots are all in QA-script robustness and subtask-process hygiene rather than in the high-level design: a naive-but-plausible implementation of the "null-safe coordinate" predicate (Finding 1) or the "no CDN script" audit (Finding 3) would each ship a real, silent violation of the plan's own stated invariants while every literally-scripted check in §3c.8 still reports green. Recommend folding Findings 1–5 into §3c.4/§3c.6/§3c.8 before ST-3c-1 begins; Findings 6–12 can be picked up during implementation without blocking the owner's Q1–Q8 sign-off.


---

## Operator addendum (Diane, 2026-09-13)

All 12 findings folded into `PLAN.md` §3c before owner sign-off — F1 (verified idiom: nested `ne X nil` + float-type + bounds guard, with the explicit-`null` and removed-key fixtures now both in §3c.8), F2 (LICENSE fetch line added; fetch verified), F3 (regex made quote-tolerant; all three `src=` forms verified), F4 (Model/Size/Depends added to ST-3c-1…7), F5 (referrer check added to the VISUAL list + explicit `referrerPolicy` in the tile layer), F6 (derived `EXPECTED_MAP_PAGES` from the data via python3), F7 (named disposable-fixture recipe noted for AGENTS.md), F8 (correction commits must be separate/labeled), F9 (wrapper `<div class="closing-heat-N">` + padding stated), F10 (`#433` margin noted), F11 (sourcemap 404 noted as expected), F12 (parallelism note). Pin proofs run on pod Hugo **v0.166.0 extended**: idiom fixture (4 verdicts correct, build green), regex (2→3 forms caught), LICENSE fetch (HTTP 200). All other lane reproductions accepted as reported. No blockers; awaiting owner Q1–Q8 answers.
