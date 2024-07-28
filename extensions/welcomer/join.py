import asyncpg
from disnake import TextInputStyle
from disnake.ext import commands

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *


class MemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member) -> None:
        await database(member)

        guild = member.guild

        async with AsyncSession(engine) as session:
            db_guild = await session.scalar(
                select(Guilds).where(guild_id == guild.id)  # type: ignore
            )

        if not db_guild.join_channel_id:
            pass

        join_channel = await guild.get_channel(db_guild.join_channel_id)

        join_embed = disnake.Embed(
            description=f"{member.mention} +",
            color=EmbedColor.MAIN_COLOR.value
        )
        try:
            await join_channel.send(embed=join_embed)
        except AttributeError:
            pass


def setup(bot):
    bot.add_cog(MemberJoin(bot))
