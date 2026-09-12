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
