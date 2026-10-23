"""Génère le site statique dans docs/ à partir de content.json.

Usage : python3 build.py
Aucune dépendance : seul Python 3 est nécessaire.
"""
import json, re, shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
DOMAIN = "www.space-junk.net"

data = json.loads((ROOT / "content.json").read_text())
site = data["site"]
tags = data["tags"]
projects = [p for p in data["projects"] if not p.get("hidden")]
current = [p for p in projects if not p.get("archived")]
archived = [p for p in projects if p.get("archived")]


def page(title, body, desc=None, cls=""):
    full_title = f"{escape(title)} · {escape(site['title'])}" if title else escape(site["title"])
    nav = ['<a href="/about-me/">À propos</a>']
    if archived:
        nav.append('<a href="/archives/">Archives</a>')
    if site.get("email"):
        nav.append(f'<a href="mailto:{escape(site["email"])}">Contact</a>')
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{escape(desc or site['description'])}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Azeret+Mono:wght@400&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
</head>
<body class="{cls}">
<header class="site-header wrap">
  <a class="site-title" href="/">{escape(site['title'])}</a>
  <nav>{''.join(nav)}</nav>
</header>
<main>
{body}
</main>
<footer class="site-footer wrap">© {escape(site['author'])}</footer>
<script src="/site.js" defer></script>
</body>
</html>
"""


def write(path, html):
    f = OUT / path / "index.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html)


def grid(items):
    cards = []
    for p in items:
        cards.append(f"""<a class="card" href="/{p['slug']}/">
  <img src="/{p['thumb']}" width="600" height="600" alt="" loading="lazy">
  <h2>{escape(p['title'])}</h2>
</a>""")
    return f'<div class="grid">{"".join(cards)}</div>'


def tag_nav(active=None):
    links = [f'<a href="/"{" class=active" if active is None else ""}>Tout</a>']
    for key, label in tags.items():
        cls = " class=active" if key == active else ""
        links.append(f'<a href="/tag/{key}/"{cls}>{escape(label)}</a>')
    return f'<nav class="tags">{"".join(links)}</nav>'


def asset_html(a):
    if a["type"] == "image":
        return (f'<a class="zoom" href="/{a["src"]}"><img src="/{a["src"]}" '
                f'width="{a["w"]}" height="{a["h"]}" alt="" loading="lazy"></a>')
    if a["type"] == "vimeo":
        return (f'<div class="video"><iframe src="https://player.vimeo.com/video/{a["id"]}?dnt=1" '
                f'allow="fullscreen; picture-in-picture" allowfullscreen loading="lazy" title="Vidéo"></iframe></div>')
    if a["type"] == "youtube":
        return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{a["id"]}" '
                f'allow="fullscreen; picture-in-picture" allowfullscreen loading="lazy" title="Vidéo"></iframe></div>')
    if a["type"] == "text":
        return f'<div class="text">{a["html"]}</div>'
    raise ValueError(f"type d'élément inconnu : {a['type']}")


def plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def project_page(p, siblings):
    meta = []
    for key, label in [("date", "Année"), ("client", "Client"), ("role", "Rôle")]:
        if p.get(key):
            meta.append(f"<dt>{label}</dt><dd>{escape(p[key])}</dd>")
    if p.get("url"):
        shown = re.sub(r"^https?://(www\.)?", "", p["url"]).rstrip("/")
        meta.append(f'<dt>Lien</dt><dd><a href="{escape(p["url"])}" target="_blank" rel="noopener">{escape(shown)}</a></dd>')
    if p.get("tags"):
        links = ", ".join(f'<a href="/tag/{t}/">{escape(tags.get(t, t))}</a>' for t in p["tags"])
        meta.append(f"<dt>Tags</dt><dd>{links}</dd>")

    i = siblings.index(p)
    prev_p, next_p = siblings[i - 1], siblings[(i + 1) % len(siblings)]
    body = f"""<article class="project wrap">
  <div class="assets">{''.join(asset_html(a) for a in p['assets'])}</div>
  <aside class="info">
    <h1>{escape(p['title'])}</h1>
    <div class="description">{p.get('description', '')}</div>
    <dl class="meta">{''.join(meta)}</dl>
  </aside>
</article>
<nav class="pager wrap">
  <a href="/{prev_p['slug']}/">← {escape(prev_p['title'])}</a>
  <a href="/{next_p['slug']}/">{escape(next_p['title'])} →</a>
</nav>"""
    desc = plain(p.get("description", ""))[:160] or None
    return page(p["title"], body, desc, "is-project")


def main():
    if OUT.exists():
        for f in OUT.iterdir():
            if f.name not in ("img", "CNAME"):
                shutil.rmtree(f) if f.is_dir() else f.unlink()
    OUT.mkdir(exist_ok=True)
    for f in (ROOT / "static").iterdir():
        shutil.copy(f, OUT / f.name)
    (OUT / "CNAME").write_text(DOMAIN + "\n")
    (OUT / ".nojekyll").write_text("")

    write("", page(None, f'<div class="wrap">{tag_nav()}{grid(current)}</div>'))
    for key, label in tags.items():
        items = [p for p in current if key in p.get("tags", [])]
        write(f"tag/{key}", page(label, f'<div class="wrap">{tag_nav(key)}{grid(items)}</div>'))
    for p in current:
        write(p["slug"], project_page(p, current))
    if archived:
        intro = '<h1 class="page-title">Archives</h1><p class="lead">Projets plus anciens.</p>'
        write("archives", page("Archives", f'<div class="wrap">{intro}{grid(archived)}</div>'))
        for p in archived:
            write(p["slug"], project_page(p, archived))

    about = data["about"]
    write("about-me", page("À propos", f"""<article class="wrap prose">
  <h1 class="page-title">{escape(about['title'])}</h1>
  {about['html']}
</article>"""))

    (OUT / "404.html").write_text(page("Page introuvable", """<div class="wrap prose">
  <h1 class="page-title">Page introuvable</h1>
  <p><a href="/">Retour à l'accueil</a></p>
</div>"""))

    urls = [""] + [p["slug"] + "/" for p in projects] + ["about-me/"]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>https://{DOMAIN}/{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    print(f"Site généré dans {OUT} : {len(current)} projets, {len(archived)} en archives.")


if __name__ == "__main__":
    main()
