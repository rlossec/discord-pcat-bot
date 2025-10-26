"""
Configuration du logging pour le bot Discord
Doit être importé en premier pour éviter les doublons
"""
import logging
import os

# Supprimer tous les handlers existants
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Configuration propre du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('src/data/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ],
    force=True
)

# Configuration spécifique pour Discord.py (moins verbeux)
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('discord.client').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)

# Logger principal du bot
logger = logging.getLogger('DictaBot')
