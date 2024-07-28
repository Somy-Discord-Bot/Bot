import disnake
from disnake import MessageInteraction, ModalInteraction
from disnake.ext import commands
from disnake.ui import TextInput, StringSelect

from sqlalchemy import select, delete
from sqlalchemy import and_
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *
from extensions.private_channels.voice import VKickSelect, VoiceSettings
from extensions.info.user import userinfo
from extensions.utils.embed_creator import FieldEditor, EmbedCreator


class ViewListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_dropdown")
    async def on_dropdown_selectors(self, interaction: MessageInteraction) -> None:
        value = interaction.values[0]
        author = interaction.author
        authorDB = await database(author)

        if value == 'v_change_name':
            if await private_channel_checker(author, authorDB, interaction) is False:
                return

            await interaction.response.send_modal(
                title="Приватный канал",
                custom_id="v_change_name_modal",
                components=[
                    TextInput(
                        label="Название",
                        placeholder="",
                        custom_id="m_v_name",
                        max_length=32,
                        style=TextInputStyle.short,
                        required=True,
                    )
                ]
            )
            return

        elif value == 'v_set_users_limit':
            await interaction.response.send_modal(
                title="Приватный канал",
                custom_id="v_change_limit_modal",
                components=[
                    TextInput(
                        label="Лимит",
                        placeholder="",
                        custom_id="m_v_limit",
                        max_length=2,
                        style=TextInputStyle.short,
                        required=True,
                    )
                ]
            )
            return
            
        elif value == 'v_open':
            if await private_channel_checker(author, authorDB, interaction) is False:
                return

            everyone = interaction.guild.default_role
            connect = author.voice.channel.permissions_for(everyone).connect

            if connect is True:
                embed = disnake.Embed(
                    title="Комната уже открыта",
                    color=EmbedColor.PCHANNEL_SETTINGS.value,
                )
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            async with AsyncSession(engine) as session:
                await session.execute(
                    update(Users)
                    .where(
                        and_(
                            Users.user_id == author.id,
                            Users.guild_id == author.guild.id,
                        )
                    )
                    .values(p_channel_lock=True)
                )
                await session.commit()

            await author.voice.channel.set_permissions(everyone, connect=True)

            embed = Embed(
                title="Управление приватной комнатой",
                description=f"{EmbedEmoji.ACCESS_ALLOWED.value}<@!{author.id}> открывает комнату <#{author.voice.channel.id}>",
                color=EmbedColor.PCHANNEL_SETTINGS.value,
            )
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        elif value == 'v_close':
            if await private_channel_checker(author, authorDB, interaction) is False:
                return

            everyone = interaction.guild.default_role
            connect = author.voicechannel.permissions_for(everyone).connect

            if connect is False:
                embed = disnake.Embed(
                    title="Комната уже открыта",
                    color=EmbedColor.PCHANNEL_SETTINGS.value,
                )
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            async with AsyncSession(engine) as session:
                await session.execute(
                    update(Users)
                    .where(
                        and_(
                            Users.user_id == author.id,
                            Users.guild_id == author.guild.id,
                        )
                    )
                    .values(p_channel_lock=False)
                )
                await session.commit()

            await author.voice.channel.set_permissions(everyone, connect=False)

            embed = Embed(
                title="Управление приватной комнатой",
                description=f"{EmbedEmoji.ACCESS_ALLOWED.value}<@!{author.id}> закрывает комнату <#{author.voice.channel.id}>",
                color=EmbedColor.PCHANNEL_SETTINGS.value,
            )
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        elif value == 'v_kick':
            if await private_channel_checker(author, authorDB, interaction) is False:
                return

            channel_members = author.voice.channel.members
            select_view = disnake.ui.View()
            select_view.add_item(VKickSelect(channel_members))

            await interaction.response.send_message(
                view=select_view, ephemeral=True, delete_after=60
            )
            return 

    @commands.Cog.listener("on_modal_submit")
    async def modal_submit(self, interaction: ModalInteraction) -> None:
        author = interaction.author
        authorDB = await database(interaction.author)
        # mentionDB = await database(member)

        if interaction.custom_id == "v_change_name_modal":
            if await private_channel_checker(author, authorDB, interaction) is False:
                return

            m_v_name = interaction.text_values["m_v_name"]

            async with AsyncSession(engine) as session:
                await session.execute(
                    update(Users)
                    .where(
                        and_(
                            Users.user_id == author.id,
                            Users.guild_id == author.guild.id,
                        )
                    )
                    .values(p_channel_name=m_v_name)
                )
                await session.commit()

            await author.voice.channel.edit(name=m_v_name)

            embed = Embed(
                title="Управление приватной комнатой",
                description=f"<@!{author.id}> меняет настройки комнаты <#{author.voice.channel.id}> ",
                color=EmbedColor.PCHANNEL_SETTINGS.value,
            )
            embed.add_field(
                name=f"{EmbedEmoji.ACCESS_ALLOWED.value} Название успешно изменено",
                value=f"Название:\n```{m_v_name}```",
                inline=False,
            )
            embed.timestamp = datetime.datetime.utcnow()
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        elif interaction.custom_id == "v_change_limit_modal":
            if await private_channel_checker(author, authorDB, interaction) is False:
                return

            try:
                m_v_limit = int(interaction.text_values["m_v_limit"])
            except (TypeError, ValueError):
                embed = await accessDeniedCustom("Неверный тип данных")
                embed.add_field(
                    name="Ожидаемый тип данных", value="`int` *Число*", inline=True
                )
                embed.add_field(
                    name="Полученный тип данных",
                    value=f"`{type(interaction.text_values['m_transfer_silver_coin'])}`",
                    inline=True,
                )
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            if 0 > m_v_limit > 99:
                embed = await accessDeniedCustom("Укажите число от `0` до `99`")
                await interaction.send(embed=embed, ephemeral=True)
                return

            await author.voice.channel.edit(name=m_v_limit)

            async with AsyncSession(engine) as session:
                await session.execute(
                    update(Users)
                    .where(
                        and_(
                            Users.user_id == author.id,
                            Users.guild_id == author.guild.id,
                        )
                    )
                    .values(p_channel_users_limit=m_v_limit)
                )
                await session.commit()

            embed = Embed(
                title="Управление приватной комнатой",
                description=f"<@!{author.id}> меняет настройки комнаты <#{author.voice.channel.id}>",
                color=EmbedColor.PCHANNEL_SETTINGS.value,
            )
            embed.add_field(
                name=f"{EmbedEmoji.ACCESS_ALLOWED.value}Лимит успешно изменен",
                value=f"Лимит комнаты изменен на `{m_v_limit}`",
                inline=False,
            )
            await interaction.send(embed=embed, ephemeral=True, delete_after=15)
            return

        elif interaction.custom_id == "m_transfer_silver_coin":
            try:
                amount = int(interaction.text_values["m_transfer_silver_coin"])
            except (TypeError, ValueError):
                embed = await accessDeniedCustom("Неверный тип данных")
                embed.add_field(
                    name="Ожидаемый тип данных", value="`int` *Число*", inline=True
                )
                embed.add_field(
                    name="Полученный тип данных",
                    value=f"`{type(interaction.text_values['m_transfer_silver_coin'])}`",
                    inline=True,
                )
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            if amount > authorDB.currency:
                embed = await accessDeniedNoMoney(amount, authorDB)
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)

            if amount <= 0:
                embed = await accessDeniedCustom("Значение не должно быть меньше чем `0`")
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            async with AsyncSession(engine) as session:
                await session.execute(
                    update(Users)
                    .where(
                        and_(
                            Users.user_id == interaction.author.id,
                            Users.guild_id == interaction.guild.id,
                        )
                    )
                    .values(currency=Users.currency - amount)
                )
                await session.execute(
                    update(Users)
                    .where(
                        and_(
                            Users.user_id == member.id,
                            Users.guild_id == interaction.guild.id,
                        )
                    )
                    .values(currency=Users.currency + amount)
                )
                await session.commit()

            DM = member.create_dm()

            embedDM = disnake.Embed(
                title="Перевод монет",
                description=f"<@!{author.id}> перевел(а) вам **{amount:,}** {EmbedEmoji.SILVER_COIN.value}",
                color=EmbedColor.MAIN_COLOR.value,
            )
            embedDM.add_field(
                name="Баланс",
                value=f"**{authorDB.currency + amount:,}** {EmbedEmoji.SILVER_COIN.value}",
                inline=True,
            )

            try:
                await DM.send(embed=embedDM, mention_author=False)
            except TypeError:
                pass

            embed = disnake.Embed(
                title="Перевод монет",
                description=f"Вы перевели <@{member.id}> **{amount:,}** {EmbedEmoji.SILVER_COIN.value}",
                color=EmbedColor.MAIN_COLOR.value,
            )
            embed.add_field(
                name="Перевод монет",
                value=f"Баланс: **{mentionDB.currency - amount:,}** {EmbedEmoji.SILVER_COIN.value}",
                inline=True,
            )

            await interaction.send(
                embed=embed,
                ephemeral=True,
            )
            return

        elif interaction.custom_id == "u_profile_changed_desc":
            m_about = str(interaction.text_values["m_about"])
            if await banWords(m_about) is True:
                await interaction.response.send_message(
                    f"{EmbedEmoji.ACCESS_DENIED.value} В профиле запрещено использовать мат",
                    ephemeral=True,
                )
                return

            async with AsyncSession(engine) as session:
                await session.execute(
                    update(User_global)
                    .where(User_global.user_id == interaction.author.id)
                    .values(description=m_about)
                )
                await session.commit()

            file = await getRankCard(interaction.author)
            embed = await userinfo(interaction.author, file)
            await interaction.response.edit_message(embed=embed)
            return

        elif interaction.custom_id == "u_profile_changed_vk_url":
            m_vk_url = str(interaction.text_values["m_vk_url"])

            async with AsyncSession(engine) as session:
                await session.execute(
                    update(User_global)
                    .where(User_global.user_id == interaction.author.id)
                    .values(vk_url=f"https://vk.com/{m_vk_url}")
                )
                await session.commit()

            file = await getRankCard(interaction.author)
            embed = await userinfo(interaction.author, file)
            await interaction.response.edit_message(embed=embed)
            return

        elif interaction.custom_id == "u_profile_changed_inst_url":
            m_inst_url = str(interaction.text_values["m_inst_url"])

            async with AsyncSession(engine) as session:
                await session.execute(
                    update(User_global)
                    .where(User_global.user_id == interaction.author.id)
                    .values(inst_url=f"https://www.instagram.com/{m_inst_url}")
                )
                await session.commit()

            file = await getRankCard(interaction.author)
            embed = await userinfo(interaction.author, file)
            await interaction.response.edit_message(embed=embed)
            return

        elif interaction.custom_id == "u_profile_changed_tg_url":
            m_tg_url = str(interaction.text_values["m_tg_url"])

            async with AsyncSession(engine) as session:
                await session.execute(
                    update(User_global)
                    .where(User_global.user_id == interaction.author.id)
                    .values(tg_url=f"https://t.me/{m_tg_url}")
                )
                await session.commit()

            file = await getRankCard(interaction.author)
            embed = await userinfo(interaction.author, file)
            await interaction.response.edit_message(embed=embed)
            return

        elif interaction.custom_id == "ec_add_field":
            m_name = interaction.text_values["m_name"]
            m_value = interaction.text_values["m_value"]
            m_inline = interaction.text_values["m_inline"]

            if m_inline.lower() == "да":
                m_inline = True
            else:
                m_inline = False

            dict_embed = interaction.message.embeds[0].to_dict()
            embed = Embed().from_dict(dict_embed)

            embed.add_field(
                name=m_name,
                value=m_value,
                inline=m_inline,
            )

            await save_embed_dict(embed, interaction.author)

            await interaction.response.edit_message(
                embed=embed, view=FieldEditor(embed, interaction.author)
            )
            return

        elif interaction.custom_id == "ec_add_text":
            content = interaction.text_values["m_text"]

            async with AsyncSession(engine) as session:
                await session.execute(
                    update(User_global)
                    .where(User_global.user_id == interaction.author.id)
                    .values(embed_text=content)
                )
                await session.commit()

            await interaction.response.edit_message(content)
            return

        elif interaction.custom_id == "ec_add_title":
            dict_embed = interaction.message.embeds[0].to_dict()

            dict_embed[f"title"] = interaction.text_values["m_title"]
            dict_embed[f"description"] = interaction.text_values["m_desc"]

            if interaction.text_values["m_color"] == '' or int(interaction.text_values["m_color"], 16) >= 16777215:
                pass
            else:
                dict_embed[f"color"] = int(interaction.text_values["m_color"], 16)

            embed = Embed().from_dict(dict_embed)

            await save_embed_dict(embed, interaction.author)

            await interaction.response.edit_message(
                embed=embed, view=EmbedCreator(interaction.author)
            )
            return

        elif interaction.custom_id == "ec_add_thumbnail_link":
            m_thumbnail = interaction.text_values["m_thumbnail"]

            dict_embed = interaction.message.embeds[0].to_dict()
            embed = Embed().from_dict(dict_embed)

            if check_url(m_thumbnail) is False:
                embed = await accessDeniedCustom("Неверная ссылка")
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            embed.set_thumbnail(url=m_thumbnail)

            await save_embed_dict(embed, interaction.author)

            await interaction.response.edit_message(
                embed=embed, view=EmbedCreator(interaction.author)
            )
            return

        elif interaction.custom_id == "ec_add_image_link":
            m_image = interaction.text_values["m_image"]

            dict_embed = interaction.message.embeds[0].to_dict()
            embed = Embed().from_dict(dict_embed)

            if check_url(m_image) is False:
                embed = await accessDeniedCustom("Неверная ссылка")
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            embed.set_image(url=m_image)

            await save_embed_dict(embed, interaction.author)

            await interaction.response.edit_message(
                embed=embed, view=EmbedCreator(interaction.author)
            )
            return

        elif interaction.custom_id == "ec_add_footer":
            m_footer = interaction.text_values["m_footer"]
            m_footer_icon = interaction.text_values["m_footer_icon"]

            dict_embed = interaction.message.embeds[0].to_dict()
            embed = Embed().from_dict(dict_embed)

            embed.set_footer(
                text=interaction.text_values["m_footer"],
            )

            if check_url(m_footer_icon) is False:
                embed = await accessDeniedCustom("Неверная ссылка")
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            embed.set_footer(
                text=m_footer,
                icon_url=m_footer_icon,
            )

            await save_embed_dict(embed, interaction.author)

            await interaction.response.edit_message(
                embed=embed, view=EmbedCreator(interaction.author)
            )
            return

        elif interaction.custom_id == "ec_add_author":
            m_author_name = interaction.text_values["m_author_name"]
            m_author_url = interaction.text_values["m_author_url"]
            m_author_icon_url = interaction.text_values["m_author_icon_url"]

            dict_embed = interaction.message.embeds[0].to_dict()
            embed = Embed().from_dict(dict_embed)

            embed.set_author(
                name=m_author_name,
            )

            if await check_url(m_author_url) is False:
                embed = await accessDeniedCustom("Неверная ссылка")
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            embed.set_author(
                name=m_author_name,
                url=m_author_url,
            )

            if await check_url(m_author_icon_url) is False:
                embed = await accessDeniedCustom("Неверная ссылка")
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            embed.set_author(
                name=m_author_name,
                icon_url=m_author_icon_url,
            )

            await save_embed_dict(embed, interaction.author)

            await interaction.response.edit_message(
                embed=embed, view=EmbedCreator(interaction.author)
            )
            return

        elif interaction.custom_id == "ec_send":
            await interaction.response.defer()
            dict_embed = interaction.message.embeds[0].to_dict()

            try:
                channel = interaction.guild.get_channel(
                    int(interaction.text_values["m_channel_id"])
                )
            except AttributeError:
                await accessDeniedCustom("Вы указали несуществующий канал")
                return

            if channel.guild.id != interaction.author.id:
                embed = await accessDeniedCustom(
                    "Вы не можете отправить эмбед в эту гильдию"
                )
                await interaction.send(embed=embed, ephemeral=True)
                return

            async with AsyncSession(engine) as session:
                text = await session.scalar(
                    select(Users).where(Users.user_id == interaction.author.id)
                )

            embed = disnake.Embed().from_dict(dict_embed)

            await interaction.delete_original_response()

            await channel.send(content=text, embed=embed)
            return


def setup(bot):
    bot.add_cog(ViewListeners(bot))
