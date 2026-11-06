# Maç Saati — macsaati.co.uk

Live football on UK TV plus the Turkish Süper Lig, in UK and Turkish time.

- `data/fixtures.json` — this week's fixtures. Each match is listed only when a broadcaster's or organiser's own page confirms it (`source` key → `sources`).
- `data/notes.json` — site settings (incl. `excluded_competitions`: women's competitions are excluded by owner's choice) and the weekly Süper Lig banner text (EN/TR).
- `src/style.css`, `src/app.js` — shared styles and the small script for filters and the UK/TSİ time toggle.
- `build.py` — generates the static site into `docs/`: home (every confirmed match from `generated` onwards on one page, by month, with jump links for this week's days and later months; `/upcoming/` just redirects to the home page), Süper Lig page, Turkish page, Türkiye page, one page per club, sitemap, robots, CNAME.
- Each day is grouped by competition (collapsible; viewers' collapsed groups are remembered in their browser).
- `data/fixtures.json` is a rolling list: past dates are dropped each week and newly announced TV picks are added as far ahead as broadcasters/leagues have announced them.

```
python3 build.py
```

GitHub Pages serves the `docs/` folder on `main`. Listings are refreshed every Friday.

## Live score links
While a match is live (kick-off to +115 min) the status tag becomes a "Live score ↗" link to an official page (TNT Sports for the Süper Lig, bundesliga.com, mlssoccer.com, otherwise Sky Sports scores for that date). After full time it becomes "Result ↗". See `live_url()` in build.py.
