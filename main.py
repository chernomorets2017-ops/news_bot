import os
import telebot
import requests
from bs4 import BeautifulSoup
import time
from openai import OpenAI

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
CHANNEL_ID = "@SUP_V_BotK"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916"
DEEPSEEK_API_KEY = "sk-8d8ec9586c6745e6bf11e438539533db"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def get_processed_links():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: 
        lines = f.read().splitlines()
        return lines[-100:]

def save_link(link):
    with open(DB_FILE, "a") as f: f.write(link + "\n")

def get_full_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']): s.decompose()
        text = ' '.join([p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 50])
        return text[:2000]
    except: return None

def smart_trim(text, limit):
    if len(text) <= limit: return text
    trimmed = text[:limit]
    last_dot = trimmed.rfind('.')
    return trimmed[:last_dot + 1] if last_dot != -1 else trimmed

def ai_rewrite(title, text):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты редактор. Пиши кратко, до 300 символов. Никакой политики."},
                {"role": "user", "content": f"Сделай микро-пересказ новости (макс 300 знаков). Заголовок жирным. Тема: {title}\nТекст: {text}"}
            ],
            max_tokens=400,
            temperature=0.6
        )
        return response.choices[0].message.content
    except: return None

def run():
    url = f"https://newsapi.org/v2/everything?q=(music OR bloggers OR hollywood OR gadgets OR apple)&language=ru&sortBy=publishedAt&pageSize=30&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        articles = r.json().get("articles", [])
        db = get_processed_links()
        posted = 0
        for a in articles:
            if posted >= 2: break
            l = a["url"]
            if l not in db and not any(w in a.get("title", "").lower() for w in ['топ', 'список', 'подборка']):
                raw = get_full_text(l)
                if not raw or len(raw) < 250: continue
                txt = ai_rewrite(a.get("title", ""), raw)
                if not txt: continue
                
                footer = "\n\n[📟 .sup.news](https://t.me/SUP_V_BotK)"
                final_text = smart_trim(txt, 1000 - len(footer)) + footer
                
                img = a.get("urlToImage")
                try:
                    if img and img.startswith("http"):
                        bot.send_photo(CHANNEL_ID, img, caption=final_text, parse_mode='Markdown')
                    else:
                        bot.send_message(CHANNEL_ID, final_text, parse_mode='Markdown', disable_web_page_preview=True)
                    save_link(l)
                    posted += 1
                    time.sleep(10)
                except: continue
    except: pass

if __name__ == "__main__":
    run()
