# Politique de confidentialité — Bot RCTE (brouillon)

**Version de travail — ne pas publier avant d’avoir vérifié les champs encore signalés et les traitements réellement activés.** Date d’entrée en vigueur : **6 novembre 2026**. Ce texte décrit la version cible du bot; les liaisons Riot par OAuth, les statistiques automatiques et les flux sociaux restent à développer.

## 1. Responsable et contact

Le responsable du traitement est **Krieger Noa**. Pour toute question ou demande relative aux données personnelles : **noa.krieger452@gmail.com**. Pour une aide sur le serveur, vous pouvez aussi contacter **bebou_bb** sur Discord; les demandes relatives aux droits peuvent être adressées à l’adresse e-mail ci-dessus.

## 2. Personnes concernées et âge

Le bot est destiné aux membres du serveur Discord RCTE âgés d’au moins **15 ans**. Le serveur est accessible via [cette invitation Discord](https://discord.gg/2vKc5TGYc). Le bot ne demande pas de date de naissance; Discord applique ses propres contrôles d’âge et conditions d’accès.

## 3. Données traitées

Selon les fonctionnalités activées, le bot peut traiter :

- identifiant Discord, nom d’affichage et appartenance au serveur;
- identifiant Riot/VALORANT et données de compte ou de jeu associées;
- résultats et statistiques de matchs, notamment K/D, tirs à la tête, ACS, rang et historique de matchs;
- données de gestion de l’équipe RCTE : effectif, composition, présence, résultats, classement, pronostics et statistiques saisies par les responsables;
- contenu des debriefs saisis par les membres autorisés, dont le nom de l’auteur et les commentaires d’équipe;
- informations publiques de publications VALORANT officielles, telles que leur titre, leur lien, leur plateforme et leur date de publication;
- données techniques nécessaires au fonctionnement et au diagnostic du bot, notamment les journaux d’erreurs.

La saisie ou liaison des données de jeu est volontaire. Les statistiques individuelles sont visibles par **les membres du serveur RCTE**. La version actuelle du bot enregistre un Riot ID saisi via une commande; une authentification Riot officielle et un import automatique des statistiques ne sont pas encore implémentés.

## 4. Finalités et bases juridiques

| Finalité | Base envisagée — à confirmer |
|---|---|
| Enregistrer volontairement un Riot ID et afficher les données associées | Consentement de la personne (à confirmer selon la mise en œuvre finale) |
| Gérer l’effectif, la composition, les présences, les matchs et les statistiques d’équipe | Base juridique à confirmer avant mise en service de la version cible |
| Fournir des liens vers les actualités et contenus officiels | Base juridique à confirmer; flux sociaux non encore activés |
| Diagnostiquer les erreurs, protéger le bot et prévenir les abus | Base juridique et données de journal à confirmer selon la configuration déployée |

Les données ne sont pas réutilisées à d’autres fins sans information préalable et, lorsque nécessaire, sans nouvelle base juridique.

## 5. Sources et destinataires

Les données proviennent de Discord, des joueurs qui saisissent volontairement leur Riot ID, des responsables RCTE qui saisissent les données d’équipe et de fournisseurs tiers sollicités par le bot.

Les destinataires peuvent inclure le responsable du traitement et les membres du serveur pour les données affichées par les commandes. Le code actuel sollicite Discord, l’API communautaire HenrikDev (profils Valorant et actualités), l’API communautaire VLR.gg (calendrier VCT) et Valorant-API (catalogue d’agents). Ces fournisseurs peuvent recevoir les paramètres nécessaires à chaque requête, notamment le Riot ID pour la recherche de profil. Les futures API officielles Riot/RSO et les flux YouTube, TikTok, Instagram ou X ne sont pas encore intégrés.

Le bot ne demande ni n’enregistre le mot de passe Riot. La version actuelle ne stocke pas de jeton OAuth Riot. Si une future intégration RSO nécessite de tels jetons, la présente politique devra être mise à jour avant sa mise en service pour préciser leur stockage, leur protection et leur suppression.

## 6. Hébergement et transferts

Pour le moment, le bot et sa base sont hébergés localement, sur la machine qui exécute le bot; aucun hébergeur de base de données externe n’a été déclaré. Les fournisseurs d’API cités ci-dessus reçoivent cependant les requêtes nécessaires à leurs services. Le lieu de leurs traitements, les sauvegardes locales, les personnes ayant accès à la machine et la région d’hébergement de production restent à documenter avant publication.

**À compléter avant publication :** emplacement et délai d’effacement des sauvegardes, personnes habilitées, région de production si elle change, et pays de traitement des fournisseurs externes.

## 7. Durées de conservation

Les données personnelles liées à un joueur sont conservées tant que son compte Riot reste lié. Après une demande de retrait de la liaison, les données identifiantes et statistiques individuelles sont supprimées dans un délai maximal de **30 jours**. Les données de présence et les journaux techniques sont conservés **90 jours** puis supprimés. Les agrégats d’équipe réellement anonymisés peuvent être conservés sans limite de durée, car ils ne permettent plus d’identifier un joueur. Les sauvegardes devront suivre ces règles; leur délai d’effacement reste à définir.

Les données d’effectif ou de résultats qui identifient encore un joueur suivent la règle de suppression sous 30 jours après le retrait de sa liaison ou sa demande d’effacement. Les seules données conservées au-delà sont les agrégats anonymisés. Les pronostics non liés à une personne identifiable seront supprimés ou anonymisés lors de la clôture du traitement correspondant.

## 8. Droits et retrait du consentement

Dans les conditions prévues par la réglementation, les personnes peuvent demander l’accès à leurs données, leur rectification, leur effacement, la limitation du traitement, s’opposer à certains traitements et retirer leur consentement. Elles peuvent adresser leur demande à **noa.krieger452@gmail.com**, en précisant leur identifiant Discord et le serveur concerné. Une vérification raisonnable de l’identité pourra être demandée.

Une personne peut demander la suppression de sa liaison Riot et de ses statistiques identifiantes; le délai maximal de suppression est de 30 jours. Un administrateur RCTE peut exécuter cette demande avec la commande Discord `/datas delete` en sélectionnant le membre. La commande supprime les enregistrements identifiants de la base locale, retire les données du sondage de présence actif et tente de retirer les rôles de pronostics. Les debriefs créés depuis l’ajout de cette fonction sont reliés à l’identifiant Discord de leur auteur et supprimés par la commande. Les anciens debriefs dépourvus d’identifiant sont signalés pour vérification manuelle.

La commande ne supprime pas les anciens messages déjà publiés dans les salons Discord ni les données ou journaux conservés par les fournisseurs externes. Une demande complémentaire doit être adressée à **noa.krieger452@gmail.com** pour leur examen; la suppression auprès d’un fournisseur dépend de ses propres moyens et règles. Le retrait n’affecte pas la licéité des traitements effectués avant celui-ci. Les résultats collectifs ne seront conservés que sous forme véritablement anonymisée.

Une réclamation peut être adressée à la [CNIL](https://www.cnil.fr/fr/plaintes).

## 9. Sécurité et changements

Seul **Krieger Noa** a actuellement accès à la machine locale et à la base, selon les informations fournies. L’accès aux fonctions d’administration du bot est limité aux personnes ayant le rôle `Admin RCTE`. Le responsable met en place des mesures adaptées pour protéger les fichiers et identifiants.

La version en vigueur sera publiée à l’endroit où les membres consultent cette politique. Les mises à jour ordinaires ne donneront pas lieu à une notification individuelle. Si une modification substantielle ou une nouvelle finalité exige d’informer les personnes avant un nouveau traitement, cette information sera fournie avant sa mise en œuvre.

### Éléments à valider avant publication

1. Emplacement et délai d’effacement des sauvegardes; la machine locale est actuellement accessible à Krieger Noa seulement.
2. Base juridique des données d’équipe et des journaux; mécanisme concret de retrait de la liaison Riot.
3. Publier la politique au même endroit que celui où les membres la consultent; notifier les membres seulement si une modification substantielle l’exige.
4. Mettre à jour cette politique avant d’activer OAuth/RSO ou les flux sociaux, et confirmer les conditions des fournisseurs API.

Références : [CNIL — durées de conservation](https://www.cnil.fr/fr/passer-laction/les-durees-de-conservation-des-donnees) · [CNIL — information et droits](https://www.cnil.fr/fr/passer-laction/rgpd-les-premieres-etapes) · [Discord — âge minimum](https://support.discord.com/hc/fr/articles/360040724612-Pourquoi-Discord-me-demande-ma-date-de-naissance).
