import telegram
from parser import get_news

TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
CHANNEL = "@SUP_V_BotK"

bot = telegram.Bot(token=TOKEN)

def send_news():
    news = get_news()

    for n in news:
        text = f"""🌍 *Мир*

*{n['title']}*

{n['text']}

👉 [Читать в источнике]({n['link']})
👉 [Наш канал](https://t.me/sup_news)
"""

        bot.send_message(
            chat_id=CHANNEL,
            text=text,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )


if __name__ == "__main__":
    send_news()