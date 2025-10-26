"""
Service métier pour les utilisateurs
"""
import logging
from typing import Optional
from bot.core.interfaces.unit_of_work import UnitOfWork
from bot.domain.models import UserResponse

logger = logging.getLogger(__name__)


class UserService:
    """Service métier pour les utilisateurs"""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    def get_user_by_discord_id(self, discord_id: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par son ID Discord"""
        with self.uow:
            user = self.uow.users.get_by_discord_id(discord_id)
            return UserResponse.from_orm(user) if user else None
    
    def create_or_update_user(self, discord_id: str, username: str, official_name: str = None) -> UserResponse:
        """Crée ou met à jour un utilisateur"""
        with self.uow:
            user = self.uow.users.get_or_create_by_discord_id(discord_id, username, official_name)
            self.uow.commit()
            return UserResponse.from_orm(user)
    
    def update_username(self, discord_id: str, new_name: str) -> Optional[UserResponse]:
        """Met à jour le nom d'un utilisateur"""
        with self.uow:
            user = self.uow.users.update_username(discord_id, new_name)
            if user:
                self.uow.commit()
                return UserResponse.from_orm(user)
            return None
