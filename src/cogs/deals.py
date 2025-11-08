"""
Cog pour la gestion des promotions de jeux
Utilise la nouvelle architecture Clean Architecture
"""
import aiohttp
from discord.ext import commands

from bot.domain.services import GameService, DealService
from bot.infrastructure.unit_of_work_impl import create_unit_of_work
from bot.core.utils import safe_float, format_currency, format_percentage

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
            
            message = "✅ **Jeu ajouté**\n\n"
            message += f"Le jeu **{game.name}** a été ajouté avec succès !\n"
            message += f"**ID:** {game.id}\n"
            message += f"**Nom:** {game.name}"
            
            await ctx.send(message)
            
        except Exception as e:
            await ctx.send(f"❌ **Erreur**\n\nImpossible d'ajouter le jeu : {str(e)}")
    
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
                await ctx.send("📋 **Jeux suivis**\n\nAucun jeu suivi pour le moment.")
                return
            
            message = f"📋 **Jeux suivis**\n\n{len(games)} jeu(s) suivi(s)\n\n"
            
            # Limiter à 25 jeux (limite Discord)
            games_to_show = games[:25]
            
            for game in games_to_show:
                message += f"🎮 **{game.name}**\n"
                message += f"ID: {game.id} | Steam: {game.steam_id or 'N/A'} | Epic: {game.epic_id or 'N/A'}\n\n"
            
            if len(games) > 25:
                message += f"... et {len(games) - 25} autres jeux"
            
            await ctx.send(message)
            
        except Exception as e:
            await ctx.send(f"❌ **Erreur**\n\nImpossible de lister les jeux : {str(e)}")
    
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
                await ctx.send(f"❌ **Jeu non trouvé**\n\nLe jeu **{game_name}** n'est pas suivi.")
                return
            
            # Récupérer les promotions existantes
            existing_deals = deal_service.get_deals_by_game(game.id)
            
            if not existing_deals:
                message = f"🎮 **Promotions pour {game.name}**\n\nAucune promotion trouvée pour ce jeu."
            else:
                message = f"🎮 **Promotions pour {game.name}**\n\n{len(existing_deals)} promotion(s) trouvée(s)\n\n"
                
                # Limiter à 10 promotions
                deals_to_show = existing_deals[:10]
                
                for deal in deals_to_show:
                    savings_percent = format_percentage(deal.savings, deal.normal_price)
                    sale_price_str = format_currency(deal.sale_price)
                    normal_price_str = format_currency(deal.normal_price)
                    
                    message += f"💰 **{deal.title}**\n"
                    message += f"Prix: {sale_price_str} (au lieu de {normal_price_str})\n"
                    message += f"Économie: {savings_percent} | Store: {deal.store_id}\n\n"
                
                if len(existing_deals) > 10:
                    message += f"... et {len(existing_deals) - 10} autres promotions"
            
            await ctx.send(message)
            
        except Exception as e:
            await ctx.send(f"❌ **Erreur**\n\nImpossible de vérifier les promotions : {str(e)}")
    
    @commands.command(name="searchdeals", help="Recherche des promotions sur CheapShark")
    async def search_deals(self, ctx, *, search_term: str):
        """Recherche des promotions sur CheapShark"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_URL}/deals", params={"title": search_term}) as response:
                    if response.status == 200:
                        deals_data = await response.json()
                        
                        if not deals_data:
                            await ctx.send(f"🔍 **Recherche de promotions**\n\nAucune promotion trouvée pour **{search_term}**")
                            return
                        
                        message = f"🔍 **Promotions pour {search_term}**\n\n{len(deals_data)} promotion(s) trouvée(s)\n\n"
                        
                        # Limiter à 10 résultats
                        deals_to_show = deals_data[:10]
                        
                        for deal in deals_to_show:
                            savings_amount = safe_float(deal.get('savings', 0))
                            sale_price = safe_float(deal.get('salePrice', 0))
                            normal_price = safe_float(deal.get('normalPrice', 0))
                            
                            savings_percent = format_percentage(savings_amount, normal_price)
                            sale_price_str = format_currency(sale_price)
                            normal_price_str = format_currency(normal_price)
                            
                            message += f"🎮 **{deal.get('title', 'Titre inconnu')}**\n"
                            message += f"Prix: {sale_price_str} (au lieu de {normal_price_str})\n"
                            message += f"Économie: {savings_percent} | Store: {deal.get('storeID', 'N/A')}\n\n"
                        
                        if len(deals_data) > 10:
                            message += f"... et {len(deals_data) - 10} autres promotions"
                        
                        await ctx.send(message)
                    else:
                        await ctx.send("❌ **Erreur API**\n\nImpossible de contacter l'API CheapShark")
                        
        except Exception as e:
            await ctx.send(f"❌ **Erreur**\n\nErreur lors de la recherche : {str(e)}")


async def setup(bot):
    """Setup du cog"""
    await bot.add_cog(DealsCog(bot))
