"""
Module des modèles Pydantic pour la validation et la sérialisation
Exporte tous les modèles du domaine
"""

# Modèles utilisateur
from .user import UserBase, UserCreate, UserUpdate, UserResponse

# Modèles événement
from .event import EventBase, EventCreate, EventUpdate, EventResponse

# Modèles participation
from .participation import ParticipationBase, ParticipationCreate, ParticipationResponse

# Modèles jeu
from .game import GameBase, GameCreate, GameUpdate, GameResponse

# Modèles promotion
from .deal import DealBase, DealCreate, DealUpdate, DealResponse

__all__ = [
    # User models
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    # Event models
    'EventBase',
    'EventCreate',
    'EventUpdate',
    'EventResponse',
    # Participation models
    'ParticipationBase',
    'ParticipationCreate',
    'ParticipationResponse',
    # Game models
    'GameBase',
    'GameCreate',
    'GameUpdate',
    'GameResponse',
    # Deal models
    'DealBase',
    'DealCreate',
    'DealUpdate',
    'DealResponse',
]
