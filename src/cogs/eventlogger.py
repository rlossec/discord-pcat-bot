import discord
from discord.ext import commands, tasks
from tinydb import TinyDB, Query
from datetime import datetime, timezone, timedelta
from config.settings import DB_PATH


class EventLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild_id = bot.guild_id
        self.db = TinyDB(DB_PATH)
        if not self.db.contains(lambda doc: 'events' in doc):
            self.db.insert({'events': {}})
        self.bot_ready_check.start()

    @tasks.loop(count=1)
    async def bot_ready_check(self):
        """Check tous les events à chaque démarrage"""
        await self.bot.wait_until_ready()

        print("⏱ Vérification des inscriptions aux scheduled events...")

        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            print("❌ Guild introuvable")
            return

        # Date Paris for now
        now_iso = datetime.now(timezone.utc).astimezone().isoformat()
        
        events_db = self.db.all()

        events_data = events_db[0].get('events', {})
        events_discord = await guild.fetch_scheduled_events()


        for event in events_discord:
            event_id = str(event.id)
            users_dict = events_data.get(event_id, {})

            async for user in event.users():
                user_id = str(user.id)
                username = user.display_name
                if user_id not in users_dict:
                    users_dict[user_id] = now_iso
                    print(f"✅ {user} ajouté à l'event {event.name} à {now_iso}")
                    users_dict[user_id] = {"username": username, "joined_at": now_iso} 

            events_data[event_id] = users_dict

        # Met à jour la DB
        self.db.update({'events': events_data})
        print("✅ Vérification terminée.")

    @commands.command(name="event_inscriptions")
    async def event_inscriptions(self, ctx, event_id: int):
        """Affiche les inscrits avec la date d'inscription"""


        events_data = self.db.all()[0].get('events', {})
        if not events_data:
            await ctx.send("Aucune donnée d'inscription trouvée.")
            return

        users_dict = events_data.get(str(event_id), {})

        if not users_dict:
            await ctx.send("Aucun inscrit trouvé pour cet event.")
            return

        message = "\n".join([f"- {user['username']} (enregistré le {datetime.strptime(user['joined_at'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%d/%m/%Y %H:%M')})"
                             for user_id, user in users_dict.items()])
        await ctx.send(f"👥 Inscriptions pour l'event {event_id} :\n{message}")


async def setup(bot: commands.Bot):
    await bot.add_cog(EventLogger(bot))

