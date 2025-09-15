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

        events_in_db = events_db[0].get('events', {})
        events_discord = await guild.fetch_scheduled_events()

        passed_events = events_db[0].get('passed_events', {})
        # update the db with the new events users
        for event in events_discord:
            event_id = str(event.id)

            users_in_db = events_in_db.get(event_id, {})

            # fetch the users of the event
            event_users = []
            async for user in event.users():
                event_users.append(user)

            print(f"🔍 {event.name} a {len(event_users)} inscrits.")

            # update the db with the new events users
            for user in event_users:
                user_id = str(user.id)
                username = user.display_name
                if user_id not in users_in_db:
                    users_in_db[user_id] = now_iso
                    print(f"✅ {user} s'est inscrit à l'event {event.name}.")
                    users_in_db[user_id] = {"username": username, "joined_at": now_iso}
            
            # remove the users that have unsubscribed from the db
            unsubscribed_users = []
            for user_id, user in users_in_db.items():

                event_users_ids = [str(user.id) for user in event_users]

                if user_id not in event_users_ids:
                    unsubscribed_users.append(user_id)
                    print(f"❌ {user['username']} s'est désinscrit de l'event {event.name}.")

            for user_id in unsubscribed_users:
                users_in_db.pop(user_id)

            events_in_db[event_id] = users_in_db

        events_in_db_copy = events_in_db.copy()
        for event_id, users_in_db in events_in_db_copy.items():
            event_ids = [str(event.id) for event in events_discord]
            # Passed events transfered in another db
            if event_id not in event_ids:
                print(f"❌ {event_id} est passé.")
                passed_events[event_id] = users_in_db
                events_in_db.pop(event_id)

        # Met à jour la DB
        self.db.update({'events': events_in_db})
        self.db.update({'passed_events': passed_events})
        print("✅ Vérification terminée.")


    @commands.command(name="event_inscriptions")
    async def event_inscriptions(self, ctx, event_id: int):
        """Affiche les inscrits avec la date d'inscription"""

        events_in_db = self.db.all()[0].get('events', {})
        if not events_in_db:
            await ctx.send("Aucune donnée d'inscription trouvée.")
            return

        users_dict = events_in_db.get(str(event_id), {})

        if not users_dict:
            await ctx.send("Aucun inscrit trouvé pour cet event.")
            return

        message = "\n".join([f"- {user['username']} (enregistré le {datetime.strptime(user['joined_at'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%d/%m/%Y %H:%M')})"
                             for user_id, user in users_dict.items()])
        await ctx.send(f"👥 Inscriptions pour l'event {event_id} :\n{message}")


async def setup(bot: commands.Bot):
    await bot.add_cog(EventLogger(bot))

