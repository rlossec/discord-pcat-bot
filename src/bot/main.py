"""
Point d'entrée principal du bot Discord
"""

import os

import discord
from discord.ext import commands

from bot.core.logging_config import logger
from bot.core.config import validate_config, DISCORD_TOKEN, DISCORD_GUILD_ID, DISCORD_PREFIX
from bot.core.database import db_engine

from bot.infrastructure.unit_of_work_impl import create_unit_of_work
from bot.domain.services import (
    UserService, EventService, ParticipationService,
    GameService, DealService, SynchronizationService
)


SYNC_NOTIFICATION_CHANNEL_ID = 1287444752421097493


class DiscordBot(commands.Bot):
    """Bot Discord principal avec Clean Architecture"""
    
    def __init__(self):
        # Validation de la configuration
        validate_config()
        
        # Configuration du bot Discord
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guild_scheduled_events = True
        super().__init__(command_prefix=DISCORD_PREFIX, intents=intents)
        
        # Services métier
        self.uow_factory = create_unit_of_work
        self.user_service = None
        self.event_service = None
        self.participation_service = None
        self.game_service = None
        self.deal_service = None
        self.sync_service = SynchronizationService(self.uow_factory, SYNC_NOTIFICATION_CHANNEL_ID)
        
        # Configuration
        self.token = DISCORD_TOKEN
        self.guild_id = DISCORD_GUILD_ID
        
        logger.info("🚀 [STARTUP] Démarrage de DictaBot...")
    
    async def setup_hook(self):
        """Configuration initiale du bot"""
        # Créer les tables
        db_engine.create_tables()
               
        # Initialiser les services métier
        uow = self.uow_factory()
        self.user_service = UserService(uow)
        self.event_service = EventService(uow)
        self.participation_service = ParticipationService(uow)
        self.game_service = GameService(uow)
        self.deal_service = DealService(uow)
        
        # Charger les cogs
        await self.load_cogs()
        
        logger.info("✅ [SETUP] Configuration terminée")
    
    async def load_cogs(self):
        """Charge tous les cogs"""
        logger.info("🔧 [COGS] Chargement des extensions...")
        
        # Chemin absolu pour trouver les cogs
        # Ce fichier est dans src/bot/main.py, donc on remonte de deux niveaux
        bot_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.dirname(bot_dir)
        cogs_path = os.path.join(src_dir, "cogs")
        
        logger.info(f"🔍 [COGS] Chemin utilisé : {cogs_path}")
        
        if not os.path.exists(cogs_path):
            logger.error(f"❌ [COGS] Le dossier {cogs_path} n'existe pas !")
            return
        
        cogs_dir = "cogs"  # Pour le load_extension

        files = [f for f in os.listdir(cogs_path) if f.endswith(".py") and f != "__init__.py"]
        logger.info(f"📄 [COGS] Fichiers trouvés : {files}")

        loaded_cogs = 0
        for filename in files:
            extension = f"{cogs_dir}.{filename[:-3]}"
            try:
                await self.load_extension(extension)
                logger.info(f"✅ [COGS] {filename} chargé")
                loaded_cogs += 1
            except Exception as e:
                logger.error(f"❌ [COGS] Erreur lors du chargement de {filename} : {e}")
        
        logger.info(f"📊 [COGS] {loaded_cogs} cogs chargés avec succès")
    
    async def on_ready(self):
        """Event appelé quand le bot est prêt"""
        logger.info(f"✅ [DISCORD] Connecté en tant que {self.user} (ID: {self.user.id})")
        
        # Vérification du serveur
        logger.info("\n🏰 [GUILD] Vérification du serveur...")
        guild_names = [g.name for g in self.guilds]
        logger.info(f"📋 [GUILD] Guilds disponibles : {guild_names}")
        logger.info(f"🔍 [GUILD] Recherche de la guild ID: {self.guild_id}")
        
        guild = self.get_guild(self.guild_id)
        if guild is None:
            logger.error(f"❌ Guild avec l'ID {self.guild_id} introuvable")
            logger.error(f"❌ Guilds disponibles: {[f'{g.name} (ID: {g.id})' for g in self.guilds]}")
            return

        logger.info(f"✅ [GUILD] Serveur trouvé : {guild.name}")
        
        # Vérification de la santé de la base de données
        await self._check_database_health()
        
        # Synchronisation des données
        logger.info("🔄 [SYNC] Synchronisation avec Discord...")
        await self.sync_service.sync_guild(self, guild)
        
        # Résumé final
        await self._display_startup_summary()
    
    async def _check_database_health(self):
        """Vérifie la santé de la base de données"""
        try:
            logger.info("🔍 [DB-HEALTH] Vérification de l'intégrité...")
            
            uow = self.uow_factory()
            with uow:
                health = uow.database.health_check()
                
                if health['status'] == 'healthy':
                    stats = health['stats']
                    logger.info("📊 [DB-HEALTH] Statistiques de la base :")
                    logger.info(f"  - Utilisateurs enregistrés : {stats['users']}")
                    logger.info(f"  - Événements actifs : {stats['active_events']}")
                    logger.info(f"  - Participations totales : {stats['participations']}")
                    logger.info(f"  - Jeux en base : {stats['games']}")
                    logger.info("✅ [DB-HEALTH] Base de données saine")
                else:
                    logger.error(f"❌ [DB-HEALTH] Base de données non saine: {health.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ [DB-HEALTH] Erreur lors de la vérification: {e}")
    
    async def _display_startup_summary(self):
        """Affiche un résumé de démarrage"""
        logger.info("\n🎉 [STARTUP] Bot prêt et opérationnel !")
        
        # Statistiques de la base de données
        uow = self.uow_factory()
        with uow:
            stats = uow.database.get_stats()
        
        cogs_count = len([cog for cog in self.cogs.values()])
        commands_count = len(self.commands)
        
        # Statistiques de démarrage
        startup_stats = {
            "Utilisateurs": stats['users'],
            "Événements actifs": stats['active_events'],
            "Participations totales": stats['participations'],
            "Jeux": stats['games'],
            "Cogs chargés": cogs_count,
            "Commandes disponibles": commands_count
        }
        
        logger.info("📊 [STATS] Statistiques de démarrage :")
        for key, value in startup_stats.items():
            logger.info(f"  - {key}: {value}")
        
        logger.info("🔹 [COMMANDS] Commandes disponibles :")
        for command in self.commands:
            logger.info(f"  - {self.command_prefix}{command.name}: {command.help or 'Pas de description'}")
        
        logger.info("✅ [STARTUP] Bot opérationnel et prêt à recevoir des commandes !")
        logger.info("Done!")

    def run(self):
        """Lance le bot"""
        super().run(self.token, reconnect=True)
    
    def close(self):
        """Ferme proprement le bot"""
        logger.info("🛑 [SHUTDOWN] Arrêt du bot...")
        try:
            db_engine.close()
        except Exception as e:
            logger.error(f"❌ [SHUTDOWN] Erreur lors de la fermeture : {e}")


if __name__ == "__main__":
    bot = DiscordBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 [SHUTDOWN] Arrêt demandé par l'utilisateur")
    finally:
        bot.close()
