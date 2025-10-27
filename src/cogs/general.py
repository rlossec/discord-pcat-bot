"""
Cog pour les commandes générales et l'aide
Utilise la nouvelle architecture Clean Architecture
"""
import discord
from discord.ext import commands


class GeneralCommands(commands.Cog):
    """🔧 Commandes Générales - Cog pour les commandes générales et l'aide"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.name = "🔧 Commandes Générales"
        self.description = "Commandes générales et l'aide"
        # Supprimer la commande help par défaut
        self.bot.remove_command("help")

    @commands.command(name="help")
    async def custom_help(self, ctx: commands.Context, *, command=None):
        """Affiche l'aide personnalisée avec les catégories organisées"""
        # Si une commande spécifique est demandée, utiliser l'aide par défaut
        if command:
            await ctx.send_help(command)
            return

        # Construire le message d'aide personnalisé
        help_message = self._build_help_message()
        
        try:
            await ctx.send(help_message)
        except discord.Forbidden:
            await ctx.send("❌ Permissions insuffisantes pour afficher l'aide.")

    def _build_help_message(self) -> str:
        """Construit le message d'aide organisé par catégories"""
        help_text = "🤖 **DictaBot - Aide des Commandes**\n\n"
        help_text += "Voici toutes les commandes disponibles organisées par catégorie :\n\n"
        
        # Organiser les commandes par cog
        cogs_commands = {}
        uncategorized_commands = []
        
        for command in self.bot.commands:
            if command.cog and hasattr(command.cog, 'name'):
                cog_name = command.cog.name
                if cog_name not in cogs_commands:
                    cogs_commands[cog_name] = []
                cogs_commands[cog_name].append(command)
            else:
                uncategorized_commands.append(command)
        
        # Ajouter les commandes par catégorie
        for cog_name, commands_list in cogs_commands.items():
            if cog_name == self.name:  # Exclure GeneralCommands de sa propre liste
                continue
                
            help_text += f"**{cog_name}**\n"
            for cmd in commands_list:
                help_text += f"• `{self.bot.command_prefix}{cmd.name}`: {cmd.help or 'Pas de description'}\n"
            help_text += "\n"
        
        # Ajouter les commandes non catégorisées
        if uncategorized_commands:
            help_text += "**Commandes générales**\n"
            for cmd in uncategorized_commands:
                help_text += f"• `{self.bot.command_prefix}{cmd.name}`: {cmd.help or 'Pas de description'}\n"
            help_text += "\n"
        
        # Ajouter la commande help à la fin
        help_text += f"• `{self.bot.command_prefix}help <commande>`: Aide détaillée pour une commande spécifique\n"
        
        return help_text


async def setup(bot: commands.Bot):
    """Setup du cog"""
    await bot.add_cog(GeneralCommands(bot))