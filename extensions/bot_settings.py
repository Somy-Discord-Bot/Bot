import disnake
from disnake.ext import commands, tasks

from sqlalchemy import select, delete, insert, update
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *
from core.vars import *
from core.models import *


class BotSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.change_bot_status.start()

    @tasks.loop(minutes=5.0)
    async def change_bot_status(self):
        await self.bot.change_presence(
            status=disnake.Status.online,
            activity=disnake.Activity(
                type=disnake.ActivityType.watching,
                name=f"{len(self.bot.users):,} участников",
            ),
        )
        await self.bot.wait_until_ready()

    @change_bot_status.before_loop
    async def before_change_bot_status(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(BotSettings(bot))
