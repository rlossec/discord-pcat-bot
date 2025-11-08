# 🤖 Bot Discord Polyvalent

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.6.4-green.svg)](https://discordpy.readthedocs.io)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.43-red.svg)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Ce bot custom est un bot Discord polyvalent conçu pour simplifier l'organisation et le suivi des **événements planifiés** sur votre serveur Discord. Il offre également des fonctionnalités de suivi des promotions de jeux vidéo.

## ✨ Fonctionnalités Principales

### 📅 Gestion des Événements

- **Synchronisation automatique** avec les événements Discord
- **Suivi des inscriptions** en temps réel
- **Commandes pratiques** pour lister et gérer les événements
- **Archivage automatique** des événements terminés

### 🎮 Suivi des Promotions de Jeux

- **Intégration CheapShark API** pour les meilleures offres
- **Gestion des jeux suivis** avec commandes dédiées
- **Liens directs** vers Steam et les stores

### 🔧 Architecture Modulaire

- **Clean Architecture** avec séparation des responsabilités
- **Système de cogs** pour une extensibilité facile
- **Base de données SQLite** avec SQLAlchemy ORM
- **Logging centralisé** et monitoring
- **Configuration flexible** via variables d'environnement

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.9 ou supérieur
- Token de bot Discord
- Serveur Discord avec permissions de gestion des événements
- **uv** (recommandé) ou **venv** pour la gestion des dépendances

### Installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/votre_utilisateur/DictaBot.git
cd DictaBot
```

2. **Installer les dépendances**

#### Option A : Avec uv (Recommandé) ⚡

```bash
# Installer uv (si pas déjà installé)
pip install uv
# Installer les dépendances avec uv
uv sync
```

#### Option B : Avec venv traditionnel 🐍

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\activate # Windows
source venv/bin/activate # macOS/Linux

# Installer les dépendances
pip install -r requirements.txt
```

3. **Configuration**
   Créer un fichier `.env` dans le dossier `src` :

```env
DISCORD_TOKEN=votre_token_bot_discord
DISCORD_GUILD_ID=id_du_serveur_discord
```

4. **Lancer le bot**

```bash
uv run python src/main.py # avec uv
```

```bash
python src/main.py # avec un environnement virtuel actif
```

## 📋 Commandes Disponibles

### 🎮 Commandes Générales

- `$help` - Aide et liste des commandes

### 📅 Commandes d'Événements

- `$list_events` - Liste des événements actifs
- `$participants <ID>` - Participants d'un événement

### 🎯 Commandes de Jeux

- `$follow_game <nom>` - Suivre un jeu
- `$unfollow_game <nom>` - Arrêter le suivi
- `$list_games` - Jeux suivis

## 📚 Documentation Complète

## 🏗️ Structure du Projet

```
src/
├── bot/                      # Cœur du bot (Clean Architecture)
├── main.py               # Point d'entrée principal
├── core/                 # Configuration et infrastructure
│   │   ├── config.py         # Configuration centralisée
│   │   ├── database.py       # Gestion SQLAlchemy
│   │   ├── logging_config.py # Configuration logging
│   │   ├── utils.py          # Fonctions utilitaires
│   │   ├── interfaces/       # Contrats abstraits
│   │   │   ├── repository.py
│   │   │   └── unit_of_work.py
│   │   └── repositories/     # Implémentations SQLite
│   │       └── sqlite_repository.py
│   ├── domain/               # Logique métier
│   │   ├── entities.py       # Entités SQLAlchemy
│   │   ├── models.py         # Modèles Pydantic
│   │   └── services.py       # Services métier
│   └── infrastructure/       # Implémentations concrètes
│       └── unit_of_work_impl.py
├── cogs/                     # Modules de fonctionnalités
│   ├── events.py             # Gestion événements
│   ├── deals.py              # Suivi promotions
│   ├── general.py            # Commandes générales
│   └── announcement.py       # Annonces événements
├── data/                     # Données persistantes
│   ├── bot.db                # Base SQLite
│   └── bot.log               # Logs
└── main.py                   # Point d'entrée simple
scripts/                      # Scripts utilitaires
├── crud/                     # Opérations CRUD
├── tests/                    # Tests unitaires
└── utils/                    # Utilitaires
docs/                         # Documentation
pyproject.toml             # Configuration moderne
README.md
```

## 🔧 Technologies Utilisées

- **[Discord.py](https://discordpy.readthedocs.io)** - API Discord pour Python
- **[SQLAlchemy](https://sqlalchemy.org)** - ORM pour la gestion de base de données
- **[SQLite](https://sqlite.org)** - Base de données légère et portable
- **[uv](https://github.com/astral-sh/uv)** - Gestionnaire de dépendances Python ultra-rapide
- **[Pydantic](https://pydantic-docs.helpmanual.io)** - Validation de données et modèles
- **[aiohttp](https://aiohttp.readthedocs.io)** - Client HTTP asynchrone
- **[pytest](https://pytest.org)** - Framework de tests
- **Clean Architecture** - Architecture logicielle avec séparation des couches

## 🚀 Fonctionnalités Avancées

### Synchronisation Automatique

- **Utilisateurs** : Synchronisation des membres du serveur
- **Événements** : Suivi automatique des événements Discord
- **Participations** : Mise à jour en temps réel des inscriptions

### Monitoring et Observabilité

- **Logs structurés** avec niveaux de priorité
- **Health checks** automatiques
- **Statistiques** en temps réel
- **Métriques** de performance

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
