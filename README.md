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

## IndexNow
`src/static/<key>.txt` is the IndexNow key file (published at the site root). `.github/workflows/indexnow.yml` pings IndexNow with every sitemap URL after each push that changes `docs/`, so Bing re-crawls new fixtures quickly. It can also be run by hand from the Actions tab.

## Daily rebuild
`.github/workflows/daily-rebuild.yml` rebuilds the site just after UK midnight so past days drop off and the page opens on today; it pings IndexNow when something changed. `build.py` skips fixtures before today (UK date); `MACSAATI_TODAY=YYYY-MM-DD` overrides that for testing. `src/app.js` also hides past days in the browser in case a cached page is shown. Club pages stay even when a club has no upcoming match.

## Süper Lig summary bar
Built automatically from `data/fixtures.json`: every Süper Lig row has `"round": N` and, once played, `"score": "H-A"`. The bar shows the current round (all matches, UK and TSİ times, scores as they come in); between rounds it shows the last round's results plus a "Next" line. `banner_note` / `banner_note_tr` in `data/notes.json` add an optional extra line (e.g. international break). A scheduled task adds scores on Sunday, Monday and Tuesday mornings.

## Content pages
`src/pages.py` holds the Süper Lig guide (EN `/how-to-watch-super-lig-in-uk/`, TR `/tr/ingilterede-super-lig-nasil-izlenir/`), About, Contact and Privacy. Re-check the guide's facts (rights, Digiturk Play package and price) each season. Süper Lig rows use the channels ["Digiturk Play (UK)","beIN SPORTS (TR)","TOD (TR)"]; the Digiturk badge links to the guide.

## Match pages and sharing
Every match involving a Turkish club or Türkiye gets its own bilingual page at `/mac/<home>-<away>-<date>/` (title "X – Y hangi kanalda, saat kaçta?"), built automatically and listed in the sitemap; the last Süper Lig round keeps its pages with the result for 10 days. Every row has a WhatsApp "Share/Paylaş" link; Turkish rows also link to their match page.

## Instagram images
`src/social.py` (needs Pillow) writes daily images to `docs/social/` — https://macsaati.co.uk/social/ (noindex, blocked in robots.txt): "Bugün TV'de" story and post, this week's Turkish-interest matches, one post per Turkish-interest match today/tomorrow, a profile picture, and ready-made captions. Own graphics only (no crests or broadcaster logos). Fonts: DejaVu (src/fonts, free licence).
