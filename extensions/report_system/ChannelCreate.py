import disnake
from disnake.ext import commands
import datetime

from sqlalchemy import select, delete, insert, update
from sqlalchemy import and_
from sqlalchemy import insert, text
from sqlalchemy import update, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import array

from core.checker import *


class CloseTicketButtons(disnake.ui.View):
    def __init__(self, buttonAuthor: disnake.Member):
        super().__init__(timeout=None)
        self.buttonAuthor = buttonAuthor

    @disnake.ui.button(
        label="Закрыть тикет",
        custom_id="report_button_close_ticket",
        style=disnake.ButtonStyle.red,
        emoji="❌",
        row=1,
    )
    async def TakeTickerButton(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        async with AsyncSession(engine) as session:
            await session.execute(
                update(Users)
                .where(
                    and_(
                        Users.user_id == interaction.author.id,
                        Users.guild_id == interaction.guild.id,
                    )
                )
                .values(report_ticket_channel_id=None)
            )
            await session.commit()

        await interaction.channel.delete()


class TicketButtons(disnake.ui.View):
    def __init__(self, buttonAuthor: disnake.Member):
        super().__init__(timeout=None)
        self.buttonAuthor = buttonAuthor

    @disnake.ui.button(
        label="Забрать тикет",
        custom_id="report_button_take_ticket",
        style=disnake.ButtonStyle.green,
        emoji="🟢",
        row=1,
    )
    async def TakeTickerButton(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        if await check_admin(interaction) is True:
            await set_channel_permissions(interaction, self.buttonAuthor)


async def check_admin(interaction: disnake.MessageInteraction):
    db_guild = await database(interaction.author)

    if not list(
        set(db_guild[1].admin_roles_ids).intersection(
            set([ids.id for ids in interaction.author.roles])
        )
    ):
        embed = await accessDeniedCustom("У вас нет ни одной админ-роли")
        embed.add_field(
            name="> Способы решения",
            value=f"```- Получить админ-роль \n"
            f"- Указать админ-роли на [сайте]{'https://discord.gg'} в раздела 'Администрирование', "
            f"если вы администратор/владелец этой гильдии```",
            inline=False,
        )
        await interaction.send(embed=embed, ephemeral=True, delete_after=15)
        return False
    return True


async def set_channel_permissions(
    interaction: disnake.MessageInteraction, buttonAuthor: disnake.Member
):
    await channel_edit(interaction)
    await interaction.channel.set_permissions(
        interaction.guild.default_role, view_channel=False
    )
    await interaction.channel.set_permissions(
        buttonAuthor,
        read_messages=True,
        send_messages=True,
        attach_files=True,
    )
    await interaction.channel.set_permissions(
        interaction.author,
        read_messages=True,
        send_messages=True,
        attach_files=True,
    )
    return await admin_take_ticket_send(interaction, buttonAuthor)


async def channel_edit(interaction: disnake.MessageInteraction):
    await interaction.channel.edit(
        name=f"🔴│{interaction.author.name}",
    )
    return True


async def admin_take_ticket_send(
    interaction: disnake.MessageInteraction, buttonAuthor: disnake.Member
):
    embed_admin_take_ticket = disnake.Embed(
        title="Администратор забрал тикет",
        description=f"Администратор - <@{interaction.author.id}> (`{interaction.author.id}`) \n"
        f"Время: {disnake.utils.format_dt(datetime.datetime.now())}",
        colour=EmbedColor.MAIN_COLOR.value,
    )

    embed_edited_ticket = disnake.Embed(
        title="Тикет активен", color=EmbedColor.MAIN_COLOR.value
    )

    await interaction.response.send_message(embed=embed_admin_take_ticket)
    await interaction.message.edit(
        embed=embed_edited_ticket, view=CloseTicketButtons(buttonAuthor)
    )


class ReportSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def ReportButtonsTrigger(self, interaction: disnake.MessageInteraction):
        if interaction.component.custom_id == "report_button_text":
            await handle_text_report(interaction)
        elif interaction.component.custom_id == "report_button_voice":
            await handle_voice_report(interaction)


async def handle_text_report(interaction: disnake.MessageInteraction):
    db = await database(interaction.author)

    if db[0].report_ticket_channel_id:
        channel = interaction.guild.get_channel(db[0].report_ticket_channel_id)
        if channel is None:
            await reset_report_ticket_channel(interaction)
        else:
            await send_error_message(interaction, "Вы уже создали тикет")
            return

    channel = await create_text_ticket_channel(interaction)
    await send_in_report_channel(interaction, channel)
    await send_in_ticket_message(channel, interaction.author)
    await update_ticket_channel_id(interaction, channel.id)


async def send_in_report_channel(
    interaction: disnake.MessageInteraction, channel: disnake.TextChannel
):
    embed = disnake.Embed(
        title="Вы создали тикет",
        description=channel.mention,
        color=EmbedColor.ACCESS_ALLOWED.value,
    )
    await interaction.response.send_message(
        embed=embed, ephemeral=True, delete_after=15
    )
    return


async def reset_report_ticket_channel(interaction: disnake.MessageInteraction):
    async with AsyncSession(engine) as session:
        await session.execute(
            update(Users)
            .where(
                and_(
                    Users.user_id == interaction.author.id,
                    Users.guild_id == interaction.guild.id,
                )
            )
            .values(report_ticket_channel_id=None)
        )
        await session.commit()


async def send_error_message(interaction: disnake.MessageInteraction, title: str):
    embed_err = disnake.Embed(title=title, color=EmbedColor.MAIN_COLOR.value)
    await interaction.response.send_message(
        embed=embed_err, ephemeral=True, delete_after=15
    )
    return


async def create_text_ticket_channel(interaction: disnake.MessageInteraction):
    guild_data = await fetch_guild_data(interaction)
    channel = interaction.guild.get_channel(guild_data.report_channel_id)
    channel = await channel.category.create_text_channel(
        f"🟢│{interaction.author.name}"
    )
    await configure_ticket_channel_permissions(
        channel, interaction.guild, guild_data.admin_roles_ids
    )
    return channel


async def configure_ticket_channel_permissions(
    channel: disnake.TextChannel, guild: disnake.Guild, admin_roles_ids
):
    await channel.set_permissions(guild.default_role, read_messages=False)
    for role_id in admin_roles_ids:
        role = guild.get_role(role_id)
        await channel.set_permissions(
            role, read_messages=True, send_messages=True, attach_files=True
        )


async def fetch_guild_data(interaction: disnake.MessageInteraction):
    async with AsyncSession(engine) as session:
        return await session.scalar(
            select(Guilds).where(Guilds.guild_id == interaction.guild.id)
        )


async def send_in_ticket_message(channel: disnake.TextChannel, author: disnake.Member):
    embed = disnake.Embed(
        title="Тикет открыт!",
        description="Опишите подробно вашу проблему",
        color=EmbedColor.MAIN_COLOR.value,
    )
    await channel.send(embed=embed, view=TicketButtons(author))


async def update_ticket_channel_id(
    interaction: disnake.MessageInteraction, channel_id: int
):
    async with AsyncSession(engine) as session:
        await session.execute(
            update(Users)
            .where(
                Users.user_id == interaction.author.id,
                Users.guild_id == interaction.guild.id,
            )
            .values(report_ticket_channel_id=channel_id)
        )
        await session.commit()


async def handle_voice_report(interaction: disnake.MessageInteraction):
    if interaction.author.voice is None:
        await send_error_message(interaction, "Вы не находитесь в голосовом канале")
        return

    notification_channel_id = await fetch_report_notification_channel(interaction)
    if notification_channel_id:
        await notify_about_voice_report(interaction, notification_channel_id)


async def fetch_report_notification_channel(interaction: disnake.MessageInteraction):
    async with AsyncSession(engine) as session:
        return await session.scalar(
            select(Guilds.report_notif_channel_id).where(
                Guilds.guild_id == interaction.guild.id
            )
        )


async def notify_about_voice_report(
    interaction: disnake.MessageInteraction, channel_id: int
):
    channel = interaction.guild.get_channel(channel_id)
    if channel:
        embed = disnake.Embed(
            title="Голосовая жалоба",
            description=f"Поступила из канала <#{interaction.author.voice.channel.id}>",
            color=EmbedColor.MAIN_COLOR.value,
        )
        await channel.send(embed=embed)
        await send_error_message(interaction, "Жалоба отправлена")


def setup(bot):
    bot.add_cog(ReportSystem(bot))
