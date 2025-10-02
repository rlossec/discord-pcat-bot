import discord
from discord.ext import commands
import os
import logging
from tinydb import TinyDB
from config.settings import DB_PATH, PROJECT_ROOT


class DiscordBot(commands.Bot):
    def __init__(self, token: str, guild_id: int, prefix: str = "$", **kwargs):
        intents = kwargs.get("intents", discord.Intents.default())
        super().__init__(command_prefix=prefix, intents=intents)

        self.token = token
        self.guild_id = guild_id
        self.prefix = prefix
        self.config = kwargs

        # --- DATA BASE ---
        self.db = TinyDB(DB_PATH)

        # --- LOGGING GLOBAL ---
        log_file = kwargs.get("log_file", PROJECT_ROOT / "data/bot.log")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("DiscordBot")

        # --- Cogs ---
        self.cogs_dir = kwargs.get("cogs_dir", "cogs")


    async def setup_hook(self):
        """Chargement des cogs avant que le bot ne démarre réellement"""
        await self.load_cogs()

    async def load_cogs(self):
        """Recherche et charge tous les cogs dans le dossier cogs/"""

        self.logger.info("🔧 Chargement des cogs...")
        cogs_path = PROJECT_ROOT / self.cogs_dir
        if not os.path.exists(cogs_path):
            self.logger.error(f"❌ Le dossier {self.cogs_dir} n'existe pas !")
            return

        files = [f for f in os.listdir(cogs_path) if f.endswith(".py") and f != "__init__.py"]
        self.logger.info(f"📄 Fichiers trouvés : {files}")

        for filename in files:
            extension = f"{self.cogs_dir}.{filename[:-3]}"
            try:
                await self.load_extension(extension)
                self.logger.info(f"✅ Cog chargé : {extension}")
            except Exception as e:
                self.logger.error(f"❌ Erreur lors du chargement de {extension} : {e}")

    async def on_ready(self):
        """Event called when the bot is ready"""
        guild = self.get_guild(self.guild_id)
        if guild is None:
            raise ValueError(f"Guild with ID {self.guild_id} not found")

        self.logger.info(f"✅ Connecté en tant que {self.user} (ID: {self.user.id})")
        self.logger.info(f"🌐 Connecté au serveur : {guild.name} (ID: {guild.id})")
        self.logger.info("------")
        self.display_available_commands()
        self.logger.info("Done!")

    def display_available_commands(self):
        """Affiche toutes les commandes disponibles"""
        self.logger.info("🔹 Commandes disponibles :")
        for command in self.commands:
            self.logger.info(f"  - {self.command_prefix}{command.name}: {command.help or 'Pas de description'}")

    def run(self):
        """Lance le bot"""
        super().run(self.token, reconnect=True)
