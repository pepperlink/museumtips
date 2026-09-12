---
title: About
subtitle: Feeds, how to subscribe, and how the data refreshes
translationKey: about
menu:
  main:
    weight: 4
---

Museumtips publishes **temporary exhibitions at Dutch museums** as a website and as iCalendar feeds. Permanent collections are out of scope. Shows in their final month get a countdown (`Last month` → `Last 3 weeks` → `Last 2 weeks` → `Last week`) plus a `Last day` marker.

Feeds refresh **every Thursday**. Do not edit the `.ics` files by hand — they are overwritten automatically.

## Subscribe

| Feed | URL |
|---|---|
| All exhibitions | `https://museumtips.pepperlink.nl/museumtips.ics` |
| Closing soon (≤ 30 days) | `https://museumtips.pepperlink.nl/closing-soon.ics` |

**Apple Calendar.** Use the subscribe buttons on the home page (or File → New Calendar Subscription) and enter the same URL.

**Google Calendar.** Other calendars → **+** → *From URL* → paste the link.

## How the data works

The site is a plain Hugo build. Exhibitions are read from `data/exhibitions.json`. A separate pipeline will later overwrite that file with the full dataset (same schema) and trigger a rebuild. This repository currently ships a small fixture so pages can be built without fetching live data.

The `.ics` feeds stay at the same URLs. Existing subscribers do not need to change anything.
