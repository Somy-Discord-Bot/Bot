import re
from typing import Optional


def search_tracks_urls(string: str) -> Optional[tuple[str, str]]:
    tracks_links_regex = {
        "ytsearch": re.compile(r"https://www\.youtube\.com/watch\?v=([a-zA-Z0-9_-]+)"),
        "ytmsearch": re.compile(
            r"https://music\.youtube\.com/watch\?v=([a-zA-Z0-9_-]+)"
        ),
        "scsearch": re.compile(
            r"https://soundcloud\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+"
        ),
        "spsearch": re.compile(r"https://open\.spotify\.com/track/([a-zA-Z0-9]+)"),
    }

    for platform, regex in tracks_links_regex.items():
        result = regex.search(string)

        if result:
            return platform, result.group()

    return None


def search_playlists_urls(string: str) -> Optional[tuple[str, str]]:
    """
    :param string:
    :return:
    """

    platforms_playlists_urls = {
        "ytsearch": re.compile(
            r"https://www\.youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)"
        ),
        "ytmsearch": re.compile(
            r"https://music\.youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)"
        ),
        "scsearch": re.compile(
            r"https://soundcloud\.com/[a-zA-Z0-9-]+/sets/([a-zA-Z0-9]+)"
        ),
        "spsearch": re.compile(r"https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)"),
    }

    for platform, regex in platforms_playlists_urls.items():
        result = regex.search(string)

        if result:
            return platform, result.group()

    return None
