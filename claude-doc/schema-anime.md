# Le schéma animé de la page « Comment ? »

Tout tient dans **`views/comment.py`**. C'est un SVG écrit à la main, animé en
SMIL, rendu dans une iframe par `components.html`. Pas de bibliothèque, pas
d'image : ~30 Ko, net à toutes les tailles, et le timing se lit en clair.

Le GIF de `static/schema-anime.gif` n'est qu'un **export** de ce SVG, pour les
slides et le README. Il n'est jamais la source : on ne l'édite pas, on le
regénère.

---

## Ce que le schéma raconte

Un cycle de 15 secondes rejoue le trajet d'une question :

| Temps | Ce qui se passe |
|---|---|
| 0,3 – 1,6 s | le `?` de l'utilisateur descend vers l'Interface Web |
| 1,8 – 3,0 s | l'interface transmet la `question` au LLM |
| 3,7 – 5,0 s | le LLM envoie sa `réponse` à l'Extracteur |
| 3,7 – 6,1 s | …et cinq `réponse` régénérées, du bleu au rouge, vers SelfCheckGPT |
| 5,4 – 7,3 s | l'Extracteur découpe en `claim` et interroge le RAG |
| 7,6 – 9,0 s | SelfCheckGPT et RAG rendent chacun `éval. + analyse` à la Fusion |
| 9,8 – 12,6 s | la Fusion renvoie `score + catégorie + analyse` à l'interface |
| 12,8 – 14,2 s | l'interface rend l'`analyse` à l'utilisateur |

Trois acteurs, trois traitements graphiques distincts :

- **l'utilisateur** — Le Penseur, cadre de bronze : il n'appartient à aucun des
  deux systèmes, il les regarde travailler ;
- **Aletheia** — l'application : ivoire, or, frises à la grecque, lettres
  romaines. C'est elle qui possède l'interface web ;
- **Berlue** — le moteur de vérification : fond quadrillé, filets bleus, repères
  d'angle, chasse fixe. Il ne connaît pas l'interface.

Deux libellés échappent à ce découpage : **`FEVER_corpus`** et
**`SelfCheckGPT`**, les seules briques empruntées à l'extérieur. Berlue ne fait
que les mettre en œuvre, elles n'appartiennent à aucun des deux camps — d'où un
traitement unique, partagé par les deux et employé nulle part ailleurs : violet
`#7A3A93`, chasse fixe, petites capitales espacées, même corps. Il se règle en un
seul endroit, `SOURCE` / `SOURCE_TAILLE` / `SOURCE_ATTRS` en tête de fichier, et
un bloc technique le prend via `_composant_berlue(..., source=True)`. Le violet
est le seul créneau libre de la page : le bronze désigne déjà l'utilisateur,
l'orange la famille RAG, le bleu et le cyan Berlue lui-même. La légende sous le
schéma reprend la même couleur et la même casse, pour que les deux liens se
rattachent visuellement à ce qu'ils nomment.

---

## Modifier l'animation

**Le rythme et les trajets se règlent au seul endroit qui compte : le bloc
`MOUVEMENTS`.** Un mouvement par ligne, avec ses temps en secondes du cycle.

```python
_bloc("pLlmExt", "réponse", CYAN, 3.7, 5.0),
#      ^chemin   ^étiquette ^teinte ^début ^fin
```

- **Ralentir un passage** : écarter `début` et `fin`. C'est ce qui a été fait
  pour le retour du score, illisible en 1,6 s, confortable en 2,8 s.
- **Changer l'ordre** : décaler les temps. Rien d'autre à toucher.
- **Allonger le cycle** : `CYCLE`, en haut du fichier. Tous les minutages étant
  exprimés en secondes, ils suivent automatiquement.
- **Faire clignoter un composant pendant qu'il travaille** : `_halo(x, y, w, h,
  couleur, début, fin)`, aux coordonnées du bloc concerné.

### Pourquoi chaque animation dure un cycle entier

Chaque `<animate>` porte `dur="{CYCLE}s" repeatCount="indefinite"`, et c'est le
jeu de `keyTimes` qui place le mouvement réel dans la fenêtre voulue. La méthode
intuitive — une durée courte et un `begin` décalé — **ne reboucle pas** : SMIL ne
sait pas rejouer un ensemble d'animations décalées les unes des autres. C'est la
seule subtilité du fichier.

## Modifier le dessin

- **Déplacer un composant** : ses coordonnées sont dans le corps du SVG. Penser
  à bouger aussi le `<path>` de liaison correspondant **et** le `_halo` qui lui
  est associé, qui reprennent les mêmes chiffres.
- **Les liaisons sont aussi les trajectoires.** Chaque flèche est un `<path>`
  avec un identifiant (`pItfLlm`, `pLlmScg`…) que les blocs animés suivent via
  `<mpath>`. D'où l'usage de `<path>` et jamais de `<line>`/`<polyline>` :
  `<mpath>` ne sait suivre qu'un `<path>`.
- **Ajouter un composant** : `_composant_berlue(...)` ou `_composant_aletheia(...)`
  selon le monde auquel il appartient. Les deux fonctions posent le cadre, les
  filets et la typographie de leur camp.
- **Les vignettes** sont servies depuis `static/` en chemin **relatif**
  (`app/static/…`), jamais absolu : un préfixe d'URL, tel qu'en pose un
  hébergement sous chemin, casserait la forme absolue. L'iframe de
  `components.html` hérite de l'URL de base de la page qui la porte, donc le
  relatif y fonctionne aussi.
- **Le cadrage** se règle par le `viewBox`. Après l'avoir changé, ajuster
  `SCHEMA_HAUTEUR` : c'est la hauteur réservée à l'iframe, et un excédent se voit
  en blanc sous le schéma.

---

## Regénérer le GIF

```bash
make schema_gif
```

ou, pour choisir :

```bash
python scripts/schema_gif.py --largeur 1000 --fps 8 --couleurs 96
```

Environ dix secondes. Dépend de `google-chrome` (ou `chromium`) et d'ImageMagick.

### Comment il est fabriqué

Le navigateur sait figer une animation SMIL à un instant précis
(`svg.setCurrentTime`). Le script empile donc quinze copies du schéma dans une
même page, chacune figée à un instant différent, capture la page en une fois et
la redécoupe : **une capture pour quinze images**, au lieu d'un lancement de
navigateur par image. Les copies partagent leurs identifiants d'éléments, ce qui
est sans conséquence — les géométries sont identiques et chaque `<svg>` a sa
propre horloge.

Le script lit le `viewBox` pour en déduire la hauteur : changer le format du
schéma ne demande rien de plus.

### Deux pièges, déjà payés

**Ne jamais redimensionner après l'assemblage.** `-layers Optimize` ne conserve
que ce qui change d'une image à l'autre — ici, presque rien, le décor étant fixe.
Un redimensionnement en fin de chaîne rééchantillonne tout et fait diverger des
pixels jusque-là identiques : l'optimisation s'effondre et le fichier **grossit**.
Constaté : 1,4 Mo à la bonne taille, 2,6 Mo après un `-resize` censé l'alléger.
Pour un GIF plus petit, capturer plus petit (`--largeur`).

**Les photos coûtent cher.** Les trois vignettes élargissent la palette et
alourdissent le tout. C'est ce qui a fait passer le fichier de 0,7 à 2,7 Mo au fil
des ajouts. Le levier utile est alors la cadence : 5 images/seconde suffisent, le
mouvement étant lent et linéaire, et divisent le poids par deux.

---

## Les images intermédiaires ne sont pas conservées

Ni les images fixes, ni les pages d'empilement. C'est délibéré : elles sont
entièrement reconstructibles à partir de `views/comment.py`, et les garder ferait
vieillir en silence une copie du schéma. La source, c'est le SVG ; le reste se
regénère en dix secondes.
