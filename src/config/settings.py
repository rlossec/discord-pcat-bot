"""
Paramètres de configuration du bot Discord.
"""

from pathlib import Path

# Configuration des chemins de fichiers
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = DATA_DIR / "event_users.json"

# Configuration des commandes
COMMAND_PREFIX = "$"


REGISTRATION_LOG_PATH = DATA_DIR / "registration_log.txt"
REGISTRATIONS_FILE_PATH = DATA_DIR / "registrations.json"
PAST_REGISTRATIONS_FILE_PATH = DATA_DIR / "past_registrations.json"
BACKUP_FILE_PATH = DATA_DIR / "old_registrations.json"


