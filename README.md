# Bot Discord - Gestionnaire d'Événements

## Description

DictaBot est un bot Discord polyvalent conçu pour simplifier l'organisation et le suivi des **événements planifiés** sur votre serveur. Construit avec `discord.py` et une architecture modulaire en "cogs", il est à la fois puissant et facile à étendre.

## Fonctionnalités

- **Gestion des événements** : Le bot se connecte aux événements planifiés de votre serveur et les gère de manière autonome.
- **Suivi des inscriptions** : Il surveille et enregistre les participants dans une base de données locale (`TinyDB`), en notant les inscriptions et désinscriptions.
- **Commandes utiles** :
  - `$annonce` : Génère et envoie une annonce formatée pour tous les événements de la semaine à venir.
  - `$list_events` : Affiche une liste claire de tous les événements actifs.
  - `$participants <ID_event>` : Donne la liste des utilisateurs inscrits à un événement en temps réel (via l'API Discord).
  - `$event_inscriptions <ID_event>` : Fournit la liste des inscrits telle qu'elle est enregistrée dans la base de données, avec la date de leur inscription.
- **Architecture modulaire** : Les fonctionnalités sont regroupées en cogs, ce qui rend le code propre et facile à maintenir ou à enrichir.

## Installation

#### 1. Prérequis

- Python 3.8 ou supérieur
- Un serveur Discord où vous avez les permissions de gestion des événements.

**Permissions Discord requises pour le bot**

- `Send Messages`
- `Read Message History`
- `View Channels`

#### 2. Cloner le dépôt

```bash
git clone [https://github.com/votre_utilisateur/DictaBot.git](https://github.com/votre_utilisateur/DictaBot.git)
cd DictaBot
```

#### 3. Créer l'environnement virtuel et installer les dépendances

`python -m venv venv`
`.\venv\Scripts\activate` # Sur Windows :
`source venv/bin/activate` # Sur macOS/Linux :
`pip install -r requirements.txt`

#### 4. Configuration

Créer un fichier `.env` à la racine du projet :

```env
DISCORD_TOKEN=votre_token_bot_discord
GUILD_ID=id_du_serveur_discord

# IDs des canaux et threads
ANNOUNCE_CHANNEL_ID=id_canal_annonces
```

DISCORD_TOKEN : Le token de votre bot. Vous pouvez l'obtenir sur le portail des développeurs Discord.
GUILD_ID : L'ID de votre serveur Discord.
ANNOUNCE_CHANNEL_ID : L'id du channel où vous souhaitez poster vos annonces.

#### 5. Lancer le bot

```bash
python src/main.py
```

## Structure du projet

```
├── src/
│   ├── bot/                 # Classe principale du bot
│   ├── cogs/                # Modules de fonctionnalités
│   ├── config/              # Fichier de configuration (DB_PATH, etc.)
│   ├── data/                # Base de données et fichiers de logs
│   ├── main.py              # Point d'entrée principal
│   └── .env                 # Variables d'environnement à créer
├── .gitignore
├── README.md
└── requirements.txt
```

## Commandes

Réussi
