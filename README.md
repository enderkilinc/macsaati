# Maç Saati — macsaati.co.uk

Live football on UK TV plus the Turkish Süper Lig, in UK and Turkish time.

- `data/fixtures.json` — this week's fixtures. Each match is listed only when a broadcaster's or organiser's own page confirms it (`source` key → `sources`).
- `data/notes.json` — site settings and the weekly Süper Lig banner text (EN/TR).
- `src/style.css`, `src/app.js` — shared styles and the small script for filters and the UK/TSİ time toggle.
- `build.py` — generates the static site into `docs/` (home, Süper Lig page, Turkish page, Türkiye page, one page per club, sitemap, robots, CNAME).

```
python3 build.py
```

GitHub Pages serves the `docs/` folder on `main`. Listings are refreshed every Friday.
