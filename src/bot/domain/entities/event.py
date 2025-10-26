from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .entities import Base


class Event(Base):
    """Entité événement Discord"""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    is_passed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    participations = relationship("EventParticipation", foreign_keys="EventParticipation.event_discord_id", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Event(id={self.id}, discord_id='{self.discord_id}', name='{self.name}', is_passed={self.is_passed})>"



