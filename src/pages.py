"""Static content pages for Maç Saati: Süper Lig guide (EN/TR), About, Contact, Privacy.
Each entry: path, lang, title (Google), description, h1, intro (hero line), body (HTML), hreflang pairs.
Facts in the guide were checked in November 2026; re-check prices and rights each season.
"""

CONTACT_EMAIL = "contact@macsaati.co.uk"
GUIDE_EN = "/how-to-watch-super-lig-in-uk/"
GUIDE_TR = "/tr/ingilterede-super-lig-nasil-izlenir/"
DIGITURK_APP = "https://apps.apple.com/app/id434813948"   # "Digiturk Play Yurt Dışı", developer: DIGITURK

def faq_jsonld(qas):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qas]}

GUIDE_EN_FAQ = [
    ("Is the Süper Lig on UK TV in 2026/27?",
     "No. No UK channel such as Sky Sports, TNT Sports, Premier Sports, BBC or ITV has the rights to show Süper Lig matches in the 2026/27 season."),
    ("How can I watch the Süper Lig legally in the UK?",
     "Through Digiturk Play's international service (Digiturk Play Yurt Dışı) with the Sports package. It streams every Süper Lig match live with Turkish commentary over the internet, on a smart TV, Fire TV stick, Apple TV, phone or computer. The Family package alone does not include the matches."),
    ("Can I use a TOD or beIN CONNECT account from Türkiye in the UK?",
     "Those subscriptions are sold for viewing in Türkiye. Their terms restrict use abroad, and using a VPN to get round that breaks the terms and can get the account closed."),
    ("Where can I watch Galatasaray, Fenerbahçe or other Turkish clubs in Europe?",
     "Champions League, Europa League and Conference League matches are on UK TV: TNT Sports and HBO Max show most of them, and Prime Video shows one top Tuesday Champions League match each week."),
    ("What time do Süper Lig matches kick off in the UK?",
     "Turkish time (TSİ) is 3 hours ahead of the UK in winter and 2 hours ahead in summer. A 19:00 TSİ kick-off is 16:00 in the UK from late October to late March, and 17:00 the rest of the year."),
]

GUIDE_EN_BODY = f"""
<article class="prose">
<p class="lead"><b>Short answer:</b> the Süper Lig is <b>not on any UK TV channel</b> in 2026/27. The legal way to watch every match live in the UK is
<b>Digiturk Play's international Sports package</b>, an internet streaming service from Digiturk, the beIN Media Group company that holds the league's rights.</p>

<h2>1. Is the Süper Lig on Sky, TNT or any UK channel?</h2>
<p>No. Sky Sports, TNT Sports, Premier Sports, the BBC, ITV and the UK streaming services do not have the 2026/27 Süper Lig rights, so you will not find
Galatasaray, Fenerbahçe, Beşiktaş, Trabzonspor or any other Süper Lig match in UK TV listings. That is why the
<a href="/super-lig-on-tv-uk/">Süper Lig page</a> on Maç Saati shows UK kick-off times with the legal UK streaming option (Digiturk Play) and the Turkish broadcasters, rather than a UK TV channel.</p>

<h2>2. The legal option: Digiturk Play abroad (Yurt Dışı)</h2>
<p>Digiturk sells an international version of its streaming service for people living outside Türkiye. With the <b>Sports package</b> you get:</p>
<ul>
<li>every Trendyol Süper Lig and 1. Lig match live on the beIN SPORTS channels, with Turkish commentary;</li>
<li>the Turkish national channels (TRT 1, ATV, Kanal D, Show TV and others) that also come with the cheaper Family package;</li>
<li>apps for smart TVs, Amazon Fire TV, Apple TV, phones, tablets and web browsers. No satellite dish is needed.</li>
</ul>
<p><b>Important:</b> the <b>Family package on its own does not include the Süper Lig</b>. You need the Sports package (sold as "Sports + Family").</p>
<p><b>Price:</b> plans are prepaid for 3, 6, 12 or 24 months. In November 2026, UK sellers were advertising the 12-month Sports package at around
<b>£119</b>. Prices change and vary by seller, so check before you buy, and buy from Digiturk or an authorised seller.
The official app is <a href="{DIGITURK_APP}" target="_blank" rel="noopener nofollow">"Digiturk Play Yurt Dışı" by DIGITURK</a>.</p>

<h2>3. What about TOD, beIN CONNECT or a VPN?</h2>
<p>TOD and beIN CONNECT subscriptions bought in Türkiye are meant for viewing in Türkiye. Their terms restrict use from abroad, and using a VPN to get
round that breaks the terms and can get your account closed. Maç Saati lists them only so you know which Turkish channel shows a match.
Unofficial "IPTV" boxes and free streaming sites are illegal in the UK.</p>

<h2>4. Turkish clubs in Europe are on UK TV</h2>
<p>When Galatasaray, Fenerbahçe, Beşiktaş, Trabzonspor or another Turkish club plays in Europe, the match <b>is</b> on UK TV:</p>
<ul>
<li><b>Champions League:</b> TNT Sports and HBO Max show most matches; Prime Video shows one top match every Tuesday.</li>
<li><b>Europa League and Conference League:</b> TNT Sports and HBO Max.</li>
</ul>
<p>Every one of these is in the <a href="/">full listings</a>, highlighted in red.</p>

<h2>5. Türkiye national team</h2>
<p>Türkiye's Nations League matches are on <b>Prime Video</b> in the UK (and on ATV and S Sport in Türkiye). See the
<a href="/turkey-on-tv/">Türkiye on TV</a> page for the next match.</p>

<h2>6. UK kick-off times</h2>
<p>Turkish time (TSİ) is <b>3 hours ahead</b> of the UK from late October to late March and <b>2 hours ahead</b> in summer.
So a 20:00 TSİ match starts at 17:00 UK time in winter. Every match on Maç Saati shows the UK time first; tap <b>TSİ (TR)</b> at the top to switch.</p>

<h2>Find your club</h2>
<p>Each Süper Lig club has its own page with the next match, the UK and Turkish kick-off time and the channel:</p>
{{CLUB_LINKS}}

<h2>Frequently asked questions</h2>
{{FAQ}}
<p class="small">Last checked: November 2026. Maç Saati is independent and is not paid by Digiturk or any broadcaster.</p>
</article>
"""

GUIDE_TR_FAQ = [
    ("Süper Lig 2026/27 sezonunda İngiltere'de televizyonda var mı?",
     "Hayır. Sky Sports, TNT Sports, Premier Sports, BBC ve ITV gibi İngiliz kanallarının hiçbirinde 2026/27 sezonu Süper Lig yayın hakkı yok."),
    ("İngiltere'de Süper Lig yasal olarak nasıl izlenir?",
     "Digiturk Play'in yurt dışı hizmetiyle (Digiturk Play Yurt Dışı), Spor paketiyle. Tüm Süper Lig maçları Türkçe anlatımla internet üzerinden canlı yayınlanır; Smart TV, Fire TV, Apple TV, telefon ve bilgisayarda izlenebilir. Yalnızca Aile paketi maçları kapsamaz."),
    ("Türkiye'de aldığım TOD veya beIN CONNECT üyeliğini İngiltere'de kullanabilir miyim?",
     "Bu üyelikler Türkiye'de izlemek için satılır. Kullanım koşulları yurt dışından izlemeyi kısıtlar; VPN ile aşmak koşulları ihlal eder ve hesabın kapatılmasına yol açabilir."),
    ("Galatasaray, Fenerbahçe ve diğer Türk takımlarının Avrupa maçları İngiltere'de hangi kanalda?",
     "Şampiyonlar Ligi, Avrupa Ligi ve Konferans Ligi maçları İngiltere'de yayınlanıyor: çoğu TNT Sports ve HBO Max'te, her salı bir büyük Şampiyonlar Ligi maçı Prime Video'da."),
    ("Süper Lig maçları İngiltere saatiyle kaçta başlıyor?",
     "Türkiye saati (TSİ) kışın İngiltere'den 3 saat, yazın 2 saat ileridedir. TSİ 19.00'daki bir maç ekim sonundan mart sonuna kadar İngiltere saatiyle 16.00'da, yılın geri kalanında 17.00'de başlar."),
]

GUIDE_TR_BODY = f"""
<article class="prose">
<p class="lead"><b>Kısaca:</b> 2026/27 sezonunda Süper Lig <b>İngiltere'de hiçbir televizyon kanalında yok</b>. İngiltere'de tüm maçları yasal olarak canlı
izlemenin yolu <b>Digiturk Play'in yurt dışı Spor paketi</b>; lig yayın haklarına sahip beIN Media Group şirketi Digiturk'ün internet yayın hizmeti.</p>

<h2>1. Süper Lig Sky, TNT veya başka bir İngiliz kanalında var mı?</h2>
<p>Hayır. Sky Sports, TNT Sports, Premier Sports, BBC, ITV ve İngiltere'deki dijital platformların 2026/27 Süper Lig hakkı yok. Bu yüzden Galatasaray,
Fenerbahçe, Beşiktaş, Trabzonspor veya diğer Süper Lig maçlarını İngiliz yayın akışlarında bulamazsınız. Maç Saati'nin
<a href="/tr/">Süper Lig sayfası</a> bu nedenle maçları İngiltere saatiyle, İngiltere'deki yasal yayın seçeneği (Digiturk Play) ve Türk yayıncılarıyla gösterir.</p>

<h2>2. Yasal yol: Digiturk Play Yurt Dışı</h2>
<p>Digiturk, Türkiye dışında yaşayanlar için yayın hizmetinin yurt dışı sürümünü satıyor. <b>Spor paketi</b> ile:</p>
<ul>
<li>tüm Trendyol Süper Lig ve 1. Lig maçları beIN SPORTS kanallarında, Türkçe anlatımla canlı;</li>
<li>daha uygun fiyatlı Aile paketinde de bulunan ulusal kanallar (TRT 1, ATV, Kanal D, Show TV ve diğerleri);</li>
<li>Smart TV, Amazon Fire TV, Apple TV, telefon, tablet ve web tarayıcı uygulamaları. Çanak anten gerekmez.</li>
</ul>
<p><b>Önemli:</b> <b>Yalnızca Aile paketi Süper Lig maçlarını kapsamaz.</b> "Spor + Aile" olarak satılan Spor paketi gerekir.</p>
<p><b>Fiyat:</b> paketler 3, 6, 12 veya 24 aylık peşin ödemelidir. Kasım 2026'da İngiltere'deki satıcılar 12 aylık Spor paketini yaklaşık
<b>119 £</b> olarak gösteriyordu. Fiyatlar değişebilir ve satıcıya göre farklıdır; satın almadan önce kontrol edin ve Digiturk'ten ya da yetkili satıcıdan alın.
Resmi uygulama: <a href="{DIGITURK_APP}" target="_blank" rel="noopener nofollow">DIGITURK'ün "Digiturk Play Yurt Dışı" uygulaması</a>.</p>

<h2>3. TOD, beIN CONNECT veya VPN?</h2>
<p>Türkiye'de alınan TOD ve beIN CONNECT üyelikleri Türkiye'de izlemek içindir. Kullanım koşulları yurt dışından izlemeyi kısıtlar; VPN ile aşmak koşulları ihlal
eder ve hesabın kapatılmasına yol açabilir. Maç Saati bu kanalları yalnızca maçın Türkiye'de hangi kanalda olduğunu göstermek için listeler.
Resmi olmayan "IPTV" kutuları ve ücretsiz yayın siteleri İngiltere'de yasa dışıdır.</p>

<h2>4. Türk takımlarının Avrupa maçları İngiltere'de televizyonda</h2>
<p>Galatasaray, Fenerbahçe, Beşiktaş, Trabzonspor veya başka bir Türk takımı Avrupa'da oynadığında maç İngiltere'de <b>yayınlanır</b>:</p>
<ul>
<li><b>Şampiyonlar Ligi:</b> çoğu maç TNT Sports ve HBO Max'te; her salı bir büyük maç Prime Video'da.</li>
<li><b>Avrupa Ligi ve Konferans Ligi:</b> TNT Sports ve HBO Max.</li>
</ul>
<p>Bu maçların hepsi <a href="/">tüm maçlar</a> listesinde kırmızıyla işaretli.</p>

<h2>5. A Milli Takım</h2>
<p>Türkiye'nin Uluslar Ligi maçları İngiltere'de <b>Prime Video</b>'da (Türkiye'de ATV ve S Sport'ta). Sıradaki maç için
<a href="/turkey-on-tv/">Türkiye sayfasına</a> bakın.</p>

<h2>6. İngiltere saati</h2>
<p>Türkiye saati (TSİ) ekim sonundan mart sonuna kadar İngiltere'den <b>3 saat</b>, yazın <b>2 saat</b> ileridedir. Yani TSİ 20.00'deki bir maç kışın
İngiltere saatiyle 17.00'de başlar. Maç Saati her maçı önce İngiltere saatiyle gösterir; Türkiye saati için üstteki <b>TSİ (TR)</b> düğmesine dokunun.</p>

<h2>Takımınızı bulun</h2>
<p>Her Süper Lig takımının sıradaki maçı, İngiltere ve Türkiye saati ve kanalıyla kendi sayfası var:</p>
{{CLUB_LINKS}}

<h2>Sık sorulan sorular</h2>
{{FAQ}}
<p class="small">Son kontrol: Kasım 2026. Maç Saati bağımsızdır; Digiturk veya herhangi bir yayıncıdan ücret almaz.</p>
</article>
"""

ABOUT_BODY = f"""
<article class="prose">
<p class="lead">Maç Saati ("match time" in Turkish) is a free, independent guide to football on TV for the Turkish community in the UK.</p>
<h2>Why it exists</h2>
<p>If you follow Turkish football from Britain, the same questions come up every week: what time is the match here, which channel is it on, and is it on UK TV
at all? Big UK listings sites don't cover the Süper Lig, and Turkish sites give Turkish times and Turkish channels. Maç Saati puts both side by side:
UK kick-off time and Turkish time (TSİ), UK channels and Turkish channels, for the Süper Lig, Turkish clubs in Europe, the Türkiye national team,
and the main British, European and world competitions.</p>
<h2>How the listings are made</h2>
<ul>
<li>Every match is added only after it appears on a <b>broadcaster's, league's or governing body's own page</b> (for example Sky Sports, TNT Sports,
UEFA, the Premier League, LALIGA or the Turkish Football Federation). Each row links to its source.</li>
<li>New TV picks are added every Friday, Süper Lig results on the morning after each match day, and past days drop off every night.</li>
<li>Kick-off times and channels can change at short notice, so always check with the broadcaster before the match.</li>
</ul>
<h2>Independent</h2>
<p>Maç Saati is not connected to any broadcaster, league or club and is not paid to list anything. It does not show or link to illegal streams.</p>
<h2>Hakkımızda</h2>
<p>Maç Saati, İngiltere'de yaşayan Türk futbolseverler için hazırlanmış ücretsiz ve bağımsız bir maç yayın rehberidir. Her maçı İngiltere saati ve Türkiye saati
(TSİ) ile, İngiliz ve Türk yayıncılarıyla birlikte gösterir. Maçlar yalnızca yayıncının, ligin veya federasyonun kendi sayfasında yer aldıktan sonra eklenir.</p>
<p>Questions, corrections or ideas? <a href="/contact/">Get in touch</a>.</p>
</article>
"""

CONTACT_BODY = f"""
<article class="prose">
<p class="lead">Spotted a wrong time or channel, or want your club's next match added? Email us:</p>
<p class="mail"><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
<ul>
<li><b>Corrections:</b> tell us the match and, if you can, a link to the broadcaster's or league's page. We fix confirmed errors as soon as we can.</li>
<li><b>Business and sponsorship:</b> Turkish businesses in the UK that would like to support the site are welcome to get in touch.</li>
<li><b>Press:</b> happy to help with questions about watching Turkish football in the UK.</li>
</ul>
<h2>İletişim</h2>
<p>Yanlış bir saat veya kanal mı gördünüz, ya da takımınızın maçının eklenmesini mi istiyorsunuz? Bize yazın:
<a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>. Mümkünse yayıncının veya ligin sayfasının bağlantısını da ekleyin.</p>
</article>
"""

PRIVACY_BODY = f"""
<article class="prose">
<p class="lead">Short version: Maç Saati has no accounts, no adverts and no analytics, and does not set cookies.</p>
<h2>What is stored on your device</h2>
<p>The site remembers two settings in your browser's local storage so they stay the same next time you visit: whether you chose <b>UK time</b> or <b>TSİ</b>,
and which competition groups you <b>collapsed</b>. These never leave your device, and you can clear them at any time by clearing your browser's site data.</p>
<h2>Services the site uses</h2>
<ul>
<li><b>GitHub Pages</b> hosts the site. Like any web host, GitHub receives your IP address when your browser requests a page and may keep it in server logs
for security purposes. See <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener nofollow">GitHub's privacy statement</a>.</li>
<li><b>Google Fonts</b> provides the typefaces. Your browser downloads them from Google, which receives your IP address. See
<a href="https://policies.google.com/privacy" target="_blank" rel="noopener nofollow">Google's privacy policy</a>.</li>
</ul>
<h2>Email</h2>
<p>If you email {CONTACT_EMAIL}, we use your email address and message only to reply and keep a record of corrections, and we don't share them.</p>
<h2>Links to other sites</h2>
<p>Channel names and sources link to broadcasters' and leagues' own websites, which have their own privacy policies.</p>
<h2>Your rights</h2>
<p>Under UK data protection law you can ask what personal data we hold about you and ask us to delete it. Email {CONTACT_EMAIL}.
You can also complain to the Information Commissioner's Office (ico.org.uk).</p>
<h2>Changes</h2>
<p>If the site ever adds analytics or advertising, this page will be updated first, and you will be asked for consent where the law requires it.</p>
<p class="small">Last updated: November 2026.</p>
</article>
"""
