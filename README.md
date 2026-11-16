# Bot RCTE

Bot Discord centré sur l’**organisation des matchs Première** (planning, rappels, présences, composition, résultats, debriefs) et la **recherche de coéquipiers** (`/5s`, `/trio`, `/duo`). Il n’appelle aucune API externe : seules les données saisies sur le serveur sont utilisées.

## Installation

1. Installez Python 3.11 ou plus récent et [uv](https://docs.astral.sh/uv/).
2. Copiez `.env.example` vers `.env`, puis renseignez `DISCORD_TOKEN` et, pour synchroniser les commandes rapidement pendant le développement, `DISCORD_GUILD_ID`.
3. Installez les dépendances avec `uv sync` puis lancez le bot avec `uv run python main.py`.
4. Créez les rôles Discord `Admin RCTE`, `Joueur RCTE` et `Coach-RCTE`. `Joueur RCTE` peut utiliser `/presence` pour indiquer ou modifier son statut (le premier appel crée le sondage) et voter via les boutons ; `Admin RCTE` gère la composition, le planning, les résultats et les pronostics ; `Coach-RCTE` rédige les debriefs.
5. Activez les intents privilégiés **Server Members Intent** et **Presence Intent** dans le Developer Portal. Le Presence Intent sert aux annonces de stream et à l’attribution du rôle `En Stream`.
6. Dans le serveur, placez le rôle du bot au-dessus de `En Stream` et des rôles de pronostics. Le bot a besoin de `Manage Roles`, ainsi que des permissions d’envoi et de lecture dans les salons configurés.

La commande `/planning_add` ajoute un match (date et carte, sans adversaire) et `/planning_clear` vide le planning. `/nextmatch` affiche le prochain match à venir issu de ce planning. `/setmatchchannel` configure les rappels et `/rank_set` met à jour le rang et le classement. Les dates sont saisies en heure de Paris au format `AAAA-MM-JJ HH:MM`. `/compo create` permet à un Admin de choisir les cinq titulaires parmi les joueurs présents ; les autres deviennent remplaçants. `/compo update` permet de changer le statut d’un joueur (avec un maximum de cinq titulaires) et éventuellement son agent. `/predict` ouvre un pronostic et `/predict_resolve` le clôture avec le choix Victoire ou Défaite. `/debrief` est réservé au rôle `Coach-RCTE`. En production, la synchronisation globale est manuelle via `/sync` (propriétaire du bot); pour une première synchronisation sans commandes globales déjà en place, démarrez une fois avec `SYNC_GLOBAL_COMMANDS=true`, puis remettez la variable à `false`.

Les données runtime sont écrites dans `data.json` à côté de `main.py`. Le fichier est ignoré par Git; `data.example.json` documente sa structure sans inclure de données de test.

La commande `/register` associe un Riot ID à un compte Discord sans aucune vérification auprès d’un service externe (le format est simplement contrôlé). Les résultats et classements de l’équipe sont saisis manuellement. Les statistiques individuelles ACS/HS% ne sont pas proposées tant qu’aucune source fiable n’est intégrée. La liste des agents est statique : quand Riot ajoute un agent, ajoutez-le dans `utils/valorant.py`.
