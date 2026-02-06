import feedparser
from config import RSS_FEEDS, KEYWORDS

def fetch_news():
    results = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            text = title.lower()

            if any(k.lower() in text for k in KEYWORDS):
                results.append({
                    "title": title,
                    "url": link
                })

    return results