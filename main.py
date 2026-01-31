import os
import telebot
import requests
import g4f
from bs4 import BeautifulSoup
import time

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
CHANNEL_ID = "@SUP_V_BotK"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def get_processed_links():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return f.read().splitlines()

def save_link(link):
    with open(DB_FILE, "a") as f: f.write(link + "\n")

def get_full_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']): s.decompose()
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs if len(p.get_text()) > 50])
        return text[:1500]
    except:
        return None

def smart_trim(text, limit):
    if len(text) <= limit: return text
    trimmed = text[:limit]
    last_dot = trimmed.rfind('.')
    if last_dot != -1:
        return trimmed[:last_dot + 1]
    return trimmed

def ai_rewrite(title, text):
    try:
        prompt = f"Перескажи новость кратко и хайпово для ТГ. 3 абзаца, первый жирным, много эмодзи. Тема: {title}. Текст: {text}"
        response = g4f.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            timeout=20
        )
        return response
    except:
        return None

def format_fallback(title, text):
    emoji = "⚡️"
    tags = {"apple": "🍏", "сша": "🇺🇸", "трамп": "🇺🇸", "музыка": "🎸", "кино": "🍿", "политика": "🏛"}
    for word, icon in tags.items():
        if word in title.lower():
            emoji = icon
            break
    clean_text = smart_trim(text, 800)
    return f"{emoji} **{title.upper()}**\n\n{clean_text}"

def run():
    url = f"https://newsapi.org/v2/everything?q=politics OR music OR USA OR hollywood&language=ru&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        articles = r.json().get("articles", [])
        db = get_processed_links()
        posted = 0
        for a in articles:
            if posted >= 2: break
            l = a["url"]
            if l not in db:
                title = a.get("title", "")
                raw_content = get_full_text(l) or a.get("description", "")
                if not raw_content or len(raw_content) < 150: continue
                final_post = ai_rewrite(title, raw_content)
                if not final_post:
                    final_post = format_fallback(title, raw_content)
                footer = "\n\n[📟 .sup.news](https://t.me/SUP_V_BotK)"
                limit = 1000 - len(footer)
                final_post = smart_trim(final_post, limit) + footer
                img = a.get("urlToImage")
                try:
                    if img and img.startswith("http"):
                        bot.send_photo(CHANNEL_ID, img, caption=final_post, parse_mode='Markdown')
                    else:
                        bot.send_message(CHANNEL_ID, final_post, parse_mode='Markdown')
                    save_link(l)
                    posted += 1
                    time.sleep(10)
                except: continue
    except: pass

if __name__ == "__main__":
    run()
