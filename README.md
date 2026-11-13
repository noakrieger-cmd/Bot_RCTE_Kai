# Bot RCTE

Bot Discord centré sur l’**organisation des matchs Première** (planning, rappels, présences, composition, résultats, debriefs) et la **recherche de coéquipiers** (`/5s`, `/trio`, `/duo`). Il n’appelle aucune API externe : seules les données saisies sur le serveur sont utilisées.

## Installation

1. Installez Python 3.11 ou plus récent et [uv](https://docs.astral.sh/uv/).
2. Copiez `.env.example` vers `.env`, puis renseignez `DISCORD_TOKEN` et, pour synchroniser les commandes rapidement pendant le développement, `DISCORD_GUILD_ID`.
3. Installez les dépendances avec `uv sync` puis lancez le bot avec `uv run python main.py`.
4. Créez le rôle Discord `Admin RCTE` et attribuez-le aux responsables autorisés à modifier les résultats, statistiques, présence, composition, planning, pronostics et configuration.
5. Activez les intents privilégiés **Server Members Intent** et **Presence Intent** dans le Developer Portal. Le Presence Intent sert aux annonces de stream et à l’attribution du rôle `En Stream`.
6. Dans le serveur, placez le rôle du bot au-dessus de `En Stream` et des rôles de pronostics. Le bot a besoin de `Manage Roles`, ainsi que des permissions d’envoi et de lecture dans les salons configurés.

Les commandes `/nextmatch` et `/setmatchchannel` configurent les rappels. `/planning_add` ajoute un match, `/planning_clear` vide le planning, et `/rank_set` met à jour le rang et le classement. Les dates du prochain match sont saisies en heure de Paris au format `AAAA-MM-JJ HH:MM`. En production, la synchronisation globale est manuelle via `/sync` (propriétaire du bot); pour une première synchronisation sans commandes globales déjà en place, démarrez une fois avec `SYNC_GLOBAL_COMMANDS=true`, puis remettez la variable à `false`.

Les données runtime sont écrites dans `data.json` à côté de `main.py`. Le fichier est ignoré par Git; `data.example.json` documente sa structure sans inclure de données de test.

La commande `/register` associe un Riot ID à un compte Discord sans aucune vérification auprès d’un service externe (le format est simplement contrôlé). Les données et classements de l’équipe sont saisis manuellement. La liste des agents est statique : quand Riot ajoute un agent, ajoutez-le dans `utils/valorant.py`.
