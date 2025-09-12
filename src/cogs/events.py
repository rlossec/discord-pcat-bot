import discord
from discord.ext import commands
import json
import os
from datetime import datetime



class EventsCommands(commands.Cog):
    """Cog pour gérer les événements et inscriptions sur le serveur Discord"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command(name="list_events")
    async def list_events(self, ctx: commands.Context):
        """Lister tous les événements actifs"""
        events = list(ctx.guild.scheduled_events)
        
        if not events:
            await ctx.send("📅 Aucun événement trouvé.")
            return

        message = "📅 Événements actifs :\n"

        for event in events:
            event_message = f"- {event.name} ({event.start_time.strftime('%d/%m/%Y %H:%M')})\n"
            message += event_message
        
        await ctx.send(message)


    @commands.command(name="participants")
    async def participants(self, ctx, event_id: int):
        """Affiche la liste des inscrits à un scheduled event"""
        event = ctx.guild.get_scheduled_event(event_id)

        if not event:
            await ctx.send("❌ Aucun event trouvé avec cet ID.")
            return

        users = []
        async for user in event.users():
            users.append(user)

        if not users:
            await ctx.send(f"Aucun inscrit à **{event.name}**.")
        else:
            liste = "\n".join([f"- {u.display_name}" for u in users])
            await ctx.send(f"👥 Inscriptions pour **{event.name}** :\n{liste}")


async def setup(bot: commands.Bot):
    await bot.add_cog(EventsCommands(bot))