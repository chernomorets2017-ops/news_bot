import requests
from bs4 import BeautifulSoup

def parse_article(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.text if soup.title else ""
        paragraphs = [p.text for p in soup.find_all("p")]
        text = " ".join(paragraphs)[:5000]

        image = None
        og = soup.find("meta", property="og:image")
        if og:
            image = og["content"]

        return {
            "title": title,
            "text": text,
            "image": image
        }

    except:
        return {"title": None, "text": None, "image": None}