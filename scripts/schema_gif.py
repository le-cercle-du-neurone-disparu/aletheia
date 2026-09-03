#!/usr/bin/env python3
"""Fabrique le GIF du schéma animé à partir de `views/comment.py`.

Le SVG animé est la source ; ce script ne fait que le figer image par image.
Pour modifier l'animation on n'édite jamais ce fichier : tout se règle dans
`views/comment.py`, bloc `MOUVEMENTS`.

Principe : le navigateur sait figer une animation SMIL à un instant précis
(`svg.setCurrentTime`). On empile donc plusieurs copies du schéma dans une même
page, chacune figée à un instant différent, et une seule capture livre autant
d'images — au lieu d'un lancement de navigateur par image.

Dépendances externes : google-chrome (ou chromium) et ImageMagick.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import types
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
VUE = RACINE / "views" / "comment.py"
STATIQUE = RACINE / "static"


def _outil(*noms: str) -> str:
    """Premier exécutable trouvé parmi `noms`, sinon on s'arrête net."""
    for nom in noms:
        chemin = shutil.which(nom)
        if chemin:
            return chemin
    sys.exit(f"❌ Aucun de ces exécutables n'est installé : {', '.join(noms)}")


def charger_schema() -> tuple[str, str, float]:
    """Importe la vue sans lancer Streamlit et en extrait le schéma."""
    faux = types.ModuleType("streamlit")
    faux.subheader = faux.markdown = lambda *a, **k: None
    composants = types.ModuleType("streamlit.components.v1")
    composants.html = lambda *a, **k: None
    faux.components = types.SimpleNamespace(v1=composants)
    sys.modules["streamlit"] = faux
    sys.modules["streamlit.components.v1"] = composants

    import importlib.util

    spec = importlib.util.spec_from_file_location("vue_comment", VUE)
    vue = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vue)
    return vue.STYLE, vue.SCHEMA.split("</style>", 1)[1], float(vue.CYCLE)


def hauteur_utile(svg: str, largeur: int) -> int:
    """Hauteur qui respecte le viewBox — le schéma peut changer de format."""
    m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', svg)
    if not m:
        sys.exit("❌ viewBox introuvable dans le schéma.")
    _, _, w, h = (float(v) for v in m.groups())
    return round(largeur * h / w)


def ecrire_bandes(
    banc: Path,
    style: str,
    svg: str,
    instants: list[float],
    largeur: int,
    hauteur: int,
    par_bande: int,
) -> list[tuple[Path, int]]:
    """Écrit les pages d'empilement et renvoie (fichier, nombre d'images)."""
    (banc / "app").mkdir(parents=True, exist_ok=True)
    shutil.copytree(STATIQUE, banc / "app" / "static", dirs_exist_ok=True)

    bandes = []
    for debut in range(0, len(instants), par_bande):
        lot = instants[debut : debut + par_bande]
        corps = "".join(f'<div class="f">{svg}</div>' for _ in lot)
        page = f"""<!doctype html><meta charset="utf-8">
{style}
<style>
  /* Le style de la vue cadre le schéma pour la page ; ici on veut des tuiles
     jointives, à taille fixe, sans marge ni plafond de largeur. */
  html, body {{ margin: 0; padding: 0; }}
  .f {{ width: {largeur}px; height: {hauteur}px; overflow: hidden; }}
  .f svg {{ display: block; width: {largeur}px; height: {hauteur}px; max-width: none; }}
</style>
{corps}
<script>
  const instants = {json.dumps(lot)};
  document.querySelectorAll('.f svg').forEach((s, i) => {{
    s.pauseAnimations();
    s.setCurrentTime(instants[i]);
  }});
</script>"""
        fichier = banc / f"bande_{debut // par_bande}.html"
        fichier.write_text(page, encoding="utf-8")
        bandes.append((fichier, len(lot)))
    return bandes


class _Silencieux(SimpleHTTPRequestHandler):
    """Le serveur ne journalise rien : une requête par vignette et par bande
    noierait la progression."""

    def log_message(self, *a):
        pass


def servir(dossier: Path) -> tuple[ThreadingHTTPServer, int]:
    """Serveur local : les vignettes sont référencées en `app/static/…`,
    ce qu'un `file://` ne saurait pas résoudre."""
    gestionnaire = partial(_Silencieux, directory=str(dossier))
    serveur = ThreadingHTTPServer(("127.0.0.1", 0), gestionnaire)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    return serveur, serveur.server_address[1]


def capturer(chrome: str, url: str, sortie: Path, largeur: int, hauteur: int) -> None:
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--virtual-time-budget=6000",
            f"--window-size={largeur},{hauteur}",
            f"--screenshot={sortie}",
            url,
        ],
        check=True,
        capture_output=True,
    )
    if not sortie.exists():
        sys.exit(f"❌ Capture manquante : {sortie}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--largeur", type=int, default=800, help="largeur du GIF (défaut : 800)"
    )
    ap.add_argument(
        "--fps", type=int, default=5, help="images par seconde (défaut : 5)"
    )
    ap.add_argument(
        "--couleurs", type=int, default=128, help="taille de la palette (défaut : 128)"
    )
    ap.add_argument(
        "--par-bande",
        type=int,
        default=15,
        help="images empilées par capture (défaut : 15)",
    )
    ap.add_argument("--sortie", type=Path, default=STATIQUE / "schema-anime.gif")
    args = ap.parse_args()

    chrome = _outil(
        "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"
    )
    magick = _outil("magick", "convert")

    style, svg, cycle = charger_schema()
    hauteur = hauteur_utile(svg, args.largeur)
    instants = [round(i / args.fps, 4) for i in range(int(cycle * args.fps))]
    print(
        f"schéma : cycle {cycle} s · {len(instants)} images · {args.largeur}×{hauteur}"
    )

    with tempfile.TemporaryDirectory(prefix="schema-gif-") as tmp:
        banc = Path(tmp)
        bandes = ecrire_bandes(
            banc, style, svg, instants, args.largeur, hauteur, args.par_bande
        )
        serveur, port = servir(banc)
        try:
            images: list[Path] = []
            for index, (page, combien) in enumerate(bandes):
                planche = banc / f"planche_{index}.png"
                capturer(
                    chrome,
                    f"http://127.0.0.1:{port}/{page.name}",
                    planche,
                    args.largeur,
                    hauteur * combien,
                )
                # Le découpage renomme au vol, en numérotation continue.
                subprocess.run(
                    [
                        magick,
                        str(planche),
                        "-crop",
                        f"{args.largeur}x{hauteur}",
                        "+repage",
                        "-set",
                        "filename:n",
                        f"img_%[fx:{index * args.par_bande}+t]",
                        str(banc / "%[filename:n].png"),
                    ],
                    check=True,
                    cwd=banc,
                )
                images += [
                    banc / f"img_{index * args.par_bande + i}.png"
                    for i in range(combien)
                ]
                print(f"  bande {index + 1}/{len(bandes)} · {combien} images")
        finally:
            serveur.shutdown()

        args.sortie.parent.mkdir(parents=True, exist_ok=True)
        # `-layers Optimize` ne garde que ce qui change d'une image à l'autre :
        # le décor est fixe, seuls les blocs qui circulent pèsent. Ne jamais
        # redimensionner après coup — le rééchantillonnage fait diverger des
        # pixels identiques et ruine cette optimisation.
        subprocess.run(
            [
                magick,
                "-delay",
                str(round(100 / args.fps)),
                "-loop",
                "0",
                *[str(i) for i in images],
                "+dither",
                "-colors",
                str(args.couleurs),
                "-layers",
                "Optimize",
                str(args.sortie),
            ],
            check=True,
        )
    poids = args.sortie.stat().st_size / 1_048_576
    print(f"✅ {args.sortie} · {poids:.2f} Mo")


if __name__ == "__main__":
    main()
