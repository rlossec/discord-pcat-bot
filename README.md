# Bot Discord - Gestionnaire d'Événements

## Description

Bot Discord pour la gestion automatique des événements et des inscriptions. Le bot gère le suivi des inscriptions aux événements, et la création d'annonces.

## Fonctionnalités

- **Suivi des inscriptions** : Gestion des participants aux événements
- **Commandes utilisateur** : Affichage des inscrits et création d'annonces
- **Logging** : Journalisation des actions

## Installation

### Prérequis

- Python 3.8+

1. **Configuration des variables d'environnement**

   Créer un fichier `.env` à la racine du projet :

   ```env
   DICTABOT_TOKEN=votre_token_bot_discord
   GUILD_ID=id_du_serveur_discord
   ORGANISATEUR_ROLE_ID=id_du_role_organisateur

   # IDs des canaux et threads
   ANNOUNCE_CHANNEL_ID=id_canal_annonces
   ```

2. **Permissions Discord requises**
   - `Send Messages`
   - `Read Message History`
   - `View Channels`

## Utilisation

### Démarrage du bot

```bash
python main.py
```

### Commandes disponibles

- `$inscrits <event_id>` : Affiche la liste des inscrits pour un événement
- `$annonce` : Crée un message d'annonce des événements du week-end

## Structure du projet

```
DictaBot/
├── src/
│   ├── main.py              # Point d'entrée principal
│   ├── utils.py             # Fonctions utilitaires
│   ├── requirements.txt     # Dépendances Python
│   └── .env                 # Variables d'environnement (à créer)
├── data/                    # Données persistantes
│   ├── registrations.json
│   ├── registration_log.txt
│   └── old_registrations.json
```

## Data et Logs

- **Fichier de log** : `data/registration_log.txt`
- **Données d'inscription** : `data/registrations.json`
- **Sauvegarde** : `data/old_registrations.json`