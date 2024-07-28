import asyncpg
from disnake import TextInputStyle, ModalInteraction
from disnake.ui import TextInput
from disnake.ext import commands

from core.checker import *


class Transfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.user_command(name="Перевод монет")
    async def transfer(
        self, interaction: disnake.UserCommandInteraction, member: disnake.Member
    ):
        author = interaction.author

        if member.bot or not member.guild:
            return

        if interaction.author.bot or not interaction.guild:
            return

        elif member.id == author.id:
            embed = await accessDeniedCustom(
                "Вы не можете переводить монеты самому себе"
            )
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        await database(member)
        authorDB = await database(interaction.author)

        await interaction.response.send_message(
            components=[
                TextInput(
                    label=f"Серебрянных монет - {authorDB.currency:,}",
                    placeholder="Сколько вы хотите перевести серебряных монет?",
                    custom_id="m_transfer_silver_coin",
                    max_length=128,
                    style=TextInputStyle.short,
                    required=False,
                )
            ],
            ephemeral=True,
            delete_after=300
        )


def setup(bot):
    bot.add_cog(Transfer(bot))
