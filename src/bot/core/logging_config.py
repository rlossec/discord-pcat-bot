"""
Configuration du logging pour le bot Discord.
"""
import logging
from datetime import datetime, timedelta
from pathlib import Path

from bot.core.config import LOGS_DIR, LOG_RETENTION_DAYS, PARIS_TZ


def _get_session_log_path() -> Path:
    """Retourne le chemin du fichier de log pour la session en cours."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(PARIS_TZ)
    filename = f"bot_{now.strftime('%Y-%m-%d_%H-%M-%S')}.log"
    return LOGS_DIR / filename


def _cleanup_old_logs() -> None:
    """Supprime les fichiers de log plus anciens que LOG_RETENTION_DAYS."""
    if not LOGS_DIR.exists():
        return
    cutoff = datetime.now(PARIS_TZ) - timedelta(days=LOG_RETENTION_DAYS)
    removed = 0
    for path in LOGS_DIR.glob("bot_*.log"):
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=PARIS_TZ)
            if mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError:
            pass
    if removed:
        logging.getLogger("DictaBot").info(
            "🧹 [LOGS] %d fichier(s) de log supprimé(s) (rétention > %d jours)",
            removed,
            LOG_RETENTION_DAYS,
        )


# Supprimer tous les handlers existants
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Chemin du fichier de log pour cette session
_session_log_path = _get_session_log_path()

# Configuration propre du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(_session_log_path, encoding="utf-8"),
        logging.StreamHandler(),
    ],
    force=True,
)

# Nettoyage des anciens logs (après config du logger)
_cleanup_old_logs()

# Configuration spécifique pour Discord.py (moins verbeux)
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.client").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)

# Logger principal du bot
logger = logging.getLogger("DictaBot")
logger.info("📁 [LOGS] Session : %s", _session_log_path.name)
