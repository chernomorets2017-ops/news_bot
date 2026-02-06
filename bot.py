from telegram import Bot
from config import BOT_TOKEN, CHANNEL_USERNAME, CHANNEL_LINK, POSTS_PER_RUN
from rss_reader import fetch_news
from parser import parse_article
from summarizer import summarize
from deduplicator import is_duplicate, mark_posted
from logger import logger

bot = Bot(BOT_TOKEN)

def run():
    posted = 0

    for item in fetch_news():
        if posted >= POSTS_PER_RUN:
            break

        article = parse_article(item["url"])

        if is_duplicate(item["url"], article["title"]):
            continue

        text = summarize(article["text"])

        caption = (
            f"<b>{article['title']}</b>\n\n"
            f"{text}\n\n"
            f"<a href='{CHANNEL_LINK}'>@{CHANNEL_USERNAME}</a>"
        )

        try:
            bot.send_photo(
                chat_id=f"@{CHANNEL_USERNAME}",
                photo=article["image"],
                caption=caption,
                parse_mode="HTML"
            )
            mark_posted(item["url"], article["title"])
            posted += 1
            logger.info(f"Posted: {article['title']}")
        except Exception as e:
            logger.error(e)

if __name__ == "__main__":
    run()