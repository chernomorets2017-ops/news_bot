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

def get_full_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']): s.decompose()
        text = ' '.join([p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 40])
        return text[:4000]
    except:
        return None

def ai_summarize(title, body):
    prompt = f"""
    Ты — автор дерзкого новостного блога. Перескажи эту новость СВОИМИ СЛОВАМИ.
    
    ТЕМА: {title}
    ТЕКСТ: {body}
    
    ЗАДАЧА:
    1. Сделай 3 коротких, емких абзаца.
    2. Первый абзац выдели ЖИРНЫМ (это заголовок-молния).
    3. Добавь тематические эмодзи (много, по смыслу).
    4. Стиль: живой, молодежный, как пост в Telegram.
    5. Весь текст должен быть законченным, без обрывов.
    6. НЕ ставь ссылку на источник.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return None

def run():
    url = f"https://newsapi.org/v2/everything?q=politics OR music OR USA OR hollywood&language=ru&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
    try:
        articles = requests.get(url, timeout=10).json().get("articles", [])
        db = get_processed_links()
        posted = 0

        for a in articles:
            if posted >= 2: break
            l = a["url"]
            if l not in db:
                raw_text = get_full_text(l)
                source_material = raw_text if raw_text and len(raw_text) > 300 else a.get("description", "")
                
                if len(source_material) < 150: continue
                
                summary = ai_summarize(a["title"], source_material)
                if not summary: continue

                # Добавляем твою зашифрованную ссылку
                final_post = f"{summary}\n\n[📟 .sup.news](https://t.me/SUP_V_BotK)"
                img = a.get("urlToImage")

                try:
                    if img and img.startswith("http"):
                        bot.send_photo(CHANNEL_ID, img, caption=final_post[:1024], parse_mode='Markdown')
                    else:
                        bot.send_message(CHANNEL_ID, final_post[:4096], parse_mode='Markdown', disable_web_page_preview=True)
                    
                    save_link(l)
                    posted += 1
                    time.sleep(20)
                except: continue
    except: pass

if __name__ == "__main__":
    run()
