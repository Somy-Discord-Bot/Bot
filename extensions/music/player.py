import asyncio
import time
from typing import Optional

from disnake import Message, Embed
from disnake.abc import Connectable
from mafic import Player, Track

from .bot import LapisBot
from core import *


class LapisPlayer(Player):
    def __init__(self, client: LapisBot, channel: Connectable) -> None:
        super().__init__(client, channel)
        self.queue: list[Track] = []
        self.message: Optional[Message] = None

        asyncio.create_task(self.update_message_state())

    async def add_queue_or_play(self, track: Track):
        if self.current:
            self.queue.append(track)
        else:
            await self.play(track)

    async def skip(self) -> Optional[Track]:
        if self.queue:
            track = self.queue.pop(0)
            await self.play(track)
            return track

        return None

    @staticmethod
    def generate_timebar(
        length_ms: float,
        current_position_ms: float,
        bar_length=10,
    ) -> str:
        START_FILL = "<:START_FILL:1199128161313640499>"
        START_NO_FILL = "<:START_NO_FILL:1199128474082881626>"
        NO_FILL = "<:NO_FILL:1199128158541205675>"
        END_NO_FILL = "<:END_NO_FILL:1199128155366117447>"
        END_FILL = "<:END_FILL:1199128152878886942>"
        FILL = "<:FILL:1199128156813135973>"

        CELLS_COUNT = bar_length
        FULL_SOUND_LENGTH = length_ms
        SOUND_NOW_POSITION = current_position_ms

        cells_now_position = int(
            (CELLS_COUNT * SOUND_NOW_POSITION) // FULL_SOUND_LENGTH
        )

        cells = []
        cells.extend([FILL] * cells_now_position)
        cells.extend([NO_FILL] * (CELLS_COUNT - cells_now_position))

        if cells[0] == FILL:
            cells[0] = START_FILL
        else:
            cells[0] = START_NO_FILL

        if cells[-1] == FILL:
            cells[-1] = END_FILL
        else:
            cells[-1] = END_NO_FILL

        return "".join(cells)

    @staticmethod
    def milliseconds_to_time(milliseconds: float):
        seconds = int(milliseconds // 1000)

        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    async def update_message_state(self):
        while True:
            if self.message:
                if not self.current:
                    await self.message.edit(
                        embed=Embed(
                            title="Плеер",
                            description="Ничего не играет",
                            color=EmbedColor.MAIN_COLOR.value,
                        )
                    )
                    continue

                embed = Embed(
                    title=self.current.title,
                    color=EmbedColor.MAIN_COLOR.value,
                )
                embed.add_field(
                    name=f"Продолжительность",
                    value=f"{self.milliseconds_to_time(self.position)} "
                    f"{self.generate_timebar(self.current.length, self.position)}"
                    f"{self.milliseconds_to_time(self.current.length)}",
                    inline=False,
                )
                embed.add_field(
                    name="Трек", value=f"[Ссылка]({self.current.uri})", inline=True
                )
                embed.add_field(name="Пинг", value=f"**{self.ping}** ms", inline=True)
                embed.add_field(
                    name="Платформа",
                    value=f"{sources[self.current.source]}",
                    inline=True,
                )
                embed.set_author(name=self.current.author)
                embed.set_thumbnail(self.current.artwork_url)

                await self.message.edit(embed=embed)

            await asyncio.sleep(1)
