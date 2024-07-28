import disnake
from disnake.ext import commands

from core.checker import *


class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Ваша карточка рейтинга")
    async def rank(
        self,
        interaction: disnake.UserCommandInteraction,
        member: disnake.Member = commands.Param(name="пользователь", default=None),
    ) -> None:
        if not member:
            target = interaction.author
        else:
            target = member

        if target.bot or not target.guild:
            return

        await database(target)
        file = await getRankCard(target)
        await interaction.send(file=file)


def setup(bot):
    bot.add_cog(Rank(bot))
