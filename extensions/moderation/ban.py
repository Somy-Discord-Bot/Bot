from disnake.ext import tasks, commands

import datetime

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *


class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Заблокировать навсегда")
    async def ban(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(name="пользователь"),
        reason: str = commands.Param(name="причина", default="без причины"),
    ):
        if interaction.author.bot or not interaction.author.guild:
            return

        db = await database(interaction.author)
        await interaction.response.defer()

        if not list(
            set(db[1].admin_roles_ids).intersection(
                set([ids[1].id for ids in interaction.author.roles])
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

        elif list(
            set(db[1].admin_roles_ids).intersection(
                set([ids.id for ids in member.roles])
            )
        ):
            if interaction.author.top_role <= member.top_role:
                embed = await accessDeniedCustom(
                    "Вы не можете заглушить администратора чья роль выше или равна вашей"
                )
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

        elif interaction.author.id is member.id:
            embed = await accessDeniedCustom(
                "Вы не можете снять заглушку с самого себя"
            )
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        await member.ban(reason=reason, delete_message_days=7)

        embed = disnake.Embed(
            title=f"{EmbedEmoji.ACCESS_ALLOWED.value} Пользователь навсегда заблокирован",
            description=None,
            color=EmbedColor.ACCESS_ALLOWED.value,
        )
        embed.add_field(
            name="Оператор",
            value=f"<@{interaction.author.id}>\n" f"`{interaction.author.id}`",
            inline=True,
        )
        embed.add_field(
            name="Операнд", value=f"<@{member.id}>\n" f"`{member.id}`", inline=True
        )
        embed.add_field(
            name="Дата выдачи",
            value=disnake.utils.format_dt(datetime.datetime.utcnow(), "f"),
            inline=True,
        )
        embed.add_field(name="По причине", value=f"```{reason[:256]}```", inline=False)
        await interaction.response.send_message(embed=embed)

        embed = disnake.Embed(
            title=f"Вы получили вечную блокировку",
            description=f"",
            color=EmbedColor.ACCESS_ALLOWED.value,
        )
        embed.add_field(
            name="Оператор",
            value=f"<@{interaction.author.id}>\n" f"`{interaction.author.id}`",
            inline=True,
        )
        embed.add_field(name="Сервер", value=f"{interaction.guild.name}", inline=True)
        embed.add_field(
            name="Дата выдачи",
            value=disnake.utils.format_dt(datetime.datetime.utcnow(), "f"),
            inline=True,
        )
        embed.add_field(name="По причине", value=f"```{reason[:256]}```", inline=False)
        await member.send(embed=embed)


def setup(bot):
    bot.add_cog(Ban(bot))
