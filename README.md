# Bot RCTE

Bot Discord centré sur l’**organisation des matchs Première** (planning, rappels, présences, composition, résultats, debriefs), la **recherche de coéquipiers** (`/5s`, `/trio`, `/duo`) et la validation des Riot ID via Riot Account API.

## Installation

1. Installez Python 3.11 ou plus récent et [uv](https://docs.astral.sh/uv/).
2. Copiez `.env.example` vers `.env`, puis renseignez `DISCORD_TOKEN`, `RIOT_API_KEY` et, pour synchroniser les commandes rapidement pendant le développement, `DISCORD_GUILD_ID`.
3. Installez les dépendances avec `uv sync` puis lancez le bot avec `uv run python main.py`.
4. Créez les rôles Discord `Admin RCTE`, `Joueur RCTE` et `Coach-RCTE`. `Joueur RCTE` peut utiliser `/presence` pour indiquer ou modifier son statut (le premier appel crée le sondage) et voter via les boutons ; `Admin RCTE` gère la composition, le planning, les résultats et les pronostics ; `Coach-RCTE` rédige les debriefs.
5. Activez les intents privilégiés **Server Members Intent** et **Presence Intent** dans le Developer Portal. Le Presence Intent sert aux annonces de stream et à l’attribution du rôle `En Stream`.
6. Dans le serveur, placez le rôle du bot au-dessus de `En Stream` et des rôles de pronostics. Le bot a besoin de `Manage Roles`, ainsi que des permissions d’envoi et de lecture dans les salons configurés.

La commande `/planning_add` ajoute un match (date et carte, sans adversaire) et `/planning_clear` vide le planning. `/nextmatch` affiche le prochain match à venir issu de ce planning. `/setmatchchannel` configure les rappels et `/rank_set` met à jour le rang et le classement. Les dates sont saisies en heure de Paris au format `AAAA-MM-JJ HH:MM`. `/compo create` permet à un Admin de choisir les cinq titulaires parmi les joueurs présents ; les autres deviennent remplaçants. `/compo update` permet de changer le statut d’un joueur (avec un maximum de cinq titulaires) et éventuellement son agent. `/predict_create` ouvre un pronostic (Admin RCTE), `/predict` permet aux joueurs de voter et `/predict_resolve` le clôture avec le choix Victoire ou Défaite. `/debrief` est réservé au rôle `Coach-RCTE`. En production, la synchronisation globale est manuelle via `/sync` (propriétaire du bot); pour une première synchronisation sans commandes globales déjà en place, démarrez une fois avec `SYNC_GLOBAL_COMMANDS=true`, puis remettez la variable à `false`.

Les données runtime sont écrites dans `data.json` à côté de `main.py`. Le fichier est ignoré par Git; `data.example.json` documente sa structure sans inclure de données de test.

La commande `/player create` vérifie le Riot ID auprès de Riot Account API avant de l’enregistrer et conserve le PUUID. Cette vérification confirme l’existence du compte, pas sa propriété : l’opt-in RSO est nécessaire pour une vérification de propriété et pour les statistiques individuelles VALORANT. La commande `/stats_joueur` affiche le compte lié et indique clairement que les statistiques ne sont pas activées tant que l’accès Riot Production/RSO n’est pas disponible. Les résultats et classements de l’équipe restent saisis manuellement.
