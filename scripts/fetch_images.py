#!/usr/bin/env python3
"""Scarica da Pixabay una foto per ogni articolo che ha `image_query:` nel front matter
e non ha ancora il file corrispondente in static/img/articoli/.

Pensato per girare in CI (GitHub Actions ha accesso a internet pieno).
Scrive anche static/img/articoli/credits.json con l'attribuzione del fotografo,
che build.py legge per mostrare il credito sotto ogni immagine.

Uso:
  PIXABAY_API_KEY=xxxx python3 scripts/fetch_images.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"
IMG_DIR = ROOT / "static" / "img" / "articoli"
CREDITS_FILE = IMG_DIR / "credits.json"

API_KEY = os.environ.get("PIXABAY_API_KEY", "").strip()


def parse_front_matter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    _, fm, _ = text.split("---", 2)
    meta: dict = {}
    for line in fm.strip().splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value[:1] in "\"'" and value[-1:] == value[:1]:
            value = value[1:-1]
        meta[key.strip()] = value
    return meta


def pixabay_search(query: str) -> dict | None:
    params = {
        "key": API_KEY,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "per_page": 5,
        "min_width": 640,
    }
    url = "https://pixabay.com/api/?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    hits = data.get("hits", [])
    return hits[0] if hits else None


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Oddpost/1.0 (+https://oddpost.it)"})
    with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
        f.write(r.read())


def main() -> None:
    if not API_KEY:
        sys.exit("Manca PIXABAY_API_KEY nell'ambiente.")

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    credits = json.loads(CREDITS_FILE.read_text()) if CREDITS_FILE.exists() else {}

    done, skipped, no_query, failed = 0, 0, 0, 0

    for rubrica in ("storie", "oggetti"):
        for path in sorted((CONTENT / rubrica).glob("*.md")):
            meta = parse_front_matter(path.read_text(encoding="utf-8"))
            slug = meta.get("slug") or path.stem
            dest = IMG_DIR / f"{slug}.jpg"

            if dest.exists():
                skipped += 1
                continue

            query = meta.get("image_query")
            if not query:
                no_query += 1
                continue

            try:
                hit = pixabay_search(query)
                if not hit:
                    print(f"[nessun risultato] {slug} ({query})")
                    failed += 1
                    continue
                download(hit["largeImageURL"], dest)
                credits[slug] = {
                    "credit": f"Foto di {hit['user']} su Pixabay",
                    "credit_url": f"https://pixabay.com/users/{hit['user']}-{hit['user_id']}/",
                }
                print(f"[ok] {slug} <- {query}")
                done += 1
                time.sleep(0.4)
            except Exception as e:
                print(f"[errore] {slug}: {e}")
                failed += 1

    CREDITS_FILE.write_text(json.dumps(credits, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nScaricate: {done}  Già presenti: {skipped}  Senza image_query: {no_query}  Fallite: {failed}")


if __name__ == "__main__":
    main()
