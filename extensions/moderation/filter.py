import disnake
from disnake.ext import commands
from core.checker import *
from core.messages import *


class FilterBadWords(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if await banWords(str(message.content)) is True:
            await message.delete()
            await message.author.send(embed=await accessDeniedCustom("Не матерись!"))

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        caps = 0
        for letter in str(message.content):
            if letter.isupper():
                caps += 1
        try:
            if round(caps / len(str(message.content)) * 100) > 70:
                if len(str(message.content)) <= 6:
                    return
                await message.delete()
                await message.author.send(
                    embed=await accessDeniedCustom(
                        "Слишком много **КАПСА** в сообщении"
                    )
                )
        except ZeroDivisionError:
            pass


def setup(bot):
    bot.add_cog(FilterBadWords(bot))
