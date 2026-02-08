import requests
from bs4 import BeautifulSoup

def get_articles(url):
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    articles = []

    for article in soup.find_all("article")[:5]:
        title_tag = article.find("h2") or article.find("h3")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link_tag = article.find("a")
        img_tag = article.find("img")

        link = link_tag["href"] if link_tag and link_tag.has_attr("href") else None
        img = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

        if title and link:
            if link.startswith("/"):
                link = url.split("/")[0] + "//" + url.split("/")[2] + link

            articles.append({
                "title": title,
                "link": link,
                "image": img
            })

    return articles