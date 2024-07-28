import datetime
import disnake
from disnake.ext import commands

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core import *


class UnMute(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(description="Снять заглушку")
    async def unmute(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(name="пользователь"),
        reason: str = commands.Param(
            description="По умолчанию: 'без причины'", default="без причины"
        ),
    ):
        if defaultMemberChecker(interaction, member) is False:
            return

        await interaction.response.defer()
        db = await database(member)

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

        elif db[0].mute_time is None:
            embed = await accessDeniedCustom(
                f"{member.mention} `{member.id}` не заглушен"
            )
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        await member.remove_roles(db[1].mute_role, reason=reason)
        async with AsyncSession(engine) as session:
            await session.execute(
                update(Users)
                .where(
                    and_(
                        Users.user_id == member.id,
                        Users.guild_id == interaction.guild.id,
                    )
                )
                .values(mute_time=None)
            )
            await session.commit()

        embed = disnake.Embed(
            title=f"{EmbedEmoji.ACCESS_ALLOWED.value} Заглушка снята",
            description="",
            color=EmbedColor.ACCESS_ALLOWED.value,
        )
        embed.add_field(
            name="Оператор",
            value=f"<@{interaction.author.id}>\n" f"`{interaction.author.id}`",
            inline=True,
        )
        embed.add_field(
            name="Операнд", value=f"<@{member.id}> \n" f"{member.id}", inline=True
        )
        embed.add_field(name="Гильдия", value=interaction.guild.name, inline=True)
        embed.add_field(
            name="Дата снятия",
            value=disnake.utils.format_dt(datetime.datetime.now(), "f"),
            inline=True,
        )
        await interaction.send(embed=embed)

        embed_member = disnake.Embed(
            title=f"🔊 Заглушка снята",
            description="",
            color=EmbedColor.ACCESS_ALLOWED.value,
        )
        embed_member.add_field(
            name="Оператор",
            value=f"<@{interaction.author.id}>\n" f"`{interaction.author.id}`",
            inline=True,
        )
        embed_member.add_field(
            name="Гильдия", value=interaction.guild.name, inline=True
        )
        embed_member.add_field(
            name="Дата снятия",
            value=disnake.utils.format_dt(datetime.datetime.now(), "f"),
            inline=True,
        )
        await member.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(UnMute(bot))
