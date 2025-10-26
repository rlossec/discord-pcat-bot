"""
Modèles Pydantic pour les jeux
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GameBase(BaseModel):
    """Modèle de base pour les jeux"""
    name: str
    steam_id: Optional[str] = None
    epic_id: Optional[str] = None


class GameCreate(GameBase):
    """Modèle pour créer un jeu"""
    pass


class GameUpdate(BaseModel):
    """Modèle pour mettre à jour un jeu"""
    name: Optional[str] = None
    steam_id: Optional[str] = None
    epic_id: Optional[str] = None


class GameResponse(GameBase):
    """Modèle de réponse pour les jeux"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True