import discord
from discord.ext import commands
import os


class DiscordBot(commands.Bot):
    def __init__(self, token: str, guild_id: int, prefix: str = "$", **kwargs):
        intents = kwargs.get("intents", discord.Intents.default())
        super().__init__(command_prefix=prefix, intents=intents)

        self.token = token
        self.guild_id = guild_id
        self.prefix = prefix
        self.config = kwargs

    async def setup_hook(self):
        """Chargement des cogs avant que le bot ne démarre réellement"""
        await self.load_cogs()

    async def load_cogs(self):
        """Recherche et charge tous les cogs dans le dossier cogs/"""
        cogs_dir = "cogs"
        print("🔧 Chargement des cogs...")

        if not os.path.exists("src/" + cogs_dir):
            print(f"❌ Le dossier {cogs_dir} n'existe pas !")
            return

        files = [f for f in os.listdir("src/" + cogs_dir) if f.endswith(".py") and f != "__init__.py"]
        print(f"📄 Fichiers trouvés : {files}")

        for filename in files:
            extension = f"{cogs_dir}.{filename[:-3]}"
            try:
                await self.load_extension(extension)
                print(f"✅ Cog chargé : {extension}")
            except Exception as e:
                print(f"❌ Erreur lors du chargement de {extension} : {e}")

    async def on_ready(self):
        """Événement appelé quand le bot est prêt"""
        guild = self.get_guild(self.guild_id)
        if guild is None:
            raise ValueError(f"Guild with ID {self.guild_id} not found")

        print(f"✅ Connecté en tant que {self.user} (ID: {self.user.id})")
        print(f"🌐 Connecté au serveur : {guild.name} (ID: {guild.id})")
        print("------")
        self.display_available_commands()

    def display_available_commands(self):
        """Affiche toutes les commandes disponibles"""
        print("\n🔹 Commandes disponibles :")
        for command in self.commands:
            print(f"  - {self.command_prefix}{command.name}: {command.help or 'Pas de description'}")

    def run(self):
        """Lance le bot"""
        super().run(self.token, reconnect=True)
