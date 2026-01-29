import telebot
import g4f
import requests
import os
import re
from bs4 import BeautifulSoup

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916" 
CHANNEL_ID = "@SUP_V_BotK"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def get_posted_links():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return f.read().splitlines()

def save_posted_link(link):
    with open(DB_FILE, "a") as f: f.write(link + "\n")

def get_full_article(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']): s.decompose()
        paragraphs = soup.find_all('p')
        full_text = " ".join([p.get_text() for p in paragraphs])
        return full_text[:5000]
    except:
        return None

def get_news():
    query = "(IT OR технологии OR нейросети OR гаджеты OR игры OR крипта OR шоубиз OR хайп OR блогеры)"
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url).json()
        return res.get('articles', [])
    except:
        return []

def rewrite_text(title, full_content):
    prompt = (
        f"Напиши пост для Telegram в стиле ВПШ. Текст должен быть ИНФОРМАТИВНЫМ и ДЛИННЫМ.\n\n"
        f"НОВОСТЬ: {title}\n"
        f"КОНТЕНТ: {full_content}\n\n"
        f"ПЛАН:\n"
        f"1. 🧐 (Эмодзи по теме) + Заголовок (Жирным, НЕ капсом, просто важное предложение).\n"
        f"2. Основной текст новости: Разбей на 3-4 абзаца. Расскажи всё подробно, с цифрами и деталями.\n"
        f"3. Используй нормальный язык, без лишнего официоза, но и без каши.\n"
        f"4. В конце добавь краткий итог или мнение.\n\n"
        f"⚠️ СТРОГО: НЕ ОБРЫВАЙ ТЕКСТ. Напиши минимум 1000 знаков. НЕ упоминай источники и ссылки."
    )
    try:
        # Используем Gemini — она лучше всех держит контекст
        response = g4f.ChatCompletion.create(
            model="gemini", 
            messages=[{"role": "user", "content": prompt}],
            timeout=60
        )
        return response.strip()
    except:
        return f"<b>{title}</b>\n\n{full_content[:700]}..."

def run():
    posted_links = get_posted_links()
    articles = get_news()
    if not articles: return

    for art in articles:
        link = art['url']
        if link in posted_links: continue
        
        full_content = get_full_article(link)
        content_to_use = full_content if (full_content and len(full_content) > 500) else art.get('description', "")

        if len(content_to_use) < 100: continue

        text = rewrite_text(art['title'], content_to_use)
        img = art.get('urlToImage')
        
        # Убираем возможные артефакты в конце
        text = re.sub(r'\.\.\.$', '', text)
        
        caption = f"{text}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if img:
                bot.send_photo(CHANNEL_ID, img, caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_link(link)
            break 
        except:
            continue

if __name__ == "__main__":
    run()
