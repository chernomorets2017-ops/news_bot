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
    with open(DB_FILE, "r") as f: 
        lines = f.read().splitlines()
        if len(lines) > 100:
            with open(DB_FILE, "w") as fw:
                fw.write("\n".join(lines[-50:]))
            return lines[-50:]
        return lines

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

def format_post(title, full_text):
    emoji = "⚡️"
    tags = {"сша": "🇺🇸", "трамп": "🇺🇸", "музыка": "🎸", "блогер": "📸", "кино": "🍿", "политика": "🏛"}
    for word, icon in tags.items():
        if word in title.lower():
            emoji = icon
            break

    post_header = f"{emoji} **{title.upper()}**\n\n"
    footer = "\n\n[📟 .sup.news](https://t.me/SUP_V_BotK)"
    
    available_space = 1024 - len(post_header) - len(footer) - 5
    
    if full_text:
        sentences = [s.strip() for s in full_text.split('. ') if len(s) > 10]
        if len(sentences) > 2:
            mid = len(sentences) // 2
            p1 = '. '.join(sentences[:mid]) + '.'
            p2 = '. '.join(sentences[mid:]) + '.'
            body = f"{p1}\n\n{p2}"
        else:
            body = full_text
        
        body = smart_trim(body, available_space)
        return post_header + body + footer
    
    return post_header + footer

def is_bad_content(title):
    bad_words = ['топ', 'список', 'лучших', 'способов', 'причин', 'советов', 'подборка', 'рейтинг']
    for word in bad_words:
        if word in title.lower(): return True
    return False

def run():
    url = f"https://newsapi.org/v2/everything?q=politics OR music OR bloggers OR USA OR hollywood&language=ru&sortBy=publishedAt&pageSize=15&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        articles = r.json().get("articles", [])
        db = get_processed_links()
        posted = 0

        for a in articles:
            if posted >= 2: break
            l = a["url"]
            title = a.get("title", "")
            
            if l not in db and not is_bad_content(title):
                content = get_full_text(l)
                if not content or len(content) < 300: continue

                final_post = format_post(title, content)
                img = a.get("urlToImage")

                try:
                    if img and img.startswith("http"):
                        bot.send_photo(CHANNEL_ID, img, caption=final_post, parse_mode='Markdown')
                    else:
                        bot.send_message(CHANNEL_ID, final_post, parse_mode='Markdown', disable_web_page_preview=True)
                    save_link(l)
                    posted += 1
                    time.sleep(5)
                except: continue
    except: pass

if __name__ == "__main__":
    run()
