# -*- coding: utf-8 -*-
"""Genere les versions francaise et anglaise du site a partir du neerlandais.
   Les textes sont remplaces a leur position exacte, jamais par un
   rechercher-remplacer global, pour ne pas abimer le code ni les adresses."""
import io, json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tr_js import J

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "source")
OUTD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT  = json.load(io.open(os.path.join(HERE, "catalogue_nl.json"), encoding="utf-8"))
TR   = json.load(io.open(os.path.join(HERE, "translations.json"), encoding="utf-8"))
SITE = "https://taxisoesi.com"

LANGS = {"nl": {"code": "nl-BE", "nom": "Nederlands"},
         "fr": {"code": "fr-BE", "nom": "Français"},
         "en": {"code": "en",    "nom": "English"}}
ORDER = ["nl", "fr", "en"]
PAGES = ["index.html", "zakelijk.html"]

CSS = """
  /* bandeau de langue, au-dessus de la barre de navigation */
  .langbar{background:var(--surface-2); border-bottom:1px solid var(--line)}
  .langbar .wrap{display:flex; align-items:center; justify-content:flex-end; gap:10px;
        min-height:34px; padding-block:2px}
  .langbar__lab{font-size:12px; color:var(--muted); letter-spacing:.03em}
  .lang{display:inline-flex; align-items:center; gap:1px}
  .lang a{display:inline-flex; align-items:center; justify-content:center; min-width:38px;
        min-height:30px; padding:0 8px; border-radius:999px; font-size:12.5px; font-weight:500;
        letter-spacing:.05em; color:var(--muted); text-decoration:none; line-height:1}
  .lang a:hover{color:var(--ink); background:var(--surface)}
  .lang a[aria-current="true"]{background:var(--gold-soft); color:var(--gold); font-weight:600}
  @media (max-width:430px){ .langbar__lab{display:none} .lang a{min-width:44px} }
"""

def page_urls(page):
    """adresse de chaque version d'une meme page"""
    u = {}
    for lg in ORDER:
        base = SITE + ("/" if lg == "nl" else "/%s/" % lg)
        u[lg] = base if page == "index.html" else base + page
    return u

def switcher(page, cur, place):
    u = page_urls(page)
    links = "".join(
        '<a href="%s" hreflang="%s"%s>%s</a>' % (
            u[lg].replace(SITE, "") or "/", LANGS[lg]["code"],
            ' aria-current="true"' if lg == cur else "", lg.upper())
        for lg in ORDER)
    return links

def alternates(page, cur):
    u = page_urls(page)
    out = ['<link rel="canonical" href="%s">' % u[cur]]
    for lg in ORDER:
        out.append('<link rel="alternate" hreflang="%s" href="%s">' % (LANGS[lg]["code"], u[lg]))
    out.append('<link rel="alternate" hreflang="x-default" href="%s">' % u["nl"])
    return "\n".join(out)

def traduire_html(h, items, lang):
    """remplace chaque fragment a sa position, de la fin vers le debut"""
    manquants = []
    for it in sorted(items, key=lambda x: -x["a"]):
        nl = it["nl"]
        cle = re.sub(r"\s+", " ", nl).strip()
        t = TR.get(cle)
        if not t:
            manquants.append(cle); continue
        val = t[lang]
        # on garde l'espacement d'origine autour du texte
        g = re.match(r"^(\s*).*?(\s*)$", nl, re.S)
        val = g.group(1) + val + g.group(2)
        h = h[:it["a"]] + val + h[it["b"]:]
    return h, manquants

def traduire_js(h, lang):
    """les messages fabriques par le script, remplaces guillemets compris"""
    n = 0
    for nl, t in J.items():
        # fragments de code : on remplace tels quels, sans guillemets autour
        if nl.startswith(("n.toLocaleString", "return ", "maximumFractionDigits", " \u00d7 ")):
            if nl in h: h = h.replace(nl, t[lang]); n += 1
            continue
        a, b = '"%s"' % nl, '"%s"' % t[lang]
        if a in h:
            h = h.replace(a, b); n += 1
    return h, n

def construire(lang):
    """le neerlandais reste a la racine, les autres langues dans leur dossier"""
    dst = OUTD if lang == "nl" else os.path.join(OUTD, lang)
    if lang != "nl":
        if os.path.isdir(dst): shutil.rmtree(dst)
        os.makedirs(dst)
    total_manquants = []
    for page in PAGES:
        h = io.open(os.path.join(SRC, page), encoding="utf-8").read()
        if lang == "nl":
            manquants, njs = [], 0          # la source est deja en neerlandais
        else:
            h, manquants = traduire_html(h, CAT[page], lang)
            h, njs = traduire_js(h, lang)
        total_manquants += manquants
        # langue du document
        h = re.sub(r'<html lang="[^"]*"', '<html lang="%s"' % LANGS[lang]["code"], h, 1)
        # la liste des rues est partagee, elle reste a la racine
        if lang != "nl":
            h = h.replace('src="streets.js"', 'src="../streets.js"')
        # adresses des autres versions
        h = h.replace("</head>", alternates(page, lang) + "\n</head>", 1)
        # bandeau de langue, juste avant l'en-tete, pour ne pas comprimer le menu
        etiquette = {"nl": "Taal", "fr": "Langue", "en": "Language"}[lang]
        bande = ('<div class="langbar"><div class="wrap">'
                 '<span class="langbar__lab">%s</span>'
                 '<div class="lang" role="group" aria-label="Nederlands / Français / English">%s</div>'
                 '</div></div>' % (etiquette, switcher(page, lang, "bar")))
        h = re.sub(r'(<header class="topbar">)', lambda m: bande + m.group(1), h, 1)
        # style du selecteur
        h = h.replace("</style>", CSS + "</style>", 1)
        io.open(os.path.join(dst, page), "w", encoding="utf-8").write(h)
        print("  %s/%-14s %7d octets, %2d messages du script" % (lang, page, len(h), njs))
    if total_manquants:
        print("  ATTENTION, non traduits :", set(total_manquants))
    return total_manquants

def _inutilise():
    """la version neerlandaise recoit le meme selecteur et les memes liens"""
    for page in PAGES:
        p = os.path.join(SRC, page)
        h = io.open(p, encoding="utf-8").read()
        if 'class="lang"' in h: continue
        h = h.replace("</head>", alternates(page, "nl") + "\n</head>", 1)
        h = re.sub(r'(</nav>)', r'\1' + switcher(page, "nl"), h, 1)
        h = h.replace("</style>", CSS + "</style>", 1)
        io.open(p, "w", encoding="utf-8").write(h)
        print("  nl/%-14s %7d octets" % (page, len(h)))

if __name__ == "__main__":
    rate = 0
    for lg in ORDER:
        print("version %s :" % lg)
        rate += len(construire(lg))
    print("termine." if not rate else "%d fragments sans traduction" % rate)
