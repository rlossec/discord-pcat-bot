"""Gestion du moteur de base de données SQLAlchemy"""
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from bot.core.config import DB_PATH_SQLITE, LOG_LEVEL

logger = logging.getLogger(__name__)


class DatabaseEngine:
    """Gestionnaire du moteur de base de données"""
    
    def __init__(self, db_path: Path = DB_PATH_SQLITE):
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Configure le moteur de base de données"""
        try:
            # Créer le dossier data s'il n'existe pas
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Configuration de l'URL de la base de données
            database_url = f"sqlite:///{self.db_path}"
            
            # Créer le moteur
            self.engine = create_engine(
                database_url,
                echo=LOG_LEVEL == "DEBUG",
                pool_pre_ping=True,
                connect_args={"check_same_thread": False}  # Pour SQLite
            )
            
            # Créer la factory de sessions
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"✅ [DATABASE] Moteur configuré : {database_url}")
            
        except Exception as e:
            logger.error(f"❌ [DATABASE] Erreur de configuration : {e}")
            raise
    
    def get_session(self) -> Session:
        """Retourne une nouvelle session de base de données"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Crée toutes les tables"""
        from bot.domain.entities import Base
        Base.metadata.create_all(bind=self.engine)
        logger.info("✅ [DATABASE] Tables créées")
    
    def close(self):
        """Ferme le moteur de base de données"""
        if self.engine:
            self.engine.dispose()
            logger.info("🛑 [DATABASE] Moteur fermé")


# Instance globale du moteur
db_engine = DatabaseEngine()
