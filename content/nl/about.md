---
title: Over
subtitle: Feeds, abonnementen en hoe de data ververst
translationKey: about
url: /over/
menu:
  main:
    weight: 4
---

Museumtips publiceert **tijdelijke tentoonstellingen in Nederlandse musea** als website én als iCalendar-feeds. Vaste collecties staan er niet in. Shows in hun laatste maand krijgen een countdown (`Laatste maand` → `Laatste 3 weken` → `Laatste 2 weken` → `Laatste week`) en een marker op de `Laatste dag`.

De feeds worden **elke donderdag** ververst. Bewerk de `.ics`-bestanden niet met de hand — ze worden automatisch overschreven.

## Abonneren

| Feed | URL |
|---|---|
| Alle tentoonstellingen | `https://museumtips.pepperlink.nl/museumtips.ics` |
| Binnenkort afgelopen (≤ 30 dagen) | `https://museumtips.pepperlink.nl/closing-soon.ics` |

**Apple Agenda.** Gebruik de abonneer-knoppen op de homepage (of Archief → Nieuw agenda-abonnement) en plak dezelfde URL.

**Google Agenda.** Andere agenda's → **+** → *Via URL* → plak de link.

## Hoe de data werkt

De site is een gewone Hugo-build. Tentoonstellingen komen uit `data/exhibitions.json`. Een aparte pipeline schrijft later het volledige bestand weg (zelfde schema) en start een rebuild. Deze repository bevat nu een kleine fixture zodat de pagina's gebouwd kunnen worden zonder live data op te halen.

De `.ics`-feeds blijven op hetzelfde adres staan. Abonnees hoeven niets te wijzigen.
