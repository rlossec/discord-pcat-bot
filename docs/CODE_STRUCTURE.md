# 📂 Structure du Code

## Organisation des Répertoires

```
DictaBot/
├── docs/                      # Documentation du projet
│   ├── ARCHITECTURE.md        # Architecture technique
│   └── CODE_STRUCTURE.md      # Ce fichier
├── scripts/                   # Scripts
├── src/                       # Code source du bot
│   ├── bot/                   # Code principal du bot
│   ├── cogs/                  # Commands Discord (Cogs)
│   ├── data/                  # Base de données et logs
│   └── main.py                # Point d'entrée principal
├── tests/                     # Tests unitaires et d'intégration
└── requirements.txt           # Dépendances Python
```

---

## Détail des Modules Principaux

### 📁 `src/bot/` - Code Principal

#### `bot/core/`

**Rôle** : Couche d'infrastructure et configuration

```
core/
├── config.py                  # Configuration globale (DB_PATH, LOG_LEVEL, etc.)
├── database.py                # DatabaseEngine - gestion de SQLAlchemy
├── logging_config.py          # Configuration du logging
├── utils.py                   # Utilitaires généraux
├── interfaces/                # Interfaces abstraites
│   ├── repository.py          # Interfaces des repositories
│   └── unit_of_work.py        # Interface Unit of Work
└── repositories/              # Implémentations des repositories
    └── sqlite_repository.py   # Repositories SQLite
```

**Fichiers clés** :

- `config.py` : Constantes globales (chemins, niveaux de log)
- `database.py` : Moteur SQLAlchemy, gestion des sessions
- `interfaces/` : Contrats abstraits (protocoles)
- `repositories/` : Implémentations SQLite des repositories

#### `bot/domain/`

**Rôle** : Logique métier et modèles de données

```
domain/
├── entities/                  # Entités SQLAlchemy (ORM)
│   ├── user.py               # Modèle User (base de données)
│   ├── event.py               # Modèle Event
│   ├── event_participation.py
│   ├── game.py
│   └── deal.py
├── models/                    # Modèles Pydantic (API/validation)
│   ├── user.py               # UserResponse, UserCreate, etc.
│   ├── event.py
│   ├── participation.py
│   ├── game.py
│   └── deal.py
├── services/                  # Services métier
│   ├── user_service.py       # Opérations sur les utilisateurs
│   ├── event_service.py      # Opérations sur les événements
│   ├── participation_service.py
│   ├── game_service.py
│   └── deal_service.py
└── services.py               # Export des services
```

**Distinction importante** :

- **Entities** (`entities/`) : Modèles SQLAlchemy pour la base de données
- **Models** (`models/`) : Modèles Pydantic pour validation/API
- **Services** : Orchestration de la logique métier

#### `bot/infrastructure/`

**Rôle** : Implémentations concrètes

```
infrastructure/
├── unit_of_work_impl.py      # Implémentation SQLiteUnitOfWork
└── ...
```

**Fichier clé** :

- `unit_of_work_impl.py` : Gestion des transactions avec context manager

---

### 📁 `src/cogs/` - Commands Discord

```
cogs/
├── general.py                # Commandes générales (help, info)
├── events.py                 # Gestion des événements
├── deals.py                  # Gestion des promotions
└── announcement.py           # Annonces automatiques
```

**Rôle** : Interface utilisateur Discord, valide les entrées, appelle les services

**Structure typique** :

```python
# cogs/events.py
@bot.tree.command(name="event")
async def create_event(interaction, name: str):
    # Validation
    # Appel au service
    # Réponse à l'utilisateur
```

---

### 📁 `scripts/` - Scripts d'Administration

```
scripts/
├── run.py                     # Script principal (point d'accès unique)
├── crud/                      # Scripts CRUD
│   ├── crud.py               # Routeur principal
│   ├── crud_users.py         # Gestion utilisateurs
│   ├── crud_events.py        # Gestion événements
│   ├── crud_participations.py
│   └── demo_crud.py          # Démonstrations
└── utils/                     # Utilitaires
    ├── cleanup.py            # Nettoyage de la base
    ├── debug_detached_error.py
    ├── example_usage.py      # Exemples d'utilisation
    └── service_helper.py     # Helpers pour les services
```

**Usage** :

```bash
python scripts/run.py crud users list --limit 5
python scripts/run.py utils cleanup
```

---

## Hiérarchie des Imports

### Ordre d'Import Recommandé

1. **Modules standards** (sys, os, pathlib)
2. **Modules externes** (discord, sqlalchemy, pydantic)
3. **Modules internes core** (config, database)
4. **Modules internes domain** (entities, models, services)
5. **Modules internes infrastructure** (unit_of_work_impl)

### Exemple

```python
# 1. Standards
import sys
from pathlib import Path

# 2. Externes
from sqlalchemy.orm import Session

# 3. Core
from bot.core.config import DB_PATH_SQLITE

# 4. Domain
from bot.domain.entities import User
from bot.domain.models import UserResponse

# 5. Infrastructure
from bot.infrastructure.unit_of_work_impl import SQLiteUnitOfWork
```

---

## Patterns de Nommage

### Fichiers et Modules

- **Snake_case** : `user_service.py`, `event_participation.py`
- **Descriptifs** : Noms qui expriment le contenu

### Classes

- **PascalCase** : `UserService`, `EventParticipation`, `SQLiteRepository`
- **Suffixes** :
  - `Service` : Services métier
  - `Repository` : Repositories
  - `Response` : Modèles Pydantic de réponse
  - `Create` / `Update` : Modèles Pydantic pour création/mise à jour

### Variables et Fonctions

- **snake_case** : `discord_id`, `create_user()`, `get_by_discord_id()`

---

## Conventions de Code

### Services Métier

```python
class UserService:
    """Service métier pour les utilisateurs"""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def create_user(self, discord_id: str, username: str):
        """Crée un utilisateur"""
        with self.uow:  # Context manager
            user = self.uow.users.get_or_create_by_discord_id(...)
            self.uow.commit()  # Transaction
            return user
```

### Cogs Discord

```python
@bot.tree.command(name="example")
@app_commands.describe(param="Description du paramètre")
async def example_command(interaction, param: str):
    """Documentation de la commande"""
    # Validation
    # Traitement
    # Réponse
    await interaction.response.send_message("...")
```

### Repositories

```python
class SQLiteUserRepository(UserRepository):
    def get_by_discord_id(self, discord_id: str):
        """Récupère un utilisateur par son ID Discord"""
        return self.session.query(User).filter(...).first()
```

---

## Points d'Entrée

### Démarrage du Bot

```python
# src/main.py
from bot.main import main

if __name__ == "__main__":
    main()
```

### Scripts CRUD

```bash
# Via le script principal
python scripts/run.py crud users list

# Directement
python scripts/crud/crud_users.py list
```

---

## Organisation des Entités Métier

### User

- **Entité** : `bot/domain/entities/user.py`
- **Modèle** : `bot/domain/models/user.py`
- **Service** : `bot/domain/services/user_service.py`
- **Repository** : `SQLiteUserRepository` dans `sqlite_repository.py`

### Event

- **Entité** : `bot/domain/entities/event.py`
- **Modèle** : `bot/domain/models/event.py`
- **Service** : `bot/domain/services/event_service.py`
- **Repository** : `SQLiteEventRepository`

### EventParticipation

- **Entité** : `bot/domain/entities/event_participation.py`
- **Modèle** : `bot/domain/models/participation.py`
- **Service** : `bot/domain/services/participation_service.py`
- **Repository** : `SQLiteParticipationRepository`

---

## Flux de Développement

### Ajouter une Nouvelle Fonctionnalité

1. **Définir l'entité** : `entities/ma_nouvelle_entite.py`
2. **Créer le modèle** : `models/ma_nouvelle_entite.py`
3. **Implémenter le repository** : `repositories/sqlite_repository.py`
4. **Créer le service** : `services/ma_nouvelle_entite_service.py`
5. **Ajouter au Unit of Work** : `infrastructure/unit_of_work_impl.py`
6. **Créer le Cog** : `cogs/ma_nouvelle_fonctionnalite.py`
7. **Tester** : Via les scripts CRUD ou tests unitaires

---

## Fichiers de Configuration

- `config.py` : Configuration globale
- `logging_config.py` : Configuration du logging
- `database.py` : Configuration SQLAlchemy
- `requirements.txt` : Dépendances Python

---

## Points d'Attention

⚠️ **Ne pas créer de dépendances circulaires**

- Domain → Core : ✅ OK
- Domain → Infrastructure : ❌ Éviter
- Core → Domain : ❌ Éviter

⚠️ **Utiliser le Unit of Work pour les transactions**

- Toujours utiliser le context manager `with`
- Toujours appeler `commit()` après les modifications

⚠️ **Séparer les modèles Entities et Models**

- Entities : Pour la base de données
- Models : Pour la validation et les API
