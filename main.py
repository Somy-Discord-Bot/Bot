import os
import traceback
import disnake
from dotenv import load_dotenv
from disnake.ext.commands import InteractionBot


load_dotenv()


def main() -> None:
    bot = InteractionBot(
        intents=disnake.Intents.all(),
        owner_id=1004649810323845142,
        allowed_mentions=disnake.AllowedMentions(
            users=True,
            everyone=True,
            roles=True,
            replied_user=True,
        ),
    )

    local_path = [
        "extensions/level",
        "extensions/info",
        "extensions/stats",
        "extensions/private_channels",
        "extensions/utils",
        "extensions/eco/Casino/",
        "extensions/settings",
        "extensions/eco",
        "extensions/report_system",
        "extensions",
    ]

    for current_path in local_path:
        for extension in disnake.utils.search_directory(f"{current_path}"):
            try:
                bot.load_extension(extension)
                print(f"Extension {extension} load successful")
            except Exception as error:
                print(f"Failed to load extension {extension}")
                errors = traceback.format_exception(
                    type(error), error, error.__traceback__
                )
                print(errors)

    bot.run(os.getenv("DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    main()
