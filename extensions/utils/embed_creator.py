import json

import disnake
from disnake import TextInputStyle
from disnake import Embed
from disnake.ext import commands
from disnake.ext.commands import Cog
from disnake.ui import TextInput, View, StringSelect, Modal, button

from sqlalchemy import select, delete, insert, update
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *


class EditEmbedSelect(StringSelect):
    def __init__(self, embed: disnake.Embed, message: disnake.Message):
        self.embed = embed
        self.message = message

        num = 0
        options = []
        self.dict_embed = embed.to_dict()

        for field in self.dict_embed["fields"]:
            options.append(
                disnake.SelectOption(
                    value=f"{num}",
                    label=field["name"],
                )
            )
            num += 1

        super().__init__(
            placeholder="Выберите область для изменения",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(
            modal=EditFieldModal(self.embed, int(self.values[0]), self.message),
        )

        return


class EditFieldModal(Modal):
    def __init__(self, embed: disnake.Embed, num: int, message: disnake.Message):
        self.dict_embed = embed.to_dict()
        self.num = num
        self.message = message

        components = [
            TextInput(
                label="Название",
                placeholder="",
                custom_id="m_name",
                style=TextInputStyle.paragraph,
                max_length=512,
                required=True,
            ),
            TextInput(
                label="Значение",
                placeholder="",
                custom_id="m_value",
                style=TextInputStyle.paragraph,
                max_length=512,
                required=True,
            ),
            TextInput(
                label="В линию",
                placeholder="Да / нет",
                custom_id="m_inline",
                style=TextInputStyle.short,
                required=True,
            ),
        ]
        super().__init__(title="Изменение эмбеда", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        m_inline = interaction.text_values["m_inline"]
        m_name = interaction.text_values["m_name"]
        m_value = interaction.text_values["m_value"]

        if m_inline.lower() == "да":
            m_inline = True
        else:
            m_inline = False

        self.dict_embed["fields"][self.num] = {
            f"name": m_name,
            f"value": m_value,
            f"inline": m_inline,
        }

        embed = Embed().from_dict(self.dict_embed)

        await save_embed_dict(embed, interaction.author)

        await self.message.edit(
            embed=embed, view=FieldEditor(embed, interaction.author)
        )

        select_view = View().add_item(
            EditEmbedSelect(embed, interaction.message)
        )

        await interaction.response.edit_message(view=select_view)
        return


class DeleteEmbedSelect(StringSelect):
    def __init__(self, embed: disnake.Embed, message: disnake):
        self.embed = embed
        self.message = message

        num = 0
        options = []
        self.dict_embed = embed.to_dict()

        for field in self.dict_embed["fields"]:
            options.append(
                disnake.SelectOption(
                    value=f"{num}",
                    label=field["name"],
                )
            )
            num += 1

        super().__init__(
            placeholder="Выберите область для удаления",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        del self.dict_embed["fields"][int(self.values[0])]

        embed = Embed().from_dict(self.dict_embed)

        select_view = View().add_item(DeleteEmbedSelect(embed, self.message))

        await save_embed_dict(embed, interaction.author)

        await self.message.edit(
            embed=embed, view=FieldEditor(embed, interaction.author)
        )

        if not embed.to_dict().get("fields"):
            await interaction.delete_original_response()
            return

        await interaction.response.edit_message(view=select_view)
        return


class FieldEditor(View):
    def __init__(self, embed: disnake.Embed, buttonAuthor: disnake.Member):
        super().__init__(timeout=20)
        self.embed = embed
        self.buttonAuthor = buttonAuthor

        dict_embed = embed.to_dict()
        if not dict_embed.get("fields"):
            self.delete_field.disabled = True
            self.edit_field.disabled = True

    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        if interaction.author.id != self.buttonAuthor.id:
            embed = await accessDeniedButton(self.buttonAuthor)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    @button(
        label="Добавить", style=disnake.ButtonStyle.green, emoji="➕", row=1
    )
    async def add_field(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        dict_embed = interaction.message.embeds[0].to_dict()

        try:
            if len(dict_embed["fields"]) == 25:
                embed = await accessDeniedCustom(
                    "Вы достигли максимального кол-ва доступных областей"
                )
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return
        except KeyError:
            pass

        await interaction.response.send_modal(
            title="Управление эмбедом",
            custom_id="ec_add_field",
            components=[
                TextInput(
                    label="Название",
                    placeholder="",
                    custom_id="m_name",
                    style=TextInputStyle.paragraph,
                    max_length=512,
                    required=True,
                ),
                TextInput(
                    label="Значение",
                    placeholder="",
                    custom_id="m_value",
                    style=TextInputStyle.paragraph,
                    max_length=512,
                    required=True,
                ),
                TextInput(
                    label="В линию",
                    placeholder="Да / нет",
                    custom_id="m_inline",
                    style=TextInputStyle.short,
                    required=True,
                ),
            ]
        )

    @button(
        label="Удалить", style=disnake.ButtonStyle.red, emoji="➖", row=1
    )
    async def delete_field(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        dict_embed = interaction.message.embeds[0].to_dict()
        embed = Embed().from_dict(dict_embed)

        select_view = View().add_item(
            DeleteEmbedSelect(embed, interaction.message)
        )

        await interaction.response.send_message(view=select_view, ephemeral=True)

    @button(
        label="Изменить", style=disnake.ButtonStyle.secondary, emoji="✅", row=2
    )
    async def edit_field(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        dict_embed = interaction.message.embeds[0].to_dict()
        embed = Embed().from_dict(dict_embed)

        select_view = View().add_item(
            EditEmbedSelect(embed, interaction.message)
        )

        await interaction.response.send_message(view=select_view, ephemeral=True)

    @button(
        label="Назад", style=disnake.ButtonStyle.blurple, emoji="⬅️", row=2
    )
    async def back(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.edit_message(view=EmbedCreator(interaction.author))


class EmbedCreator(View):
    def __init__(self, buttonAuthor: disnake.Member):
        super().__init__(timeout=20)
        self.buttonAuthor = buttonAuthor

    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        if interaction.author.id != self.buttonAuthor.id:
            embed = await accessDeniedButton(self.buttonAuthor)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    @button(
        label="Текст", style=disnake.ButtonStyle.secondary, emoji="💬", row=1
    )
    async def text(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление эмбедом",
            custom_id="ec_add_text",
            components=[
                TextInput(
                    label="Текст",
                    placeholder="",
                    custom_id="m_text",
                    style=TextInputStyle.paragraph,
                    max_length=2000,
                    required=False,
                )
            ]
        )

    @button(
        label="Автор", style=disnake.ButtonStyle.secondary, emoji="👤", row=1
    )
    async def change_author(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление эмбедом",
            custom_id="ec_add_author",
            components=[
                TextInput(
                    label="Название",
                    placeholder="",
                    custom_id="m_title",
                    style=TextInputStyle.short,
                    max_length=50,
                    required=True,
                ),
                TextInput(
                    label="Описание",
                    placeholder="",
                    custom_id="m_desc",
                    style=TextInputStyle.paragraph,
                    max_length=256,
                    required=True,
                ),
                TextInput(
                    label="Цвет",
                    placeholder="Без #",
                    custom_id="m_color",
                    style=TextInputStyle.short,
                    max_length=6,
                    min_length=3,
                    required=True,
                ),
            ]
        )

    @button(
        label="Название, описание и цвет",
        style=disnake.ButtonStyle.secondary,
        emoji="📝",
        row=1,
    )
    async def change_main(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление эмбедом",
            custom_id="ec_add_title",
            components=[
                TextInput(
                    label="Автор",
                    placeholder="",
                    custom_id="m_title",
                    style=TextInputStyle.paragraph,
                    max_length=64,
                    required=False,
                ),
                TextInput(
                    label="Ссылка на автора",
                    placeholder="URL",
                    custom_id="m_desc",
                    style=TextInputStyle.short,
                    max_length=2048,
                    required=False,
                ),
                TextInput(
                    label="Ссылка на иконку",
                    placeholder="URL",
                    custom_id="m_color",
                    style=TextInputStyle.short,
                    max_length=2048,
                    required=False,
                )
            ]
        )

    @button(
        label="Миниатюра", style=disnake.ButtonStyle.secondary, emoji="🌆", row=1
    )
    async def change_thumbnail(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление эмбедом",
            custom_id="ec_add_thumbnail_link",
            components=[
                TextInput(
                    label="Ссылка на миниатюру",
                    placeholder="URL",
                    custom_id="m_thumbnail",
                    style=TextInputStyle.short,
                    required=False,
                )
            ]
        )

    @button(
        label="Картинка", style=disnake.ButtonStyle.secondary, emoji="🏞️", row=2
    )
    async def change_image(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление эмбедом",
            custom_id="ec_add_image_link",
            components=[
                TextInput(
                    label="Ссылка на картинку",
                    placeholder="URL",
                    custom_id="m_image",
                    style=TextInputStyle.short,
                    required=False,
                )
            ]
        )

    @button(
        label="Футер", style=disnake.ButtonStyle.secondary, emoji="🧷", row=2
    )
    async def change_footer(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление эмбедом",
            custom_id="ec_add_footer",
            components=[
                TextInput(
                    label="Футер",
                    placeholder="",
                    custom_id="m_footer",
                    style=TextInputStyle.paragraph,
                    max_length=64,
                    required=False,
                ),
                TextInput(
                    label="Ссылка на иконку",
                    placeholder="URL",
                    custom_id="m_footer_icon",
                    style=TextInputStyle.short,
                    required=False,
                ),
            ]
        )

    @button(
        label="Области", style=disnake.ButtonStyle.gray, emoji="📂", row=3
    )
    async def manage_fields(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        dict_embed = interaction.message.embeds[0].to_dict()
        embed = Embed().from_dict(dict_embed)

        await interaction.response.edit_message(
            view=FieldEditor(embed, interaction.author)
        )

    @button(
        label="Отправить", style=disnake.ButtonStyle.success, emoji="✉️", row=4
    )
    async def send(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Управление эмбедом",
            custom_id="ec_send",
            components=[
                TextInput(
                    label="ID канала(ов)",
                    placeholder="",
                    custom_id="m_channel_id",
                    style=TextInputStyle.short,
                    required=True,
                )
            ]
        )

    @button(
        label="Очистить", style=disnake.ButtonStyle.red, emoji="❌", row=4
    )
    async def delete_embed(
        self, Button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        async with AsyncSession(engine) as session:
            await session.execute(
                delete(User_global).where(User_global.user_id == interaction.author.id)
            )
            await session.commit()

        db = await database(interaction.author)

        async with AsyncSession(engine) as session:
            text = await session.scalar(
                select(User_global.embed_text).where(
                    User_global.user_id == interaction.author.id
                )
            )

        if text is None or "<Record text=None>":
            text = None

        embed = Embed().from_dict(json.loads(db[2].embed_json))

        await interaction.response.edit_message(
            text,
            embed=embed,
        )


class EmbedCreatorMain(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.save_embed = {}

    @commands.slash_command(
        name="create-embed",
        description="Конструктор эмбедов, которые ты можешь сохранить или " "отправить",
    )
    async def create_embed(self, interaction: disnake.UserCommandInteraction):
        if interaction.author.bot or not interaction.guild:
            return

        db = await database(interaction.author)

        async with AsyncSession(engine) as session:
            text = await session.scalar(
                select(User_global).where(User_global.user_id == interaction.author.id)
            )

        embed = Embed().from_dict(json.loads(db[2].embed_json))

        async with AsyncSession(engine) as session:
            await session.execute(
                update(User_global)
                .where(User_global.user_id == interaction.author.id)
                .values(embed_json=str(json.dumps(embed.to_dict())))
            )
            await session.commit()

        self.save_embed = embed.to_dict()
        await interaction.send(
            content=text.embed_text,
            embed=embed,
            view=EmbedCreator(interaction.author),
        )


def setup(bot):
    bot.add_cog(EmbedCreatorMain(bot))
