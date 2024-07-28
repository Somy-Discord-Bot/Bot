from disnake.ext import tasks, commands
import disnake

import datetime

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *


class Mute(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.auto_unmute.start()

    @tasks.loop(minutes=1)
    async def auto_unmute(self):
        async with AsyncSession(engine) as session:
            users = await session.scalars(select(Users))

        for i in users:
            if i.ban_time is not None:
                if datetime.datetime.now() >= i.mute_time:
                    guild = self.bot.get_guild(i.guild_id)

                    async with AsyncSession(engine) as session:
                        db = await session.scalar(
                            select(Guilds.mute_role).where(Guilds.guild_id == guild.id)
                        )

                    if not db:
                        try:
                            async with AsyncSession(engine) as session:
                                session.add(Guilds(guild_id=guild.id))
                                await session.commit()
                        except IntegrityError as e:
                            print(f"Ошибка уникальности: {e}")
                            pass

                    member = guild.get_member(i.user_id)

                    await member.remove_roles(
                        guild.get_role(db[1].ban_role),
                        reason="Окончание заглушки",
                    )

                    async with AsyncSession(engine) as session:
                        await session.execute(
                            update(Users)
                            .where(
                                and_(
                                    Users.user_id == member.id,
                                    Users.guild_id == guild.id,
                                )
                            )
                            .values(mute_time=None)
                        )
                        await session.commit()

                    embed_member = disnake.Embed(
                        title=f"{EmbedEmoji.ACCESS_ALLOWED.value} Срок заглушки истек",
                        color=EmbedColor.ACCESS_ALLOWED.value,
                    )
                    embed_member.add_field(
                        name="Гильдия", value=f"{guild.name}", inline=True
                    )
                    await member.send(embed=embed_member)
                    return

    @auto_unmute.before_loop
    async def before_auto_unmute(self):
        await self.bot.wait_until_ready()

    @commands.slash_command(description="Заглушить")
    async def mute(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(name="пользователь"),
        minutes: int = commands.Param(
            name="минут", default=00, min_value=0, description="По умолчанию: 0"
        ),
        reason: str = commands.Param(
            name="причина",
            default="без причины",
            description="По умолчанию: 'без причины'",
        ),
    ):
        if await defaultMemberChecker(interaction, member) is False:
            return

        await interaction.response.defer()
        db = await database(interaction.author)

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

        elif member.id == self.bot.user.id:
            embed = await accessDeniedCustom("Вы не можете заглушить Ляпи")
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        elif interaction.author.id is member.id:
            embed = await accessDeniedCustom("Вы не можете заглушить самого себя")
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        elif interaction.guild.owner_id is member.id:
            embed = await accessDeniedCustom("Вы не можете заглушить владельца гильдии")
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        elif datetime.timedelta(minutes=minutes) < datetime.timedelta(minutes=5):
            embed = await accessDeniedCustom(
                "Вы не можете выдавать заглушку **менее чем на 5 минут** включительно"
            )
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        elif datetime.timedelta(minutes=minutes) > datetime.timedelta(days=365):
            embed = await accessDeniedCustom(
                "Вы не можете выдавать заглушку **более чем на год**"
            )
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        end_mute_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)

        for role in member.roles[1:]:
            await member.remove_roles(role, reason=reason)

        if not db[1].mute_role:
            role = await interaction.guild.create_role(
                name="🔇 Заглушен",
                colour=EmbedColor.ACCESS_DENIED.value,
            )
            async with AsyncSession(engine) as session:
                await session.execute(
                    update(Guilds)
                    .where(Guilds.guild_id == interaction.guild.id)
                    .values(mute_role=role.id)
                )
                await session.commit()

        await member.add_roles(
            interaction.guild.get_role(db[1].mute_role), reason=reason
        )

        since = disnake.utils.format_dt(datetime.datetime.now(), "f")
        to = (
            disnake.utils.format_dt(end_mute_time, "f")
            + ","
            + "\n"
            + disnake.utils.format_dt(end_mute_time, "R")
        )

        async with AsyncSession(engine) as session:
            await session.execute(
                update(Users)
                .where(
                    and_(
                        Users.user_id == member.id,
                        Users.guild_id == interaction.guild.id,
                    )
                )
                .values(mute_time=end_mute_time)
            )
            await session.commit()

        embed = disnake.Embed(
            title=f"{EmbedEmoji.ACCESS_ALLOWED.value} Пользователь заглушен",
            description="Тип: роль",
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
            description="Тип: роль",
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
        return


def setup(bot):
    bot.add_cog(Mute(bot))
