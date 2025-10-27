"""
Cog pour la gestion des événements
Utilise la nouvelle architecture Clean Architecture
"""
from discord.ext import commands
from bot.infrastructure.unit_of_work_impl import create_unit_of_work


class EventsCommands(commands.Cog):
    """📅 Gestion des Événements - Cog pour gérer les événements et leurs inscriptions"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.name = "📅 Gestion des Événements"
        self.description = "Gestion des événements et leurs inscriptions sur le serveur Discord"
        self.uow_factory = create_unit_of_work

    @commands.command(name="list_events")
    async def list_events(self, ctx: commands.Context):
        """Lister tous les événements actifs"""
        try:
            # Récupérer les événements Discord
            events = list(ctx.guild.scheduled_events)
            
            if not events:
                await ctx.send("📅 Aucun événement trouvé.")
                return

            # Créer le message
            message = "📅 Événements actifs :\n"

            for event in events:
                if event.start_time:
                    event_time = event.start_time.strftime('%d/%m/%Y %H:%M')
                    # Compter les participants depuis la base de données
                    with self.uow_factory() as uow:
                        participations = uow.participations.get_by_event(str(event.id))
                        participants_count = len(participations)
                    
                    message += f"- {event.name} ({event_time}) - {participants_count} participants\n"
                else:
                    # Compter les participants même sans date
                    with self.uow_factory() as uow:
                        participations = uow.participations.get_by_event(str(event.id))
                        participants_count = len(participations)
                    
                    message += f"- {event.name} (Date non définie) - {participants_count} participants\n"
            
            await ctx.send(message)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la récupération des événements : {str(e)}")

    @commands.command(name="participants")
    async def participants(self, ctx: commands.Context, event_id: int):
        """
        Affiche la liste des inscrits d'un événement avec l'ordre chronologique
        Utilisation: $participants <ID_Event>
        """
        try:
            # Utiliser le service métier
            with self.uow_factory() as uow:
                discord_event = uow.events.get_by_discord_id(str(event_id))
                
                # Stocker le nom de l'événement pendant que la session est ouverte
                if not discord_event:
                    await ctx.send(f"❌ Aucun événement trouvé avec l'ID `{event_id}`.")
                    return
                
                event_name = discord_event.name
                
                # Récupérer les participations depuis la base de données
                participations = uow.participations.get_by_event(str(event_id))
                
                if not participations:
                    await ctx.send(f"Aucun inscrit à **{event_name}**.")
                    return

                # Récupérer les données utilisateur pendant que le contexte est ouvert
                participants_data = []
                for participation in participations:
                    user = uow.users.get_by_discord_id(participation.user_discord_id)
                    participants_data.append({
                        'username': user.username if user else 'Utilisateur inconnu',
                        'discord_id': participation.user_discord_id,
                        'joined_at': participation.joined_at
                    })
            
            # Créer le message
            message = f"👥 Inscriptions pour {event_name} :\n"
            
            for participant in participants_data:
                message += f"- {participant['username']} ({participant['joined_at'].strftime('%d/%m/%Y %H:%M')})\n"

            code_mentions = " ".join([f"<@{p['discord_id']}>" for p in participants_data])
            message += f"```{code_mentions}```"

            await ctx.send(message)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la récupération des participants : {str(e)}")

    @commands.command(name="eventinfo")
    async def event_info(self, ctx: commands.Context, event_id: int):
        """Affiche les informations détaillées d'un événement"""
        try:
            # Récupérer l'événement Discord
            discord_event = ctx.guild.get_scheduled_event(event_id)
            if not discord_event:
                await ctx.send(f"❌ Aucun événement Discord trouvé avec l'ID `{event_id}`.")
                return
            
            # Compter les participants depuis la base de données
            with self.uow_factory() as uow:
                participations = uow.participations.get_by_event(str(discord_event.id))
                participants_count = len(participations)
            
            # Créer le message simple
            message = f"📅 **{discord_event.name}**\n\n"
            message += f"🆔 ID: {discord_event.id}\n"
            message += f"📊 Participants: {participants_count}\n"
            
            if discord_event.start_time:
                message += f"📅 Début: {discord_event.start_time.strftime('%d/%m/%Y %H:%M')}\n"
            
            if discord_event.end_time:
                message += f"🏁 Fin: {discord_event.end_time.strftime('%d/%m/%Y %H:%M')}\n"
            
            if discord_event.location:
                message += f"📍 Lieu: {discord_event.location}\n"
            
            if discord_event.description:
                message += f"\n📝 Description:\n{discord_event.description}\n"
            
            message += f"\n🔗 Lien: {discord_event.url}"
            
            await ctx.send(message)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la récupération des informations : {str(e)}")


async def setup(bot: commands.Bot):
    """Setup du cog"""
    await bot.add_cog(EventsCommands(bot))