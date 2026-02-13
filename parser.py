import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

SOURCES = [
    "https://www.bbc.com/news",
    "https://www.reuters.com/world",
]

def get_news():
    news = []
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            for item in soup.find_all("a", href=True)[:5]:
                title = item.text.strip()
                link = item["href"]
                if len(title) < 20:
                    continue

                title_ru = GoogleTranslator(source="auto", target="ru").translate(title)

                news.append({
                    "title": title_ru,
                    "link": link
                })
        except:
            pass

    return news