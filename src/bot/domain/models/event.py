"""
Modèles Pydantic pour les événements
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    """Modèle de base pour les événements"""
    discord_id: str
    name: str
    is_passed: bool = False


class EventCreate(EventBase):
    """Modèle pour créer un événement"""
    pass


class EventUpdate(BaseModel):
    """Modèle pour mettre à jour un événement"""
    name: Optional[str] = None
    is_passed: Optional[bool] = None


class EventResponse(EventBase):
    """Modèle de réponse pour les événements"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

