from disnake.ext import commands
from disnake.ui import StringSelect
from disnake import GuildCommandInteraction, Embed, SelectOption
from mafic import Node

from overwritten import LapisBot, LapisPlayer
from utils import search_tracks_urls

from core import *


class MusicCog(commands.Cog):
    def __init__(self, bot: LapisBot):
        self.bot = bot
        self.play_data = dict()

    @commands.slash_command(description="Управление музыкой")
    async def play(self, interaction: GuildCommandInteraction) -> None:
        if not interaction.author.voice:
            return await interaction.send(
                embed=await accessDeniedCustom("Вы не в голосовом канале"),
                ephemeral=True,
            )

        if (
            interaction.guild.voice_client
            and interaction.guild.voice_client.channel
            != interaction.author.voice.channel
        ):
            return await interaction.send(
                embed=await accessDeniedCustom(
                    f"Бот уже используется в канале: <#{interaction.guild.voice_client.channel.id}>"
                ),
                ephemeral=True,
            )

        if not interaction.guild.voice_client:
            await interaction.author.voice.channel.connect(cls=LapisPlayer)

        message = await interaction.channel.send(
            embed=Embed(
                title="Плеер",
                description="Ничего не играет",
                color=EmbedColor.MAIN_COLOR.value,
            ),
            components=StringSelect(
                options=[
                    SelectOption(
                        label="Добавить трек", value="add_track:id", emoji="➕"
                    ),
                    SelectOption(label="Пауза | Плей", value="set_pause:id", emoji="⏯️"),
                    SelectOption(label="Следующее", value="skip:id", emoji="⏩"),
                    SelectOption(label="Плейлист", value="get_queue:id", emoji="📄"),
                    SelectOption(label="Выйти", value="quit:id", emoji="❌"),
                ],
                custom_id="player_select:id",
                placeholder="Выбрать действие",
            ),
        )
        interaction.guild.voice_client.message = message


def setup(bot: LapisBot) -> None:
    bot.add_cog(MusicCog(bot))
