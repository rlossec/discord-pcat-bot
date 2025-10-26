"""
Services métier pour la logique applicative

Ce module est maintenu pour la compatibilité descendante.
Les services sont maintenant organisés dans le module services/.
"""

from .services import (
    UserService,
    EventService,
    ParticipationService,
    GameService,
    DealService
)

__all__ = [
    'UserService',
    'EventService',
    'ParticipationService',
    'GameService',
    'DealService',
]
