# -*- coding: utf-8 -*-
"""Releve chaque morceau de texte traduisible avec sa position exacte dans le
   fichier. On travaille par positions et jamais par rechercher-remplacer :
   ainsi un mot comme << Contact >> ne peut pas etre remplace dans une URL."""
import io, json, re, os, sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source")
OUT = os.path.dirname(os.path.abspath(__file__))

# zones a ne jamais toucher
SKIP_TAGS = ("script", "style", "svg")

def zones(h):
    """intervalles a ignorer : scripts, styles, svg"""
    z = []
    for t in SKIP_TAGS:
        for m in re.finditer(r'<%s\b' % t, h):
            e = h.find("</%s>" % t, m.end())
            if e < 0: e = len(h)
            z.append((m.start(), e + len(t) + 3))
    return z

def inside(z, a, b):
    return any(s <= a and b <= e for s, e in z)

ATTRS = ("placeholder", "aria-label", "title", "alt", "content", "value")

def grab(path):
    h = io.open(path, encoding="utf-8").read()
    z = zones(h)
    items = []
    # 1. noeuds de texte
    for m in re.finditer(r'>([^<>]+)<', h):
        a, b = m.start(1), m.end(1)
        raw = m.group(1)
        if inside(z, a, b): continue
        if not raw.strip(): continue
        if not re.search(r'[A-Za-zÀ-ÿ]', raw): continue
        items.append({"a": a, "b": b, "kind": "text", "nl": raw})
    # 2. attributs. Pour content, seules la description et les balises Open Graph
    #    sont du texte : viewport et og:type sont des reglages techniques.
    for m in re.finditer(r'\b(%s)="([^"]*)"' % "|".join(ATTRS), h):
        a, b = m.start(2), m.end(2)
        val = m.group(2)
        if inside(z, a, b): continue
        if not re.search(r'[A-Za-zÀ-ÿ]', val): continue
        if len(val) < 3: continue
        if m.group(1) == "content":
            tag = h.rfind("<", 0, m.start())
            head = h[tag:m.start()]
            if not re.search(r'(name="description"|property="og:(title|description)")', head):
                continue
        items.append({"a": a, "b": b, "kind": "attr:" + m.group(1), "nl": val})
    # 3. le titre
    for m in re.finditer(r'<title>([^<]+)</title>', h):
        items.append({"a": m.start(1), "b": m.end(1), "kind": "title", "nl": m.group(1)})
    items.sort(key=lambda x: x["a"])
    # on retire les doublons de position
    clean, last = [], -1
    for it in items:
        if it["a"] >= last:
            clean.append(it); last = it["b"]
    return h, clean

cat = {}
for f in ["index.html", "zakelijk.html"]:
    h, items = grab(os.path.join(SRC, f))
    cat[f] = items
    print("%-15s %4d fragments" % (f, len(items)))

json.dump(cat, io.open(os.path.join(OUT, "catalogue_nl.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# apercu des valeurs uniques, pour la traduction
vals = []
for f in cat:
    for it in cat[f]:
        v = re.sub(r"\s+", " ", it["nl"]).strip()
        if v not in vals: vals.append(v)
io.open(os.path.join(OUT, "a_traduire.txt"), "w", encoding="utf-8").write("\n".join(vals))
print("valeurs uniques a traduire :", len(vals))
