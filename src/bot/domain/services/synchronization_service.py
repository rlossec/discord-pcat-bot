"""
Service de synchronisation entre Discord et la base de données.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from bot.core.config import PARIS_TZ, SUBSCRIPTION_COOLDOWN_SECONDS
from bot.core.interfaces.unit_of_work import UnitOfWork
from bot.core.logging_config import logger


NotificationEntry = Tuple[str, str, str, str]


class SynchronizationService:
    """Assure la synchronisation des événements, participations et utilisateurs."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        notification_channel_id: int,
    ) -> None:
        self.uow_factory = uow_factory
        self.notification_channel_id = notification_channel_id
        self._subscription_cooldown: Dict[Tuple[str, str], datetime] = {}

    def _is_in_subscription_cooldown(self, user_id: str, event_id: str) -> bool:
        """Retourne True si l'utilisateur est en cooldown pour cet événement."""
        if SUBSCRIPTION_COOLDOWN_SECONDS <= 0:
            return False
        key = (user_id, event_id)
        last = self._subscription_cooldown.get(key)
        if not last:
            return False
        return (datetime.now(PARIS_TZ) - last) < timedelta(seconds=SUBSCRIPTION_COOLDOWN_SECONDS)

    def _record_subscription_action(self, user_id: str, event_id: str) -> None:
        """Enregistre une action d'inscription/désinscription pour le cooldown."""
        if SUBSCRIPTION_COOLDOWN_SECONDS <= 0:
            return
        self._subscription_cooldown[(user_id, event_id)] = datetime.now(PARIS_TZ)

    async def sync_guild(self, bot: commands.Bot, guild: discord.Guild) -> None:
        """Synchronise les données Discord avec la base."""
        logger.info("🔄 [SYNC] Synchronisation des événements, participations et utilisateurs...")

        notification_channel = await self._resolve_notification_channel(bot, guild)
        if notification_channel is None:
            logger.warning(
                "⚠️ [SYNC] Impossible de trouver le canal de notifications (%s). Les alertes d'inscriptions seront ignorées.",
                self.notification_channel_id,
            )

        notifications: List[NotificationEntry] = []

        try:
            discord_events: List[discord.ScheduledEvent] = list(guild.scheduled_events)
            logger.info("📅 [SYNC] %d événements programmés trouvés sur Discord.", len(discord_events))

            with self.uow_factory() as uow:
                db_events = {event.discord_id: event for event in uow.events.get_all()}

                # 1. Synchronisation des événements manquants
                for discord_event in discord_events:
                    event_id = str(discord_event.id)
                    if event_id not in db_events:
                        uow.events.create_by_discord_id(event_id, discord_event.name)
                        logger.info(
                            "➕ [SYNC] Nouvel événement ajouté en base : %s (%s)",
                            discord_event.name,
                            event_id,
                        )

                # 2. Synchronisation des participations
                for discord_event in discord_events:
                    event_id = str(discord_event.id)
                    participant_ids, user_lookup = await self._collect_event_participants(discord_event)

                    db_participations = uow.participations.get_by_event(event_id)
                    db_participants = {p.user_discord_id for p in db_participations}

                    new_participants = participant_ids - db_participants
                    removed_participants = db_participants - participant_ids

                    for user_id in new_participants:
                        uow.participations.create_participation(event_id, user_id)

                        user_event_obj = user_lookup.get(user_id)
                        display_name = self._extract_display_name(user_event_obj, user_id)

                        user_entity = uow.users.get_by_discord_id(user_id)
                        if not user_entity:
                            user_entity = uow.users.get_or_create_by_discord_id(user_id, display_name)

                        username_db = user_entity.username if user_entity else display_name

                        if not self._is_in_subscription_cooldown(user_id, event_id):
                            notifications.append(("join", event_id, user_id, username_db))
                        self._record_subscription_action(user_id, event_id)
                        logger.info(
                            "✅ [SYNC] Inscription détectée pour l'événement %s (%s) : %s",
                            discord_event.name,
                            event_id,
                            username_db,
                        )

                    for user_id in removed_participants:
                        user_entity = uow.users.get_by_discord_id(user_id)
                        username_db = user_entity.username if user_entity else user_id

                        removed = uow.participations.remove_participation(event_id, user_id)
                        if removed:
                            if not self._is_in_subscription_cooldown(user_id, event_id):
                                notifications.append(("leave", event_id, user_id, username_db))
                            self._record_subscription_action(user_id, event_id)
                            logger.info(
                                "❌ [SYNC] Désinscription détectée pour l'événement %s (%s) : %s",
                                discord_event.name,
                                event_id,
                                username_db,
                            )

                # 3. Synchronisation des membres
                new_members, removed_members = await self._sync_members_table(uow, guild)
                if new_members or removed_members:
                    logger.info(
                        "👥 [SYNC] Utilisateurs synchronisés : %d ajout(s), %d suppression(s).",
                        new_members,
                        removed_members,
                    )

            # 4. Notifications dans le canal dédié
            if notifications and notification_channel:
                await self._publish_notifications(notification_channel, notifications, discord_events)

            logger.info("✅ [SYNC] Synchronisation terminée")

        except Exception as exc:
            logger.exception("❌ [SYNC] Erreur lors de la synchronisation : %s", exc)

    async def _resolve_notification_channel(
        self,
        bot: commands.Bot,
        guild: discord.Guild,
    ) -> Optional[discord.abc.Messageable]:
        """Récupère le canal de notification des inscriptions/désinscriptions."""
        channel = guild.get_channel(self.notification_channel_id) or bot.get_channel(self.notification_channel_id)
        if channel is not None:
            return channel  # type: ignore[return-value]

        try:
            channel = await bot.fetch_channel(self.notification_channel_id)
            return channel  # type: ignore[return-value]
        except discord.NotFound:
            logger.error(
                "❌ [SYNC] Canal %s introuvable. Vérifiez l'ID dans la configuration.",
                self.notification_channel_id,
            )
        except discord.Forbidden:
            logger.error(
                "❌ [SYNC] Accès refusé au canal %s. Vérifiez les permissions du bot.",
                self.notification_channel_id,
            )
        except discord.HTTPException as exc:
            logger.error("❌ [SYNC] Erreur HTTP lors de la récupération du canal : %s", exc)

        return None

    async def _collect_event_participants(
        self,
        discord_event: discord.ScheduledEvent,
    ) -> Tuple[Set[str], Dict[str, Union[discord.abc.User, discord.Member, Any]]]:
        """Retourne l'ensemble des participants d'un événement Discord."""
        participants: Set[str] = set()
        user_lookup: Dict[str, Union[discord.abc.User, discord.Member, Any]] = {}

        try:
            async for event_user in discord_event.users(limit=None):
                user_id = str(event_user.id)
                participants.add(user_id)
                user_lookup[user_id] = event_user

        except discord.Forbidden:
            logger.warning(
                "⚠️ [SYNC] Accès refusé aux participants de l'événement %s (%s).",
                discord_event.name,
                discord_event.id,
            )
        except discord.HTTPException as exc:
            logger.error(
                "❌ [SYNC] Erreur HTTP lors de la récupération des participants de %s (%s) : %s",
                discord_event.name,
                discord_event.id,
                exc,
            )

        return participants, user_lookup

    async def handle_user_add(
        self,
        bot: commands.Bot,
        scheduled_event: discord.ScheduledEvent,
        user: discord.abc.User,
    ) -> None:
        """Traite une inscription en temps réel (événement Gateway)."""
        event_id = str(scheduled_event.id)
        user_id = str(user.id)

        if self._is_in_subscription_cooldown(user_id, event_id):
            logger.debug(
                "[SYNC] Inscription ignorée (cooldown) : %s sur %s",
                user_id,
                event_id,
            )
            return

        display_name = self._extract_display_name(user, user_id)

        try:
            with self.uow_factory() as uow:
                # Vérifier si déjà inscrit (idempotence)
                existing = uow.participations.get_by_event(event_id)
                if any(p.user_discord_id == user_id for p in existing):
                    return

                uow.participations.create_participation(event_id, user_id)
                user_entity = uow.users.get_by_discord_id(user_id)
                if not user_entity:
                    uow.users.get_or_create_by_discord_id(user_id, display_name)
                uow.commit()

            logger.info(
                "✅ [SYNC] Inscription temps réel pour %s (%s) : %s",
                scheduled_event.name,
                event_id,
                display_name,
            )

            guild = getattr(scheduled_event, "guild", None) or bot.get_guild(
                getattr(scheduled_event, "guild_id", 0)
            )
            if guild:
                channel = await self._resolve_notification_channel(bot, guild)
                if channel:
                    await self._publish_notifications(
                        channel,
                        [("join", event_id, user_id, display_name)],
                        [scheduled_event],
                    )
            self._record_subscription_action(user_id, event_id)
        except Exception as exc:
            logger.exception("❌ [SYNC] Erreur lors du traitement inscription temps réel : %s", exc)

    async def handle_user_remove(
        self,
        bot: commands.Bot,
        scheduled_event: discord.ScheduledEvent,
        user: discord.abc.User,
    ) -> None:
        """Traite une désinscription en temps réel (événement Gateway)."""
        event_id = str(scheduled_event.id)
        user_id = str(user.id)

        if self._is_in_subscription_cooldown(user_id, event_id):
            logger.debug(
                "[SYNC] Désinscription ignorée (cooldown) : %s sur %s",
                user_id,
                event_id,
            )
            return

        try:
            with self.uow_factory() as uow:
                user_entity = uow.users.get_by_discord_id(user_id)
                username_db = user_entity.username if user_entity else user_id

                removed = uow.participations.remove_participation(event_id, user_id)
                if removed:
                    uow.commit()
                    logger.info(
                        "❌ [SYNC] Désinscription temps réel pour %s (%s) : %s",
                        scheduled_event.name,
                        event_id,
                        username_db,
                    )

                    guild = scheduled_event.guild or bot.get_guild(scheduled_event.guild_id)
                    if guild:
                        channel = await self._resolve_notification_channel(bot, guild)
                        if channel:
                            await self._publish_notifications(
                                channel,
                                [("leave", event_id, user_id, username_db)],
                                [scheduled_event],
                            )
                    self._record_subscription_action(user_id, event_id)
        except Exception as exc:
            logger.exception("❌ [SYNC] Erreur lors du traitement désinscription temps réel : %s", exc)

    async def _sync_members_table(
        self,
        uow: UnitOfWork,
        guild: discord.Guild,
    ) -> Tuple[int, int]:
        """Synchronise la table des utilisateurs avec les membres de la guild."""
        members_map: Dict[str, discord.Member] = {}

        try:
            async for member in guild.fetch_members(limit=None):
                members_map[str(member.id)] = member
        except discord.Forbidden:
            logger.warning(
                "⚠️ [SYNC] Accès refusé lors de la récupération des membres de la guild %s (%s).",
                guild.name,
                guild.id,
            )
        except discord.HTTPException as exc:
            logger.error(
                "❌ [SYNC] Erreur HTTP lors de la récupération des membres de la guild %s (%s) : %s",
                guild.name,
                guild.id,
                exc,
            )

        if not members_map:
            members_map = {str(member.id): member for member in guild.members}

        db_users = uow.users.get_all()
        db_users_map = {user.discord_id: user for user in db_users}

        guild_member_ids = set(members_map.keys())
        db_user_ids = set(db_users_map.keys())

        new_member_ids = guild_member_ids - db_user_ids
        removed_member_ids = db_user_ids - guild_member_ids

        for user_id in new_member_ids:
            member = members_map[user_id]
            uow.users.get_or_create_by_discord_id(user_id, member.display_name)

        for user_id in removed_member_ids:
            user = db_users_map.get(user_id)
            if user:
                uow.users.delete(user.id)

        return len(new_member_ids), len(removed_member_ids)

    async def _publish_notifications(
        self,
        channel: discord.abc.Messageable,
        notifications: List[NotificationEntry],
        discord_events: List[discord.ScheduledEvent],
    ) -> None:
        """Envoie les notifications d'inscription/désinscription dans le canal dédié."""
        events_map = {str(event.id): event for event in discord_events}

        header = self._format_notification_header()
        try:
            await channel.send(header)
        except discord.HTTPException as exc:
            logger.error("❌ [SYNC] Erreur lors de l'envoi de l'en-tête de notification : %s", exc)

        for action, event_id, _user_id, username in notifications:
            event = events_map.get(event_id)
            if event is None:
                continue

            event_name = event.name

            if action == "join":
                message = f"➕ {username} s'est inscrit à l'événement **{event_name}**."
            else:
                message = f"🛑 {username} s'est désinscrit de l'événement **{event_name}**."

            try:
                await channel.send(message)
            except discord.HTTPException as exc:
                logger.error("❌ [SYNC] Erreur lors de l'envoi de la notification : %s", exc)

    @staticmethod
    def _extract_display_name(
        user: Optional[Union[discord.abc.User, discord.Member, Any]],
        fallback_id: str,
    ) -> str:
        """Retourne un nom d'affichage exploitable pour les logs/messages."""
        if user is None:
            return f"Utilisateur {fallback_id}"

        member_attr = getattr(user, "member", None)
        if isinstance(member_attr, discord.Member):
            return member_attr.display_name

        user_attr = getattr(user, "user", None)
        if isinstance(user_attr, discord.Member):
            return user_attr.display_name
        if isinstance(user_attr, discord.User):
            return user_attr.name

        if isinstance(user, discord.Member):
            return user.display_name

        if isinstance(user, discord.User):
            return user.name

        if hasattr(user, "display_name"):
            return getattr(user, "display_name")

        if hasattr(user, "name"):
            return getattr(user, "name")

        return f"Utilisateur {fallback_id}"

    @staticmethod
    def _format_notification_header() -> str:
        """Construit l'en-tête des notifications de synchronisation."""
        now = datetime.now(PARIS_TZ)
        timestamp = now.strftime("%d/%m/%Y %H:%M UTC")
        return f"## Mise à jour des inscriptions\n{timestamp}"

