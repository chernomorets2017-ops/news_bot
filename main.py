import os, telebot, requests, time
from bs4 import BeautifulSoup

BOT_TOKEN = "7620242203:AAH78eXG5zO2r31_6z8_N-6-H7XqO_A6R8U"
CHANNEL_ID = "@sup_newss"
CHANNEL_LINK = "https://t.me/sup_newss"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def get_full_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']): s.decompose()
        ps = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text()) > 40]
        return " ".join(ps) if ps else None
    except: return None

def smart_trim(text, limit):
    if len(text) <= limit: return text
    trimmed = text[:limit]
    last_dot = trimmed.rfind('.')
    if last_dot != -1 and last_dot > (limit // 2):
        return trimmed[:last_dot + 1]
    return trimmed + "..."

def run():
    url = f"https://newsapi.org/v2/top-headlines?country=ru&pageSize=10&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    articles = r.get("articles", [])
    if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
    with open(DB_FILE, 'r', encoding='utf-8') as f: done = f.read().splitlines()
    p = 0
    for a in articles:
        if p >= 2: break
        if a["url"] not in done and a["title"] not in done:
            full_text = get_full_text(a["url"])
            source = full_text if full_text else (a.get('description') or a['title'])
            clean_title = a['title'].strip()
            content = smart_trim(source, 800)
            footer = f"\n\n🌍 <a href='{CHANNEL_LINK}'>Sup.News</a>"
            msg = f"🔥 <b>{clean_title.upper()}</b>\n\n{content}{footer}"
            try:
                if a.get("urlToImage"):
                    bot.send_photo(CHANNEL_ID, a["urlToImage"], caption=msg, parse_mode='HTML')
                else:
                    bot.send_message(CHANNEL_ID, msg, parse_mode='HTML', disable_web_page_preview=True)
                with open(DB_FILE, 'a', encoding='utf-8') as f:
                    f.write(a["url"] + "\n")
                    f.write(a["title"] + "\n")
                p += 1
                time.sleep(5)
            except: continue

if __name__ == "__main__":
    run()
