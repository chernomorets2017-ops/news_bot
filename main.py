import os
import telebot
import requests
from g4f.client import Client
import time

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
CHANNEL_ID = "@SUP_V_BotK"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)
client = Client()

def get_processed_links():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return f.read().splitlines()

def save_link(link):
    with open(DB_FILE, "a") as f:
        f.write(link + "\n")

def rewrite_text_and_format(title, description, link):
    prompt = f"Напиши хайповый пост для ТГ в 3 абзаца с жирным заголовком и эмодзи-стикерами. Тема: {title}. Суть: {description}. Ссылка: {link}"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return f"🔥 **{title}**\n\n{description}\n\n[Читать полностью]({link})"

def fetch_news():
    print("Запуск поиска новостей...")
    # Используем топ-новости технологий и развлечений (самое близкое к медиа/блогерам)
    url = f"https://newsapi.org/v2/top-headlines?country=rs&category=technology&apiKey={NEWS_API_KEY}"
    # Если нужно больше политики и США, можно попробовать этот URL вместо верхнего:
    # url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

    try:
        r = requests.get(url)
        data = r.json()
        articles = data.get("articles", [])
        print(f"Найдено новостей: {len(articles)}")
    except Exception as e:
        print(f"Ошибка API: {e}")
        return

    processed = get_processed_links()
    
    posted_count = 0
    for article in articles:
        if posted_count >= 2: break # Публикуем максимум 2 за раз
        
        link = article["url"]
        if link not in processed:
            print(f"Публикую: {article['title']}")
            title = article["title"]
            desc = article["description"] or "Нет описания"
            img = article.get("urlToImage")
            
            content = rewrite_text_and_format(title, desc, link)
            
            try:
                if img and img.startswith("http"):
                    bot.send_photo(CHANNEL_ID, img, caption=content, parse_mode='Markdown')
                else:
                    bot.send_message(CHANNEL_ID, content, parse_mode='Markdown')
                save_link(link)
                posted_count += 1
                time.sleep(5)
            except Exception as e:
                print(f"Ошибка ТГ: {e}")
        else:
            print("Новость уже была в канале.")

if __name__ == "__main__":
    fetch_news()
