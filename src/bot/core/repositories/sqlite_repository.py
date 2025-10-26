"""
Repositories SQLite pour l'accès aux données
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session
from bot.core.interfaces.repository import (
    UserRepository, EventRepository, ParticipationRepository,
    GameRepository, DealRepository, DatabaseRepository
)
from bot.domain.entities import User, Event, EventParticipation, Game, Deal

logger = logging.getLogger(__name__)


class SQLiteUserRepository(UserRepository):
    """Repository SQLite pour les utilisateurs"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, id: int) -> Optional[User]:
        return self.session.query(User).filter(User.id == id).first()
    
    def get_all(self) -> List[User]:
        return self.session.query(User).all()
    
    def get_by_discord_id(self, discord_id: str) -> Optional[User]:
        return self.session.query(User).filter(User.discord_id == discord_id).first()
    
    def get_or_create_by_discord_id(self, discord_id: str, username: str, official_name: str = None) -> User:
        user = self.get_by_discord_id(discord_id)
        if not user:
            user = User(
                discord_id=discord_id,
                username=username,
                official_name=official_name or username
            )
            self.session.add(user)
            self.session.flush()  # Pour obtenir l'ID
        else:
            # Mettre à jour le nom si nécessaire
            if user.username != username:
                user.username = username
                user.updated_at = datetime.utcnow()
        return user
    
    def create(self, entity: User) -> User:
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def update(self, entity: User) -> User:
        entity.updated_at = datetime.utcnow()
        self.session.flush()
        return entity
    
    def update_username(self, discord_id: str, new_name: str) -> Optional[User]:
        user = self.get_by_discord_id(discord_id)
        if user:
            user.username = new_name
            user.updated_at = datetime.utcnow()
            self.session.flush()
        return user
    
    def delete(self, id: int) -> bool:
        user = self.get_by_id(id)
        if user:
            self.session.delete(user)
            return True
        return False


class SQLiteEventRepository(EventRepository):
    """Repository SQLite pour les événements"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, id: int) -> Optional[Event]:
        return self.session.query(Event).filter(Event.id == id).first()
    
    def get_all(self) -> List[Event]:
        return self.session.query(Event).all()
    
    def get_by_discord_id(self, discord_id: str) -> Optional[Event]:
        return self.session.query(Event).filter(Event.discord_id == discord_id).first()
    
    def get_active_events(self) -> List[Event]:
        return self.session.query(Event).filter(Event.is_passed == False).all()
    
    def create(self, entity: Event) -> Event:
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def create_by_discord_id(self, discord_id: str, name: str) -> Event:
        event = Event(discord_id=discord_id, name=name)
        self.session.add(event)
        self.session.flush()
        return event
    
    def update(self, entity: Event) -> Event:
        entity.updated_at = datetime.utcnow()
        self.session.flush()
        return entity
    
    def update_name(self, discord_id: str, new_name: str) -> Optional[Event]:
        event = self.get_by_discord_id(discord_id)
        if event:
            event.name = new_name
            event.updated_at = datetime.utcnow()
            self.session.flush()
        return event
    
    def mark_as_passed(self, discord_id: str) -> Optional[Event]:
        event = self.get_by_discord_id(discord_id)
        if event:
            event.is_passed = True
            event.updated_at = datetime.utcnow()
            self.session.flush()
        return event
    
    def delete(self, id: int) -> bool:
        event = self.get_by_id(id)
        if event:
            self.session.delete(event)
            return True
        return False


class SQLiteParticipationRepository(ParticipationRepository):
    """Repository SQLite pour les participations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, id: int) -> Optional[EventParticipation]:
        return self.session.query(EventParticipation).filter(EventParticipation.id == id).first()
    
    def get_all(self) -> List[EventParticipation]:
        return self.session.query(EventParticipation).all()
    
    def get_by_event(self, event_discord_id: str) -> List[EventParticipation]:
        return self.session.query(EventParticipation).filter(
            EventParticipation.event_discord_id == event_discord_id
        ).all()
    
    def create(self, entity: EventParticipation) -> EventParticipation:
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def create_participation(self, event_discord_id: str, user_discord_id: str) -> EventParticipation:
        participation = EventParticipation(
            event_discord_id=event_discord_id,
            user_discord_id=user_discord_id
        )
        self.session.add(participation)
        self.session.flush()
        return participation
    
    def update(self, entity: EventParticipation) -> EventParticipation:
        self.session.flush()
        return entity
    
    def remove_participation(self, event_discord_id: str, user_discord_id: str) -> bool:
        participation = self.session.query(EventParticipation).filter(
            EventParticipation.event_discord_id == event_discord_id,
            EventParticipation.user_discord_id == user_discord_id
        ).first()
        
        if participation:
            self.session.delete(participation)
            return True
        return False
    
    def delete(self, id: int) -> bool:
        participation = self.get_by_id(id)
        if participation:
            self.session.delete(participation)
            return True
        return False


class SQLiteGameRepository(GameRepository):
    """Repository SQLite pour les jeux"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, id: int) -> Optional[Game]:
        return self.session.query(Game).filter(Game.id == id).first()
    
    def get_all(self) -> List[Game]:
        return self.session.query(Game).all()
    
    def get_by_name(self, name: str) -> Optional[Game]:
        return self.session.query(Game).filter(Game.name == name).first()
    
    def create(self, entity: Game) -> Game:
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def create_game(self, name: str, steam_id: str = None, epic_id: str = None) -> Game:
        game = Game(name=name, steam_id=steam_id, epic_id=epic_id)
        self.session.add(game)
        self.session.flush()
        return game
    
    def update(self, entity: Game) -> Game:
        entity.updated_at = datetime.utcnow()
        self.session.flush()
        return entity
    
    def delete(self, id: int) -> bool:
        game = self.get_by_id(id)
        if game:
            self.session.delete(game)
            return True
        return False


class SQLiteDealRepository(DealRepository):
    """Repository SQLite pour les promotions"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, id: int) -> Optional[Deal]:
        return self.session.query(Deal).filter(Deal.id == id).first()
    
    def get_all(self) -> List[Deal]:
        return self.session.query(Deal).all()
    
    def get_by_game(self, game_id: int) -> List[Deal]:
        return self.session.query(Deal).filter(Deal.game_id == game_id).all()
    
    def create(self, entity: Deal) -> Deal:
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def create_deal(self, game_id: int, deal_id: str, title: str, sale_price: float, 
                   normal_price: float, savings: float, store_id: str, 
                   deal_rating: float = None, release_date: datetime = None, 
                   last_change: datetime = None) -> Deal:
        deal = Deal(
            game_id=game_id,
            deal_id=deal_id,
            title=title,
            sale_price=sale_price,
            normal_price=normal_price,
            savings=savings,
            store_id=store_id,
            deal_rating=deal_rating,
            release_date=release_date,
            last_change=last_change
        )
        self.session.add(deal)
        self.session.flush()
        return deal
    
    def update(self, entity: Deal) -> Deal:
        entity.updated_at = datetime.utcnow()
        self.session.flush()
        return entity
    
    def delete(self, id: int) -> bool:
        deal = self.get_by_id(id)
        if deal:
            self.session.delete(deal)
            return True
        return False


class SQLiteDatabaseRepository(DatabaseRepository):
    """Repository SQLite pour les opérations générales"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, id: int):
        return None  # Pas applicable pour ce repository
    
    def get_all(self) -> List[Any]:
        return []  # Pas applicable pour ce repository
    
    def create(self, entity: Any):
        return None  # Pas applicable pour ce repository
    
    def update(self, entity: Any):
        return None  # Pas applicable pour ce repository
    
    def delete(self, id: int) -> bool:
        return False  # Pas applicable pour ce repository
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé de la base de données"""
        try:
            # Test de connexion simple
            self.session.execute(text("SELECT 1"))
            
            # Statistiques
            stats = self.get_stats()
            
            return {
                'status': 'healthy',
                'stats': stats,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ [DB-HEALTH] Erreur de santé : {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_stats(self) -> Dict[str, int]:
        """Récupère les statistiques de la base de données"""
        try:
            users_count = self.session.query(User).count()
            active_events_count = self.session.query(Event).filter(Event.is_passed == False).count()
            participations_count = self.session.query(EventParticipation).count()
            games_count = self.session.query(Game).count()
            
            return {
                'users': users_count,
                'active_events': active_events_count,
                'participations': participations_count,
                'games': games_count
            }
        except Exception as e:
            logger.error(f"❌ [DB-STATS] Erreur de statistiques : {e}")
            return {'users': 0, 'active_events': 0, 'participations': 0, 'games': 0}
