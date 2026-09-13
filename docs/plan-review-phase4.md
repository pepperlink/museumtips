# Independent review — Phase 4 plan

Verdict: **not build-ready**. The scope is recognizable and the repo/pipeline boundary is stated often, but the main migration contract is still a task for ST-4-1 to invent. Four blockers should be resolved in `PLAN.md` before an implementation run receives build budget.

## Claims reproduced on this lane

### Lane and baseline

- Reviewed commit `eff097b` on `cursor/phase4-plan`; the theme submodule was initially uninitialized and was initialized at pinned submodule commit `370d1cd`.
- This machine reports `hugo v0.165.0-76a5e1880ab46688155b02e99bab9be2a6134492+extended darwin/arm64`, not the authoritative v0.166.0. The operator must repeat the final battery on pinned v0.166.0.
- `hugo --minify` completed with 496 NL pages, 494 EN pages, and no warnings. `static/css/classless.css` is byte-identical to `themes/huguette/static/css/classless.css`.
- This session’s augmented PATH contains Hugo and Apple `jq 1.7.1`; a clean system PATH (`/usr/bin:/bin:/usr/sbin:/sbin`) does **not** contain Hugo. Phase 4 does not invoke `jq`, so the pod’s missing jq is harmless unless later edits introduce it.
- Current generated/curated key sets match exactly: 30 generated museum slugs = 30 curated museum keys; 187 generated exhibition slugs = 187 curated exhibition keys. There are 92 press entries across 54 exhibitions. NL/EN i18n parity is 96/96.
- The built home pages correctly emit `<html lang=nl>` and `<html lang=en>` from `layouts/_default/baseof.html:2` plus `hugo.toml:33-48`. No phase-4 owner decision is needed merely to retain that behavior, but the schema-2 contract still needs a language rule for generated titles/descriptions.

### Data-shape claim: refuted

The recon’s generated-file counts and top-level field lists are correct. Its curated museum-card list is not: `cards[]` has two live spellings for notes, and nullable acceptance.

| Existing source field | Occurrences | Proposed target/source | Result |
|---|---:|---|---|
| `exhibitions.json.schema` | 1 | No target mapping in §4.4.1 | Unmapped |
| `exhibitions.json.compiled` | 1 | No target mapping | Unmapped |
| `museums[].name` | 30 | No schema-2 mapping shown | Unmapped until ST-4-1 invents it |
| `museums[].city` | 30 | No mapping shown | Unmapped |
| `museums[].group` | 30 | No mapping shown | Unmapped |
| `museums[].site` | 30 | No mapping shown | Unmapped |
| `museums[].quirks` | 30 | No mapping shown | Unmapped |
| `museums[].slug` | 30 | Frozen identity is promised, but no target path is shown | Invariant stated; mapping absent |
| `exhibitions[].title` | 187 | No schema-2 mapping shown | Unmapped |
| `exhibitions[].museum` | 187 | No mapping/join rule shown | Unmapped |
| `exhibitions[].city` | 187 | No mapping/venue rule shown | Unmapped |
| `exhibitions[].start` | 187 | No mapping shown; nullable | Unmapped |
| `exhibitions[].end` | 187 | No mapping shown; nullable | Unmapped |
| `exhibitions[].description` | 187 | No mapping or source-language rule shown | Unmapped |
| `exhibitions[].url` | 187 | No mapping shown | Unmapped |
| `exhibitions[].slug` | 187 | Frozen identity is promised, but no target path is shown | Invariant stated; mapping absent |

The entire generated “schema 2” is therefore unspecified in the reviewed plan. Saying ST-4-1 will write it is not a mapping table that can be independently reviewed before implementation.

| Existing `museums_info.json` field | Occurrences | Proposed target | Result |
|---|---:|---|---|
| record key (slug) | 30 | Same key/file identity | Accounted for |
| `name` | 30 | Presumably schema `name` | Implied, not specified |
| `description_nl`, `description_en` | 30 each | `description.{nl,en}` | Implied by prose, exact path absent |
| `address` | 30 | `PostalAddress` components | Lossy unless the original display string/annotations are retained |
| `lat`, `lon` | 30 each | `geo.latitude`, `geo.longitude` | Accounted for |
| `hours_nl/en` | 30 each | Unnamed `_visitor` paths | Destination not specified |
| `transit_nl/en` | 30 each | Unnamed `_visitor` paths | Destination not specified |
| `parking_nl/en` | 30 each | Unnamed `_visitor` paths | Destination not specified |
| `access_nl/en` | 30 each | Unnamed `_visitor` paths | Destination not specified |
| `pricing_nl/en` | 30 each | Unnamed `_visitor` paths | Destination not specified |
| `cards[].id` | 146 | No field in proposed `Offer` | Would be dropped |
| `cards[].label` | 146 | `offers[].name` | Accounted for |
| `cards[].accepted` | 146: 144 booleans, 2 nulls | `availability` InStock/OutOfStock | Null is collapsed; semantics are also wrong for card acceptance |
| `cards[].note_nl/en` | 119 pairs | `offers[].description.{nl,en}` | Accounted for in prose |
| `cards[].notes_nl/en` | 27 pairs | No mapping; recon omitted these fields | Would be dropped |
| `sources[].fact`, `sources[].url` | 398 each | Unnamed `_meta` paths | Destination not specified |
| `notes[]` | 102 strings | Unnamed `_meta` path | Destination not specified |
| `verified` | 30 | Unnamed `_meta` path | Destination not specified |

The plural note keys occur in Foam, Museum Boijmans Van Beuningen, Kunsthal, Nederlands Fotomuseum, and Museum MORE. The null acceptance values occur for the VriendenLoterij at Huis Marseille and Museum Kranenburgh. The current template already fails to display the plural notes (`layouts/partials/museum-info.html:76-78` reads only singular `note_*`), but that pre-existing display bug does not authorize dropping curated facts during migration.

The proposed new museum fields have these origins: `@type`, nested `@type`, `addressCountry`, offer `category`, and availability IRIs are constants; address components are parsed from `address`; geo values come from lat/lon; offer names/descriptions come from card fields. Several addresses are not reversible postal strings: H’ART includes a former-building and taxi-drop-off note, Boijmans and Kunsthal include venue qualifiers, Museum MORE names a second location, and other records contain park/goods-entrance annotations.

| Existing `exhibitions_info.json` field | Occurrences | Proposed target | Result |
|---|---:|---|---|
| record key (slug) | 187 | Same key/file identity | Accounted for |
| `admission.museumkaart` | 187 | `admission_v2.admissionStatus` | Accounted for, but custom/non-schema property |
| `admission.note_nl/en` | 187 each | Offer-shaped bilingual description | Implied, exact path absent |
| `admission.source` | 187 | No exact target | Unmapped |
| `admission.verified` | 187 | No exact target | Unmapped |
| `press[].title` | 92 | `subjectOf[].headline` | Accounted for |
| `press[].outlet` | 92 | `subjectOf[].publisher.name` | Accounted for |
| `press[].url` | 92 | `subjectOf[].url` | Accounted for |
| `press[].lang` | 92 | `subjectOf[].inLanguage` | Accounted for |
| `press[].date` | 92 | `subjectOf[].datePublished` | Accounted for |
| record `verified` | 187 | No exact target | Unmapped |

New `@type`, `publisher` objects, `verified_access`, and `access_note` are constants/derived collection metadata, but §4.4.1 does not define their exact placement. More fundamentally, ST-4-3 does not create an `ExhibitionEvent`: it adds an Offer fragment and NewsArticle fragments to a slug-keyed extras record that has no title, dates, location, URL, or event `@type`.

### Navigation paint-bug claim: mostly reproduced; one proposed variant is incomplete

The actual pinned theme rule is:

```css
/* themes/huguette/static/css/classless.css:215-222 */
nav+* { margin-top: 3rem; }
body>nav, header nav {
	position: var(--navpos);
	top: 0; left: 0; right: 0;
	z-index: 41;
	box-shadow: 0vw -50vw 0 50vw var(--clight), 0 calc(-50vw + 2px) 4px 50vw var(--cdark);
}
```

`--navpos` is `absolute` at `themes/huguette/static/css/classless.css:18`. `layouts/_default/baseof.html:4-5`, `layouts/partials/navigation.html:1-8`, and `layouts/partials/lang-switcher.html:1-11` confirm two adjacent top-level body navs. Both get `position:absolute`, `top:0`, and `z-index:41`; the second also gets `margin-top:3rem` from `nav+*`. It is therefore positioned below the first bar, while its enormous negative-Y shadow paints upward. Equal stacking level plus later source order puts that shadow above the first nav’s text. The shadow-stacking explanation is correct; this is a paint-order defect, not evidence that the underlying links are absent.

The exact one-line fix `body > nav + nav { box-shadow:none !important; }` matches the second bar and removes the covering paint while retaining the two absolute offsets. It works against this stylesheet. Raising the first bar to z-index 43 also addresses the ordering, but is unnecessary if the shadow is removed.

The `.contentnav` precedent is real at `static/css/custom.css:23-33`:

```css
body>nav.contentnav,
header nav.contentnav {
  position: static;
  z-index: auto;
  box-shadow: none;
}
```

It wins the theme selector and removes absolute stacking. Applying it unchanged to both header bars does stop the overlap, but it also leaves `body`’s 3rem top padding and the theme’s `nav+* { margin-top:3rem }` active between nav 1/nav 2 and nav 2/content. That is not a finished top-bar treatment; it introduces three large vertical gaps unless the header-specific spacing is reset. The plan must not describe both alternatives as already proven.

The installed Chrome binary crashed with exit 139 in headless mode on this lane, so no trustworthy screenshot was produced during this review. That limitation strengthens, rather than relaxes, the requirement for operator screenshots in ST-4-13.

### Phase-3d leftovers claim: qualified

- CTA deferral is present in §3b.2 at `PLAN.md:247` and reiterated at `PLAN.md:535`.
- Mailto/Web Share deferral is present in D11 at `PLAN.md:416`; permalink sharing is shipped at `layouts/_default/exhibition-page.html:83-87`, with NL/EN keys at `i18n/{nl,en}.toml:259-263`.
- Telegram has no hit outside Phase 4 and no hit before Phase 4 in `PLAN.md`. It is not a phase-3d leftover evidenced by the repo. The sentence at `PLAN.md:1297` claiming “zero hits anywhere in PLAN.md” is now literally false because Phase 4 itself contains Telegram references; the defensible claim is “no pre-Phase-4 specification or implementation.”

### Verification-command claim: refuted

All actual executables used in §4.6 (`git`, `python3`, `hugo`, `grep`, shell `test`, `tee`, `diff`, `sleep`, and `kill`) are available in this session. The commands are not all copy/paste acceptance tests:

| Workstream spot-check | Lane result |
|---|---|
| A — ST-4-1 file/grep checks | Executable; expected pre-implementation exits were 1/2/2/2 because the file does not exist. A scratch Hugo build exited 0 with zero warnings. |
| B — ST-4-6 Python check | Executable; expected pre-implementation `KeyError: refresh_group`. Its later logic can pass ST-4-7 without a refresh because ST-4-6 sets both groups’ dates to today. |
| C — ST-4-9 Python check | Executable; expected pre-implementation assertion on the first press URL. It checks only legacy `press[]`, not mirrored `subjectOf[]` or fallback notes. |
| D — ST-4-10 | Scratch Hugo server started and served two adjacent navs. The proposed external-script regex catches unquoted and double-quoted URLs but **misses single-quoted** URLs on this BSD grep. |
| E — ST-4-14 | Python parity check passed, 96 keys. |
| F — ST-4-15 | Executable; expected pre-implementation grep exit 1. A single `grep -q file1 file2` would pass if only one language got the key. |

ST-4-2 and ST-4-3 contain placeholder target names (“or the exact new key name”), ST-4-8 supplies no literal command, ST-4-11 has an “exact selector” placeholder, and ST-4-13 is a prose-only gate. ST-4-12’s `grep -rl` lists matches but does not assert “every page” or “consistently absent.” The lane can run `hugo`; the clean PATH cannot, and the operator pin must be invoked explicitly. No §4.6 command needs jq.

## Numbered findings

1. **blocker — The reviewed plan has no authoritative field-by-field schema — proposed fix:** Put the exact schema-2 and both curated-file mappings in `PLAN.md` before ST-4-1, including every source field above, every target key/type/null rule, constants, provenance, versioning, and reverse/equality checks. Change ST-4-1 from “design the contract” to “transcribe and validate the owner-approved contract.”

   The current §4.4.1 is an illustration plus unnamed `_meta`/`_visitor` buckets. It cannot support an independent review, deterministic implementation, or a lossless migration. The generated store’s 16 row fields plus `schema`/`compiled` have no mapping at all.

2. **blocker — The museum transform is demonstrably lossy and cannot meet byte-identical output as written — proposed fix:** Preserve a canonical raw/display address, preserve `cards[].id`, normalize both `note_*` and `notes_*` explicitly, and retain a three-state acceptance enum (`accepted`, `not_accepted`, `unknown`) instead of coercing null. Add a 30-record/146-card semantic equality script and explicit fixtures for the two null cards and five museums using plural notes.

   Parsing the only address string into `PostalAddress` cannot reconstruct venue and access annotations. Mapping card acceptance to `InStock`/`OutOfStock` both loses null and misuses product availability to represent admission-card acceptance.

3. **blocker — The “ExhibitionEvent-shaped curated store” goal and the actual subtask are different designs — proposed fix:** Decide whether `exhibitions_info.json` remains an extras/provenance sidecar or becomes a complete `ExhibitionEvent`. If it remains a sidecar, say so and stop claiming it is event-shaped. If it becomes complete, specify the join from generated title/dates/museum/city/url and the duplicate-data ownership rule. Define source/verified mappings and require `@type: ExhibitionEvent`.

   ST-4-3 creates only `admission_v2` and `subjectOf`; the event identity and dates stay solely in schema-1 generated data.

4. **blocker — A future pipeline schema-2 emission has no safe consumer rollout — proposed fix:** Make schema 2 additive/backward-compatible until a separate site cutover is merged and pin-verified, or define an atomic operator sequence: dual-write → validate repo build against a fixture → deploy compatible templates → switch producer → verify live → remove schema 1 later. Include pipeline and site rollback steps.

   This phase deliberately leaves all templates reading schema 1 while telling the operator to emit schema 2 “on its own schedule.” If schema 2 moves or renames fields, the next weekly publish breaks the site.

5. **major — The nav diagnosis is sound, but the recommended static variant is not a complete CSS fix — proposed fix:** Either choose the proven shadow-removal rule as Q1’s recommendation, or specify the full static-header CSS including resets for body top padding and both `nav+*` margins. Require before/after desktop and 375px screenshots plus click/focus checks.

   The one-line shadow fix works against the real rule. Reusing `.contentnav` unchanged prevents overlap but creates excessive vertical spacing and has not been visually proven here.

6. **major — The curated-data lifecycle contradicts the ownership boundary — proposed fix:** Remove “drops naturally.” Define a recurring repo-side reconciliation run that adds missing curated keys, retains or removes orphaned keys according to an owner-approved retention rule, and collects press weekly. The pipeline must remain read-only with respect to curated files.

   `AGENTS.md` says the pipeline never writes curated files. Therefore an ended slug disappearing from generated `exhibitions.json` cannot automatically remove its `exhibitions_info.json` record or press links. Exact parity happens today but has no mechanism to remain exact.

7. **major — The parallel-field migration never schedules legacy-field removal — proposed fix:** Add explicit subtasks after template cutover for removing legacy museum and exhibition fields, each with complete semantic checks and rollback order; or state that legacy fields intentionally remain for the whole phase. Do not promise both.

   Q4 and §4.11 promise a follow-up commit, but ST-4-1…16 contain none. Acceptance explicitly permits either state, leaving a permanent two-source-of-truth window.

8. **major — ST-4-4’s file scope and mandatory map regression are incomplete — proposed fix:** Name `layouts/partials/exhibition-info.html`, `layouts/partials/museum-map-ready.html`, and all direct readers in scope. Re-run AGENTS.md’s missing-coordinate fixture for removed, null, string, and out-of-bounds geo values after moving lat/lon. Verify exact map-asset page counts and asset absence on non-map pages.

   `museum-map-ready.html:18-28` reads flat lat/lon; `exhibition-info.html:2-43` reads flat admission/press. The phase-3c fixture is mandatory whenever readiness changes, but §4.8 omits it.

9. **major — The migration’s verification checks do not prove losslessness — proposed fix:** Generate canonical normalized “before facts” and “after facts,” compare all 30 museums, 146 cards, 398 sources, 102 notes, 187 admissions, and 92 articles, and fail on unconsumed or extra fields. Keep targeted render snapshots for every anomalous address/card shape, not only one museum and one exhibition.

   Current scripts check a few types/counts, not note text, identifiers, nullable states, admission source dates, provenance, or reverse mapping. `diff -rq public` cannot detect facts dropped from fields that templates never rendered.

10. **major — Several §4.6 verification commands are placeholders, false-positive prone, or non-portable — proposed fix:** Replace every comment placeholder with the final key/selector, provide ST-4-8’s full command, test both i18n files separately, make ST-4-12 assert an exact expected file set, and use the quote-tolerant external-script regex already documented in `AGENTS.md`. Add `set -euo pipefail` and a server cleanup trap around browser runs.

   In particular, `["\x27]?` misses single quotes on this lane; ST-4-7 can pass without doing work; ST-4-9 ignores the mirror; and `grep -q key nl en` proves only one file matched.

11. **major — Nav QA does not capture the paint-vs-hit-test failure class — proposed fix:** Require named before/after screenshots for every representative route at desktop and 375px, retain them as review artifacts, and record real activation of every main-nav and language link by mouse and keyboard. Include computed `position`, `margin-top`, `z-index`, `box-shadow`, and bounding boxes for both top navs and each `.contentnav`.

   A prose pass/fail log and DOM grep can pass while links are painted over or an invisible overlay intercepts clicks. ST-4-13 currently mentions only a mobile width and does not require screenshots.

12. **major — Cadence bookkeeping can lie and the split is unstable as the museum set changes — proposed fix:** Do not initialize both groups’ `last_refreshed_extras` to today unless both were actually reverified. Seed from evidence or null, record `next_due`/an operator schedule, and make verification compare changed records and source dates. Define how new museums are assigned without reshuffling existing groups and how 31+ records are balanced.

   Alphabetical alternating assignment is deterministic for a fixed set, but inserting one slug flips every later assignment. ST-4-6’s “today for all” makes ST-4-7’s only substantive assertion pass before any source is opened.

13. **major — The press fallback is neither the requested “alternate paths” policy nor an S-sized task — proposed fix:** Define alternate URL discovery separately from rendered access and Wayback; define success statuses, redirects, paywalls, timeouts, archive URL handling, `access_note` vocabulary, and whether original versus archive URL is displayed. Batch the 92-link audit, size it L, and verify legacy/mirror equality plus the named hard-403 cases.

   A headless retry of the same URL is not an alternate path. One rendered request plus one archive request “per outlet per show” is also ambiguous when an outlet appears repeatedly. Checking 92 URLs and documenting outcomes cannot honestly be S.

14. **major — The 16 subtasks have labels, but several are not independently verifiable and sizing is optimistic — proposed fix:** Keep Model/Size/Depends on all 16, but resize ST-4-1 to L, ST-4-7/8 to L or 3×5-museum batches, ST-4-9 to L, ST-4-13 to M, and ST-4-16 to M. Give no-op branches explicit closeout evidence and make ST-4-8 independent of elapsed wall-clock assumptions.

   Fifteen museums × five fact families × bilingual copy is materially larger than M; phase 3b itself called 30 museums L with 5–6-museum batches. ST-4-13 covers at least 14 route/language cases before adding desktop, interaction, and screenshots.

15. **major — The ten owner questions omit decisions the build will immediately encounter — proposed fix:** Add decisions for: raw address preservation and multi-venue handling; nullable card acceptance and plural-note normalization; sidecar versus full ExhibitionEvent; schema-2 compatibility/release order; exact full-population migration proof; generated copy `inLanguage`; orphan curated-record retention; new-museum group assignment; and the precise press effort/outcome contract.

   Q8’s custom `{nl,en}` object is intentionally not schema-valid and does not provide the promised clean JSON-LD upgrade path. Prefer language-tagged value objects/arrays or keep bilingual project data under `_visitor` and define the later projection now.

16. **major — The banner alternative cannot meet its own all-pages scope — proposed fix:** Keep Q3’s plain-bar recommendation, or separately spec adapter-created month/museum/exhibition pages, the header partial override, asset licensing, and responsive dimensions. Do not claim edits to `content/{nl,en}/*.md` cover every page.

   Most routes are generated by content adapters, not markdown front matter. The theme partial at `themes/huguette/layouts/partials/headerimage.html:3-16` also hard-codes an inline `50vh` image treatment, which is not a “subtle band”; a CSS-only band is not implemented by setting its URL-valued `header:` parameter.

17. **major — Rollback is ordered correctly for templates versus curated data, but incomplete across factual refreshes and the producer handoff — proposed fix:** Add an exact commit matrix for parallel add/cutover/remove; include pipeline schema-2 rollback; preserve refreshed factual corrections during structural rollback; and state how archive/original press URLs are restored. Prefer forward-fixing fresh hours/prices over reverting them to known-stale values.

   Reverting ST-4-7/8 wholesale can deliberately republish stale visitor facts. The current rollback excludes pipeline state even though ST-4-5 is intended to cause a later producer change.

18. **major — The final regression battery is weaker than the carried-forward phase-3c/AGENTS contract — proposed fix:** Add the missing-coordinate fixture, exact script-page/tag counts, negative asset checks on home/calendar/about/exhibition pages, root/static/public feed byte-equality checks, representative route/language-switch checks, and the visual/interaction artifacts from finding 11.

   The comment says “script-page counts,” but the commands do not count them. Protected-file git diff and “files exist” do not prove the built feed copies remain byte-identical.

19. **minor — Phase-4 traceability is complete at headline level but weak at acceptance level — proposed fix:** Add a six-row traceability matrix from owner scope item → decision → subtask → acceptance check → rollback. Preserve the existing non-goals verbatim.

   The six workstreams are all present: structured data/handoffs, cadence, press fallback, nav/Home/banner, light copy, and 3d disposition. International content, served JSON-LD, theme edits, new JS, map/heat changes, slug/feed changes, and booking integration remain excluded. What is missing is an auditable link from each scope item to a decisive test; copy in particular depends on an “owner-approved copy nits list” that does not yet exist.

20. **minor — Telegram is new input, not a demonstrated 3d leftover — proposed fix:** Reword the recon to “no pre-Phase-4 repo specification or implementation” and record the owner’s source/intent before assigning it to a future phase. Keep Q6’s recommendation to defer it.

21. **minor — Tool invocation should be explicit despite this session’s augmented PATH — proposed fix:** Define `HUGO=${HUGO:-/opt/data/museum_tracker/bin/hugo}` for operator runs, print/version-gate it once, and document a local override. Keep verification in Python/shell so jq remains unnecessary.

   The current lane happens to find `~/.local/bin/hugo`; a clean PATH does not. Every current §4.6 utility otherwise exists and is runnable here.

## Required plan disposition

Resolve findings 1–4 before owner sign-off or any ST-4 implementation run. Findings 5–18 should be folded into the affected decisions/subtasks and verification battery. The plan can retain its six-workstream scope and non-goals; it does not need implementation code in this review cycle.

## Delta review (post-fold + owner decisions)

Reviewed `0042365`, `1b3f34f`, and `a3b497d` against the current Phase 4 plan, current data, CSS, adapters, site templates, and pinned theme templates. Verdict: **still not build-ready**. The fold substantially improved the plan, but the claimed authoritative contract disagrees with live data and the big-bang pre-commit proof is not yet an executable gate. The owner’s domain split is the right split; combining both stores and all consumers into one larger commit would increase blast radius without adding atomicity.

### Part A — F1–F21 dispositions

| Finding | Disposition | Evidence |
|---|---|---|
| F1 | **PARTIAL** | Tables 1–3 now exist (§4.4.1, lines 1318–1407), but Table 2’s `name` equality and `sources[].fact` enum are false for live data; `geo.@type`, `_meta.orphaned_since`, and address optionality are absent; and Table 3 omits `archiveUrl`. |
| F2 | **PARTIAL** | `address_display`, `identifier`, three-state acceptance, and singular/plural-note normalization are specified (lines 1351–1385), but the promised exact fixture/losslessness program is not present. |
| F3 | **PARTIAL** | Q13 selects the sidecar and §4.4.1.6 correctly denies a root event type (lines 1437–1443), while Goal 1 still calls that store “ExhibitionEvent-shaped” (line 1264). |
| F4 | **RESOLVED** | Table 1 is additive and §4.4.1.7 gives dual-write → fixture validation → switch → live verification → rollback (lines 1447–1457). |
| F5 | **RESOLVED** | Q1 chooses the proven shadow removal and leaves the full static-flow resets as a deferred, explicitly specified alternative (§4.4.4 item 1; lines 1506–1507). |
| F6 | **PARTIAL** | §4.4.2 replaces “drops naturally” with reconciliation and Q15’s one-cycle orphan grace (lines 1473–1480), but Goal 5 still says links drop when a show ends, and ST-4-6a defines neither a reusable implementation nor valid stub shapes. |
| F7 | **RESOLVED** | Q4 removes legacy fields inside each domain’s reshape+consumer commit; §4.4.7 explicitly retires the parallel add/cutover/remove path (lines 1522–1526). |
| F8 | **PARTIAL** | ST-4-2 names every direct reader and runs removed/null/string/out-of-bounds fixtures (lines 1660–1747), but map page/tag totals are printed rather than asserted and the final battery drops two fixture variants. |
| F9 | **PARTIAL** | §4.4.1.5 says full population and mandatory pre-commit (lines 1426–1433), but supplies no runnable canonical fact diff and contradicts itself about allowed render differences. |
| F10 | **UNRESOLVED** | Most verify blocks still lack fail-fast handling and use bare `hugo`; the exact ST-4-1 and ST-4-12 blocks both returned exit 0 on this pre-implementation tree after required checks failed. |
| F11 | **PARTIAL** | ST-4-13 now requires screenshots, computed styles, and mouse/keyboard activation (lines 2078–2088), but it runs after the changes and no earlier step captures the required “before” artifacts. |
| F12 | **UNRESOLVED** | Stable groups and honest seeding are specified (§4.4.2), but ST-4-7/8’s `or any(s["url"]...)` is true for unchanged records and there is no `changed > 0` assertion (lines 1895–1907, 1931–1943). |
| F13 | **PARTIAL** | The three-step fallback and vocabulary are concrete (§4.4.3), but `archiveUrl` is not in Table 3 and the named Leeuwarder Courant/~5-show baseline does not exist in current data. |
| F14 | **PARTIAL** | Sizes were increased and no-op evidence was added, but F10/F12 leave several subtasks not independently verifiable; ST-4-15 also remains conditional after Q6 was answered. |
| F15 | **RESOLVED** | Q11–Q16 now record address, card/null, sidecar, rollout, orphan, full-proof, and language decisions (lines 1580–1612). |
| F16 | **PARTIAL** | Adapter scope, repo-local partial override, vendoring, and license recording were added (lines 1508–1510, 2040–2075), but the gate omits month pages/404 and the Picsum patch contradicts the owner-pick dependency. |
| F17 | **PARTIAL** | §4.10 has a domain commit matrix and pipeline rollback (lines 2322–2345), but “single revert” is only true per domain, and new-shape refresh commits cannot simply be cherry-picked onto restored legacy JSON. |
| F18 | **PARTIAL** | Feed equality, route/language checks, JS checks, and coordinate fixtures were added (§4.8), but exact 62/124 map assertions, all four coordinate variants, and a non-map exhibition negative check are still absent. |
| F19 | **PARTIAL** | The six-row matrix exists (§4.7.1), but its copy row knowingly has no decided input and the Home/banner acceptance references are inconsistent with Q2/Q3. |
| F20 | **RESOLVED** | §4.3 now says “no pre-Phase-4 repo specification or implementation” rather than claiming zero present-day PLAN hits (line 1297). |
| F21 | **PARTIAL** | `$HUGO` is defined and version-printed (lines 1620–1627), yet later literal blocks still invoke bare `hugo`, including ST-4-10 and ST-4-12. |

No active Q4 dependency points to the retired ST-4-3/4/4b/4c path. Remaining hits are explicitly labeled historical, rejected, or “no longer exist”; they are noisy but not orphaned execution steps.

### Contract/data spot-check

The full census, not just the requested sample, reproduced 30 museums, 187 exhibitions, 146 cards, 398 museum sources, 102 museum notes, 187 admissions, and 92 press articles. Generated rows have exactly the six/eight fields in Table 1; `start` is null on 67 exhibitions and `end` on 6, matching the stated nullable types. Three museum checks (`rijksmuseum`, `h-art-museum`, `museum-more`) and three exhibition checks (`ed-van-der-elsken-up-close`, `into-nature-haunted-by-waters`, `yayoi-kusama`) reproduced the source shapes and nullable/admission variants.

Two exceptions invalidate the “authoritative” museum contract:

- Seven curated names are not equal to the generated name for the same slug: `de-buitenplaats`, `h-art-museum`, `huis-marseille`, `museum-boijmans-van-beuningen`, `museum-volkenkunde`, `stedelijk-museum`, and `voorlinden`.
- Table 2’s nine-value `sources[].fact` enum excludes 17 live values covering 49/398 source rows, including `description_nl`, `description_en`, `hours_nl`, `pricing - toeslag`, and `access (FAQ details)`.

All named card fixtures reproduce correctly in the source data: the two null values are `huis-marseille/vriendenloterij` and `museum-kranenburgh/vriendenloterij`; the 27 plural-note cards are Foam 6, Museum Boijmans Van Beuningen 5, Kunsthal 5, Nederlands Fotomuseum 5, and Museum MORE 6. On every plural card, `notes_nl/en` exists and `note_nl/en` does not.

### Part B — post-review owner changes

- **Q4:** The two domain commits are sane and should stay split. The direct consumer sets are disjoint, so a single all-store commit would only make review and rollback coarser. Each domain remains big-bang internally. The current plan does not, however, provide the runnable proof needed to make that risk acceptable, and a whole-migration rollback is two structural reverts (plus dependent reverts), not one.
- **Q3:** The repo-local override and adapter file scope are correctly identified; the theme need not be edited. The micro-patch changed the gate from mandatory owner choice to an operator default without updating §4.4.4, Q3, acceptance, docs, risks, or the log. Coverage and licensing defects remain below.
- **Q2:** The answer is not closed consistently. Q2/ST-4-13 say Home looks like the other links, while Goal 7, acceptance, and §4.8 still demand “unmistakable” or “visually distinct.” ST-4-11 also remains numbered and in final dependencies despite being described as removed from the critical path.
- **Q5–Q16 transcription spot-check:** Q5 and Q7–Q12/Q14–Q15 are faithfully reflected. Q13 is reflected in §4.4.1.6 but not Goal 1. Q16 is reflected as prose but not as a real gate. Q6 is stale: §4.4.6 still asks the resolved question and ST-4-15 still carries both conditional branches.

### Part C — verification rerun

- All 17 Phase-4 `sh` fences pass `bash -n`.
- Exact pre-implementation ST-4-1 verify block: required file/grep checks failed, but the block exited **0** because its final `git diff --name-only` succeeded.
- Exact pre-implementation ST-4-12 verify block: the header assertion failed and `docs/banner-shortlist.md` was absent, but the block exited **0** because its final negated external-script grep succeeded.
- `hugo v0.165.0 … +extended` (local fallback) `--minify`: exit **0**, **0 WARN**, 496 NL + 494 EN pages. The authoritative v0.166.0 pin is not installed on this lane and still requires operator rerun.

### Numbered delta findings

1. **blocker — The authoritative contract rejects the live store — proposed fix:** Decide whether generated or curated museum names own display identity and map all seven deliberate name variants without an impossible equality assertion; replace the invented `sources[].fact` enum with the actual open-string contract or enumerate all 26 current values; add the missing `geo.@type` constant and `subjectOf[].archiveUrl` row, including types/null rules.

2. **blocker — The big-bang losslessness gate is mandatory only in prose, not real or internally satisfiable — proposed fix:** Add a literal, fail-fast validator (or a named checked-in script in ST-4-2 scope) that reads immutable before snapshots plus the candidate tree, checks every mapped value/count and exact named fixture, allowlists constants/derived address fields, and rejects every unconsumed source or unexplained target. “No after fact absent from before” cannot coexist literally with required `@type`, `category`, parsed address, and other derived fields. Also resolve the “three gates” numbered 1–4 ambiguity.

3. **major — Render equality permits contradictory and over-broad exceptions — proposed fix:** Permit changes only to the ten NL/EN museum-detail HTML files for the five plural-note museums; require equality for address and null-acceptance pages, then inspect those as snapshots without exempting them. Do not use `diff -x <museum-slug>`, which excludes each museum’s entire subtree, including all exhibition pages and companion ICS files. Capture each domain’s baseline before edits in an explicit setup command.

4. **major — Verification blocks can report success after failed acceptance checks — proposed fix:** Put every multi-command block under `set -euo pipefail`, use `"$HUGO"` literally everywhere, and make scope checks assert exact sets (including staged/index state) rather than ending with informational `git diff --name-only`. The two rerun blocks’ false exit-0 results are direct reproductions, not hypothetical portability concerns.

5. **major — The Picsum micro-patch silently replaced the owner-pick gate and weakened license evidence — proposed fix:** Choose one rule and update every reference. If the operator default is the new directive, replace “owner-picked/owner pick blocks” throughout §4.4.4, Q3, §4.7, §4.9, §4.11, and §4.12. For each fixed Picsum ID, record the metadata endpoint, photographer, original source URL, exact governing license/CC0 evidence, and any depicted-person/art/trademark clearance concern; Picsum’s homepage documents delivery and source metadata, not a blanket license grant.

6. **major — Banner coverage is not “every page,” and responsive behavior is still unspecified — proposed fix:** Add every NL/EN calendar-month output and both 404 outputs to the exact expected set; explicitly assert no banner markup enters root/static/per-show ICS outputs. Define concrete desktop/mobile height or aspect-ratio rules, crop/object-position behavior, and image intrinsic dimensions. The present ST-4-12 verifier checks 442 HTML files but omits all month pages and 404 pages.

7. **major — Q2’s Home de-scope was not subtracted consistently — proposed fix:** Remove ST-4-11, renumber later subtasks and cross-references (or explicitly reserve the number without making it a dependency), and change Goal 7, §4.7, and §4.8 to the owner-approved condition: Home is visible and behaves like the other nav links, with no distinct styling. Delete the contradictory “visually distinct” gate at line 2307.

8. **major — Q6 was answered “defer all,” but the plan still presents and schedules an unresolved branch — proposed fix:** Rewrite §4.4.6 and ST-4-15 as a closed no-op disposition, or remove the subtask and renumber/correct dependencies; delete the mailto fold-in scope, verification, and commit branch from this approved plan.

9. **major — Cadence acceptance still passes a bookkeeping-only refresh — proposed fix:** Remove `or any(s["url"] …)` (all current records have source URLs), require a real `_meta.verified` advance backed by the run plus an explicit per-record checked-source result, and assert the expected 15 records and a nonzero/complete verification count. Define source-check timestamps instead of referring to “source dates” on `_meta.sources[]`, whose rows contain only `fact` and `url`.

10. **major — The press fallback contract and fixtures do not match the store — proposed fix:** Add `archiveUrl` to Table 3 and validate `accessChecked` type/date plus `verifiedAccess`/`accessNote` consistency. Replace “DVHN, Leeuwarder Courant, ~5 shows” with the current census (two DVHN shows, zero Leeuwarder Courant entries) or make discovery dynamic and stop naming nonexistent fixtures.

11. **major — Rollback is atomic per domain, not for the migration as a whole, and refreshed facts are not portable across schema rollback — proposed fix:** State explicitly that full structural rollback requires two domain reverts after reverting dependents. Preserve ST-4-7/8 facts via a schema-neutral before/after fact export or forward-translation procedure; do not suggest cherry-picking commits that edit `_visitor`/`offers` onto a legacy file containing flat visitor fields/`cards`.

12. **major — The final battery still describes exact regressions without asserting them — proposed fix:** Assert `MAP_PAGES == 62` and `SCRIPT_TAGS == 124`, run all removed/null/string/out-of-bounds coordinate fixtures in the final battery, add a representative exhibition page to the map-asset negative list, and reconcile the Home visual wording with Q2. Keep the expanded feed, route, language, and interaction checks.

13. **minor — The risk table is malformed at the big-bang row — proposed fix:** Add the missing leading pipe before “Big-bang migration (owner Q4 override)” at line 2353 so the risk and mitigation remain in the two-column table.

### Follow-up addendum

14. **major — Q15’s completed cadence cycle was mistranscribed as 14 elapsed days — proposed fix:** Track a cadence-cycle ID or completed A/B markers and delete an orphan only after both groups have completed since `orphaned_since`. ST-4-8 explicitly decouples execution from wall-clock timing, so a delayed B run must not allow age-based deletion before a real A+B cycle.

15. **major — Reconciliation is not a defined recurring mechanism and its acceptance conflicts with retained orphans — proposed fix:** Put a repeatable script or exact procedure in scope, define schema-valid museum/exhibition stub records, and test first-seen, retained, reappeared, and expired-orphan fixtures. Replace final `len(e) == 187` with relationships derived from the frozen before snapshot/current generated set; a legitimately retained orphan makes curated count exceed generated count.

16. **major — ST-4-6a re-couples the two domains that Q4 split for independent rollback — proposed fix:** Split museum and exhibition reconciliation changes into separate commits or explicitly withdraw the one-domain rollback claim. A later commit editing both curated files must otherwise be reverted in full before either domain can roll back independently.

17. **major — Address and bookkeeping target contracts remain underspecified or contradictory — proposed fix:** Make H’ART’s missing postcode explicit by defining required/optional/null rules for every `address_v2` component and asserting all 30 expected splits. Either move `refresh_group`, `last_refreshed_extras`, and `next_due` under `_meta`, or amend the rule that says all bookkeeping lives there.

18. **major — Named fixture verification does not prove the exact promised outcomes — proposed fix:** Assert both null cards by `(museum slug, card identifier, exact NL text, exact EN text, "unknown")` and all 27 plural-note values in both languages. Fix the rendered-heading grep (`entrance_cards|kortingskaarten` does not match the current NL “Toegangskaarten”), and do not treat “file changed” as proof that the right note survived. Also correct Q12’s rejected-alternative claim: coercing null to false does **not** match the current template, which renders null as unknown.

19. **major — Weekly data drift can invalidate hard-coded migration and press totals before implementation starts — proposed fix:** Freeze and record the migration baseline commit/file hashes immediately before ST-4-2, derive equality totals from that snapshot, and use dynamic lifecycle assertions in final QA. Keep 30/146/398/102/187/92 only as this review’s dated census, not timeless acceptance constants.

20. **minor — Adapter banner work lacks a direct companion-ICS regression — proposed fix:** In ST-4-12, assert the expected per-exhibition companion count and that every `.ics` starts with `BEGIN:VCALENDAR` and contains no header HTML; the final weekly-feed checks do not cover these adapter-generated files.
