from disnake.ext import commands
from disnake.ui import StringSelect, TextInput
from disnake import (
    GuildCommandInteraction,
    Embed,
    SelectOption,
    MessageInteraction,
    ModalInteraction,
)
from mafic import Node, Playlist, Track

from overwritten import LapisBot, LapisPlayer
from utils import search_tracks_urls, search_playlists_urls

from core import *


class PlayerLogicCog(commands.Cog):
    def __init__(self, bot: LapisBot):
        self.bot = bot

    @staticmethod
    async def is_player_exists(
        interaction: MessageInteraction | ModalInteraction,
    ) -> bool:
        if interaction.guild.voice_client:
            return True
        embed = Embed(
            title="Ошибка",
            description="Не удалось найти плеер!",
            color=EmbedColor.ACCESS_DENIED.value,
        )
        await interaction.send(embed=embed, ephemeral=True)
        return False

    @commands.Cog.listener("on_dropdown")
    async def player_dropdown_logic(self, interaction: MessageInteraction) -> None:
        if interaction.component.custom_id != "player_select:id":
            return

        if not await self.is_player_exists(interaction):
            return

        value = interaction.values[0]

        if value == "quit:id":
            await interaction.guild.voice_client.disconnect(force=True)
            await interaction.message.delete()
        elif value == "add_track:id":
            await interaction.response.send_modal(
                title="Добавление трека",
                custom_id="add_track_modal:id",
                components=[
                    TextInput(
                        label="Содержание",
                        placeholder="URL / название трека",
                        custom_id="track",
                    )
                ],
            )
        elif value == "set_pause:id":
            is_paused = interaction.guild.voice_client.paused
            await interaction.guild.voice_client.pause(not is_paused)
            embed = Embed(
                title="Музыка",
                description=(
                    "Плеер снят с паузы" if is_paused else "Плеер поставлен на паузу"
                ),
                color=EmbedColor.MAIN_COLOR.value,
            )
            await interaction.send(embed=embed, ephemeral=True)
        elif value == "get_queue:id":

            queue: list[Track] = interaction.guild.voice_client.queue

            await interaction.send(
                embed=Embed(
                    title="Очередь",
                    description=(
                        "Очередь пуста"
                        if not queue
                        else "\n".join(
                            [
                                f"{count}. [{track.title}]({track.uri})"
                                for count, track in enumerate(queue, 1)
                            ]
                        )
                    ),
                ),
                ephemeral=True,
            )
        elif value == "skip:id":
            player = interaction.guild.voice_client
            track = await player.skip()

            if not track:
                await interaction.send(
                    embed=Embed(
                        title="Очередь пуста", color=EmbedColor.MAIN_COLOR.value
                    ),
                    delete_after=15,
                )

            embed = Embed(title=f"{track.title}", color=EmbedColor.MAIN_COLOR.value)
            embed.add_field(name="Трек", value=f"[Ссылка]({track.uri})", inline=True)
            embed.add_field(
                name="Платформа",
                value=f"{sources[track.source]}",
                inline=True,
            )

            await interaction.send(embed=embed, delete_after=15)

    @commands.Cog.listener("on_dropdown")
    async def add_track_select_logic(self, interaction: MessageInteraction) -> None:
        if interaction.component.custom_id != "select_track:id":
            return

        if not await self.is_player_exists(interaction):
            return

        await interaction.message.delete()

        track = await self.bot.pool.get_random_node().fetch_tracks(
            interaction.values[0], search_type="ytsearch"
        )
        if not track:
            await interaction.send(
                "По вашему запросу ничего не найдено.", ephemeral=True
            )
            return

        track = track[0]

        embed = Embed(title=f"{track.title}", color=EmbedColor.MAIN_COLOR.value)
        embed.add_field(name="Трек", value=f"[Ссылка]({track.uri})", inline=True)
        embed.add_field(
            name="Платформа",
            value=f"{sources[track.source]}",
            inline=True,
        )

        await interaction.guild.voice_client.add_queue_or_play(track)
        await interaction.send(embed=embed, delete_after=15)

    @commands.Cog.listener("on_modal_submit")
    async def add_track_logic(self, interaction: ModalInteraction) -> None:
        if interaction.custom_id != "add_track_modal:id":
            return

        if not await self.is_player_exists(interaction):
            return

        user_track_input = interaction.text_values["track"]
        track_url = search_tracks_urls(user_track_input)
        playlist_url = search_playlists_urls(user_track_input)

        node: Node = self.bot.pool.get_random_node()

        if track_url:
            platform, url = track_url

            track = await node.fetch_tracks(url, search_type=platform)

            if track:
                track = track[0]

                embed = Embed(title=f"{track.title}", color=EmbedColor.MAIN_COLOR.value)
                embed.add_field(
                    name="Трек", value=f"[Ссылка]({track.uri})", inline=True
                )
                embed.add_field(
                    name="Платформа",
                    value=f"{sources[track.source]}",
                    inline=True,
                )

                await interaction.guild.voice_client.add_queue_or_play(track)
                await interaction.send(embed=embed, delete_after=15)

        elif playlist_url:
            platform, url = playlist_url

            playlist = await node.fetch_tracks(url, search_type=platform)

            embed = Embed(
                title=f"Плейлист: {playlist.name} | {len(playlist.tracks)} треков",
                color=EmbedColor.MAIN_COLOR.value,
            )

            if isinstance(playlist, Playlist):
                for track in playlist.tracks:
                    await interaction.guild.voice_client.add_queue_or_play(track)

            await interaction.send(embed=embed)
        else:
            tracks = await node.fetch_tracks(user_track_input, search_type="ytsearch")

            await interaction.response.send_message(
                embed=Embed(
                    title="Плеер",
                    description="Выберите трек",
                    color=EmbedColor.MAIN_COLOR.value,
                ),
                components=StringSelect(
                    options=[
                        SelectOption(label=track.title, value=track.uri)
                        for track in tracks
                    ][:25],
                    custom_id="select_track:id",
                ),
            )


def setup(bot: LapisBot) -> None:
    bot.add_cog(PlayerLogicCog(bot))
