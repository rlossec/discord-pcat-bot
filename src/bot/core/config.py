"""Configuration centralisée du bot Discord"""
import os
from pathlib import Path
import pytz

from dotenv import load_dotenv
load_dotenv()

# Chemins du projet
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "src" / "data"

# Configuration de la base de données
DB_PATH_SQLITE = DATA_DIR / "bot.db"

# Configuration Discord
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID: int = int(os.getenv("DISCORD_GUILD_ID", "0"))
DISCORD_PREFIX: str = os.getenv("DISCORD_PREFIX", "$")

# Configuration du logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOGS_DIR: Path = DATA_DIR / "logs"
LOG_RETENTION_DAYS: int = int(os.getenv("LOG_RETENTION_DAYS", "7"))  # Rétention des logs 7 jours

# Configuration des cogs
COGS_DIR: str = "src.cogs"

# Configuration du timezone
PARIS_TIMEZONE = "Europe/Paris"
PARIS_TZ = pytz.timezone(PARIS_TIMEZONE)

# Configuration des APIs externes
CHEAPSHARK_API_URL = "https://www.cheapshark.com/api/1.0"

# Configuration des canaux Discord
ANNOUNCE_CHANNEL_ID = int(os.getenv("ANNOUNCE_CHANNEL_ID", "0")) or None

# Synchronisation périodique (secondes) - 0 pour désactiver
SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", "3600"))

def validate_config() -> bool:
    """Valide la configuration requise"""
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN est requis")
    if not DISCORD_GUILD_ID:
        raise ValueError("DISCORD_GUILD_ID est requis")
    return True
