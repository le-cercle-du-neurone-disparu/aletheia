# Veille — détection d'hallucinations LLM

Recherche du 2026-09-03. Version consultable :
https://claude.ai/code/artifact/2b70ee07-a8d5-44dc-989d-e0819ae6242a

Deux clivages structurent tout le champ :
- **factualité** (contredit le monde réel) vs **fidélité** (contredit le contexte fourni) ;
- **boîte noire** (cohérence entre échantillons) vs **boîte blanche** (sondes sur états internes).

## 1. Groupes de travail

### Shared tasks — le plus directement exploitable
Série \*SHROOM (Helsinki NLP) — https://helsinki-nlp.github.io/shroom/
- SHROOM, SemEval-2024 tâche 6 — 4000 sorties, 5 annotateurs, 42 équipes — arXiv 2403.07726
- Mu-SHROOM, SemEval-2025 tâche 3 — **multilingue (14 langues), annotation au niveau span**,
  43 équipes, 2618 soumissions — https://aclanthology.org/2025.semeval-1.322/ · arXiv 2504.11975
- SHROOM-Visions — 4e édition, vision-langage, spans fins sur 4 langues, à UncertaiNLP@EMNLP 2026

### Workshops
- UncertaiNLP (3e éd.), EMNLP 2026, Budapest, 29 oct. 2026 — https://uncertainlp.github.io/
- TrustNLP (6e éd.), ACL 2026
- REALM, EMNLP 2026 — https://realm-workshop.github.io/

### Laboratoires
- OATML Oxford (Yarin Gal, Sebastian Farquhar, Jannik Kossen, Lorenz Kuhn) — entropie
  sémantique, Nature 2024 — https://www.cs.ox.ac.uk/news/2345-full.html
- Stanford RegLab / HAI — hallucinations en contexte juridique, HELM, MedHELM
- Helsinki NLP — série \*SHROOM
- OpenAI research — thèse des incitations d'évaluation

### Normalisation
- CEN-CENELEC JTC 21 — prEN 18229-2 (Accuracy & Robustness), prEN ISO/IEC 23282 (évaluation
  des systèmes TAL) — https://jtc21.eu/ — brouillons, à confirmer au catalogue
- NIST AI 100-5 — https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-5.pdf
- ISO/IEC 42001 — système de management IA certifiable
- International AI Safety Report — arXiv 2501.17805

### France / Europe
- **INESIA** (coordination SGDSN) fédérant Inria, LNE, PEReN, ANSSI — annonce un leaderboard
  avec benchmarks en langue française — https://www.inria.fr/fr/creation-institut-evaluation-securite-intelligence-artificielle
- LNE, programme « Évaluation de l'IA » avec Inria — https://www.lne.fr/en/testing/evaluation-artificial-intelligence-systems
- AFNOR, GT IA miroir de JTC 21 (ANSSI membre)

### Industrie / open source — concurrents directs de Berlue
| Projet | Apport |
|---|---|
| Vectara HHEM-2.1-open + leaderboard vivant | modèle open source de facto pour la fidélité RAG |
| Patronus Lynx 8B/70B | open weights, rail NeMo-Guardrails, auto-hébergeable |
| LettuceDetect (MIT, ModernBERT) | classifieur token-level, contexte long |
| RAGAS | métriques faithfulness / answer relevancy |
| NVIDIA NeMo Guardrails | rails fact-checking / grounding (pas un détecteur) |

Architecture convergente en production : petit détecteur rapide sur chaque requête +
LLM-juge sur un sous-échantillon.

## 2. Papiers

### Surveys
- Huang et al., taxonomie factualité/fidélité, ACM TOIS — arXiv 2311.05232
- Comprehensive survey 2026 — arXiv 2510.06265
- Lifecycle-based survey 2026 — arXiv 2608.26168 *(à vérifier)*
- UQ for hallucination detection — arXiv 2510.12040
- Hallucination to Truth (AI Review / Springer) — arXiv 2508.03860
- Multimodal hallucination survey — arXiv 2507.19024

### Causes
- Kalai, Nachum, Vempala et al., *Why Language Models Hallucinate* — arXiv 2509.04664,
  https://openai.com/index/why-language-models-hallucinate/, version Nature s41586-026-10549-w.
  Thèse : les évaluations notent « je ne sais pas » comme une erreur, donc le bluff est rentable.
  Barème proposé : correct positif, abstention nulle, erreur négative.
  → décision de conception pour Aletheia : comment le score traite l'abstention.

### Détection — boîte noire
- SelfCheckGPT (Manakul et al., EMNLP 2023) — baseline de référence
- Entropie sémantique (Farquhar et al., Nature 2024) — incertitude au niveau du *sens*
- Semantic Entropy Probes — arXiv 2406.15927 — même signal depuis une seule génération
- FactSelfCheck (fait par fait) — arXiv 2503.17229 · Semantic Energy — arXiv 2508.14496

### Détection — boîte blanche
- Sondes d'états cachés, sondes dynamiques inter-couches
- Divergence topologique sur graphes d'attention — arXiv 2504.10063
- Features spectrales des cartes d'attention — arXiv 2502.17598
- LLM-Check (logits + états internes, sans échantillonnage multiple)
- Détection temps réel non supervisée — arXiv 2403.06448

### Spécifique RAG
- ReDeEP (ICLR 2025) — interprétabilité mécaniste, sépare contexte et mémoire paramétrique
- Luna — arXiv 2406.00975

### Garanties
- Principled Detection via Multiple Testing — arXiv 2508.18473 — contrôle explicite du FPR

### Benchmarks
Mu-SHROOM (spans, FR) · Vectara Hallucination Leaderboard · HalluLens (arXiv 2504.17550) ·
FaithBench (NAACL 2025) · TruthfulQA · HELM / MedHELM ·
vague 2026 OpenHalDet / HalluScore / CAP / HALC-Bench *(à vérifier)*

### Verticales
- Juridique — *Large Legal Fictions* (800k questions, 58–88 % d'hallucination) ;
  *Hallucination-Free?* sur Lexis+ AI et Westlaw (Stanford RegLab)
- Médical — MedHalu (arXiv 2409.19492), MedHELM, ClinHallu *(à vérifier)*
- Citations inventées : le cas le plus vérifiable automatiquement — arXiv 2605.07723,
  arXiv 2601.18724 *(à vérifier)*

## 3. Publications grand public

Anglophone : billet OpenAI *Why language models hallucinate* · Nature (incitations) ·
Axios 30/05/2026 *AI is still getting things wrong, more confidently than ever* ·
étude Oxford Internet Institute / Nature sur les chatbots « chaleureux » plus erronés ·
Live Science (amplification des croyances de l'utilisateur) · tech.co (liste d'incidents) ·
The Walrus (le NYT pris à publier des hallucinations)

Francophone : Le Temps (le plus complet) · Le Grand Continent 10/03/2026 (angle économique) ·
Slate.fr (mécanisme) · Wikipédia FR *Hallucination (intelligence artificielle)* ·
LNE *Un cadre de confiance urgent* · critique du terme lui-même — arXiv 2401.06796

## 4. Suites pour Berlue

- **Baselines à afficher** : HHEM-2.1-open, Lynx, LettuceDetect, SelfCheckGPT / SEP.
- **Évaluation** : Mu-SHROOM en premier (spans + français + 43 équipes de comparaison),
  puis FaithBench ou HalluLens selon la cible. À raccorder à `plan-branchement-eval.md`.
- **À trancher** : factualité ou fidélité — la seconde ne demande que le contexte, la première
  une source de vérité, ce qui change le coût d'exploitation.
- **Angle** : le francophone est peu couvert par les détecteurs open source, et l'INESIA
  annonce justement un leaderboard FR.

## 5. Fiabilité

- Groupes / workshops / institutions : **solide** (sources officielles).
- Papiers antérieurs à mi-2026 : **solide** (arXiv, ACL Anthology recoupés).
- Papiers arXiv 26xx : **à vérifier** — identifiants remontés par la recherche, non ouverts un
  par un. À confirmer avant toute citation.
- Chiffres de « taux d'hallucination » issus de pages agrégatrices (sqmagazine, suprmind,
  blogs « statistiques 2026 ») : **prudence**, méthodologie non traçable ; au moins un
  benchmark cité (« BullshitBench v2 ») est sans source primaire trouvable.
- Numéros prEN : **à vérifier** au catalogue CEN-CENELEC, les brouillons évoluent.
