import os
import telebot
import requests
import g4f
from g4f.client import Client
from bs4 import BeautifulSoup
import time

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
CHANNEL_ID = "@SUP_V_BotK"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)
client = Client()

def get_processed_links():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return f.read().splitlines()

def save_link(link):
    with open(DB_FILE, "a") as f: f.write(link + "\n")

def get_article_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']): s.decompose()
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        return text[:4000] if len(text) > 300 else None
    except:
        return None

def make_post(title, body, link):
    prompt = f"Напиши пост для ТГ на русском. 3 абзаца, жирный заголовок. Вставляй очень много тематических эмодзи в каждое предложение. Тема: {title}. Текст: {body}. Ссылка: {link}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return None

def run():
    urls = [
        f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}",
        f"https://newsapi.org/v2/everything?q=politics OR music OR bloggers&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    ]
    
    db = get_processed_links()
    posted = 0

    for url in urls:
        if posted >= 2: break
        try:
            r = requests.get(url, timeout=10)
            articles = r.json().get("articles", [])
            
            for a in articles:
                if posted >= 2: break
                l = a["url"]
                if l not in db:
                    full_text = get_article_content(l)
                    source = full_text if full_text else a.get("description", "")
                    
                    if not source or len(source) < 100: continue
                    
                    post = make_post(a["title"], source, l)
                    if not post: continue

                    img = a.get("urlToImage")
                    try:
                        if img and img.startswith("http"):
                            bot.send_photo(CHANNEL_ID, img, caption=post[:1024], parse_mode='Markdown')
                        else:
                            bot.send_message(CHANNEL_ID, post, parse_mode='Markdown', disable_web_page_preview=True)
                        
                        save_link(l)
                        posted += 1
                        time.sleep(15)
                    except:
                        continue
        except:
            continue

if __name__ == "__main__":
    run()
