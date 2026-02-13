import feedparser

FEEDS = [
   
    "https://rss.cnn.com/rss/edition.rss",
    "https://www.theguardian.com/world/rss",

   
    "https://lenta.ru/rss/news",
    "https://www.rbc.ru/rss/news"
]

def get_news():
    result = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries[:7]:
            title = e.title
            link = e.link
            summary = getattr(e, "summary", "")

            if len(title) < 15:
                continue

            result.append({
                "title": title,
                "link": link,
                "summary": summary
            })
    return result