from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .entities import Base


class Deal(Base):
    """Entité promotion de jeu"""
    __tablename__ = 'deals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    deal_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    sale_price = Column(Float, nullable=False)
    normal_price = Column(Float, nullable=False)
    savings = Column(Float, nullable=False)
    store_id = Column(String, nullable=False)
    deal_rating = Column(Float, nullable=True)
    release_date = Column(DateTime, nullable=True)
    last_change = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    game = relationship("Game", back_populates="deals")
    
    def __repr__(self):
        return f"<Deal(id={self.id}, game_id={self.game_id}, deal_id='{self.deal_id}', title='{self.title}', sale_price={self.sale_price})>"
