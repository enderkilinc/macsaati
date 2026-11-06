#!/usr/bin/env python3
"""Build the Maç Saati static site from data/fixtures.json + data/notes.json into ./docs
Run:  python3 build.py
"""
import json, os, re, shutil, html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")  # GitHub Pages serves main:/docs
LON, IST = ZoneInfo("Europe/London"), ZoneInfo("Europe/Istanbul")

D = json.load(open(os.path.join(ROOT, "data", "fixtures.json"), encoding="utf-8"))
N = json.load(open(os.path.join(ROOT, "data", "notes.json"), encoding="utf-8"))
DOMAIN = N["domain"].rstrip("/")
SITE = N["site_name"]
SOURCES = D["sources"]
FIX = sorted(D["fixtures"], key=lambda f: (f["date"], f["uk"], f["home"]))

esc = lambda s: html.escape(str(s), quote=True)
TRMAP = str.maketrans("çğıöşüÇĞİÖŞÜâÂ", "cgiosuCGIOSUaA")
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.translate(TRMAP).lower()).strip("-")

for f in FIX:
    dt = datetime.fromisoformat(f"{f['date']}T{f['uk']}").replace(tzinfo=LON)
    f["dt"] = dt
    f["iso"] = dt.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
    tr = dt.astimezone(IST)
    f["tr"] = tr.strftime("%H:%M")
    f["tr_next"] = tr.date() != dt.date()
    f["turk"] = f["comp"] == "Süper Lig" or "Türkiye" in (f["home"], f["away"])

SUPERLIG = [f for f in FIX if f["comp"] == "Süper Lig"]
CLUBS = sorted({t for f in SUPERLIG for t in (f["home"], f["away"])}, key=lambda s: s.translate(TRMAP))
BIG = ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor"]
for b in BIG:
    if b not in CLUBS: CLUBS.append(b)

GROUPS = [
  ("Turkish", ["Süper Lig"]),
  ("British", ["Premier League","Championship","League One","League Two","FA Cup","EFL Trophy","Scottish Premiership","Scottish Championship"]),
  ("European", ["La Liga","La Liga 2","Serie A","Bundesliga","Ligue 1"]),
  ("Women's", ["WSL","Women's Champions League"]),
  ("International", ["UEFA Nations League"]),
  ("Rest of the World", ["MLS"]),
]
FTA = re.compile(r"^(BBC|ITV|STV|S4C|Channel 4)")

def ch_class(c):
    if c == "No UK TV" or "TBC" in c: return "none"
    if "(TR)" in c: return "bein" if "beIN" in c else "tr"
    for pat, cl in [(r"^Sky","sky"),(r"^TNT|HBO","tnt"),(r"^BBC","bbc"),(r"^ITV|^STV","itv"),(r"^Premier","prem"),
                    (r"DAZN","dazn"),(r"Amazon|Prime","amazon"),(r"Apple","apple"),(r"Disney","disney"),(r"YouTube","yt")]:
        if re.search(pat, c): return cl
    return ""
def ch_link(c):
    s = SOURCES
    for pat, key in [(r"^Sky","sky"),(r"^TNT|HBO","tnt"),(r"^BBC","bbc"),(r"^ITV|^STV","itv"),(r"^Premier","premier"),
                     (r"DAZN","dazn"),(r"Disney","disney"),(r"Prime Video|Amazon","amazon"),(r"Apple","apple"),(r"beIN|TOD","tff")]:
        if re.search(pat, c) and key in s: return s[key]["url"]
    if c.startswith("ATV"): return "https://www.atv.com.tr/canli-yayin"
    return ""

def fmt_day(d, lang="en"):
    dt = datetime.fromisoformat(d)
    if lang == "tr":
        days = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
        months = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
        return f"{dt.day} {months[dt.month-1]} {dt.year}, {days[dt.weekday()]}"
    return dt.strftime("%A ") + str(dt.day) + dt.strftime(" %B %Y")

def row(f, lang="en"):
    chs = []
    for c in f["channels"]:
        u = ch_link(c)
        cl = ch_class(c)
        chs.append(f'<a class="ch {cl}" href="{esc(u)}" target="_blank" rel="noopener nofollow">{esc(c)}</a>' if u
                   else f'<span class="ch {cl}">{esc(c)}</span>')
    src = SOURCES.get(f["source"])
    tags = []
    if f["comp"] == "Süper Lig": tags.append('<span class="tag slg">Süper Lig</span>')
    if any(FTA.search(c) for c in f["channels"]): tags.append('<span class="tag fta">Free</span>' if lang=="en" else '<span class="tag fta">Ücretsiz</span>')
    srcl = (f'<a class="src" href="{esc(src["url"])}" target="_blank" rel="noopener nofollow">{"Source" if lang=="en" else "Kaynak"}: {esc(src["name"].split(" – ")[0])}</a>') if src else ""
    comp = "" if f["comp"] == "Süper Lig" else esc(f["comp"])
    search = " ".join([f["home"], f["away"], f["comp"], *f["channels"]]).translate(TRMAP).lower()
    return (f'<div class="row{" turk" if f["turk"] else ""}" data-iso="{f["iso"]}" data-comp="{esc(f["comp"])}" '
            f'data-turk="{int(f["turk"])}" data-fta="{int(any(FTA.search(c) for c in f["channels"]))}" data-q="{esc(search)}">'
            f'<div class="time"><span class="uk">{f["uk"]}</span><span class="trt">{f["tr"]}{"<small>+1</small>" if f["tr_next"] else ""}</span></div>'
            f'<div class="fx"><div class="teams">{esc(f["home"])}<span class="v">v</span>{esc(f["away"])}</div>'
            f'<div class="comp">{comp} {" ".join(tags)} <span class="st"></span> {srcl}</div></div>'
            f'<div class="chs">{"".join(chs)}</div></div>')

def listing(fixtures, lang="en", empty=None):
    if not fixtures:
        return f'<div class="list"><div class="empty">{esc(empty or "No televised matches this week.")}</div></div>'
    out, days = [], {}
    for f in fixtures: days.setdefault(f["date"], []).append(f)
    for d, rows in days.items():
        n = len(rows)
        cnt = (f"{n} match{'es' if n>1 else ''}") if lang=="en" else f"{n} maç"
        out.append(f'<section class="day-sec" id="d{d}"><div class="dayhead"><h2>{fmt_day(d, lang)}</h2><span>{cnt}</span></div>'
                   f'<div class="list">{"".join(row(f, lang) for f in rows)}</div></section>')
    return "".join(out)

def jsonld(fixtures, page_url, title):
    events = []
    for f in fixtures:
        events.append({
          "@type": "SportsEvent", "name": f'{f["home"]} v {f["away"]}', "sport": "Football",
          "startDate": f["iso"], "eventStatus": "https://schema.org/EventScheduled",
          "homeTeam": {"@type": "SportsTeam", "name": f["home"]},
          "awayTeam": {"@type": "SportsTeam", "name": f["away"]},
          "superEvent": {"@type": "SportsEvent", "name": f["comp"]},
          "description": f'{f["comp"]}: {f["home"]} v {f["away"]}, kick-off {f["uk"]} UK time. On TV: {", ".join(f["channels"])}.',
          "url": page_url,
        })
    return json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": title, "url": page_url},
        *events]}, ensure_ascii=False)

CSS = open(os.path.join(ROOT, "src", "style.css"), encoding="utf-8").read()
JS = open(os.path.join(ROOT, "src", "app.js"), encoding="utf-8").read()

def nav(lang):
    if lang == "tr":
        return ('<nav class="links"><a href="/tr/">Süper Lig (TR)</a><a href="/">Tüm maçlar</a>'
                '<a href="/super-lig-on-tv-uk/">Super Lig on UK TV</a><a href="/turkey-on-tv/">Türkiye</a></nav>')
    return ('<nav class="links"><a href="/">All matches</a><a href="/super-lig-on-tv-uk/">Süper Lig on TV</a>'
            '<a href="/turkey-on-tv/">Türkiye</a><a href="/tr/">Türkçe</a></nav>')

def page(path, title, desc, h1, intro, body, fixtures, lang="en", hreflang=None, controls=True, banner=True):
    url = DOMAIN + path
    alt = ""
    if hreflang:
        alt = "".join(f'<link rel="alternate" hreflang="{l}" href="{DOMAIN}{p}">' for l, p in hreflang)
    days = sorted({f["date"] for f in fixtures})
    strip = "".join(
        f'<a class="day" href="#d{d}"><b>{datetime.fromisoformat(d).strftime("%a") if lang=="en" else ["Pzt","Sal","Çar","Per","Cum","Cmt","Paz"][datetime.fromisoformat(d).weekday()]}</b>'
        f'<span>{datetime.fromisoformat(d).day}{"<i class=tr-dot></i>" if any(f["turk"] and f["date"]==d for f in fixtures) else ""}</span></a>'
        for d in days)
    t = {"uk": "UK time" if lang=="en" else "İngiltere saati", "tr": "TSİ (TR)",
         "search": "Search team, competition or channel…" if lang=="en" else "Takım, lig veya kanal ara…",
         "turk": "🇹🇷 Turkish football only" if lang=="en" else "🇹🇷 Sadece Türk futbolu",
         "fta": "Free-to-air" if lang=="en" else "Ücretsiz yayın"}
    comps = sorted({f["comp"] for f in fixtures})
    opts = '<option value="all">' + ("All competitions" if lang=="en" else "Tüm organizasyonlar") + "</option>"
    for g, lst in GROUPS:
        o = [c for c in lst if c in comps]
        if o: opts += f'<optgroup label="{g}">' + "".join(f"<option>{esc(c)}</option>" for c in o) + "</optgroup>"
    ctl = (f'<div class="controls"><div class="wrap ctl"><label class="search"><input id="q" type="search" placeholder="{t["search"]}" autocomplete="off" aria-label="Search"></label>'
           f'<select id="comp" aria-label="Competition">{opts}</select>'
           f'<label class="toggle tr"><input type="checkbox" id="turkOnly"> {t["turk"]}</label>'
           f'<label class="toggle"><input type="checkbox" id="ftaOnly"> {t["fta"]}</label></div></div>') if controls else ""
    band = ""
    if banner and N.get("banner_title"):
        band = (f'<section class="sl"><div><h2><span class="tag slg">Süper Lig</span> {esc(N.get("banner_title_tr", N["banner_title"]) if lang=="tr" else N["banner_title"])}</h2>'
                f'<p>{esc(N["banner_text_tr"] if lang=="tr" else N["banner_text"])}</p></div>'
                f'<a class="btn" href="{"/tr/" if lang=="tr" else "/super-lig-on-tv-uk/"}">{"Süper Lig programı" if lang=="tr" else "Süper Lig on TV"}</a></section>')
    srcs = "".join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener nofollow">{esc(s["name"])}</a></li>' for s in SOURCES.values())
    foot_en = (f'<p><b>Times</b> are UK time by default; switch to TSİ for Turkish time. Kick-offs and channels can change — always check with the broadcaster.</p>'
               f'<p><b>How this guide is built:</b> every match is listed only once it appears on a broadcaster\'s, league\'s or organiser\'s own page; each row shows its source and every channel links to that broadcaster. Updated every Friday. Last update: {esc(D["generated"])}.</p>'
               f'<p><b>Süper Lig in the UK:</b> {"no UK TV deal has been announced for 2026/27, so Süper Lig matches show the Turkish broadcasters." if not N.get("uk_superlig_rights") else "UK channels shown where confirmed."}</p>')
    foot_tr = (f'<p><b>Saatler</b> varsayılan olarak İngiltere saatidir; Türkiye saati için TSİ\'yi seçin. Maç saatleri ve kanallar değişebilir — yayıncıdan kontrol edin.</p>'
               f'<p><b>Nasıl hazırlanıyor:</b> her maç yalnızca yayıncının veya organizatörün kendi sayfasında yer aldıktan sonra listelenir. Her cuma güncellenir. Son güncelleme: {esc(D["generated"])}.</p>')
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">{alt}
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="{SITE}">
<meta name="theme-color" content="#0d3b2e">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23c8f169'/%3E%3Crect x='6' y='8' width='20' height='13' rx='2' fill='none' stroke='%230d3b2e' stroke-width='2.4'/%3E%3Cpath d='M11 26h10' stroke='%230d3b2e' stroke-width='2.4' stroke-linecap='round'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Archivo+Narrow:wght@600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{jsonld(fixtures, url, title)}</script>
</head>
<body data-lang="{lang}">
<header class="top"><div class="wrap">
  <div class="brandrow">
    <a class="brand" href="{"/tr/" if lang=="tr" else "/"}"><span class="logo" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24" fill="none"><rect x="2.5" y="5" width="19" height="12.5" rx="2" stroke="#0d3b2e" stroke-width="2"/><path d="M8 21h8" stroke="#0d3b2e" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="11.2" r="3" stroke="#0d3b2e" stroke-width="1.8"/></svg></span>
      <span><span class="name">MAÇ SAATİ</span><small>{"Live football on TV · UK &amp; Türkiye" if lang=="en" else "Canlı maç yayınları · İngiltere &amp; Türkiye"}</small></span></a>
    <div class="tz" role="group" aria-label="Time zone"><button data-tz="uk" class="on">{t["uk"]}</button><button data-tz="tr">{t["tr"]}</button></div>
  </div>
  {nav(lang)}
  <div class="hero"><h1>{esc(h1)}</h1><p>{intro}</p></div>
  <div class="days">{strip}</div>
</div></header>
{ctl}
<main class="wrap">
{band}
{body}
</main>
<footer><div class="wrap">{foot_tr if lang=="tr" else foot_en}<p><b>{"Sources" if lang=="en" else "Kaynaklar"}:</b></p><ul class="srclist">{srcs}</ul>
<p class="small">© {datetime.now().year} {SITE} · macsaati.co.uk · {"Independent guide, not affiliated with any broadcaster or league." if lang=="en" else "Bağımsız rehber; hiçbir yayıncı veya lig ile bağlantılı değildir."}</p></div></footer>
<script>{JS}</script>
</body></html>"""

def write(path, content):
    p = os.path.join(OUT, path.strip("/"), "index.html") if path.endswith("/") else os.path.join(OUT, path.strip("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(content)

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    pages = []
    wk = N["week_label"]
    # Home
    write("/", page("/", f"Live Football on TV Today & This Week (UK) | Premier League, EFL & Süper Lig | {SITE}",
        f"What football is on TV in the UK this week ({wk}): kick-off times and channels for the Premier League, EFL, FA Cup, La Liga, Serie A, Bundesliga, MLS and Women's Champions League on Sky Sports, TNT Sports, BBC, ITV, Premier Sports, DAZN, Prime Video, Apple TV and Disney+ — plus every Turkish Süper Lig match in UK time.",
        "Live football on TV this week",
        f"Every confirmed televised match in the UK for {esc(wk)}, taken from the broadcasters' and leagues' own schedules — plus the full Turkish Süper Lig programme in UK time. Tap a channel to open its schedule.",
        listing(FIX), FIX, hreflang=[("en-GB","/"),("tr","/tr/")]))
    pages.append(("/", "daily", "1.0"))
    # Super Lig (EN)
    sl_intro = ("No UK broadcaster has announced Süper Lig rights for 2026/27, so there is currently no way to watch it on UK TV. "
                "In Türkiye every match is live on beIN SPORTS and the TOD app. Below are all of this week's fixtures with UK and Turkish kick-off times.") \
               if not N.get("uk_superlig_rights") else "This week's Süper Lig fixtures with UK channels and kick-off times."
    write("/super-lig-on-tv-uk/", page("/super-lig-on-tv-uk/",
        f"Süper Lig on TV in the UK – {N['superlig_round']} fixtures & UK kick-off times | {SITE}",
        f"Turkish Süper Lig {N['superlig_round']} fixtures in UK time: Galatasaray, Fenerbahçe, Beşiktaş, Trabzonspor and more. Can you watch the Süper Lig on UK TV? Channels and times for {wk}.",
        "Turkish Süper Lig on TV in the UK", esc(sl_intro),
        listing(SUPERLIG, empty="No Süper Lig matches this week."), SUPERLIG, hreflang=[("en-GB","/super-lig-on-tv-uk/"),("tr","/tr/")], controls=False))
    pages.append(("/super-lig-on-tv-uk/", "daily", "0.9"))
    # Turkish page
    turk = [f for f in FIX if f["turk"]]
    write("/tr/", page("/tr/", f"İngiltere'de Süper Lig maçları saat kaçta, hangi kanalda? | {SITE}",
        f"Süper Lig {N['superlig_round']} maçları İngiltere saati ve Türkiye saati ile: Galatasaray, Fenerbahçe, Beşiktaş, Trabzonspor maçları hangi kanalda? İngiltere'de yaşayanlar için haftalık maç rehberi.",
        "İngiltere'de Süper Lig maç saatleri ve kanallar",
        "İngiltere'de yaşayan futbolseverler için Süper Lig ve A Milli Takım maçları, İngiltere ve Türkiye saatiyle. 2026/27 sezonu için İngiltere'de Süper Lig yayıncısı açıklanmadı; Türkiye'de tüm maçlar beIN SPORTS ve TOD'da.",
        listing(turk, "tr", empty="Bu hafta Türk futbolu maçı yok."), turk, lang="tr", hreflang=[("tr","/tr/"),("en-GB","/super-lig-on-tv-uk/")], controls=False))
    pages.append(("/tr/", "daily", "0.9"))
    # Türkiye national team
    nat = [f for f in FIX if "Türkiye" in (f["home"], f["away"])]
    write("/turkey-on-tv/", page("/turkey-on-tv/", f"Türkiye (Turkey) national team on TV – UK kick-off times | {SITE}",
        "When is Türkiye playing next? Turkey national team fixtures with UK kick-off times and TV channels in the UK and Türkiye.",
        "Türkiye national team on TV", "Upcoming Türkiye matches with UK and Turkish kick-off times and where to watch.",
        listing(nat, empty="No Türkiye matches in this week's listings."), nat, controls=False, banner=False))
    pages.append(("/turkey-on-tv/", "weekly", "0.7"))
    # Club pages
    for c in CLUBS:
        fx = [f for f in FIX if c in (f["home"], f["away"])]
        sl = f"/{slug(c)}-on-tv/"
        nxt = fx[0] if fx else None
        intro = (f"Next televised match: <b>{esc(nxt['home'])} v {esc(nxt['away'])}</b> on {fmt_day(nxt['date'])} at {nxt['uk']} UK time ({nxt['tr']} TSİ)."
                 if nxt else f"{esc(c)} have no match in this week's listings.") + \
                (" There is no UK TV deal for the Süper Lig in 2026/27; matches are live in Türkiye on beIN SPORTS and TOD." if not N.get("uk_superlig_rights") else "")
        write(sl, page(sl, f"{c} on TV – next match, UK kick-off time & channel | {SITE}",
            f"When is {c} playing? {c} fixtures with UK kick-off times and TV channels (UK and Türkiye), updated every week.",
            f"{c} on TV", intro, listing(fx, empty=f"No {c} match this week."), fx, controls=False, banner=False))
        pages.append((sl, "weekly", "0.6"))
    # Club index section on home & super lig page is via links list
    clubs_html = '<section class="clubs"><h2>Süper Lig clubs</h2><ul>' + "".join(
        f'<li><a href="/{slug(c)}-on-tv/">{esc(c)} on TV</a></li>' for c in CLUBS) + "</ul></section>"
    for p in ["index.html", "super-lig-on-tv-uk/index.html"]:
        fp = os.path.join(OUT, p); s = open(fp, encoding="utf-8").read()
        open(fp, "w", encoding="utf-8").write(s.replace("</main>", clubs_html + "</main>", 1))
    # 404
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(
        page("/404.html", f"Page not found | {SITE}", "Page not found", "Page not found",
             'That page doesn\'t exist. <a href="/" style="color:#c8f169">Go to this week\'s listings</a>.', "", [], controls=False, banner=False)
        .replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"'))
    # sitemap / robots / CNAME
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p, freq, pri in pages:
        sm.append(f"<url><loc>{DOMAIN}{p}</loc><lastmod>{D['generated']}</lastmod><changefreq>{freq}</changefreq><priority>{pri}</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm))
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    open(os.path.join(OUT, "CNAME"), "w").write(DOMAIN.split("//")[1] + "\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    print(f"Built {len(pages)} pages, {len(FIX)} fixtures -> {OUT}")

if __name__ == "__main__":
    build()
