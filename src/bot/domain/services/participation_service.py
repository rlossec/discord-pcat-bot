"""
Service métier pour les participations
"""
import logging
from typing import List
from bot.core.interfaces.unit_of_work import UnitOfWork
from bot.domain.models import ParticipationResponse

logger = logging.getLogger(__name__)


class ParticipationService:
    """Service métier pour les participations"""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    def get_event_participations(self, event_discord_id: str) -> List[ParticipationResponse]:
        """Récupère les participations d'un événement"""
        with self.uow:
            participations = self.uow.participations.get_by_event(event_discord_id)
            return [ParticipationResponse.from_orm(p) for p in participations]
    
    def add_participation(self, event_discord_id: str, user_discord_id: str) -> ParticipationResponse:
        """Ajoute une participation à un événement"""
        with self.uow:
            participation = self.uow.participations.create_participation(event_discord_id, user_discord_id)
            self.uow.commit()
            return ParticipationResponse.from_orm(participation)
    
    def remove_participation(self, event_discord_id: str, user_discord_id: str) -> bool:
        """Supprime une participation"""
        with self.uow:
            success = self.uow.participations.remove_participation(event_discord_id, user_discord_id)
            if success:
                self.uow.commit()
            return success
