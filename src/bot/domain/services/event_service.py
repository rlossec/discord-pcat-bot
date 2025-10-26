"""
Service métier pour les événements
"""
import logging
from typing import List, Optional
from bot.core.interfaces.unit_of_work import UnitOfWork
from bot.domain.models import EventResponse

logger = logging.getLogger(__name__)


class EventService:
    """Service métier pour les événements"""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    def get_active_events(self) -> List[EventResponse]:
        """Récupère les événements actifs"""
        with self.uow:
            events = self.uow.events.get_active_events()
            return [EventResponse.from_orm(event) for event in events]
    
    def create_event(self, discord_id: str, name: str) -> EventResponse:
        """Crée un nouvel événement"""
        with self.uow:
            event = self.uow.events.create_by_discord_id(discord_id, name)
            self.uow.commit()
            return EventResponse.from_orm(event)
    
    def update_event_name(self, discord_id: str, new_name: str) -> Optional[EventResponse]:
        """Met à jour le nom d'un événement"""
        with self.uow:
            event = self.uow.events.update_name(discord_id, new_name)
            if event:
                self.uow.commit()
                return EventResponse.from_orm(event)
            return None
    
    def mark_event_as_passed(self, discord_id: str) -> Optional[EventResponse]:
        """Marque un événement comme terminé"""
        with self.uow:
            event = self.uow.events.mark_as_passed(discord_id)
            if event:
                self.uow.commit()
                return EventResponse.from_orm(event)
            return None
