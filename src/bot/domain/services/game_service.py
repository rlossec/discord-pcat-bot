"""
Service métier pour les jeux
"""
import logging
from typing import List, Optional
from bot.core.interfaces.unit_of_work import UnitOfWork
from bot.domain.models import GameResponse

logger = logging.getLogger(__name__)


class GameService:
    """Service métier pour les jeux"""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    def get_all_games(self) -> List[GameResponse]:
        """Récupère tous les jeux"""
        with self.uow:
            games = self.uow.games.get_all()
            return [GameResponse.from_orm(game) for game in games]
    
    def get_game_by_name(self, name: str) -> Optional[GameResponse]:
        """Récupère un jeu par son nom"""
        with self.uow:
            game = self.uow.games.get_by_name(name)
            return GameResponse.from_orm(game) if game else None
    
    def create_game(self, name: str, steam_id: str = None, epic_id: str = None) -> GameResponse:
        """Crée un nouveau jeu"""
        with self.uow:
            game = self.uow.games.create_game(name, steam_id, epic_id)
            self.uow.commit()
            return GameResponse.from_orm(game)
