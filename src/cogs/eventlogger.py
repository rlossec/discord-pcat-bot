
from discord.ext import commands, tasks
from tinydb import Query
from datetime import datetime, timezone



class EventLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild_id = bot.guild_id
        self.db = bot.db
        self.Events = Query()
        # Init DB if empty
        if not self.db.contains(self.Events.events.exists()):
            self.db.insert({"events": {}, "passed_events": {}})
        self.bot_ready_check.start()

    def _load_db(self) -> dict:
        """Load the structure of the DB"""
        return self.db.get(self.Events.events.exists()) or {"events": {}, "passed_events": {}}

    def _save_db(self, data: dict):
        """Update the DB"""
        self.db.update(data, self.Events.events.exists())

    def _parse_date(self, iso_str: str) -> str:
        """Transform an ISO date to a readable format"""
        try:
            dt = datetime.fromisoformat(iso_str)
            return dt.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return iso_str

    @tasks.loop(count=1)
    async def bot_ready_check(self):
        """Check all events at each startup"""
        await self.bot.wait_until_ready()

        self.bot.logger.info("⏱ Vérification des inscriptions aux scheduled events...")

        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            self.bot.logger.error("❌ Guild introuvable")
            return

        try:
            events_discord = await guild.fetch_scheduled_events()
        except Exception as e:
            self.bot.logger.error(f"⚠️ Erreur lors du fetch des events : {e}")
            return
        
        now_iso = datetime.now(timezone.utc).astimezone().isoformat()
        db_data = self._load_db()
        events_in_db = db_data.get("events", {})
        passed_events = db_data.get("passed_events", {})

        # update the db with the new events users
        for event in events_discord:
            event_id = str(event.id)

            users_in_db = events_in_db.get(event_id, {})

            # fetch the subscribed users of the event
            event_users = []
            async for user in event.users():
                event_users.append(user)

            self.bot.logger.info(f"🔍 {event.name} a {len(event_users)} inscrits.")

            # update the db with the new events users
            for user in event_users:
                user_id = str(user.id)
                if user_id not in users_in_db:
                    users_in_db[user_id] = {
                        "username": user.display_name,
                        "joined_at": now_iso
                    }
                    self.bot.logger.info(f"✅ {user.display_name} s'est inscrit à l'event {event.name}.")
            
            # remove the users that have unsubscribed from the db
            event_user_ids = {str(user.id) for user in event_users}
            unsubscribed_users = [
                uid for uid in users_in_db if uid not in event_user_ids
            ]
            for uid in unsubscribed_users:
                self.bot.logger.error(f"❌ {users_in_db[uid]['username']} s'est désinscrit de {event.name}.")
                users_in_db.pop(uid)

            events_in_db[event_id] = users_in_db

        # transfer the passed events to the passed_events db
        active_event_ids = {str(event.id) for event in events_discord}
        for event_id in list(events_in_db.keys()):
            if event_id not in active_event_ids:
                self.bot.logger.info(f"📦 Event {event_id} terminé, archivé.")
                passed_events[event_id] = events_in_db.pop(event_id)

        # Update the DB
        self._save_db({"events": events_in_db, "passed_events": passed_events})
        self.bot.logger.info("✅ Vérification des events terminée.")


    @commands.command(name="event_inscriptions")
    async def event_inscriptions(self, ctx, event_id: int):
        """Display the subscribers of an event"""

        db_data = self._load_db()
        events_in_db = db_data.get("events", {})
        users_dict = events_in_db.get(str(event_id), {})
        if not users_dict:
            await ctx.send("Aucun inscrit trouvé pour cet event.")
            return

        # Sort the users by joined_at
        sorted_users_dict = sorted(users_dict.values(), key=lambda x: x['joined_at'])

        message = "\n".join(
            [
                f"- {user['username']} (inscrit le {self._parse_date(user['joined_at'])})"
                for user in sorted_users_dict
            ]
        )
        await ctx.send(f"👥 Inscriptions pour l'event {event_id} :\n{message}")


async def setup(bot: commands.Bot):
    await bot.add_cog(EventLogger(bot))

