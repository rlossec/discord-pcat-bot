"""
Service métier pour les promotions
"""
import logging
from typing import List
from datetime import datetime
from bot.core.interfaces.unit_of_work import UnitOfWork
from bot.domain.models import DealResponse

logger = logging.getLogger(__name__)


class DealService:
    """Service métier pour les promotions"""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    def get_deals_by_game(self, game_id: int) -> List[DealResponse]:
        """Récupère les promotions d'un jeu"""
        with self.uow:
            deals = self.uow.deals.get_by_game(game_id)
            return [DealResponse.from_orm(deal) for deal in deals]
    
    def create_deal(self, game_id: int, deal_id: str, title: str, sale_price: float, 
                   normal_price: float, savings: float, store_id: str, 
                   deal_rating: float = None, release_date: datetime = None, 
                   last_change: datetime = None) -> DealResponse:
        """Crée une nouvelle promotion"""
        with self.uow:
            deal = self.uow.deals.create_deal(
                game_id, deal_id, title, sale_price, normal_price, 
                savings, store_id, deal_rating, release_date, last_change
            )
            self.uow.commit()
            return DealResponse.from_orm(deal)
