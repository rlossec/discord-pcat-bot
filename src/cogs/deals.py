"""
Cog pour la gestion des promotions de jeux
Utilise la nouvelle architecture Clean Architecture
"""
import aiohttp
import discord
from discord.ext import commands
from datetime import datetime
from bot.domain.services import GameService, DealService
from bot.infrastructure.unit_of_work_impl import create_unit_of_work
from bot.core.utils import safe_float, safe_int, format_currency, format_percentage

API_URL = "https://www.cheapshark.com/api/1.0"
TEST_CHANNEL_ID = 1287444577933983806


class DealsCog(commands.Cog):
    """Cog pour la gestion des promotions de jeux"""
    
    def __init__(self, bot):
        self.bot = bot
        self.name = "🎮 Suivi des Promotions"
        self.uow_factory = create_unit_of_work
    
    @commands.command(name="addgame", help="Ajoute un jeu à suivre")
    async def add_game(self, ctx, *, game_name: str):
        """Ajoute un jeu à suivre"""
        try:
            # Utiliser le service métier
            uow = self.uow_factory()
            game_service = GameService(uow)
            
            # Créer le jeu
            game = game_service.create_game(game_name)
            
            embed = discord.Embed(
                title="✅ Jeu ajouté",
                description=f"Le jeu **{game.name}** a été ajouté avec succès !",
                color=discord.Color.green()
            )
            embed.add_field(name="ID", value=game.id, inline=True)
            embed.add_field(name="Nom", value=game.name, inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible d'ajouter le jeu : {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="listgames", help="Liste tous les jeux suivis")
    async def list_games(self, ctx):
        """Liste tous les jeux suivis"""
        try:
            # Utiliser le service métier
            uow = self.uow_factory()
            game_service = GameService(uow)
            
            # Récupérer tous les jeux
            games = game_service.get_all_games()
            
            if not games:
                embed = discord.Embed(
                    title="📋 Jeux suivis",
                    description="Aucun jeu suivi pour le moment.",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📋 Jeux suivis",
                description=f"{len(games)} jeu(s) suivi(s)",
                color=discord.Color.blue()
            )
            
            # Limiter à 25 jeux (limite Discord)
            games_to_show = games[:25]
            
            for game in games_to_show:
                embed.add_field(
                    name=f"🎮 {game.name}",
                    value=f"ID: {game.id}\nSteam: {game.steam_id or 'N/A'}\nEpic: {game.epic_id or 'N/A'}",
                    inline=True
                )
            
            if len(games) > 25:
                embed.set_footer(text=f"... et {len(games) - 25} autres jeux")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de lister les jeux : {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="checkdeals", help="Vérifie les promotions pour un jeu")
    async def check_deals(self, ctx, *, game_name: str):
        """Vérifie les promotions pour un jeu"""
        try:
            # Utiliser le service métier
            uow = self.uow_factory()
            game_service = GameService(uow)
            deal_service = DealService(uow)
            
            # Trouver le jeu
            game = game_service.get_game_by_name(game_name)
            if not game:
                embed = discord.Embed(
                    title="❌ Jeu non trouvé",
                    description=f"Le jeu **{game_name}** n'est pas suivi.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            
            # Récupérer les promotions existantes
            existing_deals = deal_service.get_deals_by_game(game.id)
            
            embed = discord.Embed(
                title=f"🎮 Promotions pour {game.name}",
                color=discord.Color.blue()
            )
            
            if not existing_deals:
                embed.description = "Aucune promotion trouvée pour ce jeu."
            else:
                embed.description = f"{len(existing_deals)} promotion(s) trouvée(s)"
                
                # Limiter à 10 promotions (limite Discord)
                deals_to_show = existing_deals[:10]
                
                for deal in deals_to_show:
                    savings_percent = format_percentage(deal.savings, deal.normal_price)
                    sale_price_str = format_currency(deal.sale_price)
                    normal_price_str = format_currency(deal.normal_price)
                    
                    embed.add_field(
                        name=f"💰 {deal.title}",
                        value=f"Prix: {sale_price_str} (au lieu de {normal_price_str})\nÉconomie: {savings_percent}\nStore: {deal.store_id}",
                        inline=False
                    )
                
                if len(existing_deals) > 10:
                    embed.set_footer(text=f"... et {len(existing_deals) - 10} autres promotions")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de vérifier les promotions : {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="searchdeals", help="Recherche des promotions sur CheapShark")
    async def search_deals(self, ctx, *, search_term: str):
        """Recherche des promotions sur CheapShark"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_URL}/deals", params={"title": search_term}) as response:
                    if response.status == 200:
                        deals_data = await response.json()
                        
                        if not deals_data:
                            embed = discord.Embed(
                                title="🔍 Recherche de promotions",
                                description=f"Aucune promotion trouvée pour **{search_term}**",
                                color=discord.Color.orange()
                            )
                            await ctx.send(embed=embed)
                            return
                        
                        embed = discord.Embed(
                            title=f"🔍 Promotions pour {search_term}",
                            description=f"{len(deals_data)} promotion(s) trouvée(s)",
                            color=discord.Color.green()
                        )
                        
                        # Limiter à 10 résultats
                        deals_to_show = deals_data[:10]
                        
                        for deal in deals_to_show:
                            savings_amount = safe_float(deal.get('savings', 0))
                            sale_price = safe_float(deal.get('salePrice', 0))
                            normal_price = safe_float(deal.get('normalPrice', 0))
                            
                            savings_percent = format_percentage(savings_amount, normal_price)
                            sale_price_str = format_currency(sale_price)
                            normal_price_str = format_currency(normal_price)
                            
                            embed.add_field(
                                name=f"🎮 {deal.get('title', 'Titre inconnu')}",
                                value=f"Prix: {sale_price_str} (au lieu de {normal_price_str})\nÉconomie: {savings_percent}\nStore: {deal.get('storeID', 'N/A')}",
                                inline=False
                            )
                        
                        if len(deals_data) > 10:
                            embed.set_footer(text=f"... et {len(deals_data) - 10} autres promotions")
                        
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title="❌ Erreur API",
                            description="Impossible de contacter l'API CheapShark",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche : {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Setup du cog"""
    await bot.add_cog(DealsCog(bot))
