import feedparser

FEEDS = [
    "https://rss.app/feeds/_GkzYwQk9kK7rYj9m.xml",  # пример, можешь заменить
    "https://rss.cnn.com/rss/edition.rss",
    "https://www.theguardian.com/world/rss",
]

def get_news():
    news = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link
            news.append(f"{title}\n{link}")
    return news