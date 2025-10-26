"""Interface Unit of Work pour la gestion des transactions"""
from abc import ABC, abstractmethod
from typing import Protocol
from bot.core.interfaces.repository import (
    UserRepository, EventRepository, ParticipationRepository,
    GameRepository, DealRepository, DatabaseRepository
)


class UnitOfWork(Protocol):
    """Interface Unit of Work pour la gestion des transactions"""
    
    # Repositories
    users: UserRepository
    events: EventRepository
    participations: ParticipationRepository
    games: GameRepository
    deals: DealRepository
    database: DatabaseRepository
    
    def __enter__(self):
        """Context manager entry"""
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
    
    def commit(self):
        """Valide la transaction"""
        pass
    
    def rollback(self):
        """Annule la transaction"""
        pass
    
    def close(self):
        """Ferme la session"""
        pass
