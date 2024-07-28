from sqlalchemy import select, delete, func
from sqlalchemy import and_, desc
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

import disnake
from disnake.ext import commands

from core.checker import *


class ClearMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        description="Удаление сообщений",
    )
    async def clear(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        amount: int = commands.Param(name="кол-во", min_value=0, max_value=100),
    ):
        if interaction.author.bot or not interaction.author.guild:
            return

        channel = interaction.channel
        num = 0
        db = await database(interaction.author)

        START_FILL = EmbedEmoji.START_FILL.value
        START_NO_FILL = EmbedEmoji.START_NO_FILL.value
        END_FILL = EmbedEmoji.END_FILL.value
        FILL = EmbedEmoji.FILL.value
        NO_FILL = EmbedEmoji.NO_FILL.value
        END_NO_FILL = EmbedEmoji.END_NO_FILL.value

        if not list(
            set(db[1].admin_roles_ids).intersection(
                set([ids.id for ids in interaction.author.roles])
            )
        ):
            embed = await accessDeniedCustom("У вас нет ни одной-админ роли")
            embed.add_field(
                name="> Способы решения",
                value=f"```- Получить админ-роль \n"
                f"- Указать админ-роли на [сайте]{'https://discord.gg'} в раздела 'Администрирование', "
                f"если вы администратор/владелец этой гильдии```",
                inline=False,
            )
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        embed = disnake.Embed(
            title="Удаление сообщений",
            description="",
            color=EmbedColor.MAIN_COLOR.value,
        )
        embed.add_field(name="Секунду...", value="", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

        while num <= amount:
            await channel.purge(limit=num)

            END_CHECK = END_FILL if num == amount else END_NO_FILL
            START_CHECK = START_FILL if num > 0 else START_NO_FILL
            fill_count = round(10 * num / amount)
            current_count = f"**{num}** {START_CHECK}{FILL * fill_count}{NO_FILL * (10 - fill_count)}{END_CHECK} **{amount}**"

            num += 1

            edited_embed = disnake.Embed(
                title="Удаление сообщений",
                description="",
                color=EmbedColor.MAIN_COLOR.value,
            )
            edited_embed.add_field(
                name="В процессе...", value=current_count, inline=True
            )

            try:
                await interaction.edit_original_response(embed=edited_embed)
            except disnake.errors.NotFound:
                pass

        embed = disnake.Embed(
            title=f"{EmbedEmoji.ACCESS_ALLOWED.value} Удаление сообщений",
            description=f"Удалено **{amount}** сообщений",
            color=EmbedColor.ACCESS_ALLOWED.value,
        )

        try:
            await interaction.edit_original_response(embed=embed)
        except disnake.errors.NotFound:
            await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(ClearMessage(bot))
