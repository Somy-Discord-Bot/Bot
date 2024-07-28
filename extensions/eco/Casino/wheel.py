import datetime
import random

import disnake
from disnake import Embed
from disnake.ext import commands

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *


class Wheel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(description="Колесо удачи")
    async def wheel(
        self,
        interaction: disnake.UserCommandInteraction,
        amount: int = commands.Param(name="ставка"),
    ):
        if interaction.author.bot or not interaction.guild:
            return

        author = interaction.author
        choice = random.choice(WHEEL)
        authorDB = await database(author)

        if await amount_checker(amount, authorDB, interaction) is False:
            return

        async with AsyncSession(engine) as session:
            await session.execute(
                update(Users)
                .where(
                    and_(
                        Users.user_id == interaction.author.id,
                        Users.guild_id == interaction.guild.id,
                    )
                )
                .values(currency=(Users.currency - amount) + round(amount * choice))
            )
            await session.commit()

        embed = Embed(
            title="Колесо удачи",
            description=f"<@{author.id}> выиграл(а) **{round(amount * choice):,}** {EmbedEmoji.SILVER_COIN.value}\n\n"
            f"`Ставка:`**{amount:,}** {EmbedEmoji.SILVER_COIN.value}\n"
            f"`Множитель:` **{choice}**\n"
            f"`Баланс:` **"
            f"{round((authorDB[0].currency - amount) + (amount * choice)):,}** {EmbedEmoji.SILVER_COIN.value}",
            color=EmbedColor.CASINO_ORANGE.value,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Wheel(bot))
