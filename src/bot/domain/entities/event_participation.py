from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .entities import Base


class EventParticipation(Base):
    """Entité participation à un événement"""
    __tablename__ = 'event_participations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_discord_id = Column(String, ForeignKey('events.discord_id'), nullable=False)
    user_discord_id = Column(String, ForeignKey('users.discord_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    event = relationship("Event", foreign_keys=[event_discord_id], back_populates="participations")
    user = relationship("User", foreign_keys=[user_discord_id], back_populates="participations")
    
    # Contrainte unique
    __table_args__ = (UniqueConstraint('event_discord_id', 'user_discord_id', name='unique_participation'),)
    
    def __repr__(self):
        return f"<EventParticipation(id={self.id}, event_discord_id='{self.event_discord_id}', user_discord_id='{self.user_discord_id}')>"



