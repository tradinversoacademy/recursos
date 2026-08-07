"""Escribe en index.html las tarjetas de la biblioteca a partir del catálogo.

assets/js/resources.js sigue siendo la única fuente de verdad: al añadir un
recurso allí, se ejecuta este script y las tarjetas quedan en el HTML. Así la
biblioteca es indexable por Google y visible sin JavaScript, sin renunciar a
editar los recursos en un solo sitio.

    python tools/build_library.py
"""

import json
import re
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "assets" / "js" / "resources.js"
INDEX = ROOT / "index.html"

START = "<!-- resource-list:start -->"
END = "<!-- resource-list:end -->"


def load_catalog():
    source = CATALOG.read_text(encoding="utf-8")
    match = re.search(r"window\.TRADINVERSO_RESOURCES\s*=\s*(\[.*?\]);", source, re.S)
    if not match:
        raise SystemExit("No se encuentra window.TRADINVERSO_RESOURCES en resources.js")

    body = match.group(1)
    # El catálogo declara una propiedad por línea, así que basta con entrecomillar
    # la clave inicial de cada línea: los dos puntos dentro de los textos no se tocan.
    lines = [re.sub(r'^(\s*)(\w+):', r'\1"\2":', line) for line in body.splitlines()]
    body = re.sub(r",(\s*[}\]])", r"\1", "\n".join(lines))
    return json.loads(body)


def render_card(resource):
    return f"""          <article class="resource-list-card" data-resource-card data-category="{escape(resource['category'])}" data-search="{escape(resource['search'])}">
            <div class="resource-list-top"><span class="resource-symbol">{escape(resource['symbol'])}</span><span class="resource-list-type">{escape(resource['type'])}</span></div>
            <h3>{escape(resource['title'])}</h3>
            <p>{escape(resource['description'])}</p>
            <a href="recursos/{escape(resource['slug'])}/index.html">{escape(resource['cta'])} <span aria-hidden="true">&rarr;</span></a>
          </article>"""


def main():
    # Los destacados ya tienen su tarjeta propia arriba y los ocultos no se listan.
    resources = [
        item for item in load_catalog()
        if not item.get("hidden") and not item.get("featured")
    ]
    cards = "\n\n".join(render_card(item) for item in resources)
    html = INDEX.read_text(encoding="utf-8")

    if START not in html or END not in html:
        raise SystemExit(f"Faltan los marcadores {START} / {END} en index.html")

    html = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        f"{START}\n{cards}\n          {END}",
        html,
        flags=re.S,
    )

    # El contador incluye las tarjetas destacadas, que son estáticas.
    featured = html.count('class="library-card library-card-featured"')
    total = len(resources) + featured
    html = re.sub(r"(<strong data-total-count>)\d+(</strong>)", rf"\g<1>{total}\g<2>", html)
    html = re.sub(
        r'(<span class="library-visible-count" data-visible-count>)\d+ recursos(</span>)',
        rf"\g<1>{total} recursos\g<2>",
        html,
    )

    INDEX.write_text(html, encoding="utf-8", newline="\n")
    print(f"{len(resources)} tarjetas escritas + {featured} destacadas = {total} recursos")


if __name__ == "__main__":
    main()
