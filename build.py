#!/usr/bin/env python3
"""Build the Maç Saati static site from data/fixtures.json + data/notes.json into ./docs
Run:  python3 build.py
"""
import json, os, re, shutil, html, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from flags import flag, COMP_FLAG, TEAM_FLAG
import pages as CONTENT
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
EXCLUDED = set(N.get("excluded_competitions", []))
# "Today" in UK time. The site is rebuilt every day by .github/workflows/daily-rebuild.yml,
# so yesterday's matches drop off the top. MACSAATI_TODAY=YYYY-MM-DD overrides it for testing.
TODAY = (datetime.fromisoformat(os.environ["MACSAATI_TODAY"]).date() if os.environ.get("MACSAATI_TODAY")
         else datetime.now(ZoneInfo("Europe/London")).date())
FIX = sorted((f for f in D["fixtures"] if f["comp"] not in EXCLUDED and " Women" not in f["home"]
              and f["date"] >= TODAY.isoformat()),
             key=lambda f: (f["date"], f["uk"], f["home"]))

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
    f["turk"] = False  # set below once the list of Turkish clubs is known

ALL_SL_CLUBS = {t for f in D["fixtures"] if f["comp"] == "Süper Lig" for t in (f["home"], f["away"])}  # incl. past days, so club pages never vanish
TURK_CLUBS = ALL_SL_CLUBS | {"Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Türkiye"}
for f in FIX:
    f["turk"] = f["comp"] == "Süper Lig" or f["home"] in TURK_CLUBS or f["away"] in TURK_CLUBS
GEN = max(datetime.fromisoformat(D["generated"]).date(), TODAY)  # "this week" starts today
WEEK_END = GEN + timedelta(days=6)
WEEK = [f for f in FIX if f["dt"].date() <= WEEK_END]
LATER = [f for f in FIX if f["dt"].date() > WEEK_END]
_last = datetime.fromisoformat(FIX[-1]["date"]) if FIX else datetime.now()
LAST_LABEL = f"{_last.day} {_last.strftime('%b %Y')}"
SUPERLIG = [f for f in FIX if f["comp"] == "Süper Lig"]
CLUBS = sorted(ALL_SL_CLUBS, key=lambda s: s.translate(TRMAP))
BIG = ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor"]
for b in BIG:
    if b not in CLUBS: CLUBS.append(b)

GROUPS = [
  ("Turkish football", ["Süper Lig"]),
  ("British", ["Premier League","Championship","League One","League Two","FA Cup","Carabao Cup","EFL Trophy","WSL","Scottish Premiership","Scottish League Cup","Scottish Championship"]),
  ("UEFA competitions", ["UEFA Champions League","UEFA Europa League","UEFA Conference League","UEFA Nations League","Women's Champions League"]),
  ("FIFA competitions", ["FIFA World Cup","FIFA World Cup qualifiers","FIFA Club World Cup","FIFA U-17 Women's World Cup"]),
  ("European leagues", ["La Liga","La Liga 2","Serie A","Bundesliga","Ligue 1"]),
  ("Rest of the World", ["MLS"]),
]
COMP_ORDER = [c for _, lst in GROUPS for c in lst]
COMP_GROUP = {c: g for g, lst in GROUPS for c in lst}
def comp_rank(c): return COMP_ORDER.index(c) if c in COMP_ORDER else len(COMP_ORDER)
COMP_BADGE = {"UEFA competitions": "UEFA", "FIFA competitions": "FIFA"}
FTA = re.compile(r"^(BBC|ITV|STV|S4C|Channel 4)")

def ch_class(c):
    if c == "No UK TV" or "TBC" in c: return "none"
    if c.startswith("Digiturk"): return "digi"
    if "(TR)" in c: return "bein" if "beIN" in c else "tr"
    for pat, cl in [(r"^Sky","sky"),(r"^TNT|HBO","tnt"),(r"^BBC","bbc"),(r"^ITV|^STV","itv"),(r"^Premier","prem"),
                    (r"DAZN","dazn"),(r"Amazon|Prime","amazon"),(r"Apple","apple"),(r"Disney","disney"),(r"YouTube","yt")]:
        if re.search(pat, c): return cl
    return ""
def ch_link(c):
    s = SOURCES
    if c.startswith("Digiturk"): return CONTENT.GUIDE_EN
    for pat, key in [(r"^Sky","sky"),(r"^TNT|HBO","tnt"),(r"^BBC","bbc"),(r"^ITV|^STV","itv"),(r"^Premier","premier"),
                     (r"DAZN","dazn"),(r"Disney","disney"),(r"^Ligue 1\+","ligue1plus"),(r"Prime Video|Amazon","amazon"),(r"Apple","apple"),(r"beIN|TOD","tff")]:
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

TRD_FULL = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
TRM_ALL = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
def match_path(f):
    """Dedicated page for every match involving a Turkish club or Türkiye."""
    return f"/mac/{slug(f['home'])}-{slug(f['away'])}-{f['date']}/"
def mday_tr(f):
    d = f["dt"].date(); return f"{d.day} {TRM_ALL[d.month-1]} {TRD_FULL[d.weekday()]}"
def mday_en(f):
    return f["dt"].strftime("%a ") + str(f["dt"].day) + f["dt"].strftime(" %b")
def wa_link(f):
    url = DOMAIN + (match_path(f) if f["turk"] else f"/#d{f['date']}")
    txt = (f"⚽ {f['home']} – {f['away']} ({f['comp']})\n"
           f"🗓 {mday_tr(f)} · {f['uk']} İngiltere saati ({f['tr']} TSİ)\n"
           f"📺 {', '.join(f['channels'])}\n{url}")
    from urllib.parse import quote
    return "https://wa.me/?text=" + quote(txt)
WA_ICON = ('<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3a.5.5 0 0 0 0-.5l-.8-1.9c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z"/></svg>')

def row(f, lang="en"):
    chs = []
    for c in f["channels"]:
        u = ch_link(c)
        cl = ch_class(c)
        chs.append(f'<a class="ch {cl}" href="{esc(u)}" target="_blank" rel="noopener nofollow">{esc(c)}</a>' if u
                   else f'<span class="ch {cl}">{esc(c)}</span>')
    src = SOURCES.get(f["source"])
    tags = []
    if any(FTA.search(c) for c in f["channels"]): tags.append('<span class="tag fta">Free</span>' if lang=="en" else '<span class="tag fta">Ücretsiz</span>')
    srcl = (f'<a class="src" href="{esc(src["url"])}" target="_blank" rel="noopener nofollow">{"Source" if lang=="en" else "Kaynak"}: {esc(src["name"].split(" – ")[0])}</a>') if src else ""
    search = " ".join([f["home"], f["away"], f["comp"], *f["channels"]]).translate(TRMAP).lower()
    return (f'<div class="row{" turk" if f["turk"] else ""}" data-iso="{f["iso"]}" data-comp="{esc(f["comp"])}" '
            f'data-turk="{int(f["turk"])}" data-live="{esc(live_url(f))}" data-fta="{int(any(FTA.search(c) for c in f["channels"]))}" data-q="{esc(search)}">'
            f'<div class="time"><span class="uk">{f["uk"]}</span><span class="trt">{f["tr"]}{"<small>+1</small>" if f["tr_next"] else ""}</span></div>'
            f'<div class="fx"><div class="teams">{tname(f["home"], f["comp"])}<span class="v">v</span>{tname(f["away"], f["comp"])}</div>'
            f'<div class="comp">{" ".join(tags)} <span class="st"></span> {srcl}'
            + (f'<a class="mp" href="{match_path(f)}">{"Match page" if lang=="en" else "Maç sayfası"} →</a>' if f["turk"] else "")
            + f'<a class="wa" href="{esc(wa_link(f))}" target="_blank" rel="noopener nofollow" title="WhatsApp">{WA_ICON}{"Share" if lang=="en" else "Paylaş"}</a>'
            + '</div></div>'
            f'<div class="chs">{"".join(chs)}</div></div>')

MONTHS_EN = ["January","February","March","April","May","June","July","August","September","October","November","December"]
MONTHS_TR = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
def month_name(d, lang="en"):
    dt = datetime.fromisoformat(d)
    return f'{(MONTHS_TR if lang=="tr" else MONTHS_EN)[dt.month-1]} {dt.year}'

def live_url(f):
    c = f["comp"]
    if c == "Süper Lig": return "https://www.tntsports.co.uk/football/turkish-super-lig/calendar-results.shtml"
    if c == "Bundesliga": return "https://www.bundesliga.com/en/bundesliga/matchday"
    if c == "MLS": return "https://www.mlssoccer.com/competitions/mls-regular-season/2026/schedule/week-with-matches"
    return f"https://www.skysports.com/football-scores-fixtures/{f['date']}"

INTL = {"UEFA Nations League", "FIFA World Cup", "FIFA World Cup qualifiers", "European Qualifiers"}
def tname(t, comp=""):
    code = TEAM_FLAG.get(t)   # national teams only; clubs show just the name
    return (flag(code, t) + " " + esc(t)) if code else esc(t)

def listing(fixtures, lang="en", empty=None, months=False):
    if not fixtures:
        return f'<div class="list"><div class="empty">{esc(empty or "No televised matches this week.")}</div></div>'
    out, days, cur_m = [], {}, None
    for f in fixtures: days.setdefault(f["date"], []).append(f)
    for d, rows in days.items():
        if months and d[:7] != cur_m:
            cur_m = d[:7]
            out.append(f'<h2 class="month" id="m{cur_m}">{month_name(d, lang)}</h2>')
        n = len(rows)
        cnt = (f"{n} match{'es' if n>1 else ''}") if lang=="en" else f"{n} maç"
        comps = {}
        for f in rows: comps.setdefault(f["comp"], []).append(f)
        blocks = []
        for c in sorted(comps, key=lambda c: (comp_rank(c), c)):
            fx = sorted(comps[c], key=lambda f: (f["uk"], f["home"]))
            badge = COMP_BADGE.get(COMP_GROUP.get(c, ""), "")
            cls = " slg" if c == "Süper Lig" else (" intl" if badge else "")
            m = len(fx)
            blocks.append(f'<details class="grp{cls}" data-comp="{esc(c)}" open><summary class="grphead"><span class="arrow" aria-hidden="true"></span>{flag(COMP_FLAG[c], c) if c in COMP_FLAG else ""}<h3>{esc(c)}</h3>'
                          f'{f"<span class=gb>{badge}</span>" if badge else ""}<span class="gn">{m}</span></summary>'
                          f'<div class="list">{"".join(row(f, lang) for f in fx)}</div></details>')
        out.append(f'<section class="day-sec" id="d{d}"><div class="dayhead"><h2>{fmt_day(d, lang)}</h2><span>{cnt}</span></div>'
                   f'{"".join(blocks)}</section>')
    return "".join(out)

ORGANISER = [  # competition -> organising body (schema.org "organizer")
    (("Süper Lig",), "Türkiye Futbol Federasyonu", "https://www.tff.org"),
    (("UEFA",), "UEFA", "https://www.uefa.com"),
    (("FIFA", "World Cup"), "FIFA", "https://www.fifa.com"),
    (("Premier League",), "Premier League", "https://www.premierleague.com"),
    (("Championship", "League One", "League Two", "EFL", "Carabao Cup"), "English Football League", "https://www.efl.com"),
    (("FA Cup",), "The Football Association", "https://www.thefa.com"),
    (("Scottish",), "SPFL", "https://spfl.co.uk"),
    (("La Liga",), "LALIGA", "https://www.laliga.com"),
    (("Serie A",), "Lega Serie A", "https://www.legaseriea.it"),
    (("Bundesliga",), "DFL Deutsche Fußball Liga", "https://www.bundesliga.com"),
    (("Ligue 1",), "Ligue de Football Professionnel", "https://www.ligue1.com"),
    (("MLS",), "Major League Soccer", "https://www.mlssoccer.com"),
]
def organiser(comp):
    for keys, name, url in ORGANISER:
        if any(k in comp for k in keys): return {"@type": "SportsOrganization", "name": name, "url": url}
    return {"@type": "SportsOrganization", "name": comp}

OG_IMAGE = DOMAIN + "/og-image.png"

def jsonld(fixtures, page_url, title):
    events = []
    for f in fixtures:
        start = datetime.fromisoformat(f["iso"].replace("Z", "+00:00"))
        end = (start + timedelta(minutes=115)).strftime("%Y-%m-%dT%H:%M:%SZ")
        watch = next((u for u in (ch_link(c) for c in f["channels"]) if u), page_url)
        home = {"@type": "SportsTeam", "name": f["home"]}; away = {"@type": "SportsTeam", "name": f["away"]}
        events.append({
          "@type": "SportsEvent", "name": f'{f["home"]} v {f["away"]} – {f["comp"]}', "sport": "Football",
          "startDate": f["iso"], "endDate": end,
          "eventStatus": "https://schema.org/EventScheduled",
          "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
          "location": {"@type": "VirtualLocation", "url": watch},
          "homeTeam": home, "awayTeam": away, "competitor": [home, away], "performer": [home, away],
          "organizer": organiser(f["comp"]),
          "image": [OG_IMAGE],
          "description": f'{f["comp"]}: {f["home"]} v {f["away"]}, kick-off {f["uk"]} UK time. On TV: {", ".join(f["channels"])}.',
          "url": page_url,
        })
    return json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": title, "url": page_url, "primaryImageOfPage": OG_IMAGE},
        *events]}, ensure_ascii=False)

CSS = open(os.path.join(ROOT, "src", "style.css"), encoding="utf-8").read()
JS = open(os.path.join(ROOT, "src", "app.js"), encoding="utf-8").read()

def nav(lang):
    if lang == "tr":
        return ('<nav class="links"><a href="/tr/">Süper Lig (TR)</a><a href="/">Tüm maçlar</a>'
                '<a href="/super-lig-on-tv-uk/">Super Lig on UK TV</a><a href="/turkey-on-tv/">Türkiye</a></nav>')
    return ('<nav class="links"><a href="/">All matches (to {last})</a><a href="/super-lig-on-tv-uk/">Süper Lig on TV</a>'
            '<a href="/turkey-on-tv/">Türkiye</a><a href="/tr/">Türkçe</a></nav>').replace("{last}", LAST_LABEL)

# ---- Süper Lig summary bar: built from fixtures.json (Süper Lig rows carry "round" and, once played, "score") ----
TRM_FULL = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
TRD_SHORT = ["Pzt","Sal","Çar","Per","Cum","Cmt","Paz"]
def _sl_rounds():
    rows = []
    for f in D["fixtures"]:
        if f["comp"] != "Süper Lig" or "round" not in f: continue
        g = dict(f); dt = datetime.fromisoformat(f"{f['date']}T{f['uk']}").replace(tzinfo=LON)
        g["dt"] = dt; g["tr"] = dt.astimezone(IST).strftime("%H:%M"); rows.append(g)
    rounds = {}
    for g in sorted(rows, key=lambda g: (g["dt"], g["home"])): rounds.setdefault(g["round"], []).append(g)
    return [rounds[k] for k in sorted(rounds)]
def _range(ms, lang):
    a, z = ms[0]["dt"].date(), ms[-1]["dt"].date()
    if lang == "tr":
        return f"{a.day}–{z.day} {TRM_FULL[z.month-1]}" if a.month == z.month else f"{a.day} {TRM_FULL[a.month-1]} – {z.day} {TRM_FULL[z.month-1]}"
    return f"{a.day}–{z.day} {z.strftime('%B')}" if a.month == z.month else f"{a.day} {a.strftime('%b')} – {z.day} {z.strftime('%b')}"
def _team(t): return f'<a href="/{slug(t)}-on-tv/">{esc(t)}</a>' if t in ALL_SL_CLUBS else esc(t)
def superlig_banner(lang):
    rounds = _sl_rounds()
    if not rounds: return ""
    cur = next((r for r in rounds if any(g["dt"].date() >= TODAY for g in r)), None)
    prev = None
    if cur is None: prev = rounds[-1]
    else:
        i = rounds.index(cur)
        if cur[0]["dt"].date() > TODAY + timedelta(days=3) and i > 0 and all(g.get("score") for g in rounds[i-1]): prev = rounds[i-1]
    show = prev or cur
    n = show[0]["round"]
    done = all(g.get("score") for g in show)
    if lang == "tr":
        title = f"Süper Lig {n}. hafta " + ("sonuçları" if done else "") + f" · {_range(show, 'tr')}"
    else:
        title = f"Süper Lig Week {n} " + ("results" if done else "") + f" · {_range(show, 'en')}"
    title = title.replace("  ", " ")
    cells = []
    for g in show:
        d = g["dt"].date()
        when = (f'{TRD_SHORT[d.weekday()]} {d.day}' if lang == "tr" else g["dt"].strftime("%a ") + str(d.day))
        if g.get("score"):
            h, a = g["score"].split("-")
            mid = f'<b class="sc">{h}–{a}</b>'
            meta = "MS" if lang == "tr" else "FT"
        else:
            mid = '<span class="v">v</span>'
            meta = f'{when} · <span class="uk">{g["uk"]} UK</span> · <span>{g["tr"]} TSİ</span>'
        cells.append(f'<li><span class="m">{_team(g["home"])} {mid} {_team(g["away"])}</span><span class="mt">{meta}</span></li>')
    nxt = ""
    if prev and cur:
        nxt = (f'<p class="nx"><b>{cur[0]["round"]}. hafta:</b> {_range(cur, "tr")} — maç saatleri aşağıda.</p>' if lang == "tr"
               else f'<p class="nx"><b>Next – Week {cur[0]["round"]}:</b> {_range(cur, "en")}; kick-off times are in the listings below.</p>')
    note = N.get("banner_note_tr" if lang == "tr" else "banner_note", "")
    sub = ("İngiltere'de 2026/27 için TV yayıncısı yok; İngiltere'de yasal olarak Digiturk Play Yurt Dışı Spor paketiyle izlenebilir (rehbere bakın). Türkiye'de: beIN SPORTS ve TOD." if lang == "tr"
           else "No UK TV channel for 2026/27 — watch legally in the UK on Digiturk Play's international Sports package (see our guide). In Türkiye: beIN SPORTS and TOD.") if not N.get("uk_superlig_rights") else ""
    return (f'<section class="sl"><div class="slh"><h2><span class="tag slg">Süper Lig</span> {esc(title)}</h2>'
            f'<a class="btn" href="{"/tr/" if lang=="tr" else "/super-lig-on-tv-uk/"}">{"Süper Lig programı" if lang=="tr" else "Süper Lig on TV"}</a></div>'
            f'<ul class="slg-list">{"".join(cells)}</ul>{nxt}'
            f'<p class="sub">{esc(sub)}{(" " + esc(note)) if note else ""}</p></section>')

def page(path, title, desc, h1, intro, body, fixtures, lang="en", hreflang=None, controls=True, banner=True):
    url = DOMAIN + path
    alt = ""
    if hreflang:
        alt = "".join(f'<link rel="alternate" hreflang="{l}" href="{DOMAIN}{p}">' for l, p in hreflang)
    days = sorted({f["date"] for f in fixtures})
    if len(days) > 10:
        wk_days = [d for d in days if datetime.fromisoformat(d).date() <= WEEK_END]
        later_ms = sorted({d[:7] for d in days if datetime.fromisoformat(d).date() > WEEK_END})
        wd = ["Pzt","Sal","Çar","Per","Cum","Cmt","Paz"]
        strip = "".join(
            f'<a class="day" href="#d{d}"><b>{datetime.fromisoformat(d).strftime("%a") if lang=="en" else wd[datetime.fromisoformat(d).weekday()]}</b>'
            f'<span>{datetime.fromisoformat(d).day}{"<i class=tr-dot></i>" if any(f["turk"] and f["date"]==d for f in fixtures) else ""}</span></a>' for d in wk_days)
        strip += "".join(f'<a class="day mon" href="#m{m}"><b>{month_name(m+"-01", lang).split()[0][:3]}</b><span>{m[:4]}</span></a>' for m in later_ms)
    else:
      spread = len(days) > 1 and (datetime.fromisoformat(days[-1]) - datetime.fromisoformat(days[0])).days > 6
      trm = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"]
      lab = lambda d: (datetime.fromisoformat(d).strftime("%b") if lang=="en" else trm[datetime.fromisoformat(d).month-1]) if spread else \
                      (datetime.fromisoformat(d).strftime("%a") if lang=="en" else ["Pzt","Sal","Çar","Per","Cum","Cmt","Paz"][datetime.fromisoformat(d).weekday()])
      strip = "".join(
        f'<a class="day" href="#d{d}"><b>{lab(d)}</b>'
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
           f'<label class="toggle"><input type="checkbox" id="ftaOnly"> {t["fta"]}</label>'
           f'<span class="cx"><button type="button" id="collapseAll">{"Collapse all" if lang=="en" else "Tümünü kapat"}</button><button type="button" id="expandAll">{"Expand all" if lang=="en" else "Tümünü aç"}</button></span></div></div>') if controls else '<div class="controls slim"><div class="wrap ctl"><span class="cx"><button type="button" id="collapseAll">' + ("Collapse all" if lang=="en" else "Tümünü kapat") + '</button><button type="button" id="expandAll">' + ("Expand all" if lang=="en" else "Tümünü aç") + '</button></span></div></div>'
    band = superlig_banner(lang) if banner else ""
    used = {f["source"] for f in FIX} | {k for k in ("amazon", "apple", "bbc", "itv", "tnt", "sky") if k in SOURCES}
    srcs = "".join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener nofollow">{esc(s["name"])}</a></li>' for k, s in SOURCES.items() if k in used)
    foot_en = (f'<p><b>Times</b> are UK time by default; switch to TSİ for Turkish time. Kick-offs and channels can change — always check with the broadcaster.</p>'
               f'<p><b>How this guide is built:</b> every match is listed only once it appears on a broadcaster\'s, league\'s or organiser\'s own page; each row shows its source and every channel links to that broadcaster. Updated every morning. Last update: {esc(D["generated"])}.</p>'
               f'<p><b>Süper Lig in the UK:</b> {'no UK TV channel has the rights for 2026/27. The legal way to watch in the UK is Digiturk Play\'s international Sports package — see <a href="' + CONTENT.GUIDE_EN + '">how to watch the Süper Lig in the UK</a>.' if not N.get("uk_superlig_rights") else "UK channels shown where confirmed."}</p>')
    foot_tr = (f'<p><b>Saatler</b> varsayılan olarak İngiltere saatidir; Türkiye saati için TSİ\'yi seçin. Maç saatleri ve kanallar değişebilir — yayıncıdan kontrol edin.</p>'
               f'<p><b>Nasıl hazırlanıyor:</b> her maç yalnızca yayıncının veya organizatörün kendi sayfasında yer aldıktan sonra listelenir. Her sabah güncellenir. Son güncelleme: {esc(D["generated"])}.</p>')
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">{alt}
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="{SITE}"><meta property="og:image" content="{OG_IMAGE}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#B5000F">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23E30A17'/%3E%3Crect x='6' y='8' width='20' height='13' rx='2' fill='none' stroke='%23ffffff' stroke-width='2.4'/%3E%3Cpath d='M11 26h10' stroke='%23ffffff' stroke-width='2.4' stroke-linecap='round'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Archivo+Narrow:wght@600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{jsonld(fixtures, url, title)}</script>
</head>
<body data-lang="{lang}">
<header class="top"><div class="wrap">
  <div class="brandrow">
    <a class="brand" href="{"/tr/" if lang=="tr" else "/"}"><span class="logo" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24" fill="none"><rect x="2.5" y="5" width="19" height="12.5" rx="2" stroke="#E30A17" stroke-width="2"/><path d="M8 21h8" stroke="#E30A17" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="11.2" r="3" stroke="#E30A17" stroke-width="1.8"/></svg></span>
      <span><span class="name">MAÇ SAATİ</span><small>{"Live football on TV · UK streams" if lang=="en" else "Canlı maç yayınları · İngiltere"}</small></span></a>
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
<p class="footlinks"><a href="{CONTENT.GUIDE_TR if lang=="tr" else CONTENT.GUIDE_EN}">{"İngiltere'de Süper Lig nasıl izlenir?" if lang=="tr" else "How to watch the Süper Lig in the UK"}</a> · <a href="/about/">{"Hakkımızda" if lang=="tr" else "About"}</a> · <a href="/contact/">{"İletişim" if lang=="tr" else "Contact"}</a> · <a href="/privacy/">{"Gizlilik" if lang=="tr" else "Privacy"}</a></p>
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
    shutil.copytree(os.path.join(ROOT, "src", "flagsvg"), os.path.join(OUT, "flags"))
    for fn in os.listdir(os.path.join(ROOT, "src", "static")):   # IndexNow key file etc.
        shutil.copy(os.path.join(ROOT, "src", "static", fn), OUT)
    pages = []
    wk = N["week_label"]
    # Home: every confirmed match, one page
    write("/", page("/", f"Live Football on TV (UK) – today, this week & all fixtures to {LAST_LABEL} | Premier League, Champions League & Süper Lig | {SITE}",
        f"What football is on TV in the UK: kick-off times and channels for every confirmed match up to {LAST_LABEL} — Premier League, EFL, FA Cup, Champions League, Europa League, Conference League, Nations League, La Liga, Serie A, Bundesliga and MLS on Sky Sports, TNT Sports, BBC, ITV, Premier Sports, DAZN, Prime Video and Apple TV — plus every Turkish Süper Lig match in UK time.",
        "Live football on TV",
        f"Every confirmed televised match in the UK up to {LAST_LABEL}, taken from the broadcasters' and leagues' own schedules — plus the full Turkish Süper Lig programme in UK time. Jump to a day or month below; tap a channel to open its schedule.",
        listing(FIX, months=True), FIX, hreflang=[("en-GB","/"),("tr","/tr/")]))
    pages.append(("/", "daily", "1.0"))
    # Old /upcoming/ address now points to the home page
    os.makedirs(os.path.join(OUT, "upcoming"), exist_ok=True)
    open(os.path.join(OUT, "upcoming", "index.html"), "w", encoding="utf-8").write(
        f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{SITE}</title><link rel="canonical" href="{DOMAIN}/">'
        f'<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=/"></head><body><a href="/">{SITE}</a></body></html>')
    # Super Lig (EN)
    sl_intro = ("No UK TV channel has Süper Lig rights for 2026/27, but every match can be watched legally in the UK on Digiturk Play's international Sports package "
                f'(<a href="{CONTENT.GUIDE_EN}" style="color:#fff;text-decoration:underline">how to watch</a>). In Türkiye matches are on beIN SPORTS and TOD. All fixtures with UK and Turkish kick-off times are below.') \
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
        "İngiltere'de yaşayan futbolseverler için Süper Lig ve A Milli Takım maçları, İngiltere ve Türkiye saatiyle. 2026/27'de Süper Lig İngiliz kanallarında yok; İngiltere'de yasal olarak Digiturk Play Yurt Dışı Spor paketiyle izlenebilir "
        f'(<a href="{CONTENT.GUIDE_TR}" style="color:#fff;text-decoration:underline">nasıl izlenir</a>). Türkiye\'de tüm maçlar beIN SPORTS ve TOD\'da.',
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
        TRM = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
        TRD = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
        no_uk = f' Süper Lig matches are not on UK TV in 2026/27 but can be watched legally on Digiturk Play\'s international Sports package (<a href="{CONTENT.GUIDE_EN}" style="color:#fff;text-decoration:underline">how to watch</a>).' if not N.get("uk_superlig_rights") else ""
        if nxt:
            d = nxt["dt"].date()
            rel_en = "Today" if d == TODAY else "Tomorrow" if d == TODAY + timedelta(days=1) else nxt["dt"].strftime("%a")
            rel_tr = "Bugün" if d == TODAY else "Yarın" if d == TODAY + timedelta(days=1) else TRD[d.weekday()]
            en_day = f'{rel_en} {d.day} {nxt["dt"].strftime("%b")}'
            tr_day = f'{d.day} {TRM[d.month-1]} {rel_tr}'
            vs = f'{nxt["home"]} v {nxt["away"]}'
            chans = ", ".join(nxt["channels"])
            title = f'{c} maçı hangi kanalda? {vs} – {en_day} {nxt["uk"]} UK ({nxt["tr"]} TSİ) | {SITE}'
            desc = (f'{c} maçı saat kaçta? {nxt["home"]} – {nxt["away"]}: {tr_day}, İngiltere saati {nxt["uk"]}, Türkiye saati {nxt["tr"]}. '
                    f'Kanal: {chans}. What channel is {c} on in the UK? {vs}, {en_day}, kick-off {nxt["uk"]} UK time.')
            intro = (f'<a href="{match_path(nxt)}" style="color:#fff"><b>{esc(vs)}</b></a> · {esc(en_day)} · {nxt["uk"]} UK time ({nxt["tr"]} TSİ) · {esc(chans)}<br>'
                     f'{esc(c)} maçı {esc(tr_day)} günü İngiltere saatiyle {nxt["uk"]}\'da (TSİ {nxt["tr"]}) başlıyor.' + no_uk)
        else:
            title = f"{c} maçı hangi kanalda, saat kaçta? İngiltere saati | {c} on TV UK | {SITE}"
            desc = (f"{c} maçları İngiltere saati ve Türkiye saati ile, yayın kanallarıyla. What channel is {c} on in the UK? "
                    f"{c} fixtures with UK kick-off times, updated every day.")
            intro = f"{esc(c)} have no match in the current listings yet. / Henüz açıklanmış {esc(c)} maçı yok." + no_uk
        write(sl, page(sl, title, desc, f"{c} maçı hangi kanalda? · {c} on TV", intro,
            listing(fx, empty=f"No {c} match in the listings yet."), fx, controls=False, banner=False))
        pages.append((sl, "daily", "0.7"))
    # Club index section on home & super lig page is via links list
    clubs_html = '<section class="clubs"><h2>Süper Lig clubs</h2><ul>' + "".join(
        f'<li><a href="/{slug(c)}-on-tv/">{esc(c)} on TV</a></li>' for c in CLUBS) + "</ul></section>"
    for p in ["index.html", "super-lig-on-tv-uk/index.html"]:
        fp = os.path.join(OUT, p); s = open(fp, encoding="utf-8").read()
        open(fp, "w", encoding="utf-8").write(s.replace("</main>", clubs_html + "</main>", 1))
    # Match pages: every match with a Turkish club or Türkiye (upcoming + last Süper Lig round with scores)
    extra = []
    seen = {(f["date"], f["home"], f["away"]) for f in FIX}
    for g in D["fixtures"]:
        if g["comp"] in EXCLUDED or (g["date"], g["home"], g["away"]) in seen: continue
        if not g.get("score") or g["date"] < (TODAY - timedelta(days=10)).isoformat(): continue
        h = dict(g); dt = datetime.fromisoformat(f"{g['date']}T{g['uk']}").replace(tzinfo=LON)
        h.update(dt=dt, iso=dt.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ"), tr=dt.astimezone(IST).strftime("%H:%M"),
                 tr_next=dt.astimezone(IST).date() != dt.date(), turk=True)
        extra.append(h)
    turk_fx = [f for f in FIX if f["turk"]] + extra
    upcoming_turk = [f for f in FIX if f["turk"]]
    for f in turk_fx:
        p = match_path(f)
        uk_ch = [c for c in f["channels"] if "(TR)" not in c]
        tr_ch = [c.replace(" (TR)", "") for c in f["channels"] if "(TR)" in c]
        score = f.get("score")
        sl = f["comp"] == "Süper Lig"
        if sl:
            how = (f'<p><b>İngiltere\'de nasıl izlenir?</b> Süper Lig 2026/27\'de İngiliz TV kanallarında yok. İngiltere\'de yasal yol <b>Digiturk Play Yurt Dışı Spor paketi</b>. '
                   f'Türkiye\'de maç beIN SPORTS ve TOD\'da. <a href="{CONTENT.GUIDE_TR}">Ayrıntılı rehber →</a></p>'
                   f'<p><b>How to watch in the UK:</b> the Süper Lig is not on UK TV in 2026/27; the legal option is Digiturk Play\'s international Sports package. '
                   f'<a href="{CONTENT.GUIDE_EN}">Full guide →</a></p>')
        else:
            how = (f'<p><b>İngiltere\'de nasıl izlenir?</b> Bu maç İngiltere\'de <b>{esc(", ".join(uk_ch))}</b> üzerinden yayınlanıyor.</p>'
                   f'<p><b>How to watch in the UK:</b> live on <b>{esc(", ".join(uk_ch))}</b>.</p>')
        rows_ = [("Organizasyon / Competition", esc(f["comp"])),
                 ("Tarih / Date", f'{esc(mday_tr(f))} · {f["dt"].strftime("%A")} {f["dt"].day} {f["dt"].strftime("%B %Y")}'),
                 ("İngiltere saati / UK time", f'<b>{f["uk"]}</b>'),
                 ("Türkiye saati / TSİ", f'<b>{f["tr"]}</b>{" (+1 gün)" if f["tr_next"] else ""}'),
                 ("İngiltere'de / UK", esc(", ".join(uk_ch)) or "—"),
                 ("Türkiye'de / In Türkiye", esc(", ".join(tr_ch)) or "—")]
        if score: rows_.insert(0, ("Sonuç / Result", f'<b class="big">{esc(score.replace("-", " – "))}</b>'))
        clubs = [t for t in (f["home"], f["away"]) if t in ALL_SL_CLUBS]
        others = [g for g in upcoming_turk if g is not f][:8]
        vs_tr = f'{f["home"]} – {f["away"]}'
        body = (f'<article class="prose match">'
                + (f'<p class="lead"><b>{esc(vs_tr)}</b> maçı <b>{esc(mday_tr(f))}</b> günü İngiltere saatiyle <b>{f["uk"]}</b>\'da (TSİ {f["tr"]}) başlıyor. '
                   f'{esc(f["home"])} v {esc(f["away"])} kicks off at <b>{f["uk"]} UK time</b> on {esc(f["dt"].strftime("%A"))} {f["dt"].day} {esc(f["dt"].strftime("%B"))}.</p>' if not score else
                   f'<p class="lead"><b>{esc(vs_tr)}</b> maçı <b>{esc(score)}</b> sona erdi. {esc(f["home"])} {esc(score)} {esc(f["away"])} (full time).</p>')
                + '<table class="mt">' + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows_) + '</table>'
                + how
                + f'<p><a class="wa big" href="{esc(wa_link(f))}" target="_blank" rel="noopener nofollow">{WA_ICON} WhatsApp\'ta paylaş / Share on WhatsApp</a></p>'
                + ('<h2>Takım sayfaları</h2><p>' + " · ".join(f'<a href="/{slug(c)}-on-tv/">{esc(c)} maçları / on TV</a>' for c in clubs) + '</p>' if clubs else '')
                + ('<h2>Diğer Türk takımı maçları · More Turkish matches</h2><ul class="others">' + "".join(
                    f'<li><a href="{match_path(g)}">{esc(g["home"])} – {esc(g["away"])}</a> <span>{esc(mday_tr(g))} · {g["uk"]} UK</span></li>' for g in others) + '</ul>' if others else '')
                + '</article>')
        title = (f'{vs_tr} hangi kanalda, saat kaçta? {f["dt"].day} {TRM_ALL[f["dt"].month-1]} · İngiltere {f["uk"]} (TSİ {f["tr"]}) | {SITE}' if not score
                 else f'{f["home"]} {score} {f["away"]} – maç sonucu ({f["dt"].day} {TRM_ALL[f["dt"].month-1]}) | {SITE}')
        desc = (f'{vs_tr} maçı ne zaman, saat kaçta, hangi kanalda? {mday_tr(f)}, İngiltere saati {f["uk"]}, Türkiye saati {f["tr"]}. '
                f'Kanal: {", ".join(f["channels"])}. What time is {f["home"]} v {f["away"]} in the UK and what channel is it on?')
        html_ = page(p, title, desc, f'{vs_tr} hangi kanalda?',
                     f'{esc(f["comp"])} · {esc(mday_tr(f))} · {f["uk"]} İngiltere saati · {f["tr"]} TSİ', body, [f], lang="tr", controls=False, banner=False)
        html_ = re.sub(r'<div class="controls slim">.*?</div></div>', "", html_, count=1, flags=re.S)
        write(p, html_)
        pages.append((p, "daily", "0.6"))

    # Content pages (guide EN/TR, about, contact, privacy)
    club_links = lambda lang: '<ul class="clublinks">' + "".join(
        f'<li><a href="/{slug(c)}-on-tv/">{esc(c)}{" maçı" if lang=="tr" else " on TV"}</a></li>' for c in CLUBS) + "</ul>"
    def faq_html(qas): return "".join(f"<details class=faq><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in qas)
    content = [
        (CONTENT.GUIDE_EN, "en", f"How to watch the Süper Lig in the UK (2026/27) – legal options, channels & UK kick-off times | {SITE}",
         "Is the Turkish Süper Lig on UK TV? Not in 2026/27 – here is the legal way to watch Galatasaray, Fenerbahçe, Beşiktaş and every Süper Lig match in the UK, plus Turkish clubs in Europe and UK kick-off times.",
         "How to watch the Süper Lig in the UK", "Every legal option for 2026/27, Turkish clubs in Europe, the national team and UK kick-off times.",
         CONTENT.GUIDE_EN_BODY.replace("{CLUB_LINKS}", club_links("en")).replace("{FAQ}", faq_html(CONTENT.GUIDE_EN_FAQ)),
         CONTENT.GUIDE_EN_FAQ, [("en-GB", CONTENT.GUIDE_EN), ("tr", CONTENT.GUIDE_TR)], "0.8"),
        (CONTENT.GUIDE_TR, "tr", f"İngiltere'de Süper Lig nasıl izlenir? (2026/27) Yasal yollar, kanallar ve İngiltere saati | {SITE}",
         "Süper Lig İngiltere'de televizyonda var mı? 2026/27'de yok – Galatasaray, Fenerbahçe, Beşiktaş ve tüm Süper Lig maçlarını İngiltere'de yasal olarak izlemenin yolu, Türk takımlarının Avrupa maçları ve İngiltere saati.",
         "İngiltere'de Süper Lig nasıl izlenir?", "2026/27 için tüm yasal yollar, Türk takımlarının Avrupa maçları, A Milli Takım ve İngiltere saati.",
         CONTENT.GUIDE_TR_BODY.replace("{CLUB_LINKS}", club_links("tr")).replace("{FAQ}", faq_html(CONTENT.GUIDE_TR_FAQ)),
         CONTENT.GUIDE_TR_FAQ, [("en-GB", CONTENT.GUIDE_EN), ("tr", CONTENT.GUIDE_TR)], "0.8"),
        ("/about/", "en", f"About Maç Saati – football on TV for the Turkish community in the UK | {SITE}",
         "Maç Saati is a free, independent guide to football on TV for the Turkish community in the UK, with UK and Turkish kick-off times and channels from official sources.",
         "About Maç Saati", "Hakkımızda · Football on TV for the Turkish community in the UK.", CONTENT.ABOUT_BODY, None, None, "0.4"),
        ("/contact/", "en", f"Contact Maç Saati | {SITE}", "Contact Maç Saati with corrections, questions or sponsorship enquiries.",
         "Contact", "İletişim · Corrections, questions and ideas.", CONTENT.CONTACT_BODY, None, None, "0.3"),
        ("/privacy/", "en", f"Privacy policy | {SITE}", "How Maç Saati handles your data: no accounts, no adverts, no analytics and no cookies.",
         "Privacy policy", "No accounts, no adverts, no analytics, no cookies.", CONTENT.PRIVACY_BODY, None, None, "0.2"),
    ]
    for path, lang, title, desc, h1, intro, body, faq, hl, prio in content:
        html_ = page(path, title, desc, h1, esc(intro), body, [], lang=lang, hreflang=hl, controls=False, banner=False)
        html_ = re.sub(r'<div class="controls slim">.*?</div></div>', "", html_, count=1, flags=re.S)
        if faq:
            extra = json.dumps({"@context": "https://schema.org", **CONTENT.faq_jsonld(faq)}, ensure_ascii=False)
            html_ = html_.replace("</head>", f'<script type="application/ld+json">{extra}</script></head>', 1)
        write(path, html_)
        pages.append((path, "monthly", prio))
    # 404
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(
        page("/404.html", f"Page not found | {SITE}", "Page not found", "Page not found",
             'That page doesn\'t exist. <a href="/" style="color:#fff;text-decoration:underline">Go to this week\'s listings</a>.', "", [], controls=False, banner=False)
        .replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"'))
    # sitemap / robots / CNAME
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p, freq, pri in pages:
        sm.append(f"<url><loc>{DOMAIN}{p}</loc><lastmod>{D['generated']}</lastmod><changefreq>{freq}</changefreq><priority>{pri}</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm))
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    open(os.path.join(OUT, "CNAME"), "w").write(DOMAIN.split("//")[1])
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    print(f"Built {len(pages)} pages, {len(FIX)} fixtures -> {OUT}")

if __name__ == "__main__":
    build()
