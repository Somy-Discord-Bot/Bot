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
from core.models import *
from core.messages import *


class Coin(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(description="Орёл и решка")
    async def coin(
        self,
        interaction: disnake.UserCommandInteraction,
        amount: int = commands.Param(name="ставка", ge=0),
        coin: str = commands.Param(name="монетка", choices=COIN),
    ):
        if interaction.author.bot or not interaction.guild:
            return

        author = interaction.author
        authorDB = await database(author)

        if await amount_checker(amount, authorDB, interaction) is False:
            return

        r_coin = random.choice(COIN)

        if coin != r_coin:
            async with AsyncSession(engine) as session:
                await session.execute(
                    update(Users)
                    .where(
                        and_(
                            Users.user_id == interaction.author.id,
                            Users.guild_id == interaction.guild.id,
                        )
                    )
                    .values(currency=Users.currency - amount)
                )
                await session.commit()

            embed = Embed(
                title=f"Орёл и решка",
                description=f"<@!{author.id}> выбил **{r_coin}** и ничего не выиграл\n\n"
                f"`Ставка:`**{amount:,}** {EmbedEmoji.SILVER_COIN.value}\n"
                f"`Ваша монетка:` **{coin}**\n"
                f"`Выпавшая монетка:` **{r_coin}**\n"
                f"`Баланс:` **{authorDB[0].currency - amount:,}** {EmbedEmoji.SILVER_COIN.value}",
                color=EmbedColor.CASINO_ORANGE.value,
            )
            await interaction.send(embed=embed, ephemeral=True)
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
                .values(currency=(Users.currency - amount) + (amount * 2))
            )
            await session.commit()

        embed = Embed(
            title=f"Орёл и решка",
            description=f"<@!{author.id}> выбил **{r_coin}** и получает **{amount * 2:,}** {EmbedEmoji.SILVER_COIN.value}\n\n"
            f"`Ставка:`**{amount:,}** {EmbedEmoji.SILVER_COIN.value}\n"
            f"`Множитель:` **x2**\n"
            f"`Баланс:` **{(authorDB[0].currency - amount) + (amount * 2):,}** {EmbedEmoji.SILVER_COIN.value}",
            color=EmbedColor.CASINO_ORANGE.value,
        )
        await interaction.send(embed=embed, ephemeral=True)
        return


def setup(bot):
    bot.add_cog(Coin(bot))
