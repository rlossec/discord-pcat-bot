"""
Implémentation Unit of Work pour la gestion des transactions
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from bot.core.database import db_engine
from bot.core.interfaces.unit_of_work import UnitOfWork
from bot.core.repositories.sqlite_repository import (
    SQLiteUserRepository, SQLiteEventRepository, SQLiteParticipationRepository,
    SQLiteGameRepository, SQLiteDealRepository, SQLiteDatabaseRepository
)

logger = logging.getLogger(__name__)


class SQLiteUnitOfWork:
    """Implémentation Unit of Work pour SQLite"""
    
    def __init__(self):
        self.session: Optional[Session] = None
        self._repositories = {}
    
    def __enter__(self):
        """Context manager entry - démarre une transaction"""
        self.session = db_engine.get_session()
        
        # Initialiser les repositories avec la session
        self.users = SQLiteUserRepository(self.session)
        self.events = SQLiteEventRepository(self.session)
        self.participations = SQLiteParticipationRepository(self.session)
        self.games = SQLiteGameRepository(self.session)
        self.deals = SQLiteDealRepository(self.session)
        self.database = SQLiteDatabaseRepository(self.session)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - gère la transaction"""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        
        self.close()
    
    def commit(self):
        """Valide la transaction"""
        if self.session:
            try:
                self.session.commit()
                logger.debug("✅ [UOW] Transaction commitée")
            except Exception as e:
                logger.error(f"❌ [UOW] Erreur lors du commit : {e}")
                self.session.rollback()
                raise
    
    def rollback(self):
        """Annule la transaction"""
        if self.session:
            try:
                self.session.rollback()
                logger.debug("🔄 [UOW] Transaction annulée")
            except Exception as e:
                logger.error(f"❌ [UOW] Erreur lors du rollback : {e}")
    
    def close(self):
        """Ferme la session"""
        if self.session:
            try:
                self.session.close()
                logger.debug("🛑 [UOW] Session fermée")
            except Exception as e:
                logger.error(f"❌ [UOW] Erreur lors de la fermeture : {e}")
            finally:
                self.session = None


def create_unit_of_work() -> UnitOfWork:
    """Factory pour créer une nouvelle Unit of Work"""
    return SQLiteUnitOfWork()
