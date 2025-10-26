"""Interfaces (abstractions) pour les repositories"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime


class Repository(ABC):
    """Interface de base pour tous les repositories"""
    
    @abstractmethod
    def get_by_id(self, id: int):
        """Récupère une entité par son ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Any]:
        """Récupère toutes les entités"""
        pass
    
    @abstractmethod
    def create(self, entity: Any):
        """Crée une nouvelle entité"""
        pass
    
    @abstractmethod
    def update(self, entity: Any):
        """Met à jour une entité"""
        pass
    
    @abstractmethod
    def delete(self, id: int):
        """Supprime une entité par son ID"""
        pass


class UserRepository(Repository):
    """Repository pour les utilisateurs"""
    
    @abstractmethod
    def get_by_discord_id(self, discord_id: str):
        """Récupère un utilisateur par son ID Discord"""
        pass
    
    @abstractmethod
    def get_or_create_by_discord_id(self, discord_id: str, username: str, official_name: str = None):
        """Récupère ou crée un utilisateur par son ID Discord"""
        pass
    
    @abstractmethod
    def update_username(self, discord_id: str, new_name: str):
        """Met à jour le nom d'un utilisateur"""
        pass


class EventRepository(Repository):
    """Repository pour les événements"""
    
    @abstractmethod
    def get_by_discord_id(self, discord_id: str):
        """Récupère un événement par son ID Discord"""
        pass
    
    @abstractmethod
    def get_active_events(self) -> List[Any]:
        """Récupère les événements actifs"""
        pass
    
    @abstractmethod
    def create_by_discord_id(self, discord_id: str, name: str):
        """Crée un événement avec un ID Discord"""
        pass
    
    @abstractmethod
    def update_name(self, discord_id: str, new_name: str):
        """Met à jour le nom d'un événement"""
        pass
    
    @abstractmethod
    def mark_as_passed(self, discord_id: str):
        """Marque un événement comme terminé"""
        pass


class ParticipationRepository(Repository):
    """Repository pour les participations"""
    
    @abstractmethod
    def get_by_event(self, event_discord_id: str) -> List[Any]:
        """Récupère les participations d'un événement"""
        pass
    
    @abstractmethod
    def create_participation(self, event_discord_id: str, user_discord_id: str):
        """Crée une participation"""
        pass
    
    @abstractmethod
    def remove_participation(self, event_discord_id: str, user_discord_id: str):
        """Supprime une participation"""
        pass


class GameRepository(Repository):
    """Repository pour les jeux"""
    
    @abstractmethod
    def get_by_name(self, name: str):
        """Récupère un jeu par son nom"""
        pass
    
    @abstractmethod
    def create_game(self, name: str, steam_id: str = None, epic_id: str = None):
        """Crée un nouveau jeu"""
        pass


class DealRepository(Repository):
    """Repository pour les promotions"""
    
    @abstractmethod
    def get_by_game(self, game_id: int) -> List[Any]:
        """Récupère les promotions d'un jeu"""
        pass
    
    @abstractmethod
    def create_deal(self, game_id: int, deal_id: str, title: str, sale_price: float, 
                   normal_price: float, savings: float, store_id: str, 
                   deal_rating: float, release_date: datetime, last_change: datetime):
        """Crée une nouvelle promotion"""
        pass


class DatabaseRepository(Repository):
    """Repository pour les opérations générales de base de données"""
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé de la base de données"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        """Récupère les statistiques de la base de données"""
        pass
