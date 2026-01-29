import telebot
import g4f
import requests
import os
import re

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

def clean_text(text):
    # Удаляет сторонние ссылки из текста, чтобы аудитория не уходила
    return re.sub(r'http[s]?://\S+', '', text)

def get_news():
    query = "(Россия OR экономика OR celebrity OR нейросети OR ТикТок OR TikTok OR YouTube OR Twitch OR Instagram OR Reels OR блогеры OR хайп OR инфлюенсеры OR MrBeast OR Logan+Paul OR поп-культура)"
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url).json()
        return res.get('articles', [])
    except:
        return []

def rewrite_text(title, description):
    prompt = (
        f"Ты топовый редактор медиа. Сделай хайповый пересказ новости. "
        f"Заголовок: {title}. Суть: {description}. "
        f"ТРЕБОВАНИЯ: "
        f"1. Пиши дерзко, с иронией. "
        f"2. Если блогеры или соцсети — добавь сленга и обсуди скандалы. "
        f"3. Если экономика — объясни последствия. "
        f"4. Используй ОЧЕНЬ МНОГО тематических ЭМОДЗИ и символов. "
        f"5. Заголовок сделай жирным КАПСОМ. "
        f"6. НЕ вставляй в текст никакие ссылки на сторонние сайты. "
        f"Объем: минимум 600 знаков."
    )
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return clean_text(response)
    except:
        return f"<b>{title.upper()}</b>\n\n{description}"

def run():
    posted_links = get_posted_links()
    articles = get_news()
    
    for art in articles:
        link = art['url']
        if link in posted_links or not art.get('description'): 
            continue
        
        text = rewrite_text(art['title'], art['description'])
        img = art.get('urlToImage')
        
        caption = (
            f"{text}\n\n"
            f"📍 <a href='{link}'>ИСТОЧНИК</a>\n"
            f"🗞 <b>Читать в: <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        )
        
        try:
            if img:
                bot.send_photo(CHANNEL_ID, img, caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            
            save_posted_link(link)
            break 
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run()
