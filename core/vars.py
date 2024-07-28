from enum import Enum

ID_CARD_NAMES = {
    0: "Стандартная карточка рейтинга",
}

SELECT = ["по уровню", "по монетам"]
COIN_TYPE = ["Серебряные монеты", "Золотые монеты"]
WHEEL = [2.4, 1.7, 1.2, 1.5, 0.1, 0.1, 3, 0.2, 0.2, 0.7, 0.7, 3, 0.5, 0.5, 0, 0, 0, 2.4]
SLOT = [
    "🍒",
    "🍒",
    "🍒",
    "🍒",
    "🍒",
    "🍒",
    "🍒",
    "🔔",
    "🔔",
    "🔔",
    "🔔",
    "🔔",
    "🔔",
    "🔔",
    "🔔",
    "🔔",
    "💎",
    "💎",
    "💎",
    "💎",
    "🍇",
    "🍇",
    "🍇",
    "🍇",
    "🍇",
    "🍇",
]
COIN = ["орёл", "решка"]
ACTION_TYPE = [
    "нежно",
    "страстно",
    "извращенно",
    "дерзко",
    "больно",
    "приятно",
    "крепко",
]

CURRENCIES = [
    "USD",
    "EUR",
    "JPY",
    "GBP",
    "AUD",
    "CAD",
    "CHF",
    "CNY",
    "SEK",
    "NZD",
    "MXN",
    "SGD",
    "HKD",
    "NOK",
    "KRW",
    "TRY",
    "RUB",
    "INR",
    "BRL",
    "ZAR",
    "DKK",
    "PLN",
    "TWD",
    "THB",
    "IDR",
    # "HUF",
    # "CZK",
    # "ILS",
    # "CLP",
    # "PHP",
    # "AED",
    # "COP",
    # "SAR",
    # "MYR",
    # "RON",
    # "PEN",
    # "VND",
    # "EGP",
    # "NGN",
    # "BDT",
    # "ARS",
    # "IRR",
    # "UAH",
    # "MAD",
    # "PKR",
    # "DZD",
    # "KZT",
    # "QAR",
    # "KES",
    # "OMR",
]

sources = {"youtube": "<:YOUTUBE:1223035874766491728> YouTube"}


class EmbedColor(Enum):
    CASINO_ORANGE = 0xFFA933
    CASINO_WIN2X = 0xF25252
    CASINO_WIN4X = 0xF0F252
    CASINO_WIN10X = 0xF2528D
    CASINO_WIN50X = 0x9852F2
    CASINO_WIN100X = 0x52CDF2
    MAIN_COLOR = 0x383E54
    ACCESS_DENIED = 0xCF5D5D
    ACCESS_ALLOWED = 0x5DCF68
    PCHANNEL_SETTINGS = 0x3374FF


class EmbedEmoji(Enum):
    ACCESS_DENIED = "<:ACCESS_DENIED:1171913433030070292>"
    ACCESS_ALLOWED = "<:ACCESS_ALLOWED:1171913427762028635>"
    SILVER_COIN = "<:SILVER_COIN:1171925159783972896>"
    GOLD_COIN = "<:GOLD_COIN:1171931314329489458>"
    HAS_NITRO = "<a:nitro_subs:1026110302389022831>"
    VK_ICON = "<:vk_icon:1177285119313195078>"
    INST_ICON = "<:inst_icon:1177285557827686490>"
    TG_ICON = "<:tg_icon:1177285839621996586>"
    BOT = "<:BOT:951238054339821639>"
    STATUS_DND = "<:STATUS_DND:951168257992319056>"
    STATUS_ONLINE = "<:STATUS_ONLINE:951168297146138674>"
    STATUS_OFFLINE = "<:STATUS_OFFLINE:951168283036487711>"
    STATUS_IDLE = "<:STATUS_IDLE:951168270591987803>"
    NITRO_BOOST = "<:NITRO_BOOST:951168246978056273>"
    NITRO = "<:NITRO:951168230460891216>"
    NSFW = "<:18:1181007907584745483>"
    ACCOUNT_CREATED_AT = "<:ACCOUNT_CREATED_AT:1181007910441062421>"
    ACTIVITY = "<:ACTIVITY:1181007911951020102>"
    ALL_MEMBERS = "<:ALL_MEMBERS:1181008806029820054>"
    MEMBER = "<:MEMBER:1181008803672629341>"
    NITRO_BOOSTERS = "<:NITRO_BOOSTERS:1181011969885601812>"
    FOLDER = "<:FOLDER:1181013907024920648>"
    TOTAL_CHANNELS = "<:TOTAL_CHANNELS:1181014149849952316>"
    TEXT_CHANNEL = "<:TEXT_CHANNEL:1181014432122404955>"
    VOICE_CHANNEL = "<:VOICE_CHANNEL:1181014750696587304>"
    STAGE_CHANNEL = "<:STAGE_CHANNEL:1181015071267225711>"
    FORUM_CHANNEL = "<:CREATION_DATE:1181016152550408354>"
    ROLE = "<:ROLE:1181015319502929940>"
    RULES = "<:RULES:1181015534188367903>"
    OWNER = "<:OWNER:1181015825986101319>"
    CREATION_DATE = "<:CREATION_DATE:1181016152550408354>"
    PROTECTION = "<:PROTECTION:1181016425788354671>"
    START_FILL = "<:START_FILL:1199128161313640499>"
    START_NO_FILL = "<:START_NO_FILL:1199128474082881626>"
    FILL = "<:FILL:1199128156813135973>"
    NO_FILL = "<:NO_FILL:1199128158541205675>"
    END_FILL = "<:END_FILL:1199128152878886942>"
    END_NO_FILL = "<:END_NO_FILL:1199128155366117447>"
