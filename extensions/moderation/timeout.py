from disnake.ext import tasks, commands
import disnake

import datetime

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core import *


class Timeout(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command()
    async def timeout(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(name="пользователь"),
        minutes: int = commands.Param(name="минут", description="максимум 29 дней"),
        reason: str = commands.Param(name="причина", default="без причины"),
    ):
        if await defaultMemberChecker(interaction, member) is False:
            return

        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration=duration, reason=reason)

        timeout_end_time = datetime.datetime.now() + duration
        since = disnake.utils.format_dt(datetime.datetime.now(), "f")
        to = (
            disnake.utils.format_dt(timeout_end_time, "f")
            + ","
            + "\n"
            + disnake.utils.format_dt(timeout_end_time, "R")
        )

        embed = disnake.Embed(
            title=f"{EmbedEmoji.ACCESS_ALLOWED.value} Пользователь заглушен",
            description="Тип: timeout",
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
        embed.add_field(name="_ _", value="_ _", inline=True)
        embed.add_field(name="Дата выдачи", value=since, inline=True)
        embed.add_field(name="Дата снятия", value=to, inline=True)
        embed.add_field(name="По причине", value=f"```{reason[:256]}```", inline=False)
        await interaction.send(embed=embed)

        embed_member = disnake.Embed(
            title=f"🔇 Вы заглушены",
            description="Тип: timeout",
            color=EmbedColor.ACCESS_DENIED.value,
        )
        embed_member.add_field(
            name="Оператор",
            value=f"<@{interaction.author.id}>\n" f"`{interaction.author.id}`",
            inline=True,
        )
        embed_member.add_field(
            name="Гильдия", value=f"{interaction.guild.name}", inline=True
        )
        embed_member.add_field(name="_ _", value="_ _", inline=True)
        embed_member.add_field(name="Дата выдачи", value=since, inline=True)
        embed_member.add_field(name="Дата снятия", value=to, inline=True)
        embed_member.add_field(
            name="По причине", value=f"```{reason[:256]}```", inline=False
        )
        await member.send(embed=embed_member)


def setup(bot):
    bot.add_cog(Timeout(bot))
