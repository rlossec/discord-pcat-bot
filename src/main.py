
import discord
import os
from config.check import check_configuration
from models.discordbot import DiscordBot
from dotenv import load_dotenv


def main():

    # Check configuration and load environment variables
    check_configuration()
    load_dotenv()

    # Initialize Discord client
    intents = discord.Intents.default()
    intents.message_content = True
    DICTABOT_TOKEN = os.getenv("DICTABOT_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID"))
    bot = DiscordBot(DICTABOT_TOKEN, GUILD_ID, intents)
    bot.initialize_client()
    bot.run()


if __name__ == "__main__":
    main()