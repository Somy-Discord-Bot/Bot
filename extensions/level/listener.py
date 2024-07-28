import disnake
import datetime
from disnake import Embed
from disnake.ext import commands

from sqlalchemy import select, delete
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *


class ExpAdder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        elif len(message.content) < 5:
            return

        author = message.author
        guild = message.guild

        if not guild:
            return

        db = await database(author)
        user_exp = 5 * (db[0].level ** 2) + (50 * db[0].level) + 100

        if db[0].exp >= 5040055:
            async with AsyncSession(engine) as session2:
                await session2.execute(
                    update(Users)
                    .where(and_(Users.user_id == author.id, Users.guild_id == guild.id))
                    .values(level=999, exp=5040055)
                )
                await session2.commit()

            await author.send(embed=await maxLevel())
            return

        if db[0].exp >= user_exp:
            async with AsyncSession(engine) as session2:
                await session2.execute(
                    update(Users)
                    .where(and_(Users.user_id == author.id, Users.guild_id == guild.id))
                    .values(
                        level=Users.level + 1,
                        exp=Users.exp - user_exp,
                    )
                )
                await session2.commit()

            embed = Embed(
                title=f"{guild.name}",
                description=f"Ты достиг **{db[0].level + 1}-го** уровня",
                color=EmbedColor.MAIN_COLOR.value,
            )
            embed.timestamp = datetime.datetime.utcnow()

        async with AsyncSession(engine) as session:
            await session.execute(
                update(Users)
                .where(and_(Users.user_id == author.id, Users.guild_id == guild.id))
                .values(exp=Users.exp + 3)
            )
            await session.commit()


def setup(bot):
    bot.add_cog(ExpAdder(bot))
