# Structured-data target schema spec

> Transcribed from `PLAN.md` §4.4.1 (Tables 1, 2, 2b, 3 and §4.4.1.4–§4.4.1.7). Authoritative field-by-field contract for phase 4 structured-data migration. Censused against live data on 2026-09-12 (30 museum records / 146 cards / 398 sources / 102 notes / 187 exhibition records / 92 press entries). **This document does not design the schema — it transcribes the plan.**

## Scope split

This repo migrates the **curated** stores (`data/museums_info.json`, `data/exhibitions_info.json`) directly, in-repo, agent-run, human-gated. The **generated** store (`data/exhibitions.json`) keeps schema 1 unchanged in this phase; phase 4 only writes the target "schema 2" contract (Table 1 below) for the operator to implement on the pipeline host later. Site templates therefore change only where they read curated fields — they keep reading generated `exhibitions.json` exactly as today until the operator switches producers.

**Filenames (owner Q7, 2026-09-13):** keep `museums_info.json` and `exhibitions_info.json` — only the internal shape changes; no rename.

## Cross-cutting design choices

Apply to every table below; do not relitigate per field.

- **Bilingual leaf values (owner Q8, 2026-09-13):** stay an internal `{ "nl": …, "en": … }` sub-object wherever literal schema.org/JSON-LD expects one string per node — a deliberate, documented deviation from JSON-LD validity, acceptable because serving our own JSON-LD is deferred (non-goal #2).
- **Extension subtrees:** two named extension subtrees hold everything schema.org has no literal node for, always at the object's top level next to the schema.org-shaped keys:
  - **`_visitor`** — bilingual free-text visitor information (hours/transit/parking/access/pricing)
  - **`_meta`** — provenance and bookkeeping (`sources[]`, `notes[]`, `verified`, per-field `source`/`verified` pairs)
- **Big-bang migration (owner Q4, 2026-09-13):** every migrated record gets exactly one new top-level `"@type"` key (`"Museum"` or, for the sidecar shape §4.4.1.6(a), no root `@type` — see below); no existing key is renamed — legacy flat keys are **removed in the same big-bang commit(s)** that add the new shape. No parallel-fields staging window; no separate legacy-removal step.
- **Card acceptance (owner Q12, 2026-09-13):** three-state string enum, never a boolean and never `InStock`/`OutOfStock` (schema.org `availability` is a stock-keeping vocabulary for physical/e-commerce goods, not admission-card acceptance): `"accepted"` | `"not_accepted"` | `"unknown"`, mapped 1:1 from legacy `true`/`false`/`null`.
- **Note-field normalization (owner Q12, 2026-09-13):** `note_*` and `notes_*` are two live spellings of the same fact (never both present on one card) and both normalize into the same target leaf; see Table 2b.

## Big-bang migration commit sequence (owner Q4)

ST-4-2 follows a **two domain-split commits** sequence — museums, then exhibitions — each reshape + template cutover together:

1. **Commit 1 — museums domain (data + templates together):** reshape `data/museums_info.json` per Tables 2/2b; cut over every museum-only template reader (`museum-info.html`, `museum-page.html`, `museums.html`, `museum-map-ready.html`, `head.html`); remove all legacy flat keys in the same commit. Mandatory pre-commit gates (§4.4.1.5) must pass on the staged tree before this commit lands.

2. **Commit 2 — exhibitions domain (data + templates together):** reshape `data/exhibitions_info.json` per Table 3 (sidecar shape only, §4.4.1.6(a)); cut over exhibition-only template readers (`exhibition-info.html`, `exhibition-page.html`); remove legacy `admission`/`press[]` in the same commit. Mandatory pre-commit gates must pass on the staged tree before this commit lands.

There is **no** parallel-fields staging, **no** separate legacy-removal step (`ST-4-4b`/`ST-4-4c` do not exist). Rollback: revert the big-bang commit(s) atomically.

---

## Table 1 — `data/exhibitions.json` (pipeline-generated, schema 1 → schema 2 target)

All 16 existing fields (2 root + 6 per museum row × 30 rows + 8 per exhibition row × 187 rows) keep their **exact current key, path, and type** — schema 2 is additive-only (§4.4.1.7); the only new content is one `@type` key per row. This table is the complete generated-store mapping.

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

**Reverse/equality checks for Table 1 (run whenever the operator emits a schema-2 fixture):** every schema-1 key/value pair present in a pre-cutover fixture is byte-identical in the schema-2 fixture; the only diff is the 30+187 new `@type` keys; `schema` is the only value that changes.

### `inLanguage` limitation (owner Q16b, 2026-09-13)

Generated `exhibitions.json`'s `title`/`description` are single-value strings authored once and rendered verbatim on **both** the NL and EN site (`exhibition-page.html` renders `$ex.description` unconditionally, no per-language branch) — there is no `inLanguage` this phase can honestly assign per site-language page. Record this as a known, accepted limitation of the generated store (out of scope to fix — would require a pipeline-host authoring change) rather than silently defaulting `inLanguage` to the current page's language, which would be a false claim once JSON-LD is ever served.

---

## Table 2 — `data/museums_info.json` (curated, 30 records) — scalar and address fields

| Existing field | Occurrences | Type / nullability | Target path | Notes |
|---|---:|---|---|---|
| record key (slug) | 30 | string, frozen identity | unchanged (same key) | must equal `exhibitions.json museums[].slug` for the same museum — reverse check |
| `name` | 30 | string, required | `name` (unchanged) | **display-identity ownership (delta F1):** curated `name` is the display identity rendered on museum pages and stays authoritative for display — it is **not** required to equal `exhibitions.json museums[].name` for the same slug. Live data has exactly 7 deliberate spelling/fullness variants between the two stores (censused 2026-09-12, verified against the live file, not asserted from memory): `de-buitenplaats` (curated "Drents Museum De Buitenplaats" vs generated "De Buitenplaats"), `h-art-museum` ("H'ART Museum (voorheen Hermitage Amsterdam)" vs "H'ART Museum (ex-Hermitage Amsterdam)"), `huis-marseille` ("Huis Marseille, Museum voor Fotografie" vs "Huis Marseille"), `museum-boijmans-van-beuningen` ("Museum Boijmans Van Beuningen (Depot Boijmans Van Beuningen)" vs "Museum Boijmans Van Beuningen (Depot)"), `museum-volkenkunde` ("Wereldmuseum Leiden (Museum Volkenkunde)" vs "Museum Volkenkunde"), `stedelijk-museum` ("Stedelijk Museum Amsterdam" vs "Stedelijk Museum"), `voorlinden` ("Museum Voorlinden" vs "Voorlinden"). The reverse check is a **variant map**, not a naive equality assertion: `_meta.generatedNameVariant` (new field, string, required only on these 7 records) stores the exact `exhibitions.json museums[].name` value the curated `name` maps to; the equality check compares `_meta.generatedNameVariant` (when present) or `name` (for the other 23 records, where the two are identical) against the live generated value — never a blanket `curated.name == generated.name` assertion, which is false for 7/30 records today. |
| `description_nl` | 30 | string, required | `description.nl` | bilingual leaf sub-object |
| `description_en` | 30 | string, required | `description.en` | bilingual leaf sub-object |
| `address` | 30 | string, required | **both** `address_display` (verbatim copy, canonical raw/display string — F2) **and** `address_v2.{@type:"PostalAddress", streetAddress, postalCode, addressLocality, addressCountry:"NL", venueNote}` (parsed) — legacy `address` is **removed in the same big-bang commit** that adds these two (owner Q4; the pre-commit losslessness proof, §4.4.1.5, is what makes this safe to do in one step) | see §4.4.1.4 for the parse rule, `venueNote`, and the 6 non-reversible records |
| `lat` | 30 | float, required | `geo.latitude` — legacy `lat` removed in the same big-bang commit (Q4) | `geo.latitude == lat` bit-exact — reverse check, run **before** the commit as part of the losslessness proof |
| `lon` | 30 | float, required | `geo.longitude` — legacy `lon` removed in the same big-bang commit (Q4) | `geo.longitude == lon` bit-exact — reverse check, run **before** the commit as part of the losslessness proof |
| *(new — delta F1)* | 30 | constant | `geo.@type: "GeoCoordinates"` | additive constant; allowlisted derived field, not traced to any legacy source value |
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
| `sources[].fact` | 398 | **open string, not an enum (delta F1 — corrects the earlier invented 9-value enum, which was false for live data)** | `_meta.sources[].fact` | provenance, unchanged shape. Full census against the live file (2026-09-13), 398 rows, 26 distinct values, reproduced exactly (not sampled): `pricing` 47, `access` 44, `hours` 43, `description` 42, `parking` 42, `transit` 42, `address` 30, `coordinates` 30, `cards` 29 (these 9 account for 349/398 rows); plus 17 further non-enum values covering the remaining 49/398 rows: `access_nl` 5, `description_en` 5, `description_nl` 5, `hours_nl` 5, `parking_nl` 5, `pricing_nl` 5, `transit_nl` 5, `description_en_page` 4, `pricing - toeslag` 2, `access (FAQ details)` 1, `access - begeleider en hulpmiddelen` 1, `description - 50 jaar` 1, `description_en_pages` 1, `hours_holidays` 1, `parking - toegankelijk` 1, `pricing - CJP` 1, `vriendenloterij (not valid)` 1. **Contract:** `fact` is a free-text provenance label the migration must preserve verbatim, byte-for-byte, for all 398 rows — it is never validated against a closed enum, and ST-4-2 must not coerce, normalize, or drop any of the 17 non-standard spellings. |
| `sources[].url` | 398 | URL string, required | `_meta.sources[].url` | provenance, unchanged shape |
| *(new — delta F9)* | 0 pre-migration, populated by ST-4-6/6a/7/8 | ISO date string, nullable | `_meta.sources[].checked` | additive; stamped with the run date on any source row actually re-verified during a cadence refresh batch — this is the per-record "checked-source result" the cadence acceptance check asserts against, since `_meta.sources[]` otherwise carries no date field to distinguish "verified this batch" from "verified at initial migration" |
| `notes[]` | 102 strings total | string list | `_meta.notes[]` | unchanged shape, verbatim |
| `verified` | 30 | ISO date string, required | `_meta.verified` | unchanged value; the big-bang commit (ST-4-2, owner Q4) moves the "last verified" read from top-level `verified` to `_meta.verified` in the same step it removes the legacy key |
| *(new)* | 30 | constant | `"@type": "Museum"` | additive |
| *(new, cadence — §4.4.2)* | 30 | see §4.4.2 | `refresh_group`, `last_refreshed_extras`, `next_due` | not part of the schema.org migration; added by ST-4-6, documented in §4.4.2 |

---

## Table 2b — `museums_info.json` `cards[]` → `offers[]` (146 cards across 30 museums)

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

### Card-acceptance and note-normalization rule (owner Q12, 2026-09-13)

Three-state `acceptance` enum (`accepted`/`not_accepted`/`unknown`) replacing boolean/null, and `note_*`/`notes_*` merged into one `description.{nl,en}` leaf per card regardless of which spelling the source record used. Losslessly covers the 2 null-accepted cards (`huis-marseille`, `museum-kranenburgh`) and 27 plural-note cards across Foam, Museum Boijmans Van Beuningen, Kunsthal, Nederlands Fotomuseum, and Museum MORE; also fixes the pre-existing `museum-info.html` plural-notes display bug as a side effect of the template cutover.

**Pre-existing display bug, fixed in the same big-bang commit (F2):** `layouts/partials/museum-info.html` reads only `.note_nl`/`.note_en` per card and has never rendered the 27 `notes_nl`/`notes_en` values for Foam, Museum Boijmans Van Beuningen, Kunsthal, Nederlands Fotomuseum, or Museum MORE — those five museums' plural-note cards have displayed with no note text since C1. ST-4-2 (owner Q4's big-bang migration) fixes this as a named part of the combined data-reshape + template-cutover commit: once templates read `offers[].description.{nl,en}` (which the normalization above already merges from whichever spelling exists), the bug disappears as a side effect.

---

## Table 3 — `data/exhibitions_info.json` (curated, 187 records)

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
| *(new)* | 92, `subjectOf[]` only — §4.4.3/ST-4-9 | bool | `subjectOf[].verifiedAccess` | additive, from the press-fallback pass; **legacy `press[]` no longer exists to mirror onto** — ST-4-2's big-bang commit (owner Q4) already removed it, so ST-4-9 writes these fields to `subjectOf[]` only |
| *(new)* | 92, `subjectOf[]` only | string, controlled vocabulary (§4.4.3) | `subjectOf[].accessNote` | additive |
| *(new)* | 92, `subjectOf[]` only | ISO date string | `subjectOf[].accessChecked` | additive |
| *(new — delta F1/F10, was missing from this table)* | 0 pre-migration, populated only when `accessNote == "archived"` (§4.4.3) | URL string, nullable | `subjectOf[].archiveUrl` | additive; the Wayback snapshot URL, recorded separately from `subjectOf[].url` — never overwrites the live `url` (§4.4.3 rule) |
| *(new)* | 92 | constant | `"@type": "NewsArticle"` (on each `subjectOf[]` item) | additive |
| *(new — delta F1/F14, reconciliation, §4.4.2/ST-4-6a)* | 0 pre-migration; populated only for orphaned records | ISO date string, nullable | `_meta.orphaned_since` | additive; stamped by ST-4-6a's reconciliation run the first cycle it finds the record's slug absent from generated `exhibitions.json`; cleared (`null`) if the slug reappears before deletion; see §4.4.2 for the completed-A+B-cycle deletion rule |

**Reverse/equality checks for Tables 2/2b/3:**

- `geo.latitude == lat` and `geo.longitude == lon`, bit-exact, all 30.
- `address_display` equals the original `address` string verbatim, all 30 (independent of how well the `PostalAddress` split worked — this is the true losslessness gate, not the parse quality).
- `address_v2` satisfies the §4.4.1.4 optionality table for all 30: `streetAddress`/`addressLocality`/`addressCountry` non-null for all 30; `postalCode` non-null for 29, explicitly `null` only for `h-art-museum`; `venueNote` non-null for exactly the 6 flagged slugs, null/absent for the other 24.
- Curated `name` for the 7 slugs listed in Table 2's name row carries a `_meta.generatedNameVariant` equal to the live `exhibitions.json museums[].name` value for that slug; for the other 23, `name` itself equals the generated value — **never** a blanket `name == generated name` assertion across all 30.
- Every one of the 398 `_meta.sources[].fact` values is preserved byte-for-byte from the source `sources[].fact` string — no coercion to a closed set, no dropped or renamed non-standard spelling (26 distinct values, per Table 2's census).
- `{o.identifier for o in offers}` == `{c.id for c in cards}` per museum, all 30 (146 total).
- `offers[i].acceptance` == three-state mapping of `cards[i].accepted`, all 146, **including both `null` cases** (`huis-marseille`, `museum-kranenburgh`).
- `offers[i].description.{nl,en}` == the note text from whichever of `note_*`/`notes_*` was present on `cards[i]`, all 146, **including all 27 plural-note cards** across Foam / Museum Boijmans Van Beuningen / Kunsthal / Nederlands Fotomuseum / Museum MORE.
- `admission_v2.admissionStatus` == `admission.museumkaart`, all 187.
- `len(subjectOf) == len(press)` per exhibition and `sum(len(subjectOf)) == 92`, all 187.
- Post-ST-4-9 only: every `subjectOf[].accessChecked` is a valid ISO date string; `verifiedAccess == True` implies `accessNote` is `"ok"` or `"archived"`; `verifiedAccess == False` implies `accessNote` is one of the failure vocabulary terms (`http_403`/`http_404`/`http_410`/`timeout`/`paywall`/`redirect_loop`); `archiveUrl` is non-null if and only if `accessNote == "archived"`, and is never equal to the live `url`.

---

## §4.4.1.4 Address / multi-venue handling rule (owner Q11, 2026-09-13)

The single `address` string is not always a clean `street, postcode city` triple. Six of the 30 records carry venue/access annotations the naive split would either mangle or silently drop: `h-art-museum` (former-building name + taxi drop-off note — **and, separately, no postal code at all in the source string**, see below), `museum-boijmans-van-beuningen` and `kunsthal` (venue qualifier prefix — "Depot Boijmans Van Beuningen," / "Museumpark,"), `museum-more` (names a second location, Kasteel Ruurlo), `kroller-muller-museum` (park annotation), `museum-volkenkunde` (goods-entrance annotation).

**Rule (owner Q11):** `address_v2.streetAddress`/`postalCode`/`addressLocality`/`addressCountry` capture only the parseable postal triple; **any remaining text that isn't part of the postal triple is preserved verbatim in `address_v2.venueNote`** (single string, not bilingual — the source text has no language split today, matching the original field), never dropped and never force-fit into a `PostalAddress` sub-property that doesn't semantically fit (e.g. "Depot Boijmans Van Beuningen" is not a `streetAddress`). `address_display` (verbatim original string, top-level sibling of `address_v2`) is the backstop losslessness check regardless of how the split or `venueNote` assignment turned out.

**Required/optional/null rule per `address_v2` component:**

| Component | Rule |
|---|---|
| `@type` | Required, constant `"PostalAddress"`, all 30. |
| `streetAddress` | Required, all 30 — every record's source string has a parseable street+number token. |
| `postalCode` | **Optional — `null` when the source string has no 4-digit+2-letter Dutch postcode token.** Exactly one record has no postcode in the source data, verified against the live file: `h-art-museum` ("Amstel 51, Amsterdam …" — no postcode substring anywhere in the original `address`). `postalCode: null` for that one record is not a parse failure to fix; it is the correct, honest transcription of a source string that never carried a postcode. All other 29 records have a postcode and `postalCode` is required (non-null) for them. |
| `addressLocality` | Required, all 30 — every record's source string names a city, even `h-art-museum` ("Amsterdam", present without a postcode). |
| `addressCountry` | Required, constant `"NL"`, all 30. |
| `venueNote` | Optional — `null`/absent for the 24 records whose source string is a clean postal triple with nothing left over; a non-empty string for the 6 flagged records above, holding every character of the source string not captured by `streetAddress`/`postalCode`/`addressLocality`. |

---

## §4.4.1.6 `ExhibitionEvent` — sidecar shape (owner Q13, 2026-09-13)

**Chosen: extras/provenance sidecar — option (a).** `exhibitions_info.json[slug]` stays a slug-keyed extras record: `admission_v2`, `subjectOf[]`, `_meta.*`. It carries **no** title, dates, museum, city, or `url` — those remain solely in generated `exhibitions.json`, joined by slug at render time exactly as today (`exhibition-page.html` already does this join). Nothing is duplicated on disk, so there is no drift risk between the two stores, and no cross-file join logic needs to change. **This is the only shape ST-4-2 implements.**

**Not chosen: complete `ExhibitionEvent` — option (b).** The rejected alternative: add `"@type": "ExhibitionEvent"` at the record root; `name`, `startDate`, `endDate`, `location.{@type:"Place", name, address}`, and `url` computed at render time (joined from generated `exhibitions.json` + the museum's `museums_info.json` row) rather than stored a second time; `offers` becomes `[admission_v2]` (array). More schema.org-literal, useful only once JSON-LD is actually served (non-goal #2 this phase); would have cost a render-time cross-file join with no current visible benefit — **not built**.

Note: generated `exhibitions.json` schema 2 adds `"@type": "ExhibitionEvent"` per row (Table 1) — this marker does not imply the curated sidecar has a root `@type`.

---

## §4.4.1.7 Pipeline schema-2 rollout safety (owner Q14, 2026-09-13)

Schema 2 (Table 1) is additive/backward-compatible by construction — every schema-1 key/path/type is unchanged; the only addition is a per-row `@type`. The atomic operator sequence for the *actual* future producer switch (pipeline-host, out of this repo) is:

1. **Dual-write:** pipeline emits both `schema:1` (legacy, unchanged) and a `schema:2` fixture file side by side for at least one full weekly cycle, without switching the file the site build reads.
2. **Fixture-validate:** run this repo's `hugo --minify` against the `schema:2` fixture in a scratch destination; assert zero WARN and the same page count as the `schema:1` build (990 pages, current baseline).
3. **Deploy compatible templates:** merge and publish (via the normal `gh-pages` flow) any repo template change that can read either schema (there should be none needed, since schema 2 only adds a key nothing reads yet).
4. **Switch producer:** pipeline starts writing `schema:2` as the live `data/exhibitions.json`.
5. **Verify live:** re-run the §4.8 battery against the live site after the next publish; confirm page count, feed byte-equality, and zero regressions.
6. **Remove schema 1 emission later:** only after step 5 is clean for at least one full cycle, the pipeline stops dual-writing.

**Rollback, both sides:**

- *pipeline* — revert the producer to `schema:1`-only emission (step 4 in reverse); the dual-write fixture from step 1 is disposable.
- *site* — if a site-side template change shipped in step 3 turns out to depend on `@type` being present, revert that template commit before the pipeline rolls back its producer: a template expecting `@type` must never be live while the producer is back to schema 1.

**Migration ownership:**

| Store | Who writes the new shape | How |
|---|---|---|
| `data/museums_info.json` | This repo's agents | Big-bang structural migration (ST-4-2, museums-domain commit), same file, same 30 keys, human-gated diff review |
| `data/exhibitions_info.json` | This repo's agents | Big-bang structural migration (ST-4-2, exhibitions-domain commit), same file, same 187 keys |
| `data/exhibitions.json` | Pipeline (operator, out-of-repo) | This repo only ships the Table 1 target-contract doc; no code change here; pipeline emits schema 2 per §4.4.1.7's sequence, unchanged until then |

NL is absent from Google's event-rich-result region list, so even once JSON-LD is served (future phase), rich-result coverage will be patchy — this only affects the deferred surface, not this phase's store migration.

---

## §4.4.1.5 Losslessness proof — mandatory pre-commit gate (owner Q4, Q16a)

Because Q4 chose **big-bang** migration (data reshape + template cutover land in the same commit(s), no parallel-fields window to fall back on), this proof is a **hard pre-commit gate**: it must pass on the working tree **before** ST-4-2's big-bang commit(s) are made. Five gates, all mandatory, full population (all 30/146/398/102/187/92 — owner Q16a: no reduced-sample substitute):

0. Freeze the migration baseline (record commit hash, sha256sum of curated files, pre-migration Hugo build).
1. Full-population before/after fact diff via `scripts/verify-losslessness.py`.
2. Named fixtures (2 null-accepted cards, 27 plural-note cards).
3. Scratch render-equality check — exact 10-file allowed-diff list for plural-notes museums only.
4. Targeted snapshots for 13 anomalous museum-detail pages (6 non-reversible addresses + 5 plural-notes museums + 2 null-accepted cards).

All five gates run against the **staged, uncommitted** tree; a failure at any gate blocks the commit.
