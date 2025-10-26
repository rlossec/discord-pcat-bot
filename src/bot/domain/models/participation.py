"""
Modèles Pydantic pour les participations
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ParticipationBase(BaseModel):
    """Modèle de base pour les participations"""
    event_discord_id: str
    user_discord_id: str


class ParticipationCreate(ParticipationBase):
    """Modèle pour créer une participation"""
    pass


class ParticipationResponse(ParticipationBase):
    """Modèle de réponse pour les participations"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

