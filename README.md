# Museumtips

Auto-generated iCalendar (`.ics`) feeds — and a small multilingual website — of current
**temporary exhibitions at Dutch museums**, refreshed weekly (Thursdays). Shows get
countdown labels as they approach their end
(`Last month:` → `Last 3 weeks:` → `Last 2 weeks:` → `Last week:`) plus a `Last day:` marker.

**Do not edit the feed files by hand** — they are regenerated and overwritten automatically.

Published at <https://museumtips.pepperlink.nl/>.

## Subscribe

| Feed | URL |
|---|---|
| All exhibitions | `https://museumtips.pepperlink.nl/museumtips.ics` |
| Closing soon (≤ 30 days) | `https://museumtips.pepperlink.nl/closing-soon.ics` |

- Apple Calendar: tap the subscribe buttons on the site (or File → New Calendar Subscription).
- Google Calendar: Other calendars → "+" → From URL → paste the link.

## Website (Hugo + Huguette)

The browsable site is a **plain Hugo static build** (Dutch default, English under `/en/`).
It uses the owner's [Huguette](https://github.com/cathelijne/hugo-theme-huguette) theme,
added as a **git submodule** at `themes/huguette` (not a remote Hugo Module). `hugo.toml`
imports that local theme and mounts only its layouts — the theme's Netlify CMS `admin/`
files are left out.

Clone with the theme:

```sh
git clone --recurse-submodules https://github.com/pepperlink/museumtips.git
# already cloned?
git submodule update --init --recursive
```

### Preview locally

Requires [Hugo](https://gohugo.io/installation/) (extended is fine; no Node, no Netlify).

```sh
hugo server
```

Open the printed local URL (usually `http://localhost:1313/`). Switch language with the
Nederlands / English links in the header. Dutch pages live at `/`, `/kalender/`,
`/kalender/YYYY-MM/` (month views), `/museums/` (grouped by city),
`/museums/<museum-slug>/`, `/museums/<museum-slug>/tentoonstelling/<slug>/` (with a
per-show `.ics` sibling at `/museums/<museum-slug>/tentoonstelling/<slug>.ics`), `/over/`;
English at `/en/`, `/en/calendar/`, `/en/calendar/YYYY-MM/`, `/en/museums/` (grouped by
city), `/en/museums/<museum-slug>/`, `/en/museums/<museum-slug>/exhibition/<slug>/` (with
`/en/museums/<museum-slug>/exhibition/<slug>.ics`), `/en/about/`.

### Museum maps (phase 3c exception)

Map-ready museum **detail** pages (`/museums/<slug>/`, `/en/museums/<slug>/`) and the
**museums index** (`/museums/`, `/en/museums/`) when at least one museum has coordinates
may load a small Leaflet map. Every other page stays **no-JavaScript** (calendar, home,
about, exhibition pages).

The only JavaScript in the repo is exactly two files, both same-origin and deferred:

| File | Role |
|---|---|
| `static/vendor/leaflet/1.9.4/leaflet.js` | Vendored Leaflet **1.9.4** |
| `static/js/museum-map.js` | Site initializer (detail + index overview) |

Leaflet is copied from the official release archive
(`https://github.com/Leaflet/Leaflet/releases/download/v1.9.4/leaflet.zip`; SHA-256
`aaec1d5c3239a613a53e996087629aca1483cb2f0438b11b8a335c6cede4c16b`) into
`static/vendor/leaflet/1.9.4/` (runtime CSS, JS, marker images, and upstream `LICENSE` only).

Basemap tiles come from **OpenStreetMap Standard**
(`https://tile.openstreetmap.org/{z}/{x}/{y}.png`). The map shows the required
`© OpenStreetMap contributors` attribution (linked to
<https://www.openstreetmap.org/copyright>). This is a best-effort, no-SLA public tile
service; the page referrer is sent to OSM on tile requests. If tiles are unavailable, the
curated street address on the page remains the fallback.

Museum coordinates live in curated `data/museums_info.json` (`lat`/`lon` per museum slug);
the weekly pipeline does not write them.

### Build

```sh
hugo --minify
```

Output is `public/`. That directory is the entire site: HTML plus the `.ics` feeds copied
from `static/` (Hugo does not follow symlinks). Host `public/` as static files — no
external services. The weekly pipeline writes the feed files at the repo root and the
`static/*.ics` copies in the same commit, then rebuilds and publishes the site.

### Publish

The site build + `gh-pages` publish runs as a GitHub Action: [`.github/workflows/publish-site.yml`](.github/workflows/publish-site.yml) (added in [#17](https://github.com/pepperlink/museumtips/pull/17)) — scheduled Thursdays 17:00 UTC, with `workflow_dispatch` for on-demand runs (the `force` input publishes even when unchanged). It builds `main` with pinned Hugo v0.166.0 extended (theme submodule included), copies the root `.ics` feeds plus `.nojekyll` into the output, and force-pushes the result to `gh-pages` — the branch GitHub Pages serves at <https://museumtips.pepperlink.nl/>. The publish is idempotent: an unchanged build pushes nothing. The legacy pod-side rebuild runs in parallel until cutover.

### Data refresh

`data/exhibitions.json` is **generated** by the weekly pipeline — never hand-edit it.

`data/museums_info.json` and `data/exhibitions_info.json` are **curated by hand** for visitor
extras (hours, prices, cards, press, coordinates, …). The weekly pipeline must not touch or
overwrite them. Phase 4 reshaped both files to a schema.org-aligned internal contract while
keeping the same filenames and **frozen slugs** (record keys must match
`exhibitions.json` `museums[].slug` / `exhibitions[].slug`; URLs under `/museums/<slug>/` and
`/museums/<slug>/tentoonstelling/<slug>/` depend on those keys — never rename them). Full
field-by-field mapping: [`docs/structured-data-schema.md`](docs/structured-data-schema.md).

**Curated store shapes (summary):**

| File | Root shape | Main subtrees |
|---|---|---|
| `museums_info.json` | each record `"@type": "Museum"` | `address_v2` (`PostalAddress`) + verbatim `address_display`; `geo` (`GeoCoordinates`); `offers[]` (admission cards); `_visitor.*` (hours/transit/parking/access/pricing, bilingual `{nl,en}`); `_meta` (provenance: `sources[]`, `notes[]`, `verified`); cadence fields at top level (see below) |
| `exhibitions_info.json` | **sidecar** — no root `@type` | `admission_v2` (`Offer`); `subjectOf[]` (`NewsArticle` press links); `_meta` (`verified`, optional `orphaned_since`) |

Extension subtrees **`_visitor`** and **`_meta`** hold facts schema.org has no literal node for;
they sit at the top level next to the schema.org-shaped keys. Cadence scheduling
(`refresh_group`, `last_refreshed_extras`, `next_due`) deliberately lives **outside** `_meta`
(operational scheduling, not provenance). A file-level **`_cadence`** sibling key
(`last_completed_a` / `last_completed_b`) records when each refresh half last finished — read by
`scripts/reconcile-curated.py` for orphan grace.

**Extras refresh cadence (~15 museums per week, alternating A/B):** every museum carries
`refresh_group: "A"|"B"` (seeded 15/15, alphabetical-by-slug; new museums get the smaller
group via `scripts/reconcile-curated.py --domain museums`). Each refresh batch re-verifies one
group against the museum’s own site, stamps `_meta.sources[].checked` on rows actually
rechecked, advances `_meta.verified` and `last_refreshed_extras`, sets `next_due`, and marks
`_cadence.last_completed_a` or `_cadence.last_completed_b`. Run reconciliation before each
cycle (`python3 scripts/reconcile-curated.py --domain museums` then `--domain exhibitions`).
Exhibition orphans (ended shows) get `_meta.orphaned_since` and are deleted only after **both**
A and B batches have completed since that date (Q15 grace rule — four named fixtures in the
script’s test harness).

**Press links (`subjectOf[]`):** each article carries `verifiedAccess` (bool), `accessNote`
(from a controlled vocabulary: `ok`, `archived`, `http_403`, `http_404`, `http_410`, `timeout`,
`paywall`, `redirect_loop`), `accessChecked` (ISO date), and optionally `archiveUrl` (Wayback
snapshot, **never** overwrites the live `url`). Auditing follows a bounded three-step ladder
(alternate URL → rendered access check → Wayback); if all steps fail, the original link stays
and records an honest terminal state (`verifiedAccess: false` + specific `accessNote`).

Exhibition copy for the website comes from `data/exhibitions.json`:

```json
{
  "schema": 1,
  "compiled": "YYYY-MM-DD",
  "museums": [{ "name", "city", "group", "site", "quirks", "slug" }],
  "exhibitions": [{ "title", "museum", "city", "start", "end", "description", "url", "slug" }]
}
```

`start` may be `null` when the tracker only saw a closing date.

The site runs on the **live weekly dataset** (currently ~111 exhibitions across ~30
museums). Every Thursday the pipeline regenerates `data/exhibitions.json`, the root
`.ics` feeds, and the `static/*.ics` copies, commits to `main`, and publishes the rebuilt
site to GitHub Pages. The `.ics` files stay at the repo root and keep the same public
URLs.

### Navigation and banner (phase 4)

The main menu and language switcher are two adjacent floating `<nav>` bars. The theme paints a
full-bleed box-shadow on the second bar that covered the first bar’s link text (links still
worked, but were invisible). **Fix (Q1):** `body > nav + nav { box-shadow: none !important; }`
plus `body > nav:first-of-type { z-index: 43 }` in `static/css/custom.css` — smallest proven
patch; static-in-flow nav is deferred. **Home (Q2):** already the first menu item; no chip or
extra styling — visibility only.

**Photo banner (Q3):** a licensed museum-atrium image (operator default: Picsum id 1033,
vendored as `static/images/banner.jpg`) renders on every page via a repo override of
`layouts/partials/headerimage.html`. License and swap candidates:
[`docs/banner-shortlist.md`](docs/banner-shortlist.md). Hugo minification strips quotes from
`class=` attributes; the partial carries a `data-header-band` marker so verify scripts can
grep for banner presence without weakening the check.

## Theme notes

Huguette is a classless-CSS boilerplate (optional [classless.css](https://classless.de/),
no JavaScript). Site layouts extend its `baseof` / partials and override navigation for
i18n. Classless CSS is copied to `static/css/` as the theme README asks. Netlify CMS is
**not** enabled.
