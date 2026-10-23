"""Optimise les images de content.json pour le web.

Toute image dont le chemin ne commence pas par "img/" (URL ou fichier local,
par ex. "originals/mon-projet/photo.jpg") est convertie en WebP dans docs/img/<slug>/,
et content.json est mis à jour avec le nouveau chemin et les dimensions.
Les originaux téléchargés sont gardés dans originals/<slug>/.

Usage : python tools/images.py   (nécessite Pillow : pip install Pillow)
"""
import json, urllib.parse, urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
MAX_W = 1600      # largeur max des images de projet
THUMB = 600       # vignette carrée de la page d'accueil
QUALITY = 80


def load(src, slug):
    """Renvoie les octets de l'image, en gardant une copie dans originals/."""
    if src.startswith("http"):
        cache = ROOT / "originals" / slug / src.rsplit("/", 1)[-1]
        if not cache.exists():
            cache.parent.mkdir(parents=True, exist_ok=True)
            url = urllib.parse.quote(src, safe=":/?=&%")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                cache.write_bytes(r.read())
        return cache.read_bytes()
    return (ROOT / src).read_bytes()


def open_image(data):
    im = ImageOps.exif_transpose(Image.open(BytesIO(data)))
    if im.mode in ("P", "LA") or (im.mode == "RGBA" and im.getextrema()[3][0] < 255):
        return im.convert("RGBA")
    return im.convert("RGB")


def save(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "WEBP", quality=QUALITY, method=6)
    return path.relative_to(OUT).as_posix()


def main():
    content_file = ROOT / "content.json"
    data = json.loads(content_file.read_text())
    for p in data["projects"]:
        slug = p["slug"]
        n = 0
        for a in p["assets"]:
            if a["type"] != "image":
                continue
            n += 1
            if a["src"].startswith("img/"):
                continue
            im = open_image(load(a["src"], slug))
            if im.width > MAX_W:
                im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
            a["src"] = save(im, OUT / "img" / slug / f"{n:02d}.webp")
            a["w"], a["h"] = im.size
            print(a["src"])
        if p.get("thumb") and not p["thumb"].startswith("img/"):
            im = ImageOps.fit(open_image(load(p["thumb"], slug)), (THUMB, THUMB), Image.LANCZOS)
            p["thumb"] = save(im, OUT / "img" / slug / "thumb.webp")
            print(p["thumb"])
        content_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    about = data.get("about", {})
    if about.get("photo") and not about["photo"].startswith("img/"):
        im = open_image(load(about["photo"], "about"))
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        about["photo"] = save(im, OUT / "img" / "about.webp")
        content_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
