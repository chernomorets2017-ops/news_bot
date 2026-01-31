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
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']): s.decompose()
        text = ' '.join([p.get_text() for p in soup.find_all('p')])
        return text[:4000] if len(text) > 300 else None
    except Exception as e:
        print(f"Scraper error: {e}")
        return None

def make_post(title, body, link):
    prompt = f"Напиши пост для ТГ на русском. 3 абзаца, жирный заголовок, много эмодзи. Тема: {title}. Текст: {body}. Ссылка: {link}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            provider=g4f.Provider.ChatGptEs # Используем стабильный провайдер
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI error: {e}")
        return None

def run():
    print("Starting news fetch...")
    # Ищем и по России, и по США для максимального охвата
    urls = [
        f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}",
        f"https://newsapi.org/v2/everything?q=politics OR music OR bloggers&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    ]
    
    db = get_processed_links()
    posted = 0

    for url in urls:
        if posted >= 2: break
        try:
            articles = requests.get(url).json().get("articles", [])
            print(f"Found {len(articles)} articles in source")
            
            for a in articles:
                if posted >= 2: break
                l = a["url"]
                if l not in db:
                    print(f"Analyzing: {a['title']}")
                    full_text = get_article_content(l)
                    source = full_text if full_text else a.get("description", "")
                    
                    if not source or len(source) < 150:
                        print("Content too short, skipping...")
                        continue
                    
                    post = make_post(a["title"], source, l)
                    if not post: continue

                    img = a.get("urlToImage")
                    if img and img.startswith("http"):
                        bot.send_photo(CHANNEL_ID, img, caption=post[:1024], parse_mode='Markdown')
                    else:
                        bot.send_message(CHANNEL_ID, post, parse_mode='Markdown', disable_web_page_preview=True)
                    
                    save_link(l)
                    posted += 1
                    print("SUCCESS: Posted to Telegram")
                    time.sleep(15)
        except Exception as e:
            print(f"Loop error: {e}")

if __name__ == "__main__":
    run()
