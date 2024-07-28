import disnake
from disnake.ext import tasks, commands

import datetime

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *


class VoiceStats(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.voiceStats.start()

    @tasks.loop(minutes=10)
    async def voiceStats(self):
        async with AsyncSession(engine) as session:
            db = await session.scalars(select(Guilds))

        for DBrow in db:
            guild_id = DBrow.guild_id

            if self.bot.get_guild(guild_id) is not disnake.Guild:
                return

            guild: disnake.Guild = self.bot.get_guild(guild_id)

            try:
                member_channel = guild.get_channel(DBrow.member_stats_channel_id)
                await member_channel.edit(name=f"👥│{len(guild.members):,}")
            except (AttributeError, disnake.errors.NotFound):
                async with AsyncSession(engine) as session:
                    await session.execute(
                        update(Guilds)
                        .where(Guilds.guild_id == guild.id)
                        .values(member_stats_channel_id=None)
                    )
                    await session.commit()

            try:
                boosts_channel = guild.get_channel(DBrow.boosts_stats_channel_id)
                await boosts_channel.edit(name=f"🚀│{guild.premium_subscription_count}")
            except (AttributeError, disnake.errors.NotFound):
                async with AsyncSession(engine) as session:
                    await session.execute(
                        update(Guilds)
                        .where(Guilds.guild_id == guild.id)
                        .values(boosts_stats_channel_id=None)
                    )
                    await session.commit()

            try:
                voice_members_channel = guild.get_channel(
                    DBrow.voice_members_channel_id
                )
                voice_members = 0
                for x in guild.voice_channels + guild.stage_channels:
                    voice_members += len(x.members)

                await voice_members_channel.edit(name=f"🔊│{voice_members}")
            except (AttributeError, disnake.errors.NotFound):
                async with AsyncSession(engine) as session:
                    await session.execute(
                        update(Guilds)
                        .where(Guilds.guild_id == guild.id)
                        .values(voice_members_channel_id=None)
                    )
                    await session.commit()

            try:
                date_channel = guild.get_channel(DBrow.date_channel_id)
                month = datetime.datetime.now().strftime("%B").capitalize()
                await date_channel.edit(
                    name=f"📅│{datetime.datetime.now().strftime(f'%d-ое {month}, %A по МСК')}"
                )
            except (AttributeError, disnake.errors.NotFound):
                async with AsyncSession(engine) as session:
                    await session.execute(
                        update(Guilds)
                        .where(Guilds.guild_id == guild.id)
                        .values(date_channel_id=None)
                    )
                    await session.commit()

    @voiceStats.before_loop
    async def before_voiceStats(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(VoiceStats(bot))
