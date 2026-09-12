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
`/kalender/YYYY-MM/` (month views), `/museums/` (grouped by city), `/over/`; English at
`/en/`, `/en/calendar/`, `/en/calendar/YYYY-MM/`, `/en/museums/` (grouped by city),
`/en/about/`.

### Build

```sh
hugo --minify
```

Output is `public/`. That directory is the entire site: HTML plus the `.ics` feeds copied
from `static/` (Hugo does not follow symlinks). Host `public/` as static files — no
external services. The weekly pipeline writes the feed files at the repo root and the
`static/*.ics` copies in the same commit, then rebuilds and publishes the site.

### Data refresh

`data/exhibitions.json` is **generated** by the weekly pipeline — never hand-edit it.

`data/museums_info.json` and `data/exhibitions_info.json` are **curated by hand** (collection
process) for visitor extras (hours, prices, cards, press, …). The weekly pipeline must not
touch or overwrite them.

Exhibition copy for the website comes from `data/exhibitions.json`:

```json
{
  "schema": 1,
  "compiled": "YYYY-MM-DD",
  "museums": [{ "name", "city", "group", "site", "quirks" }],
  "exhibitions": [{ "title", "museum", "city", "start", "end", "description", "url" }]
}
```

`start` may be `null` when the tracker only saw a closing date.

The site runs on the **live weekly dataset** (currently ~111 exhibitions across ~30
museums). Every Thursday the pipeline regenerates `data/exhibitions.json`, the root
`.ics` feeds, and the `static/*.ics` copies, commits to `main`, and publishes the rebuilt
site to GitHub Pages. The `.ics` files stay at the repo root and keep the same public
URLs.

## Theme notes

Huguette is a classless-CSS boilerplate (optional [classless.css](https://classless.de/),
no JavaScript). Site layouts extend its `baseof` / partials and override navigation for
i18n. Classless CSS is copied to `static/css/` as the theme README asks. Netlify CMS is
**not** enabled.
