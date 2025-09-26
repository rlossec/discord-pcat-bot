
from discord.ext import commands


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
    async def participants(self, ctx: commands.Context, event_id: int):
        """
        Affiche la liste des inscrits à un scheduled event par nom, et fournit les pings dans un bloc de code.
        Utilisation: $participants <ID_Event>
        """
        event = ctx.guild.get_scheduled_event(event_id)

        if not event:
            await ctx.send(f"❌ Aucun événement trouvé avec l'ID `{event_id}`.")
            return

        users = []
        async for user in event.users():
            users.append(user)

        if not users:
            await ctx.send(f"Aucun inscrit à **{event.name}**.")
            return

        # 1. Liste par noms d'affichage (pour la lecture)
        liste_display_names = "\n".join([f"- {user.display_name}" for user in users])

        # 2. Liste par mentions (pour le ping)
        # On utilise le format de mention (user.mention) et on les joint par un espace.
        liste_mentions = " ".join([user.mention for user in users])

        # 3. Construction du message final
        message = (
            f"👥 Inscriptions pour **{event.name}** :\n"
            f"{liste_display_names}\n\n"
            f"--- Copiez/Collez pour le ping ---\n"
            f"```{liste_mentions}```"
        )

        await ctx.send(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(EventsCommands(bot))