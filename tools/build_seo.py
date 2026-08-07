"""Genera sitemap.xml y robots.txt, y añade el canonical a cada página.

El canonical de las páginas `recurso.html` apunta a su `index.html`: son
desarrollos del mismo recurso y no deben competir en Google con la landing.

    python tools/build_seo.py
"""

import re
from datetime import date
from pathlib import Path

from build_library import load_catalog


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://tradinversoacademy.github.io/recursos/"


def canonical_for(path):
    """URL canónica de una página del sitio."""
    if path.name == "index.html" and path.parent == ROOT:
        return BASE
    if path.name == "recurso.html":
        # El desarrollo largo consolida en la landing del recurso.
        return f"{BASE}recursos/{path.parent.name}/"
    return f"{BASE}recursos/{path.parent.name}/"


def apply_canonical(path):
    html = path.read_text(encoding="utf-8")
    link = f'    <link rel="canonical" href="{canonical_for(path)}">\n'

    if 'rel="canonical"' in html:
        html = re.sub(r'[ \t]*<link rel="canonical"[^>]*>\n', link, html)
    else:
        html = html.replace('    <link rel="icon"', link + '    <link rel="icon"', 1)

    path.write_text(html, encoding="utf-8", newline="\n")


def build_sitemap(pages):
    today = date.today().isoformat()
    urls = []
    for url in pages:
        priority = "1.0" if url == BASE else "0.8"
        urls.append(
            "  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def main():
    catalog = load_catalog()
    # Los recursos ocultos existen pero no se anuncian en el sitemap.
    public = {item["slug"] for item in catalog if not item.get("hidden")}

    pages = [ROOT / "index.html"] + sorted(ROOT.glob("recursos/*/*.html"))
    for page in pages:
        apply_canonical(page)

    urls = [BASE]
    for slug in sorted(public):
        if (ROOT / "recursos" / slug / "index.html").exists():
            urls.append(f"{BASE}recursos/{slug}/")

    (ROOT / "sitemap.xml").write_text(build_sitemap(urls), encoding="utf-8", newline="\n")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n"
        f"\nSitemap: {BASE}sitemap.xml\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"canonical en {len(pages)} páginas · sitemap con {len(urls)} URLs · robots.txt")


if __name__ == "__main__":
    main()
