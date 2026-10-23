"""Importe le contenu du site Dunked dans content.json.

  python3 tools/import_dunked.py                  -> import complet (écrase content.json)
  python3 tools/import_dunked.py --archives a b   -> ajoute les projets a, b en archives
Puis lancer tools/images.py pour récupérer les images.
"""
import json, re, sys, html, urllib.request
from pathlib import Path

BASE = "https://space-junk.dunked.com"
ROOT = Path(__file__).resolve().parent.parent

def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8")

def clean_html(s):
    s = re.sub(r'\s(rel|linkonpaste|openonclick|draggable|contenteditable|class|style)="[^"]*"', "", s)
    s = re.sub(r'https?://space-junk\.dunked\.com/([a-z0-9-]+)', r'/\1/', s)
    s = re.sub(r'<p>(\s|<br>|&nbsp;)*</p>', "", s)
    return s.strip()

def parse_project(slug, archived=False):
    h = get(f"{BASE}/{slug}")
    assets = []
    for m in re.finditer(r'<div id="asset-\d+" class="(image|video|text)"(.*?)(?=<div id="asset-|</div>\s*</div>\s*<header|</div>\s*<header)', h, re.S):
        kind, body = m.group(1), m.group(2)
        if kind == "image":
            a = re.search(r'href="([^"]+)" class="lightbox" data-size="(\d+)x(\d+)"', body)
            if a:
                assets.append({"type": "image", "src": a.group(1), "w": int(a.group(2)), "h": int(a.group(3))})
        elif kind == "video":
            v = re.search(r'player\.vimeo\.com/video/(\d+)', body)
            y = re.search(r'youtube(?:-nocookie)?\.com/embed/([\w-]+)', body)
            if v: assets.append({"type": "vimeo", "id": v.group(1)})
            elif y: assets.append({"type": "youtube", "id": y.group(1)})
            else: print("vidéo inconnue", slug, body[:200], file=sys.stderr)
        else:
            assets.append({"type": "text", "html": clean_html(body)})
    title = html.unescape(re.search(r'<h1 class="title">(.*?)</h1>', h, re.S).group(1).strip())
    d = re.search(r'<div class="project-description">(.*?)</div>\s*(<footer|</article)', h, re.S)
    meta = {}
    for k in ["date", "client", "role"]:
        mm = re.search(rf'<span class="{k}">(.*?)</span>', h, re.S)
        if mm: meta[k] = html.unescape(mm.group(1).strip())
    mm = re.search(r'<a href="([^"]+)" class="url"', h)
    if mm: meta["url"] = mm.group(1)
    return {"slug": slug, "title": title, "archived": archived,
            "description": clean_html(d.group(1)) if d else "", **meta, "assets": assets}

def main():
    home = get(BASE + "/")
    tags = {m.group(1): html.unescape(m.group(2)) for m in re.finditer(r'href="https://space-junk\.dunked\.com/tag/([^"]+)">([^<]+)</a>', home)}
    projects = []
    for m in re.finditer(r'<article id="project-\d+" class="project([^"]*)">(.*?)</article>', home, re.S):
        slug = re.search(r'href="https://space-junk\.dunked\.com/([^"]+)"', m.group(2)).group(1)
        thumb = re.search(r'srcset="(\S+)', m.group(2)).group(1)
        p = parse_project(slug)
        p["tags"] = m.group(1).split()
        # vignette Dunked recadrée en carré : on garde l'original, recadré au build
        p["thumb"] = re.sub(r'/\d+x\d+(-\d)?_', '/', thumb)
        projects.append(p)
        print("ok", p["slug"], len(p["assets"]), file=sys.stderr)
    about = get(BASE + "/about-me")
    a = re.search(r'<div class="page-content cf">(.*?)</div>\s*</div>\s*</article>', about, re.S)
    data = {"site": {"title": "space-junk", "author": "Muriel Colagrande"},
            "tags": tags,
            "about": {"title": "Muriel Colagrande", "html": clean_html(a.group(1))},
            "projects": projects}
    (ROOT / "content.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))

def add_archives(slugs):
    f = ROOT / "content.json"
    data = json.loads(f.read_text())
    known = {p["slug"] for p in data["projects"]}
    for slug in slugs:
        if slug in known:
            print("déjà présent :", slug, file=sys.stderr)
            continue
        p = parse_project(slug, archived=True)
        p["tags"] = []
        p["thumb"] = next((a["src"] for a in p["assets"] if a["type"] == "image"), "")
        data["projects"].append(p)
        print("archive ajoutée :", slug, len(p["assets"]), file=sys.stderr)
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--archives"]:
        add_archives(sys.argv[2:])
    else:
        main()
