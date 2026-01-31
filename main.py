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

def get_full_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']): s.decompose()
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs if len(p.get_text()) > 50])
        return text[:1200]
    except:
        return None

def format_post(title, full_text):
    emoji = "⚡️"
    tags = {
        "apple": "🍏", "iphone": "📱", "сша": "🇺🇸", "трамп": "🇺🇸", "байден": "🇺🇸",
        "музыка": "🎸", "певец": "🎤", "рэп": "🎧", "блогер": "📸", "tiktok": "🎬",
        "кино": "🍿", "голливуд": "🌟", "политика": "🏛", "интервью": "🎙"
    }
    
    for word, icon in tags.items():
        if word in title.lower():
            emoji = icon
            break

    post = f"{emoji} **{title.upper()}**\n\n"
    
    if full_text:
        sentences = full_text.split('. ')
        if len(sentences) > 4:
            count = len(sentences)
            p1 = '. '.join(sentences[:count//3]) + '.'
            p2 = '. '.join(sentences[count//3:2*count//3]) + '.'
            p3 = '. '.join(sentences[2*count//3:]) + '.'
            post += f"{p1}\n\n{p2}\n\n{p3}"
        else:
            post += full_text
            
    post += f"\n\n[📟 .sup.news](https://t.me/SUP_V_BotK)"
    return post

def run():
    url = f"https://newsapi.org/v2/everything?q=politics OR music OR bloggers OR USA OR hollywood&language=ru&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
    
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
                content = get_full_text(l)
                
                if not content or len(content) < 200:
                    content = a.get("description", "")
                    if not content or "…" in content or "..." in content:
                        continue

                final_post = format_post(title, content)
                img = a.get("urlToImage")

                try:
                    if img and img.startswith("http"):
                        bot.send_photo(CHANNEL_ID, img, caption=final_post[:1024], parse_mode='Markdown')
                    else:
                        bot.send_message(CHANNEL_ID, final_post[:4096], parse_mode='Markdown')
                    
                    save_link(l)
                    posted += 1
                    time.sleep(5)
                except:
                    continue
    except:
        pass

if __name__ == "__main__":
    run()
