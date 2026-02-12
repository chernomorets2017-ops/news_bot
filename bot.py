import telegram
from parser import get_news

TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
CHANNEL = "@SUP_V_BotK"

bot = telegram.Bot(token=TOKEN)

def post():
    news = get_news()

    for n in news:
        caption = f"""📰 *Актуальные новости*

*{n['title']}*

{n['text']}

🔗 [.sup.news](https://t.me/SUP_V_BotK)
"""

        if n["img"]:
            bot.send_photo(chat_id=CHANNEL, photo=n["img"], caption=caption, parse_mode="Markdown")
        else:
            bot.send_message(chat_id=CHANNEL, text=caption, parse_mode="Markdown")

if __name__ == "__main__":
    post()