# Correctifs Bot RCTE

## Commandes et droits
- `/presence` et les boutons de vote sont réservés au rôle `Joueur RCTE`. La commande demande le statut `Présent` ou `Absent` ; le premier appel crée le sondage.
- Réexécuter `/presence` modifie le statut du joueur sans réinitialiser les réponses des autres. Le sondage est automatiquement réinitialisé lorsque la date du prochain match planifié change.
- `/compo create` est réservé à `Admin RCTE` : l'administrateur choisit cinq titulaires parmi les présents, les autres sont enregistrés comme remplaçants.
- `/compo update` permet de passer un remplaçant titulaire ou inversement, avec une limite de cinq titulaires, et de modifier son agent.
- `/debrief` est réservé au rôle `Coach-RCTE`.

## Planning et matchs
- `/planning_add` ne demande plus d'adversaire : seules la date et la carte sont enregistrées.
- `/nextmatch` affiche le prochain match à venir depuis le planning et ne permet plus de le créer.
- Les rappels utilisent également le planning et n'affichent plus d'adversaire.

## Pronostics et joueurs
- `/predict_create` crée le sondage de pronostic (Admin RCTE). `/predict` permet aux joueurs de voter pour le match annoncé tant que le sondage est ouvert.
- `/predict_resolve` clôture le pronostic avec les seules options `Victoire` et `Défaite`.
- `/player_create` est supprimée.
- `/stats_player` et `/top` sont supprimées : aucune statistique individuelle ACS/HS% n'est affichée sans source de données fiable.

## Sécurité du paquet
- Le paquet ne contient pas `.env`, `data.json`, `.venv` ni `.git`.
- Recréez le fichier `.env` localement depuis `.env.example` avant de démarrer le bot.
