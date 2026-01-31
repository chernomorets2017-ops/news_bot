import os
import telebot
import requests
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

def format_text(title, description, link):
    emoji = "⚡️"
    tags = {
        "apple": "🍏", "iphone": "📱", "сша": "🇺🇸", "трамп": "🇺🇸", 
        "музыка": "🎸", "певец": "🎤", "блогер": "📸", "tiktok": "🎬",
        "кино": "🍿", "голливуд": "🌟", "политика": "🏛"
    }
    
    for word, icon in tags.items():
        if word in title.lower() or word in description.lower():
            emoji = icon
            break

    text = f"{emoji} **{title.upper()}**\n\n"
    clean_desc = description.split("...")[0].split("…")[0]
    
    text += f"{clean_desc}\n\n"
    text += f"🔥 _Следите за подробностями в нашем канале!_\n\n"
    text += f"[Читать полностью]({link})"
    
    return text

def run():
    url = f"https://newsapi.org/v2/everything?q=politics OR music OR bloggers&language=ru&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
    
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
                desc = a.get("description", "")
                
                if not desc or len(desc) < 40: continue
                
                post_content = format_text(title, desc, l)
                img = a.get("urlToImage")

                try:
                    if img and img.startswith("http"):
                        bot.send_photo(CHANNEL_ID, img, caption=post_content, parse_mode='Markdown')
                    else:
                        bot.send_message(CHANNEL_ID, post_content, parse_mode='Markdown', disable_web_page_preview=True)
                    
                    save_link(l)
                    posted += 1
                    time.sleep(5)
                except:
                    continue
    except:
        pass

if __name__ == "__main__":
    run()
