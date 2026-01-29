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
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'button']): s.decompose()
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])
        return text[:4000]
    except:
        return None

def rewrite_text(title, content):
    full_prompt = (
        f"Ты — профессиональный редактор новостного Telegram-канала. Твоя задача — сделать качественный и законченный пересказ новости.\n\n"
        f"ЗАГОЛОВОК НОВОСТИ: {title}\n"
        f"ИСХОДНЫЙ ТЕКСТ: {content}\n\n"
        f"ИНСТРУКЦИЯ ПО ОФОРМЛЕНИЮ:\n"
        f"1. Начни с жирного заголовка и тематического эмодзи (например, 🔥, ⚡️, 🚀).\n"
        f"2. Первый блок: Суть новости в 2-3 предложениях.\n"
        f"3. Второй блок: Ключевые подробности и интересные факты списком. Используй разные эмодзи-маркеры (✅, 📍, 🔍).\n"
        f"4. Третий блок: Итог или вывод одним предложением.\n\n"
        f"ЖЕСТКИЕ ТРЕБОВАНИЯ:\n"
        f"- ПИШИ ДО КОНЦА. Текст не должен обрываться на полуслове или заканчиваться многоточием.\n"
        f"- НИКАКИХ ссылок на сайты и фраз типа 'сообщает источник'.\n"
        f"- Используй много эмодзи, чтобы пост выглядел живым.\n"
        f"- Общий объем текста: от 600 до 1000 знаков.\n"
        f"- Если не хватает данных, просто красиво заверши мысль на основе того, что есть."
    )
    
    providers = [g4f.Provider.Blackbox, g4f.Provider.ChatGptEs, g4f.Provider.DarkAI]
    
    for provider in providers:
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-4o",
                provider=provider,
                messages=[{"role": "user", "content": full_prompt}],
                timeout=60
            )
            if response and len(response) > 100:
                res = response.strip()
                res = re.sub(r'\.{2,}|…$', '.', res)
                return res
        except:
            continue
            
    return f"<b>{title}</b>\n\n{content[:500]}."

def run():
    url = f"https://newsapi.org/v2/everything?q=(IT OR технологии OR нейросети OR блогеры)&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        articles = requests.get(url).json().get('articles', [])
    except:
        return

    posted = get_posted_links()

    for art in articles:
        link = art['url']
        if link in posted: continue
        
        raw_text = get_full_article(link)
        content = raw_text if (raw_text and len(raw_text) > 400) else art.get('description', "")
        
        if not content or len(content) < 100: continue

        final_post = rewrite_text(art['title'], content)
        caption = f"{final_post}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if art.get('urlToImage'):
                bot.send_photo(CHANNEL_ID, art['urlToImage'], caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_link(link)
            break
        except:
            continue

if __name__ == "__main__":
    run()
