import disnake
from disnake import TextInputStyle, MessageInteraction, Embed
from disnake.ext import commands
from disnake.ui import TextInput, button, View

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *

import datetime


async def userinfo(member: disnake.Member, file: disnake.File) -> disnake.Embed:
    memberDB = await database(member)

    vk_url = format_url(memberDB[2].vk_url, "https://vk.com/")
    inst_url = format_url(memberDB[2].inst_url, "https://www.instagram.com/")
    tg_url = format_url(memberDB[2].tg_url, "https://t.me/")
    description = memberDB[2].description[:256]
    currency = f"{memberDB[0].currency:,}"
    donate = f"{memberDB[2].donate:,}"
    voice_seconds = str(datetime.timedelta(seconds=int(memberDB[0].all_voice_time)))

    if member.avatar:
        icon_url = member.avatar
    else:
        icon_url = None

    embed = Embed(description=member.mention, color=EmbedColor.MAIN_COLOR.value)
    embed.set_author(
        name=member.name,
        icon_url=icon_url,
    )
    embed.add_field(
        name="> 💬 Статус",
        value=f"```{description}```",
        inline=False,
    )
    embed.add_field(
        name="> 🔊 Время в войсе", value=f"```{voice_seconds}```", inline=True
    )
    embed.add_field(
        name=f"> {EmbedEmoji.SILVER_COIN.value} Серебрянные монеты",
        value=f"```{currency}```",
        inline=True,
    )
    embed.add_field(
        name=f"> {EmbedEmoji.GOLD_COIN.value} Золотые монеты",
        value=f" ```{donate}```",
        inline=True,
    )
    embed.add_field(
        name=f"> {EmbedEmoji.VK_ICON.value} **VK**",
        value=vk_url or "Ссылка не установлена",
        inline=True,
    )
    embed.add_field(
        name=f"> {EmbedEmoji.INST_ICON.value} **Instagram**",
        value=inst_url or "Ссылка не установлена",
        inline=True,
    )
    embed.add_field(
        name=f"> {EmbedEmoji.TG_ICON.value} **Telegram**",
        value=tg_url or "Ссылка не установлена",
        inline=True,
    )

    embed.set_image(file=file)
    return embed


class UserChange(disnake.ui.View):
    def __init__(self, buttonAuthor: disnake.Member):
        super().__init__(timeout=None)
        self.buttonAuthor = buttonAuthor
        self.message = None

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        if self.buttonAuthor.id != interaction.author.id:
            embed = await accessDeniedButton(self.buttonAuthor)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    @button(
        label="Изменить статус", style=disnake.ButtonStyle.secondary, emoji="📃", row=1
    )
    async def change_status(
        self, ui_button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление профилем",
            custom_id="u_profile_changed_desc",
            components=[
                TextInput(
                    label='Статус"',
                    placeholder="Напишите что-нибудь",
                    custom_id="m_about",
                    max_length=256,
                    style=TextInputStyle.long,
                    required=True,
                )
            ]
        )

    @button(
        label="Изменить карточку рейтинга",
        style=disnake.ButtonStyle.secondary,
        emoji="🎆",
        row=1,
    )
    async def change_rank_card(
        self, ui_button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        user_global = await database(interaction.author)
        select_view = View()
        message = interaction.message
        select_view.add_item(RankCardSelect(user_global[2], message))

        await interaction.response.send_message(
            view=select_view, ephemeral=True, delete_after=30
        )

    @button(
        label="Редактировать ссылку на VK",
        style=disnake.ButtonStyle.secondary,
        emoji=EmbedEmoji.VK_ICON.value,
        row=2,
    )
    async def change_url_vk(
        self, ui_button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление профилем",
            custom_id="u_profile_changed_vk_url",
            components=[
                TextInput(
                    label="Ссылка на ВК",
                    placeholder="Укажите ваш тег без @ и ссылок",
                    custom_id="m_vk_url",
                    max_length=32,
                    style=TextInputStyle.short,
                    required=True,
                )
            ]
        )

    @button(
        label="Редактировать ссылку на Instagram",
        style=disnake.ButtonStyle.secondary,
        emoji=EmbedEmoji.INST_ICON.value,
        row=2,
    )
    async def change_url_inst(
        self, ui_button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление профилем",
            custom_id="u_profile_changed_inst_url",
            components=[
                TextInput(
                    label="Ссылка на Instagram",
                    placeholder="Укажите ваш тег без @ и ссылок",
                    custom_id="m_inst_url",
                    max_length=32,
                    style=TextInputStyle.short,
                    required=True,
                )
            ]
        )

    @button(
        label="Редактировать ссылку на Telegram",
        style=disnake.ButtonStyle.secondary,
        emoji=EmbedEmoji.TG_ICON.value,
        row=2,
    )
    async def change_url_tg(
        self, ui_button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление профилем",
            custom_id="u_profile_changed_tg_url",
            components=[
                TextInput(
                    label="Ссылка на Telegram",
                    placeholder="Укажите ваш тег без @ и ссылок",
                    custom_id="m_tg_url",
                    max_length=32,
                    style=TextInputStyle.short,
                    required=True,
                )
            ]
        )


class RankCardSelect(disnake.ui.StringSelect):
    def __init__(self, user_global, message):
        self.message = message

        options = []
        for i in user_global.cards:
            options.append(
                disnake.SelectOption(
                    value=f"{i}",
                    label=f"{ID_CARD_NAMES[i]}",
                    description=f'Выбрать карточку "{ID_CARD_NAMES[i]}"',
                )
            )

        super().__init__(
            placeholder="Выберите отображаемую карточку рейтинга",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        async with AsyncSession(engine) as session:
            await session.execute(
                update(Users)
                .where(
                    and_(
                        Users.user_id == interaction.author.id,
                        Users.guild_id == interaction.guild.id,
                    )
                )
                .values(select_card=int(self.values[0]))
            )
            await session.commit()

        await interaction.response.edit_message(
            f'Вы выбрали "{ID_CARD_NAMES[int(self.values[0])]}"', view=None
        )
        await interaction.delete_original_response(delay=10)

        org_message = self.message
        file = await getRankCard(interaction.author)
        embed = await userinfo(interaction.author, file)
        await org_message.edit(embed=embed)


class UserInfo(commands.Cog):
    def __init__(self, bot) -> None:
        self.message = None
        self.bot = bot

    @commands.user_command(name="Профиль")
    async def profile_popup(
        self, interaction: disnake.UserCommandInteraction, member: disnake.Member
    ):
        await interaction.response.defer()

        if not interaction.guild or interaction.author.bot:
            return

        await database(interaction.author)

        file = await getRankCard(member)
        embed = await userinfo(member, file)
        change_user = UserChange(interaction.author)

        if interaction.author.id is member.id:
            await interaction.send(
                embed=embed,
                view=change_user,
                ephemeral=False,
                delete_after=300,
            )
            return

        await interaction.send(
            file=file, embed=embed, ephemeral=True, delete_after=300
        )

    @commands.slash_command(
        name="profile", description="Выводит информацию о пользователе"
    )
    async def profile_no_popup(
        self,
        interaction: disnake.UserCommandInteraction,
        member: disnake.Member = commands.Param(name="пользователь", default=None),
    ):
        await interaction.response.defer()

        if not interaction.guild or interaction.author.bot:
            return

        if not member:
            target = interaction.author
        else:
            target = member

        await database(target)
        file = await getRankCard(target)
        embed = await userinfo(target, file)

        if member is None or interaction.author is member:
            await interaction.send(
                embed=embed,
                view=UserChange(target),
                ephemeral=False,
                delete_after=300,
            )
            return

        await interaction.send(
            file=file, embed=embed, ephemeral=True, delete_after=300
        )


def setup(bot):
    bot.add_cog(UserInfo(bot))
