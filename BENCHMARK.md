# 6.1.4) État de l'art / benchmark

Comparatif basé sur la documentation publique de chaque fournisseur (prix,
quotas, langues, RGPD), par famille d'API. Objectif : justifier les choix
faits pour Scribe (Recall.ai, AssemblyAI, Groq) face aux alternatives les
plus citées sur ce marché.

Dernière vérification : 25/08/2026.

## Famille 1 : Transcription avec diarisation

| Critère | Deepgram (Nova-3 Multilingual) | AssemblyAI (Universal-2) | gpt-4o-transcribe-diarize |
|---|---|---|---|
| Prix transcription | 0,31 $/h | 0,15 $/h | 0,36 $/h |
| Diarisation | +0,12 $/h | +0,02 $/h | Incluse |
| Coût réel avec diarisation | ~0,43 $/h | ~0,17 $/h | ~0,36 $/h |
| Français | Oui | Oui | Oui |
| RGPD | Conforme | Conforme | Conforme |

**Choix retenu : AssemblyAI.** Le moins cher des trois une fois la
diarisation incluse (~0,17 $/h, presque 3x moins cher que Deepgram), et
endpoint européen disponible (`api.eu.assemblyai.com`) — effectivement
utilisé par Scribe.

## Famille 2 : LLM pour le résumé et l'extraction d'actions

| Critère | Llama 3.3 70B Versatile | Qwen3 32B | openai/gpt-oss-120b |
|---|---|---|---|
| Prix entrée | 0,59 $/M tokens | 0,29 $/M tokens | 0,15 $/M tokens |
| Prix sortie | 0,79 $/M tokens | 0,59 $/M tokens | 0,60 $/M tokens |
| Vitesse | 394 tokens/seconde | 662 tokens/seconde | ~477 tokens/seconde |
| Taille | 70 milliards de paramètres | 32 milliards de paramètres | 117 Md (MoE, 5,1 Md actifs/token) |
| Français | Oui | Oui | Oui |
| Réponse JSON structurée | Oui | Oui | Oui |

**⚠️ Correction en cours de projet :** Llama 3.3 70B Versatile était le
modèle initialement retenu et utilisé en production. Il a été retiré du
catalogue Groq en cours de route (l'API a commencé à répondre 404 "modèle
introuvable" sans prévenir), ce qui a fait échouer silencieusement toute
analyse de réunion pendant un moment (le compte-rendu ne se remplissait
plus, bug détecté via les logs Railway). Après avoir testé les modèles
disponibles sur le compte Groq, **openai/gpt-oss-120b est le modèle
effectivement utilisé aujourd'hui** — moins cher à l'entrée que Llama 3.3
70B et Qwen3 32B, vitesse intermédiaire, et fiable sur le prompt/schéma
JSON déjà en place (validé avant bascule).

**Choix retenu : openai/gpt-oss-120b.** Le moins cher des trois à l'entrée,
tout en restant plus rapide que Llama 3.3 70B. Limite assumée face à
Qwen3 32B : moins rapide et légèrement plus cher en sortie, mais la marge
reste négligeable à l'échelle du volume de ce projet.

## Famille 3 : Approche de classification (thème, catégorie, humeur)

| Approche | En quoi ça consiste | Avantages | Inconvénients |
|---|---|---|---|
| **Classification par le LLM** | Le LLM qui fait le résumé renvoie aussi thème, catégorie, humeur | Coût marginal quasi nul : classification incluse dans un appel déjà nécessaire pour le résumé | Dépend du prompt ; nécessite une liste fermée |
| Modèle de classification dédié | Un modèle de classification séparé, à héberger ou à appeler via une API tierce | Résultats réguliers, spécialisés | Coût supplémentaire distinct (serveur ou abonnement API) ; ne remplace pas le LLM, qui reste nécessaire pour le résumé et les actions ; donc coût cumulé, pas coût de remplacement |

**Choix retenu : classification par le LLM.** Un seul appel Groq produit
`theme`, `categorie`, `humeur`, `resume` et `actions` en une seule réponse
JSON (`utils/analysis.py::analyze`) — pas de coût ni de latence
supplémentaire par rapport à un modèle dédié qui, de toute façon, ne
dispenserait pas d'appeler un LLM pour le résumé.

## Famille 4 : Bot réunion

| Critères | Recall.ai | Vexa.ai |
|---|---|---|
| Tarification ($) | 0,50 $ par heure de connexion du bot | 0,30 $/h (Cloud). 0,00 $ si auto-hébergé sur votre infrastructure |
| Compatibilité plateformes | Universelle (Google Meet, Zoom, MS Teams, Slack, Webex) | Restreinte (principalement Google Meet et MS Teams actuellement) |
| Conformité RGPD / Souveraineté | Hébergement en Europe (serveurs AWS situés à Francfort) | Totale : possibilité de déployer la solution localement pour garder le contrôle absolu des flux |
| Extraction du flux audio | Oui : lien direct fourni via webhook pour télécharger le fichier brut | Oui : récupération directe du fichier audio après la réunion |

**Choix retenu : Recall.ai.** Plus cher que Vexa.ai à l'usage, mais
compatibilité universelle (Zoom/Teams/Meet/Webex/Slack) contre une
couverture encore restreinte chez Vexa.ai, et déjà conforme RGPD sans
nécessiter d'auto-hébergement (que le projet n'a pas les moyens
d'opérer/maintenir à ce stade).

## Sources

- [AssemblyAI — Speech-to-Text API Pricing](https://www.assemblyai.com/blog/speech-to-text-api-pricing)
- [Deepgram Pricing 2026](https://costbench.com/software/ai-transcription-apis/deepgram/)
- [Groq Pricing 2026](https://costbench.com/software/llm-api-providers/groq/)
- [GPT-OSS 120B — GroqDocs](https://console.groq.com/docs/model/openai/gpt-oss-120b)
- [gpt-oss-120b — Performance & Price Analysis, Artificial Analysis](https://artificialanalysis.ai/models/gpt-oss-120b/providers)
- [Recall.ai — New Pricing for 2026](https://www.recall.ai/blog/new-recall-ai-pricing-for-2026)
