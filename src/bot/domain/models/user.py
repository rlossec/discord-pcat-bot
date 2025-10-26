"""
Modèles Pydantic pour les utilisateurs
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Modèle de base pour les utilisateurs"""
    discord_id: str
    username: str
    official_name: Optional[str] = None


class UserCreate(UserBase):
    """Modèle pour créer un utilisateur"""
    discord_id: str
    username: str
    official_name: Optional[str] = None


class UserUpdate(BaseModel):
    """Modèle pour mettre à jour un utilisateur"""
    username: Optional[str] = None
    official_name: Optional[str] = None


class UserResponse(UserBase):
    """Modèle de réponse pour les utilisateurs"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True



