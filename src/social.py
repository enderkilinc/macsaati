"""Daily Instagram images for Maç Saati (built by build.py into docs/social/).

today-story.png  1080x1920  "Bugün TV'de" story (add a link sticker to macsaati.co.uk)
today-post.png   1080x1350  same day as a 4:5 feed post
week-turk.png    1080x1350  Turkish-interest matches in the next 7 days
match-*.png      1080x1350  one post per Turkish-interest match today/tomorrow
profile.png      1080x1080  profile picture
captions.txt + index.html  ready-to-copy captions and download links (noindex)
Own graphics only: no club crests, league logos or broadcaster logos.
"""
import os
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "fonts", "DejaVuSans-Bold.ttf")
R = os.path.join(HERE, "fonts", "DejaVuSans.ttf")
TRM = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
TRD = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
RED1, RED2 = (142, 0, 12), (227, 10, 23)
F = lambda p, s: ImageFont.truetype(p, s)

def bg(w, h):
    im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(RED1[i] + (RED2[i] - RED1[i]) * t) for i in range(3)))
    return im, d

def logo(d, x, y, s=1.0, col="white"):
    w = int(4 * s)
    d.rounded_rectangle([x, y, x + int(70 * s), y + int(48 * s)], radius=int(8 * s), outline=col, width=w)
    d.line([(x + int(18 * s), y + int(62 * s)), (x + int(52 * s), y + int(62 * s))], fill=col, width=w)
    d.ellipse([x + int(24 * s), y + int(12 * s), x + int(46 * s), y + int(34 * s)], outline=col, width=w)

def fit(d, text, font_path, size, maxw):
    while size > 18:
        f = F(font_path, size)
        if d.textlength(text, font=f) <= maxw: return f
        size -= 2
    return F(font_path, size)

def chan(f):
    uk = [c for c in f["channels"] if "(TR)" not in c]
    tr = [c.replace(" (TR)", "") for c in f["channels"] if "(TR)" in c]
    s = ", ".join(uk[:2]) if uk else ""
    if tr and f.get("turk"): s = (s + " · " if s else "") + "TR: " + ", ".join(tr[:2])
    return s

def day_tr(d): return f"{d.day} {TRM[d.month-1]} {TRD[d.weekday()]}"

def header(d, w, title, sub, top=70):
    logo(d, 70, top, 1.0)
    d.text((165, top - 4), "MAÇ SAATİ", font=F(B, 52), fill="white")
    d.text((168, top + 54), "İngiltere'de maç saatleri · UK", font=F(R, 26), fill=(255, 220, 222))
    d.text((70, top + 140), title, font=F(B, 78), fill="white")
    d.text((72, top + 236), sub, font=F(R, 38), fill=(255, 225, 227))

def footer(d, w, h, line="macsaati.co.uk"):
    d.text((w // 2, h - 90), line, font=F(B, 44), fill="white", anchor="mm")

def match_rows(d, w, y, fx, maxh, row_h=150):
    n = 0
    for f in fx:
        if y + row_h > maxh: return y, n
        d.rounded_rectangle([60, y, w - 60, y + row_h - 18], radius=22, fill="white")
        d.text((92, y + 22), f["uk"], font=F(B, 44), fill=RED1)
        d.text((92, y + 76), f"TSİ {f['tr']}", font=F(R, 24), fill=(140, 110, 112))
        teams = f"{f['home']} – {f['away']}"
        d.text((260, y + 20), teams, font=fit(d, teams, B, 38, w - 360), fill=(40, 10, 14))
        sub = f"{f['comp']} · {chan(f)}"
        d.text((262, y + 74), sub, font=fit(d, sub, R, 26, w - 360), fill=(110, 80, 84))
        if f.get("turk"): d.rectangle([60, y, 70, y + row_h - 18], fill=RED2)
        y += row_h; n += 1
    return y, n

def pick_day(fixtures, today):
    for k in range(0, 8):
        d = today + timedelta(days=k)
        fx = [f for f in fixtures if f["dt"].date() == d]
        if fx: return d, fx
    return today, []

def order(fx, rank):
    return sorted(fx, key=lambda f: (not f.get("turk"), rank(f["comp"]), f["uk"]))

def build_social(fixtures, today, out, rank, match_path, domain):
    os.makedirs(out, exist_ok=True)
    made, caps = [], []
    day, fx = pick_day(fixtures, today)
    lead = "Bugün TV'de" if day == today else ("Yarın TV'de" if day == today + timedelta(days=1) else f"{TRD[day.weekday()]} TV'de")
    fx = order(fx, rank)

    # Story 1080x1920
    im, d = bg(1080, 1920)
    header(d, 1080, lead, day_tr(day), top=110)
    y, shown = match_rows(d, 1080, 480, fx, 1700)
    if len(fx) > shown: d.text((540, y + 20), f"+{len(fx) - shown} maç daha · all matches on the site", font=F(R, 30), fill="white", anchor="ma")
    footer(d, 1080, 1920)
    im.save(os.path.join(out, "today-story.png"), optimize=True); made.append("today-story.png")

    # Feed post 1080x1350
    im, d = bg(1080, 1350)
    header(d, 1080, lead, day_tr(day), top=60)
    y, shown = match_rows(d, 1080, 400, fx, 1210, row_h=140)
    if len(fx) > shown: d.text((540, y + 6), f"+{len(fx) - shown} maç daha → macsaati.co.uk", font=F(R, 28), fill="white", anchor="ma")
    footer(d, 1080, 1350)
    im.save(os.path.join(out, "today-post.png"), optimize=True); made.append("today-post.png")
    tags = "#maçsaati #süperlig #galatasaray #fenerbahçe #beşiktaş #trabzonspor #londra #ingiltere #türklerlondra"
    lines = "\n".join(f"⚽ {f['uk']} (TSİ {f['tr']}) {f['home']} – {f['away']} · {chan(f)}" for f in fx[:12])
    caps.append(("today-post.png / today-story.png", f"{lead} · {day_tr(day)}\n\n{lines}\n\nTüm maçlar, İngiltere ve Türkiye saatiyle: macsaati.co.uk (link bio'da)\n\n{tags}"))

    # Turkish-interest week
    turk = [f for f in fixtures if f.get("turk") and today <= f["dt"].date() <= today + timedelta(days=6)]
    im, d = bg(1080, 1350)
    header(d, 1080, "Bu hafta", "Türk takımları ve A Milli Takım · UK saati", top=60)
    y = 400
    for f in sorted(turk, key=lambda f: f["dt"])[:6]:
        d.rounded_rectangle([60, y, 1020, y + 112], radius=20, fill="white")
        dd = f["dt"].date()
        d.text((92, y + 16), f"{dd.day} {TRM[dd.month-1][:3]}", font=F(B, 30), fill=RED1)
        d.text((92, y + 58), f"{f['uk']} UK", font=F(R, 26), fill=(110, 80, 84))
        teams = f"{f['home']} – {f['away']}"
        d.text((260, y + 14), teams, font=fit(d, teams, B, 34, 720), fill=(40, 10, 14))
        sub = f"{f['comp']} · TSİ {f['tr']}"
        d.text((262, y + 62), sub, font=fit(d, sub, R, 24, 720), fill=(110, 80, 84))
        y += 125
    if len(turk) > 6: d.text((540, y + 4), f"+{len(turk) - 6} maç daha → macsaati.co.uk", font=F(R, 28), fill="white", anchor="ma")
    if not turk: d.text((540, 600), "Bu hafta Türk takımı maçı yok", font=F(B, 40), fill="white", anchor="mm")
    footer(d, 1080, 1350)
    im.save(os.path.join(out, "week-turk.png"), optimize=True); made.append("week-turk.png")
    caps.append(("week-turk.png", "Bu hafta Türk takımlarının maçları – İngiltere saatiyle ⏰\n\n"
                 + "\n".join(f"• {day_tr(f['dt'].date())} {f['uk']} · {f['home']} – {f['away']}" for f in sorted(turk, key=lambda f: f['dt'])[:10])
                 + f"\n\nKanallar ve tüm detaylar: macsaati.co.uk\n\n{tags}"))

    # One post per Turkish-interest match today/tomorrow
    for f in sorted([f for f in fixtures if f.get("turk") and today <= f["dt"].date() <= today + timedelta(days=1)], key=lambda f: f["dt"]):
        im, d = bg(1080, 1350)
        logo(d, 70, 60); d.text((165, 56), "MAÇ SAATİ", font=F(B, 52), fill="white")
        d.text((540, 300), f["comp"].upper(), font=F(B, 34), fill=(255, 210, 213), anchor="mm")
        d.text((540, 430), f["home"], font=fit(d, f["home"], B, 92, 960), fill="white", anchor="mm")
        d.text((540, 530), "–", font=F(B, 70), fill=(255, 210, 213), anchor="mm")
        d.text((540, 630), f["away"], font=fit(d, f["away"], B, 92, 960), fill="white", anchor="mm")
        d.rounded_rectangle([140, 740, 940, 1080], radius=30, fill="white")
        dd = f["dt"].date()
        d.text((540, 800), day_tr(dd), font=F(B, 40), fill=RED1, anchor="mm")
        d.text((540, 890), f"{f['uk']}  İngiltere saati", font=F(B, 56), fill=(40, 10, 14), anchor="mm")
        d.text((540, 960), f"{f['tr']}  TSİ", font=F(R, 38), fill=(110, 80, 84), anchor="mm")
        c = chan(f); d.text((540, 1030), c, font=fit(d, c, R, 30, 760), fill=(110, 80, 84), anchor="mm")
        d.text((540, 1180), "Nasıl izlenir? → macsaati.co.uk", font=F(B, 40), fill="white", anchor="mm")
        name = "match-" + match_path(f).strip("/").split("/")[-1] + ".png"
        im.save(os.path.join(out, name), optimize=True); made.append(name)
        caps.append((name, f"⚽ {f['home']} – {f['away']} hangi kanalda?\n🗓 {day_tr(dd)}\n⏰ {f['uk']} İngiltere saati · {f['tr']} TSİ\n📺 {c}\n\n"
                           f"İngiltere'de nasıl izlenir? Link bio'da 👉 macsaati.co.uk\n\n{tags}"))

    # Profile picture
    im, d = bg(1080, 1080)
    logo(d, 300, 260, 6.5)
    d.text((540, 820), "MAÇ SAATİ", font=F(B, 120), fill="white", anchor="mm")
    im.save(os.path.join(out, "profile.png"), optimize=True); made.append("profile.png")

    with open(os.path.join(out, "captions.txt"), "w", encoding="utf-8") as fh:
        for n, c in caps: fh.write(f"=== {n} ===\n{c}\n\n")
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    cards = "".join(f'<div class="c"><a href="{n}" download><img src="{n}" alt="" loading="lazy"></a><p><a href="{n}" download>⬇ {n}</a></p></div>' for n in made)
    capt = "".join(f'<h3>{esc(n)}</h3><textarea readonly onclick="this.select()">{esc(c)}</textarea>' for n, c in caps)
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(f'<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                 f'<meta name="robots" content="noindex,nofollow"><title>Maç Saati – Instagram</title><style>'
                 f'body{{font-family:system-ui,sans-serif;margin:0;padding:18px;background:#f7f5f5;color:#2a0d10}}h1{{color:#B5000F}}'
                 f'.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}}.c{{background:#fff;border-radius:12px;padding:10px}}'
                 f'.c img{{width:100%;border-radius:8px}}textarea{{width:100%;height:190px;font:14px system-ui;padding:8px;border-radius:8px;border:1px solid #ddd}}'
                 f'a{{color:#B5000F}}</style></head><body><h1>Instagram – {esc(day_tr(today))}</h1>'
                 f'<p>Görsele dokun ve kaydet, sonra aşağıdaki metni kopyala. Story\'de <b>link çıkartması</b> ile macsaati.co.uk ekle.</p>'
                 f'<div class="g">{cards}</div><h2>Açıklamalar / Captions</h2>{capt}</body></html>')
    return made
