import random

import disnake
from disnake.ext import tasks, commands

from sqlalchemy import select, delete, func, and_, insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import array

from core.checker import *
from core.models import *


class PrivateChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_deleted.start()

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        db = await database(member)

        async with AsyncSession(engine) as session:
            triggerChannel = await session.scalar(
                select(Guilds).where(Guilds.guild_id == member.guild.id)
            )

        async def _delete_channel():
            async with AsyncSession(engine) as session2:
                await session2.execute(
                    update(Users)
                    .where(
                        and_(
                            Users.user_id == member.id,
                            Users.guild_id == member.guild.id,
                        )
                    )
                    .values(p_channel_id=None)
                )
                await session2.commit()
            try:
                await before.channel.delete()
            except disnake.errors.NotFound:
                pass

        def _check_setup_channel() -> bool:
            return before.channel.id in triggerChannel.p_channel_ids

        def _is_owner() -> bool:
            return before.channel.id == db[0].p_channel_id

        async def _new_owner():
            if (
                not before.channel
                or _check_setup_channel()
                or not _is_owner()
            ):
                return

            if len(before.channel.members) == 0:
                await _delete_channel()
            else:
                randomUser = random.choice(before.channel.members)
                async with AsyncSession(engine) as session3:
                    await session3.execute(
                        update(Users)
                        .where(
                            Users.p_channel_id == before.channel.id,
                        )
                        .values(p_channel_id=None)
                    )
                    await session3.execute(
                        update(Users)
                        .where(
                            and_(
                                Users.user_id == randomUser.id,
                                Users.guild_id == member.guild.id,
                            )
                        )
                        .values(p_channel_id=before.channel.id)
                    )
                    await session3.commit()

        await _new_owner()

        try:
            if after.channel.id in triggerChannel.p_channel_ids:
                channelName = db[0].p_channel_name or f"{member.name}"
                channelLimit = db[0].p_channel_users_limit or 0
                channelLock = db[0].p_channel_lock
                privateChannel = await member.guild.create_voice_channel(
                    channelName, category=after.channel.category
                )

                async with AsyncSession(engine) as session5:
                    await session5.execute(
                        update(Users)
                        .where(
                            and_(
                                Users.user_id == member.id,
                                Users.guild_id == member.guild.id,
                            )
                        )
                        .values(p_channel_id=privateChannel.id)
                    )
                    await session5.commit()

                await member.move_to(privateChannel)
                await privateChannel.edit(user_limit=channelLimit)
                await privateChannel.set_permissions(
                    member.guild.default_role, connect=channelLock
                )
        except (AttributeError, disnake.errors.NotFound):
            return

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: disnake.VoiceChannel):
        async with AsyncSession(engine) as session:
            triggerChannel = await session.scalar(
                select(Guilds).where(Guilds.guild_id == channel.guild.id)
            )

        if channel.id in triggerChannel.p_channel_ids:
            async with AsyncSession(engine) as session:
                await session.execute(
                    update(Guilds)
                    .where(Guilds.guild_id == channel.guild.id)
                    .values(
                        p_channel_ids=triggerChannel.p_channel_ids.remove(channel.id)
                    )
                )
                await session.commit()
        return

    @tasks.loop(seconds=10.0)
    async def channel_deleted(self):
        async with AsyncSession(engine) as session:
            channelDB = await session.scalars(
                select(Users).where(Users.p_channel_id > 1)
            )

        for channel in channelDB:
            channelDel = channel.p_channel_id
            getChannel: disnake.VoiceChannel = self.bot.get_channel(channelDel)

            if getChannel is None:
                async with AsyncSession(engine) as session:
                    await session.execute(
                        update(Users)
                        .where(Users.p_channel_id == channelDel)
                        .values(p_channel_id=None)
                    )
                    await session.commit()
                return

            if len(getChannel.members) == 0:
                async with AsyncSession(engine) as session:
                    await session.execute(
                        update(Users)
                        .where(Users.p_channel_id == channelDel)
                        .values(p_channel_id=None)
                    )
                    await session.commit()

                await getChannel.delete()
                return

    @channel_deleted.before_loop
    async def before_channel_deleted(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(PrivateChannel(bot))
