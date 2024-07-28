from typing import List
from typing import Optional
import os
import datetime

from dotenv import load_dotenv

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String, BigInteger, DateTime, Boolean, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.dialects.postgresql import ARRAY, JSON


load_dotenv()


engine = create_async_engine(
    f"postgresql+asyncpg://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}",
    echo=False,
)


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    currency: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    level: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    exp: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    select_card: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    all_voice_time: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    mute_time: Mapped[DateTime] = mapped_column(DateTime)
    ban_time: Mapped[DateTime] = mapped_column(DateTime)
    p_channel_name: Mapped[str] = mapped_column(Text)
    p_channel_users_limit: Mapped[int] = mapped_column(BigInteger, default=0)
    p_channel_lock: Mapped[bool] = mapped_column(Boolean, default=True)
    p_channel_access_users: Mapped[List[int]] = mapped_column(
        ARRAY(BigInteger), default=[], nullable=False
    )
    p_channel_id: Mapped[int] = mapped_column(BigInteger)
    report_ticket_channel_id: Mapped[int] = mapped_column(BigInteger)


class User_global(Base):
    __tablename__ = "users_global"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    vk_url: Mapped[str] = mapped_column(
        String, default="https://vk.com/", nullable=False
    )
    tg_url: Mapped[str] = mapped_column(String, default="https://t.me/", nullable=False)
    inst_url: Mapped[str] = mapped_column(
        String, default="https://www.instagram.com/", nullable=False
    )
    select_color: Mapped[str] = mapped_column(
        String, default="0x383E54", nullable=False
    )
    donate: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    cards: Mapped[List[int]] = mapped_column(
        ARRAY(BigInteger), default=[0], nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text, default="Статус не установлен", nullable=False
    )
    prem_time: Mapped[DateTime] = mapped_column(DateTime)
    embed_json: Mapped[dict] = mapped_column(JSON)
    embed_text: Mapped[str] = mapped_column(Text)


class Guilds(Base):
    __tablename__ = "guilds"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    level_up_channel: Mapped[int] = mapped_column(BigInteger)
    admin_roles_ids: Mapped[List[int]] = mapped_column(
        ARRAY(BigInteger), default=[], nullable=False
    )
    ban_role: Mapped[int] = mapped_column(BigInteger)
    mute_role: Mapped[int] = mapped_column(BigInteger)
    join_channel_id: Mapped[int] = mapped_column(BigInteger)
    leave_channel_id: Mapped[int] = mapped_column(BigInteger)
    roles_add: Mapped[List[int]] = mapped_column(
        ARRAY(BigInteger), default=[], nullable=False
    )
    save_roles: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    saved_roles: Mapped[List[int]] = mapped_column(
        ARRAY(BigInteger), default=[], nullable=False
    )
    p_channel_ids: Mapped[List[int]] = mapped_column(
        ARRAY(BigInteger), default=[], nullable=False
    )
    member_stats_channel_id: Mapped[int] = mapped_column(BigInteger)
    boosts_stats_channel_id: Mapped[int] = mapped_column(BigInteger)
    voice_members_channel_id: Mapped[int] = mapped_column(BigInteger)
    date_channel_id: Mapped[int] = mapped_column(BigInteger)
    prem_time: Mapped[DateTime] = mapped_column(DateTime)
    report_channel_id: Mapped[int] = mapped_column(BigInteger)
    report_message_id: Mapped[int] = mapped_column(BigInteger)
    report_notif_channel_id: Mapped[int] = mapped_column(BigInteger)

