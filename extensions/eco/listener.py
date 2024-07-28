import disnake
from disnake.ext import commands
import datetime

from sqlalchemy import select, delete
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *


class CurrencyAdder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        elif len(f"{message.content}") < 5:
            return

        author = message.author
        guild = message.guild

        if not guild:
            return

        await database(author)

        async with AsyncSession(engine) as session:
            await session.execute(
                update(Users)
                .where(
                    and_(
                        Users.user_id == author.id,
                        Users.guild_id == guild.id
                    )
                )
                .values(currency=Users.currency + 1)
            )
            await session.commit()


def setup(bot):
    bot.add_cog(CurrencyAdder(bot))
