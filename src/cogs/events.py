"""
Cog pour la gestion des événements
Utilise la nouvelle architecture Clean Architecture
"""
import discord
from discord.ext import commands
from datetime import datetime
from bot.domain.services import EventService, ParticipationService
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

            # Créer l'embed
            embed = discord.Embed(
                title="📅 Événements actifs",
                color=discord.Color.blue()
            )

            for event in events:
                if event.start_time:
                    event_time = event.start_time.strftime('%d/%m/%Y %H:%M')
                    embed.add_field(
                        name=f"🎯 {event.name}",
                        value=f"Date: {event_time}\nParticipants: {len(event.subscribers)}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=f"🎯 {event.name}",
                        value="Date non définie",
                        inline=True
                    )
            
            await ctx.send(embed=embed)
            
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
            uow = self.uow_factory()
            event_service = EventService(uow)
            participation_service = ParticipationService(uow)
            
            # Récupérer l'événement Discord
            discord_event = ctx.guild.get_scheduled_event(event_id)
            if not discord_event:
                await ctx.send(f"❌ Aucun événement Discord trouvé avec l'ID `{event_id}`.")
                return
            
            # Récupérer les participations depuis la base de données
            with uow:
                participations = uow.participations.get_by_event(str(event_id))
            
            if not participations:
                await ctx.send(f"Aucun inscrit à **{discord_event.name}**.")
                return

            # Créer l'embed
            embed = discord.Embed(
                title=f"👥 Inscriptions pour {discord_event.name}",
                color=discord.Color.green()
            )

            # Liste des inscrits rangés par date d'inscription
            liste_display_names = "\n".join([
                f"- {participation.user_discord_id} ({participation.created_at.strftime('%d/%m/%Y %H:%M')})" 
                for participation in participations
            ])

            # Liste par mentions (pour le ping)
            liste_mentions = " ".join([f"<@{participation.user_discord_id}>" for participation in participations])

            embed.add_field(
                name="📋 Liste des inscrits",
                value=liste_display_names,
                inline=False
            )
            
            embed.add_field(
                name="🔔 Mentions pour ping",
                value=f"```{liste_mentions}```",
                inline=False
            )

            await ctx.send(embed=embed)
            
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
            
            # Créer l'embed détaillé
            embed = discord.Embed(
                title=f"📅 {discord_event.name}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="🆔 ID", value=str(discord_event.id), inline=True)
            embed.add_field(name="📊 Participants", value=str(len(discord_event.subscribers)), inline=True)
            
            if discord_event.start_time:
                embed.add_field(name="📅 Début", value=discord_event.start_time.strftime('%d/%m/%Y %H:%M'), inline=True)
            
            if discord_event.end_time:
                embed.add_field(name="🏁 Fin", value=discord_event.end_time.strftime('%d/%m/%Y %H:%M'), inline=True)
            
            if discord_event.description:
                embed.add_field(name="📝 Description", value=discord_event.description[:1000], inline=False)
            
            if discord_event.location:
                embed.add_field(name="📍 Lieu", value=discord_event.location, inline=True)
            
            embed.add_field(name="🔗 Lien", value=f"[Voir l'événement]({discord_event.url})", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la récupération des informations : {str(e)}")


async def setup(bot: commands.Bot):
    """Setup du cog"""
    await bot.add_cog(EventsCommands(bot))