import discord
from discord.ext import commands
import json
import os
from datetime import datetime


class GeneralCommands(commands.Cog):
    """Cog pour gérer les commandes générales sur le serveur Discord"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="hello")
    async def hello(self, ctx: commands.Context):
        """Commande de test pour vérifier que le cog fonctionne"""
        await ctx.send(f"Hello {ctx.author.mention} 👋 ! Le cog Général est opérationnel !")


async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralCommands(bot))