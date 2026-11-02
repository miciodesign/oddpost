#!/usr/bin/env python3
"""Oddpost — generatore statico.

Legge gli articoli in content/, applica i template in templates/
e scrive il sito pronto in public/.

Uso:  python3 build.py
"""
from __future__ import annotations

import datetime as dt
import html
import re
import shutil
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "public"

SITE = {
    "name": "Oddpost",
    "url": "https://oddpost.it",
    "tagline": "Strano ma vero. Ogni giorno.",
    "description": "Oddpost racconta ogni giorno il lato più strano del mondo reale: "
    "fatti bizzarri, record assurdi e scoperte curiose, tutti con la fonte.",
    "email": "redazione@oddpost.it",
    "lang": "it",
}

RUBRICHE = {
    "storie": {
        "slug": "storie",
        "name": "Storie strane ma vere",
        "short": "Storie",
        "description": "Fatti bizzarri, record assurdi e scoperte curiose, raccontati con la fonte.",
    },
    "oggetti": {
        "slug": "oggetti",
        "name": "Oggetti assurdi che esistono davvero",
        "short": "Oggetti",
        "description": "Gadget, invenzioni e prodotti improbabili che qualcuno vende sul serio.",
    },
}

TEMI = {
    "animali": {"slug": "animali", "name": "Animali", "description": "Bestie che scappano, record a quattro zampe, specie che nessuno aveva mai visto."},
    "scienza": {"slug": "scienza", "name": "Scienza strana", "description": "Scoperte, studi e fenomeni che sembrano inventati e invece sono pubblicati."},
    "record": {"slug": "record", "name": "Record assurdi", "description": "Primati mondiali a cui nessuno aveva pensato, certificati e tutto."},
    "mondo": {"slug": "mondo", "name": "Storie dal mondo", "description": "Fatti bizzarri successi davvero, da qualche parte, a qualcuno."},
    "oggetti": {"slug": "oggetti", "name": "Oggetti assurdi", "description": "Cose che qualcuno ha inventato, prodotto e messo in vendita sul serio."},
}

MESI = [
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
]


# ---------- front matter --------------------------------------------------

def parse_front_matter(text: str) -> tuple[dict, str]:
    """Front matter minimale `chiave: valore` tra due righe `---`."""
    if not text.startswith("---"):
        return {}, text
    _, fm, body = text.split("---", 2)
    meta: dict = {}
    for line in fm.strip().splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value[:1] in "\"'" and value[-1:] == value[:1]:
            value = value[1:-1]
        meta[key.strip()] = value
    return meta, body.lstrip("\n")


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[àáâä]", "a", s)
    s = re.sub(r"[èéêë]", "e", s)
    s = re.sub(r"[ìíîï]", "i", s)
    s = re.sub(r"[òóôö]", "o", s)
    s = re.sub(r"[ùúûü]", "u", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def data_italiana(d: dt.date) -> str:
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


# ---------- caricamento ----------------------------------------------------

md = markdown.Markdown(extensions=["extra", "smarty"], output_format="html5")


def load_articles() -> list[dict]:
    articles = []
    for rubrica in RUBRICHE:
        for path in sorted((CONTENT / rubrica).glob("*.md")):
            meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
            if meta.get("draft", "").lower() in ("true", "1", "yes", "sì", "si"):
                continue
            md.reset()
            content_html = md.convert(body)
            date = dt.date.fromisoformat(meta["date"])
            slug = meta.get("slug") or slugify(meta["title"])
            tema = meta.get("tema", "oggetti" if rubrica == "oggetti" else "mondo").strip().lower()
            if tema not in TEMI:
                tema = "mondo"
            in_breve = {k: meta[f"in_breve_{k}"] for k in ("dove", "cosa", "perche") if meta.get(f"in_breve_{k}")}
            art = {
                **meta,
                "rubrica": RUBRICHE[rubrica],
                "tema": TEMI[tema],
                "in_breve": in_breve,
                "seo_title": meta.get("seo_title") or meta["title"],
                "meta_description": meta.get("meta_description") or meta.get("summary", ""),
                "date": date,
                "date_it": data_italiana(date),
                "date_iso": date.isoformat(),
                "slug": slug,
                "url": f"/{rubrica}/{slug}/",
                "content": content_html,
                "reading_minutes": max(1, round(len(body.split()) / 200)),
            }
            articles.append(art)
    articles.sort(key=lambda a: (a["date"], a["title"]), reverse=True)
    return articles


def load_pages() -> list[dict]:
    pages = []
    for path in sorted((CONTENT / "pagine").glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        md.reset()
        slug = meta.get("slug") or path.stem
        pages.append({**meta, "slug": slug, "url": f"/{slug}/", "content": md.convert(body)})
    return pages


# ---------- scrittura ------------------------------------------------------

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(STATIC, OUT / "static")
    # File che devono stare nella radice del sito (verifiche Google, ecc.)
    for f in (ROOT / "root").glob("*"):
        if f.is_file():
            shutil.copy(f, OUT / f.name)

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals.update(site=SITE, rubriche=RUBRICHE, temi=TEMI, now=dt.date.today())

    articles = load_articles()
    pages = load_pages()
    by_rubrica = {k: [a for a in articles if a["rubrica"]["slug"] == k] for k in RUBRICHE}
    by_tema = {k: [a for a in articles if a["tema"]["slug"] == k] for k in TEMI}
    nav_pages = [p for p in pages if p.get("nav", "").lower() == "true"]
    env.globals["nav_pages"] = nav_pages

    # Home
    write(OUT / "index.html", env.get_template("home.html").render(
        articles=articles, by_rubrica=by_rubrica, title=None))

    # Rubriche
    for slug, rub in RUBRICHE.items():
        write(OUT / slug / "index.html", env.get_template("rubrica.html").render(
            rubrica=rub, articles=by_rubrica[slug], title=rub["name"]))

    # Temi
    for slug, tema in TEMI.items():
        write(OUT / "tema" / slug / "index.html", env.get_template("tema.html").render(
            tema=tema, articles=by_tema[slug], title=tema["name"]))

    # Articoli
    tpl = env.get_template("articolo.html")
    for i, art in enumerate(articles):
        same_tema = [a for a in by_tema[art["tema"]["slug"]] if a is not art]
        # Correlate: prima dello stesso tema, poi le più recenti di altri temi
        related = same_tema[:3]
        if len(related) < 3:
            related += [a for a in articles if a is not art and a not in related][: 3 - len(related)]
        write(OUT / art["url"].strip("/") / "index.html",
              tpl.render(article=art, related=related, title=art["seo_title"]))

    # Pagine fisse
    tpl = env.get_template("pagina.html")
    for page in pages:
        write(OUT / page["slug"] / "index.html", tpl.render(page=page, title=page["title"]))

    # 404
    write(OUT / "404.html", env.get_template("404.html").render(title="Pagina non trovata"))

    # Feed RSS
    write(OUT / "feed.xml", env.get_template("feed.xml").render(articles=articles[:30]))

    # Sitemap + robots
    urls = ["/"] + [f"/{s}/" for s in RUBRICHE] + [f"/tema/{s}/" for s in TEMI] + [a["url"] for a in articles] + [p["url"] for p in pages]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{html.escape(SITE['url'] + u)}</loc></url>" for u in urls]
    sitemap.append("</urlset>")
    write(OUT / "sitemap.xml", "\n".join(sitemap))
    write(OUT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")

    print(f"Sito generato: {len(articles)} articoli, {len(pages)} pagine → {OUT}")


if __name__ == "__main__":
    build()
