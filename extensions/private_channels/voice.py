import disnake
from disnake import TextInputStyle, Embed, SelectOption, MessageInteraction, ModalInteraction
from disnake.ui import StringSelect, TextInput
from disnake.ext import commands

from core.checker import *
from core.vars import *
from core.models import *


class VoiceSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Управлять своим приватным каналом")
    async def voice(self, interaction: disnake.UserCommandInteraction):
        author = interaction.author
        if interaction.author.bot or not interaction.guild:
            return

        user_settngs = await database(author)

        if await private_channel_checker(author, user_settngs, interaction) is False:
            return

        embed = Embed(
            title="Управление приватной комнатой",
            description="Взаимодействуйте с приватной комнатой через селектор",
            color=EmbedColor.MAIN_COLOR.value,
        )

        await interaction.response.send_message(
            embed=embed,
            components=StringSelect(
                options=[
                    SelectOption(value="v_change_name", label=f"Изменить название", emoji="📝"),
                    SelectOption(value="v_set_users_limit", label=f"Установить лимит", emoji="🔠"),
                    SelectOption(value="v_open", label=f"Открыть", emoji="🔓"),
                    SelectOption(value="v_close", label=f"Закрыть", emoji="🔒"),
                    SelectOption(value="v_kick", label=f"Выгнать", emoji="👠"),
                ]
            ),
            ephemeral=True,
            delete_after=300
        )


def setup(bot):
    bot.add_cog(VoiceSettings(bot))


class VKickSelect(disnake.ui.StringSelect):
    def __init__(self, members):
        self.members = members
        options = []
        for member in self.members:
            options.append(
                SelectOption(
                    value=f"{member.id}",
                    label=f"{member.name}",
                )
            )

        super().__init__(
            placeholder="Выберите участника(ов)",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        for m_v_kick in [self.values[0]]:
            members = "".join(m_v_kick)

            author = interaction.author
            user_settngs = await database(author)

            try:
                m_v_kick = int(m_v_kick)
            except ValueError:
                embed = await accessDeniedCustom("Укажите ID пользователя")
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            member = interaction.guild.get_member(m_v_kick)

            if author == member:
                embed = await accessDeniedCustom("Вы не можете выгнать себя")
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            if await private_channel_checker(author, user_settngs, interaction) is False:
                return

            if member not in author.voice.channel.members:
                embed = await accessDeniedCustom("Пользователь не в канале")
                await interaction.send(embed=embed, ephemeral=True, delete_after=15)
                return

            await author.voice.channel.set_permissions(member, connect=False)
            await member.move_to(None)

        embed = Embed(
            title="Управление приватной комнатой",
            description=f"<@!{members}> изгоняет пользователя из <#{author.voice.channel.id}>",
            color=EmbedColor.PCHANNEL_SETTINGS.value,
        )
        embed.add_field(
            name=f"{EmbedEmoji.ACCESS_ALLOWED.value} Пользователь успешно выгнан",
            value=f"**<@!{members}>** изгнан",
            inline=False,
        )
        await interaction.send(embed=embed, ephemeral=True, delete_after=15)
        return
