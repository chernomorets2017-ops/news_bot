import os
import telebot
import requests
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
        for s in soup(['script', 'style', 'header', 'footer', 'nav']): s.decompose()
        text = ' '.join([p.get_text() for p in soup.find_all('p')])
        return text[:4000] if len(text) > 200 else None
    except:
        return None

def make_post(title, body, link):
    prompt = f"Напиши пост для ТГ. Тема: {title}. Текст: {body}. Инструкция: 3 полных абзаца, первый - жирным, много тематических эмодзи, без упоминания сторонних сайтов, только суть. Язык: русский. Ссылка для вставки: {link}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        res = response.choices[0].message.content
        if "Читать полностью" not in res:
            res += f"\n\n[Читать полностью]({link})"
        return res
    except:
        return None

def run():
    url = f"https://newsapi.org/v2/everything?q=politics OR music OR USA OR hollywood&language=ru&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
    try:
        articles = requests.get(url).json().get("articles", [])
    except: return

    db = get_processed_links()
    count = 0

    for a in articles:
        if count >= 2: break
        l = a["url"]
        if l not in db:
            full_text = get_article_content(l)
            source = full_text if full_text else a.get("description", "")
            
            if len(source) < 100: continue
            
            post = make_post(a["title"], source, l)
            if not post or "извините" in post.lower(): continue

            img = a.get("urlToImage")
            try:
                if img and img.startswith("http"):
                    bot.send_photo(CHANNEL_ID, img, caption=post, parse_mode='Markdown')
                else:
                    bot.send_message(CHANNEL_ID, post, parse_mode='Markdown', disable_web_page_preview=True)
                save_link(l)
                count += 1
                time.sleep(15)
            except: continue

if __name__ == "__main__":
    run()
