"""Small inline SVG flags (simple, public national flags only). 3:2 viewBox 30x20."""
def _h(*cols):  # horizontal stripes
    n=len(cols); h=20/n
    return "".join(f'<rect y="{i*h:.3f}" width="30" height="{h+0.05:.3f}" fill="{c}"/>' for i,c in enumerate(cols))
def _v(*cols):  # vertical stripes
    n=len(cols); w=30/n
    return "".join(f'<rect x="{i*w:.3f}" width="{w+0.05:.3f}" height="20" fill="{c}"/>' for i,c in enumerate(cols))
def _nordic(bg, cross, inner=None):
    s=f'<rect width="30" height="20" fill="{bg}"/><rect x="8" width="5" height="20" fill="{cross}"/><rect y="7.5" width="30" height="5" fill="{cross}"/>'
    if inner: s+=f'<rect x="9.25" width="2.5" height="20" fill="{inner}"/><rect y="8.75" width="30" height="2.5" fill="{inner}"/>'
    return s
TR = ('<rect width="30" height="20" fill="#E30A17"/><circle cx="11" cy="10" r="5" fill="#fff"/><circle cx="12.25" cy="10" r="4" fill="#E30A17"/>'
      '<polygon fill="#fff" points="16.2,10 19.9,8.8 17.6,11.9 17.6,8.1 19.9,11.2"/>')
F = {
 "TR": TR,
 "ENG": '<rect width="30" height="20" fill="#fff"/><rect x="13" width="4" height="20" fill="#CE1124"/><rect y="8" width="30" height="4" fill="#CE1124"/>',
 "SCO": '<rect width="30" height="20" fill="#005EB8"/><path d="M0,0 30,20 M30,0 0,20" stroke="#fff" stroke-width="3.2"/>',
 "ES": _h("#AA151B","#F1BF00","#F1BF00","#AA151B"),
 "IT": _v("#009246","#fff","#CE2B37"),
 "DE": _h("#000","#DD0000","#FFCE00"),
 "FR": _v("#0055A4","#fff","#EF4135"),
 "NL": _h("#AE1C28","#fff","#21468B"),
 "BE": _v("#000","#FAE042","#ED2939"),
 "AT": _h("#ED2939","#fff","#ED2939"),
 "IE": _v("#169B62","#fff","#FF883E"),
 "PL": _h("#fff","#DC143C"),
 "RO": _v("#002B7F","#FCD116","#CE1126"),
 "HU": _h("#CE2939","#fff","#477050"),
 "UA": _h("#0057B7","#FFD700"),
 "EE": _h("#0072CE","#000","#fff"),
 "LV": _h("#9E3039","#9E3039","#fff","#9E3039","#9E3039"),
 "AM": _h("#D90012","#0033A0","#F2A800"),
 "BG": _h("#fff","#00966E","#D62612"),
 "LU": _h("#ED2939","#fff","#00A1DE"),
 "CZ": '<rect width="30" height="10" fill="#fff"/><rect y="10" width="30" height="10" fill="#D7141A"/><polygon points="0,0 15,10 0,20" fill="#11457E"/>',
 "CH": '<rect width="30" height="20" fill="#D52B1E"/><rect x="13" y="4" width="4" height="12" fill="#fff"/><rect x="9" y="8" width="12" height="4" fill="#fff"/>',
 "SE": _nordic("#006AA7","#FECC00"),
 "DK": _nordic("#C8102E","#fff"),
 "FI": _nordic("#fff","#002F6C"),
 "NO": _nordic("#BA0C2F","#fff","#00205B"),
 "IS": _nordic("#02529C","#fff","#DC1E35"),
 "US": _h(*["#B22234","#fff"]*3+["#B22234"]) + '<rect width="13" height="10.8" fill="#3C3B6E"/>',
}
COMP_FLAG = {"Süper Lig":"TR","Premier League":"ENG","Championship":"ENG","League One":"ENG","League Two":"ENG","FA Cup":"ENG","EFL Trophy":"ENG",
             "Scottish Premiership":"SCO","Scottish Championship":"SCO","La Liga":"ES","La Liga 2":"ES","Serie A":"IT","Bundesliga":"DE","Ligue 1":"FR","MLS":"US"}
TEAM_FLAG = {"Türkiye":"TR","England":"ENG","Scotland":"SCO","Spain":"ES","Italy":"IT","Germany":"DE","France":"FR","Netherlands":"NL","Belgium":"BE",
             "Austria":"AT","Republic of Ireland":"IE","Poland":"PL","Romania":"RO","Hungary":"HU","Ukraine":"UA","Estonia":"EE","Latvia":"LV","Armenia":"AM",
             "Bulgaria":"BG","Luxembourg":"LU","Czechia":"CZ","Switzerland":"CH","Sweden":"SE","Denmark":"DK","Finland":"FI","Norway":"NO","Iceland":"IS",
             "Albania":"AL","Andorra":"AD","Azerbaijan":"AZ","Belarus":"BY","Bosnia and Herzegovina":"BA","Croatia":"HR","Cyprus":"CY",
             "Faroe Islands":"FO","Georgia":"GE","Gibraltar":"GI","Greece":"GR","Israel":"IL","Kazakhstan":"KZ","Kosovo":"XK",
             "Liechtenstein":"LI","Moldova":"MD","Montenegro":"ME","North Macedonia":"MK","Northern Ireland":"NIR","Portugal":"PT",
             "San Marino":"SM","Serbia":"RS","Slovakia":"SK","Slovenia":"SI","Wales":"WLS"}
FILE = {"ENG":"gb-eng","SCO":"gb-sct","NIR":"gb-nir","WLS":"gb-wls"}
def flag_file(code): return FILE.get(code, code.lower())
def flag(code, title=""):
    t = title or code
    return f'<img class="flag" src="/flags/{flag_file(code)}.svg" width="16" height="12" alt="" title="{t}" loading="lazy">'
