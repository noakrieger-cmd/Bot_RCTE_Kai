# 🎯 Kaï — Bot Discord Compétitif Valorant

**Kaï** est un bot Discord complet conçu sur mesure pour la gestion opérationnelle et l'animation communautaire d'une équipe compétitive Valorant (*Équipe Première*). 

Développé sous **Python (discord.py)** avec une architecture Orientée Objet (POO) strictement modularisée en **Cogs**, Kaï centralise le suivi des statistiques, les compositions d'équipe, les pronostics et l'actualité VCT.

---

## 🛠️ Architecture du Projet

Le projet suit une structure modulaire où chaque fonctionnalité est isolée dans son propre fichier dans le dossier `cogs/` :

```text
bot_valorant/
├── main.py                     # Script principal (Bot loader & Sync Slash Commands)
├── data.json                   # Base de données locale JSON (exclue de Git)
├── discloud.config             # Configuration pour le déploiement Discloud
├── requirements.txt            # Dépendances Python du projet
├── .env                        # Variables d'environnement / Clés API (exclu de Git)
├── utils/
│   ├── storage.py              # Helper de gestion et persistance JSON
│   └── emojis.py               # Dictionnaire centralisé des emojis du bot
└── cogs/                       # Modules fonctionnels POO
    ├── help.py                 # Centre d'aide interactif (/help)
    ├── matchmaking.py          # Recherche de joueurs (/5s, /trio, /duo)
    ├── ping.py                 # Test de latence du bot (/ping)
    ├── player_register.py      # Association des profils Riot / Tracker.gg (/register, /player_create)
    ├── predictions.py          # Paris communautaires & rôles évolutifs (/predict)
    ├── premier_compo.py        # Choix de la composition & API Agents Valorant (/compo)
    ├── premier_debrief.py      # Débriefs d'après-match (/debrief)
    ├── premier_match_tracker.py# Suivi des résultats & rappels auto de matchs (/results)
    ├── premier_planning.py     # Calendrier des matchs de la saison (/planning)
    ├── premier_player_stats.py # MVP & classement individuel aux ACS (/stats_player, /top)
    ├── premier_presence.py     # Sondages de disponibilité (/presence)
    ├── premier_team_stats.py   # Tableau de bord d'équipe, winrates & rangs (/stats, /rank)
    ├── privacy.py              # Politique RGPD & Droit à l'oubli (/privacy, /forgetme)
    ├── terms.py                # Conditions Générales d'Utilisation (/terms)
    ├── streaming.py            # Rôles automatiques & annonces de live (/setstreamchannel)
    ├── valorant_news.py        # Patch notes et actualités officielles (/news)
    └── vct_tracker.py          # Planning de la scène professionnelle VCT (/vct schedule)
