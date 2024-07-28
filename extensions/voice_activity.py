import time
import disnake
from disnake.ext import commands
from sqlalchemy import select, delete
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *
import datetime


MIN_MEMBER_AMOUNT = 2


class VoiceActivityCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.count_for = {}
        self.allowed_channels = set()

    def external_sync(self, member: disnake.Member) -> None:
        if voice_state := member.voice:
            self._check_channel(voice_state.channel)
            self._sync_member(member)

    @commands.Cog.listener()
    @commands.is_owner()
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ) -> None:
        if member.bot:
            return

        if before.channel != after.channel:
            if before.channel:
                await self._check_channel(before.channel)
            if after.channel:
                await self._check_channel(after.channel)

        await self._sync_member(member)

    async def _sync_member(self, member: disnake.Member) -> None:
        await self._try_remove_from_count(member)
        await self._try_add_to_count(member)

    async def _try_remove_from_count(self, member: disnake.Member) -> None:
        if not self._is_count_for(member):
            return

        if member.bot:
            return

        db = await database(member)
        seconds = round(time.time() - self.count_for.pop(member.id))
        if seconds <= 20:
            return

        rounded_seconds = round(seconds / 15)
        exp_add = rounded_seconds * 3
        currency_add = rounded_seconds * 2
        user_exp = 5 * (db[0].level ** 2) + (50 * db[0].level) + 100

        async with AsyncSession(engine) as session:
            await session.execute(
                update(Users)
                .where(
                    and_(Users.user_id == member.id, Users.guild_id == member.guild.id)
                )
                .values(all_voice_time=Users.all_voice_time + seconds)
            )
            await session.commit()

        async with AsyncSession(engine) as session:
            await session.execute(
                update(Users)
                .where(and_(Users.user_id == member.id, Users.guild_id == member.id))
                .values(currency=Users.currency + currency_add, exp=Users.exp + exp_add)
            )
            await session.commit()

        if db[0].exp >= user_exp:
            async with AsyncSession(engine) as session2:
                await session2.execute(
                    update(Users)
                    .where(
                        and_(
                            Users.user_id == member.id,
                            Users.guild_id == member.guild.id,
                        )
                    )
                    .values(
                        level=Users.level + 1,
                        exp=Users.exp - user_exp,
                    )
                )
                await session2.commit()

            embed = disnake.Embed(
                title=f"{member.guild.name}",
                description=f"Ты достиг **{db[0].level + 1}-го** уровня",
                color=EmbedColor.MAIN_COLOR.value,
            )
            embed.timestamp = datetime.datetime.utcnow()

        channel = await levelUpChannel(member.guild)
        if not channel:
            return

        channel_guild = self.bot.get_channel(channel["level_up_channel"])
        embed_channel_levelup = disnake.Embed(
            title=f"{member.guild.name}",
            description=f"Достиг **{db[0].level + 1}-го** уровня",
            color=EmbedColor.MAIN_COLOR.value,
        )
        embed_channel_levelup.timestamp = datetime.datetime.utcnow()

        try:
            if channel_guild.id is member.guild.id:
                await channel.send(embed=embed_channel_levelup)
        except AttributeError:
            async with AsyncSession(engine) as session:
                await session.execute(
                    delete(Guilds).where(Guilds.guild_id == channel_guild.id)
                )
                await session.commit()

    async def _try_add_to_count(self, member: disnake.Member) -> None:
        voice_state = member.voice
        if not voice_state:
            return
        if not self._is_can_add_to_count(member):
            return

        self.count_for[member.id] = time.time()

    async def _check_channel(self, channel: disnake.VoiceChannel) -> None:
        members = channel.members
        members = list(filter(_is_conversation_participant, members))

        if len(members) >= MIN_MEMBER_AMOUNT:
            if not self._is_channel_allowed(channel):
                self.allowed_channels.add(channel.id)
                for member in members:
                    await self._try_add_to_count(member)
        else:
            if self._is_channel_allowed(channel):
                self.allowed_channels.remove(channel.id)
                for member in members:
                    await self._try_remove_from_count(member)

    def _is_can_add_to_count(self, member: disnake.Member) -> bool:
        voice_state = member.voice
        return (
            _is_conversation_participant(member)
            and not self._is_count_for(member)
            and self._is_channel_allowed(voice_state.channel)
        )

    def _is_count_for(self, member: disnake.Member) -> bool:
        return member.id in self.count_for

    def _is_channel_allowed(self, channel: disnake.VoiceChannel) -> bool:
        return channel.id in self.allowed_channels


def _is_conversation_participant(member: disnake.Member) -> bool:
    return not member.bot and not _is_muted(member)


def _is_muted(member: disnake.Member) -> bool:
    voice_state = member.voice
    return voice_state.deaf or voice_state.self_deaf


def setup(bot) -> None:
    bot.add_cog(VoiceActivityCog(bot))
