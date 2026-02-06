from newspaper import Article

def parse_article(url: str):
    article = Article(
        url,
        language='ru'  
    )

    article.download()
    article.parse()

    return {
        "title": article.title,        
        "text": article.text,          
        "image": article.top_image     
    }