import asyncpg
import disnake
from disnake import TextInputStyle, Embed

from core.vars import *


async def maxLevel():
    embed = Embed(
        title="Вы достигли максимального уровня", color=EmbedColor.MAIN_COLOR.value
    )
    return embed


async def banWords(message: str):
    mats_files = ["core/banwords/russian_mats.txt", "core/banwords/english_mats.txt"]
    for file_path in mats_files:
        with open(file_path, "r", encoding="utf-8") as f:
            if any(word.strip().lower() in message.lower() for word in f):
                return True


async def accessDeniedCustom(description: str):
    embed = Embed(
        title=f"{EmbedEmoji.ACCESS_DENIED.value} Отказано в доступе",
        description=description,
        color=EmbedColor.ACCESS_DENIED.value,
    )
    return embed


async def accessDeniedNoMoney(amount: int, authorQueryDBUsers):
    embed = await accessDeniedCustom("У вас недостаточно серебряных монет")
    embed.add_field(
        name="Баланс",
        value=f"{authorQueryDBUsers.currency:,}{EmbedEmoji.SILVER_COIN.value}",
        inline=True,
    )
    embed.add_field(
        name="Не хватает",
        value=f"{amount - authorQueryDBUsers.currency:,}{EmbedEmoji.SILVER_COIN.value}",
        inline=True,
    )
    return embed


async def accessDeniedButton(buttonAuthor: disnake.Member):
    embed = await accessDeniedCustom("Вы не можете использовать эту кнопку")
    embed.add_field(
        name="> Владелец кнопки", value=f"<@{buttonAuthor.id}>", inline=True
    )
    return embed


async def accessDeniedNotOwner(guildOwner: disnake.Member):
    embed = await accessDeniedCustom("Вы не являетесь владельцем этого сервера")
    embed.add_field(name="> Владелец сервера", value=f"<@{guildOwner.id}>", inline=True)
    return embed


async def min_value_100():
    embed = await accessDeniedCustom("Значение не должно быть меньше **100**")
    return embed
