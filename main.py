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

def get_clean_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']): s.decompose()
        paragraphs = [p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 60]
        return " ".join(paragraphs[:5])
    except:
        return None

def ai_rewrite(title, text):
    prompt = f"Перескажи новость как блогер. Тема: {title}. Текст: {text}. Правила: 3 абзаца, первый жирным, много эмодзи, законченная мысль."
    try:
        # Ограничиваем время ожидания ответа от ИИ до 25 секунд
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            timeout=25 
        )
        return response.choices[0].message.content
    except:
        return None

def run():
    url = f"https://newsapi.org/v2/everything?q=(politics OR music OR bloggers OR USA)&language=ru&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        articles = r.json().get("articles", [])
        db = get_processed_links()
        posted = 0

        for a in articles:
            if posted >= 2: break
            link = a["url"]
            if link not in db:
                body = get_clean_text(link) or a.get("description", "")
                if len(body) < 150: continue

                summary = ai_rewrite(a["title"], body)
                if not summary: continue

                footer = "\n\n[📟 .sup.news](https://t.me/SUP_V_BotK)"
                final_text = summary[:(1024 - len(footer) - 5)] + footer
                
                img = a.get("urlToImage")
                try:
                    if img and img.startswith("http"):
                        bot.send_photo(CHANNEL_ID, img, caption=final_text, parse_mode='Markdown')
                    else:
                        bot.send_message(CHANNEL_ID, final_text, parse_mode='Markdown', disable_web_page_preview=True)
                    
                    save_link(link)
                    posted += 1
                    time.sleep(10)
                except: continue
    except: pass

if __name__ == "__main__":
    run()
