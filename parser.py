from newspaper import Article
from config import FALLBACK_IMAGE

def parse_article(url):
    article = Article(url)
    article.download()
    article.parse()

    image = article.top_image or FALLBACK_IMAGE

    return {
        "title": article.title,
        "text": article.text,
        "image": image
    }