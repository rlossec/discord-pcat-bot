
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from bot.core.config import ANNOUNCE_CHANNEL_ID


class AnnouncementCommands(commands.Cog):
    """📢 Annonces d'Événements - Cog pour générer et envoyer des annonces"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.name = "📢 Annonces d'Événements"
        self.description = "Génération et envoi des annonces d'événements"
        self.guild_id = bot.guild_id

    @commands.command(name="annonce")
    async def annonce(self, ctx):
        """Annonce les events de la semaine à venir"""
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            await ctx.send("❌ Guild introuvable")
            return
        
        now = datetime.now(timezone.utc)

        days_until_sunday = 6 - now.weekday()
        if days_until_sunday == 0:
            days_until_sunday = 7
            
        end_of_week = now + timedelta(days=days_until_sunday, hours=23-now.hour, minutes=59-now.minute)

        events = await guild.fetch_scheduled_events()
        
        week_events = [e for e in events if e.start_time and now <= e.start_time <= end_of_week]

        if not week_events:
            await ctx.send("📅 Aucun event prévu cette semaine.")
            return

        # Tri par date
        week_events.sort(key=lambda e: e.start_time)

        # Création du message
        message = ""
        message += "```"
        message += "\n"
        message += "Bonsoir tout le monde !"
        message += "\n"
        message += "@annonce Cette semaine, on propose les soirées suivantes :\n\n"

        for event in week_events:
            event_time_unix = int(event.start_time.timestamp())
            message += f"- Soirée [**{event.name}**]({event.url}) <t:{event_time_unix}:F>\n"

        message += "\n"
        message += "Bonne semaine ! 😉"
        message += "```"
        # Envoyer le message d'annonce dans le channel de vérification des événements
        test_channel = self.bot.get_channel(ANNOUNCE_CHANNEL_ID) if ANNOUNCE_CHANNEL_ID else None
        
        if test_channel:
            await test_channel.send(message)
        else:
            await ctx.send("❌ Channel de destination introuvable. Vérifiez la configuration ANNOUNCE_CHANNEL_ID")


async def setup(bot: commands.Bot):
    await bot.add_cog(AnnouncementCommands(bot))
