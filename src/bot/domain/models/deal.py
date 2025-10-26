"""
Modèles Pydantic pour la validation et la sérialisation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class DealBase(BaseModel):
    """Modèle de base pour les promotions"""
    game_id: int
    deal_id: str
    title: str
    sale_price: float
    normal_price: float
    savings: float
    store_id: str
    deal_rating: Optional[float] = None
    release_date: Optional[datetime] = None
    last_change: Optional[datetime] = None


class DealCreate(DealBase):
    """Modèle pour créer une promotion"""
    pass


class DealUpdate(BaseModel):
    """Modèle pour mettre à jour une promotion"""
    title: Optional[str] = None
    sale_price: Optional[float] = None
    normal_price: Optional[float] = None
    savings: Optional[float] = None
    store_id: Optional[str] = None
    deal_rating: Optional[float] = None
    release_date: Optional[datetime] = None
    last_change: Optional[datetime] = None


class DealResponse(DealBase):
    """Modèle de réponse pour les promotions"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
