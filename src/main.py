
import discord
import os

from models.discordbot import DiscordBot
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()

    # Initialize Discord bot
    intents = discord.Intents.default()
    intents.message_content = True
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID"))
    
    print("🚀 Démarrage du bot...")
    bot_instance = DiscordBot(DISCORD_TOKEN, GUILD_ID, intents=intents, prefix="$")
    
    # Démarrer le bot (setup_hook et on_ready sont connectés automatiquement)
    bot_instance.run()


if __name__ == "__main__":
    main()