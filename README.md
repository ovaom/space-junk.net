# space-junk.net

Portfolio de Muriel Colagrande, en HTML statique, publié sur GitHub Pages.

## Organisation

- `content.json` : tout le contenu (projets, textes, tags, page À propos)
- `build.py` : génère le site dans `docs/` à partir de `content.json`
- `static/` : feuille de style, script de la visionneuse, favicon
- `docs/` : le site publié (généré, ne pas modifier à la main sauf `docs/img/`)
- `tools/images.py` : convertit les images en WebP optimisé
- `tools/import_dunked.py` : import depuis l'ancien site Dunked

## Modifier le site

1. Modifier `content.json` (texte, ordre des projets, tags…)
2. `python3 build.py`
3. Vérifier en local : `python3 -m http.server 8777 -d docs` puis http://localhost:8777
4. Committer et pousser : GitHub Pages met le site à jour en une minute environ.

## Ajouter un projet

1. Mettre les images dans `originals/<slug>/`
2. Ajouter une entrée dans `projects` de `content.json` :

```json
{
  "slug": "mon-projet",
  "title": "Mon projet",
  "description": "<p>Texte…</p>",
  "date": "2026",
  "client": "…",
  "role": "…",
  "url": "https://…",
  "tags": ["ux-ui"],
  "thumb": "originals/mon-projet/couverture.jpg",
  "assets": [
    { "type": "image", "src": "originals/mon-projet/photo1.jpg" },
    { "type": "vimeo", "id": "123456789" },
    { "type": "youtube", "id": "abcdEFGhij" }
  ]
}
```

3. `python tools/images.py` (nécessite Pillow : `pip install Pillow`) puis `python3 build.py`

Options d'un projet : `"archived": true` le range dans la page Archives,
`"hidden": true` le retire du site sans le supprimer.
L'ordre des projets dans `content.json` est l'ordre d'affichage.

## Contact

Dans `content.json`, rubrique `site` :
- `web3forms_key` : clé gratuite obtenue sur https://web3forms.com (les messages arrivent dans ta boîte mail, l'adresse n'apparaît pas sur le site)
- `linkedin` : adresse de ton profil LinkedIn

La page Contact n'apparaît que si l'un des deux est rempli.
