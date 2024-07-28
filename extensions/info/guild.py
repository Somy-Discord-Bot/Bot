import disnake
from disnake import Embed
from disnake.ext import commands

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.checker import *
from core.vars import *
from core.models import *


class GuildInfo(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(description="Информация о сервере", name="guild-info")
    async def guild_info(self, interaction: disnake.UserCommandInteraction):
        if interaction.author.bot or not interaction.guild:
            return

        guild = interaction.guild
        guild_name = guild.name
        guild_desc = guild.description
        if guild_desc is None:
            guild_desc = "Описание не установлено"

        owner = guild.owner.id

        prem_status = await database(interaction.author)

        members = guild.member_count
        bots = sum(member.bot for member in interaction.guild.members)
        humans = sum(not member.bot for member in interaction.guild.members)
        online = sum(
            member.status == disnake.Status.online and not member.bot
            for member in interaction.guild.members
        )
        offline = sum(
            member.status == disnake.Status.offline and not member.bot
            for member in interaction.guild.members
        )
        idle = sum(
            member.status == disnake.Status.idle and not member.bot
            for member in interaction.guild.members
        )
        dnd = sum(
            member.status == disnake.Status.dnd and not member.bot
            for member in interaction.guild.members
        )

        channels = len(guild.channels) - len(guild.categories)
        categories = len(guild.categories)
        voice_channels = len(guild.voice_channels)
        text_channels = len(guild.text_channels)
        stage_channels = len(guild.stage_channels)
        forum_channels = len(guild.forum_channels)
        roles = len(guild.roles)
        boost_subs = len(guild.premium_subscribers)
        boost_level = guild.premium_tier
        boosts = guild.premium_subscription_count

        rules_channel = guild.rules_channel

        if rules_channel is None:
            rules_channel = "Не установлен"
        else:
            rules_channel = guild.rules_channel.jump_url

        ver_level = guild.verification_level
        ver_level_dict = {
            "none": "Отсутствует",
            "low": "Низкий",
            "medium": "Средний",
            "high": "Высокий",
            "highest": "Наивысший",
        }
        ver_level = ver_level_dict[f"{ver_level}"]

        nsfw_level = guild.nsfw_level
        nsfw_level_dict = {
            "NSFWLevel.default": "По умолчанию",
            "NSFWLevel.explicit": "Низкий",
            "NSFWLevel.safe": "Средний",
            "NSFWLevel.age_restricted": "Высокий",
        }
        nsfw_level = nsfw_level_dict[f"{nsfw_level}"]
        icon_url = None

        if guild.icon is not None:
            icon_url = guild.icon.url

        embed = Embed(
            description=f"{guild_desc}",
            color=EmbedColor.MAIN_COLOR.value,
        )

        if not prem_status[1]:
            embed.set_author(
                name=guild_name,
                icon_url=icon_url,
            )
        else:
            embed.set_author(
                name=f"{guild_name} {EmbedEmoji.GOLD_COIN.value}",
                icon_url=icon_url,
            )

        embed.set_footer(text=f"Guild ID - {interaction.guild.id}")
        embed.add_field(
            name="> Участники",
            value=f"{EmbedEmoji.ALL_MEMBERS.value} Всего: **{members}**\n"
            f"{EmbedEmoji.MEMBER.value} Людей: **{humans}** \n"
            f"{EmbedEmoji.BOT.value} Ботов: **{bots}**",
            inline=True,
        )
        embed.add_field(
            name="> Статусы",
            value=f"{EmbedEmoji.STATUS_ONLINE.value} В сети: **{online}**\n"
            f"{EmbedEmoji.STATUS_IDLE.value} Не активен: **{idle}**\n"
            f"{EmbedEmoji.STATUS_DND.value} Не беспокоить: **{dnd}**\n"
            f"{EmbedEmoji.STATUS_OFFLINE.value} Не в сети: **{offline}**",
            inline=True,
        )
        embed.add_field(
            name="> Каналы",
            value=f"{EmbedEmoji.TOTAL_CHANNELS.value} Всего: **{channels}**\n"
            f"{EmbedEmoji.FOLDER.value} Категорий: **{categories}**\n"
            f"{EmbedEmoji.TEXT_CHANNEL.value} Текстовых: **{text_channels}**\n"
            f"{EmbedEmoji.VOICE_CHANNEL.value} Голосовых: **{voice_channels}**\n"
            f"{EmbedEmoji.STAGE_CHANNEL.value} Трибун: **{stage_channels}**\n"
            f"{EmbedEmoji.FORUM_CHANNEL.value} Форумов: **{forum_channels}**\n"
            f"{EmbedEmoji.ROLE.value} Ролей: **{roles}**\n"
            f"{EmbedEmoji.RULES.value} Правила: **{rules_channel}**",
            inline=True,
        )
        embed.add_field(
            name="> Nitro boost",
            value=f"{EmbedEmoji.NITRO.value} Уровень: **{boost_level}**\n"
            f"{EmbedEmoji.NITRO_BOOST.value} Бустов: **{boosts}**\n"
            f"{EmbedEmoji.NITRO_BOOSTERS.value} Бустеров: **{boost_subs}**",
            inline=True,
        )
        embed.add_field(
            name="> Владелец",
            value=f"{EmbedEmoji.OWNER.value} <@{owner}>",
            inline=True,
        )
        embed.add_field(
            name="> Дата создания",
            value=f'{EmbedEmoji.CREATION_DATE.value} {disnake.utils.format_dt(guild.created_at, "f")}\n'
            f'{disnake.utils.format_dt(guild.created_at, "R")}',
            inline=True,
        )
        embed.add_field(
            name="> Уровень защиты",
            value=f"{EmbedEmoji.PROTECTION.value} {ver_level}",
            inline=True,
        )
        embed.add_field(
            name="> Уровень NSFW",
            value=f"{EmbedEmoji.NSFW.value} {nsfw_level}...",
            inline=True,
        )
        await interaction.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(GuildInfo(bot))
