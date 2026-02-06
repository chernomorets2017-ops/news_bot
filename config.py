import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

RSS_FEEDS = [
    "https://lenta.ru/rss/news",
    "https://www.intermedia.ru/rss",
    "https://www.the-flow.ru/rss/all",
    "https://www.billboard.com/feed/",
    "https://pitchfork.com/rss/news/"
]

KEYWORDS = [
    "music", "album", "track", "single",
    "rapper", "singer", "band", "concert",
    "музыка", "артист", "альбом", "клип",
    "шоу-бизнес", "рэпер", "певец"
]

POSTS_PER_RUN = 1

FALLBACK_IMAGE = "https://i.imgur.com/8Km9tLL.jpg"