"""
Cog pour la gestion des événements
"""


from datetime import datetime, timezone

from discord.ext import commands

from bot.infrastructure.unit_of_work_impl import create_unit_of_work
from bot.domain.utils.create_text_table import create_text_table
from bot.core.config import PARIS_TZ
from bot.core.logging_config import logger


class EventsCommands(commands.Cog):
    """📅 Cog pour gérer les événements et leurs inscriptions"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.name = "📅 Gestion des Événements"
        self.description = "Gestion des événements et leurs inscriptions sur le serveur Discord"
        self.uow_factory = create_unit_of_work

    @commands.command(name="list_events")
    async def list_events(self, ctx: commands.Context):
        """Lister tous les événements actifs avec un meilleur format"""
        try:
            # Récupérer les événements Discord
            events = sorted(list(ctx.guild.scheduled_events), key=lambda e: e.start_time if e.start_time else datetime.min)
            
            if not events:
                await ctx.send("##📅 Aucun événement trouvé.")
                return

            message = "**📅 Événements Actifs**\n"
            
            # Préparer les données pour l'affichage tabulaire
            data_rows = []

            # Récupérer les participants en amont pour éviter l'ouverture/fermeture UOW répétée
            participants_map = {}
            with self.uow_factory() as uow:
                for event in events:
                    participations = uow.participations.get_by_event(str(event.id))
                    participants_map[event.id] = len(participations)
            
            for event in events:
                participants_count = participants_map.get(event.id, 0)
                event_time_str = event.start_time.astimezone(PARIS_TZ).strftime('%d/%m %H:%M') if event.start_time else "Date indéfinie"
                
                data_rows.append({
                    'id': str(event.id),
                    'name': event.name,
                    'time': event_time_str,
                    'count': str(participants_count)
                })

            columns = {
                'id': 'ID',
                'name': 'Nom',
                'time': 'Heure',
                'count': 'Participants'
            }

            table_content = create_text_table(data_rows, columns)

            await ctx.send(message + f"```\n{table_content}```\nPour les détails, utilisez `$event_detail <ID>`")
            
        except Exception as e:
            logger.exception("❌ [EVENTS] Erreur lors de la récupération des événements : %s", e)
            await ctx.send(f"❌ Erreur lors de la récupération des événements : {str(e)}")

    @commands.command(name="event_detail")
    async def event_detail(self, ctx: commands.Context, event_id: int):
        """
        Affiche les détails d'un événement et la liste de ses inscrits.
        Utilisation: $<prefix>event_detail <ID_Event>
        """
        await ctx.defer()
        try:
            # 1. Récupérer l'événement Discord
            # Dictionary of events
            events_discord = {event.id: event for event in ctx.guild.scheduled_events}
            discord_event = events_discord.get(event_id)
            if not discord_event:
                await ctx.send(f"❌ Aucun événement Discord trouvé avec l'ID `{event_id}`.")
                return

            # 2. Récupérer les participations et les données utilisateurs
            participants_data = []
            with self.uow_factory() as uow:
                # Récupérer les participations depuis la base de données
                participations = uow.participations.get_by_event(str(event_id))
                
                # Récupérer les données utilisateur
                for participation in participations:
                    # Tente de récupérer l'objet membre Discord pour avoir le nom à jour et mention
                    member = ctx.guild.get_member(int(participation.user_discord_id))
                    user = uow.users.get_by_discord_id(participation.user_discord_id)
                    
                    participants_data.append({
                        'username': member.display_name if member else (user.username if user else 'Utilisateur Inconnu'),
                        'discord_id': participation.user_discord_id, # Garder pour la mention
                        'joined_at': participation.joined_at
                    })
            
            # Trie par date d'inscription
            participants_data.sort(key=lambda p: p['joined_at'])
            participants_count = len(participants_data)
            
            # 3. Construction du message de détails (Markdown)
            
            message = f"## 📅 {discord_event.name}\n"
            
            if discord_event.description:
                # Description dans un bloc de citation pour la démarquer
                desc = discord_event.description.replace('\n', '\n> ')
                message += f"> **📝 Description :**\n> {desc}\n"
            
            # 4. Liste des participants (format tabulaire ou liste simple)
            message += f"### 👥 {participants_count} inscrits \n\n"

            if participants_data:
                # Préparer les données des participants pour le tableau
                p_rows = []
                for i, p in enumerate(participants_data, 1):
                    # Convertir la date en timezone Paris avant l'affichage
                    # Si joined_at est naïf (sans timezone), on le considère comme UTC
                    if p['joined_at'].tzinfo is None:
                        joined_at_utc = p['joined_at'].replace(tzinfo=timezone.utc)
                    else:
                        joined_at_utc = p['joined_at']
                    joined_at_paris = joined_at_utc.astimezone(PARIS_TZ)
                    p_rows.append({
                        'rank': str(i).ljust(2),
                        'username': p['username'],
                        'joined_at': joined_at_paris.strftime('%H:%M %d/%m')
                    })
                
                # Création du tableau des participants
                p_columns = {
                    'rank': '#',
                    'username': 'Nom',
                    'joined_at': 'Inscrit le'
                }
                
                participants_table = create_text_table(p_rows, p_columns)
                message += "```md\n"
                message += participants_table
                message += "```\n\n"
                
                # 5. CODE DE MENTION (Gardé Intact)
                message += "Pour mentionner les participants, utilisez le code suivant : \n"

                code_mentions = " ".join([f"<@{p['discord_id']}>" for p in participants_data])
                message += f"```{code_mentions}```" # <-- CODE INTАCT
                
            else:
                message += "*Aucun inscrit enregistré dans la base de données.*\n"

            await ctx.send(message)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la récupération des détails : {str(e)}")


async def setup(bot: commands.Bot):
    """Setup du cog"""
    await bot.add_cog(EventsCommands(bot))