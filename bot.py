import requests, time
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
CHANNEL = "@SUP_V_BotK"
CHANNEL_LINK = "https://t.me/SUP_V_BotK"

NEWS_SITES = [
    "https://www.bbc.com/news",
    "https://www.reuters.com/world/",
    "https://www.rbc.ru/"
]

bot = Bot(BOT_TOKEN)

def load_posted():
    try:
        return set(open("posted.txt").read().splitlines())
    except:
        return set()

def save_posted(link):
    open("posted.txt", "a").write(link+"\n")

def translate(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {"client":"gtx","sl":"en","tl":"ru","dt":"t","q":text}
    return requests.get(url, params=params).json()[0][0][0]

def get_image(url):
    try:
        soup = BeautifulSoup(requests.get(url).text,"html.parser")
        return soup.find("meta",property="og:image")["content"]
    except:
        return None

def get_description(url):
    try:
        soup = BeautifulSoup(requests.get(url).text,"html.parser")
        return soup.find("meta",property="og:description")["content"]
    except:
        return ""

def parse_news():
    posted = load_posted()

    for site in NEWS_SITES:
        soup = BeautifulSoup(requests.get(site).text,"html.parser")
        for a in soup.find_all("a", href=True):
            link = a["href"]
            if not link.startswith("http"):
                continue
            if link in posted:
                continue

            title = a.get_text().strip()
            if len(title) < 30:
                continue

            desc = get_description(link)
            img = get_image(link)

            if title:
                title_ru = translate(title)
                desc_ru = translate(desc) if desc else ""

                text = f"🌍 Мир\n\n<b>{title_ru}</b>\n\n{desc_ru}\n\n<a href='{CHANNEL_LINK}'>.sup.news</a>"

                if img:
                    bot.send_photo(CHANNEL, img, caption=text, parse_mode="HTML")
                else:
                    bot.send_message(CHANNEL, text, parse_mode="HTML")

                save_posted(link)
                time.sleep(60)
                return

while True:
    parse_news()
    time.sleep(3600)