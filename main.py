import os
import telebot
import requests
from g4f.client import Client
from bs4 import BeautifulSoup
import time

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
CHANNEL_ID = "@SUP_V_BotK"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)
client = Client()

def get_processed_links():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return f.read().splitlines()

def save_link(link):
    with open(DB_FILE, "a") as f: f.write(link + "\n")

def get_full_article_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        full_text = " ".join([p.get_text() for p in paragraphs])
        return full_text[:3500]
    except:
        return None

def rewrite_text_and_format(title, raw_body, link):
    prompt = f"""
    Write a news post for Telegram.
    Title: {title}
    Source text: {raw_body}
    
    Rules:
    1. Exactly 3 distinct paragraphs. Complete the story fully.
    2. First paragraph must be BOLD (⚡️ CATCHY HEADLINE).
    3. Use thematic emojis and stickers.
    4. Do not mention the original source website name.
    5. No cut-off sentences.
    6. Language: Russian.
    
    End with: [Читать полностью]({link})
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return f"**{title}**\n\nНовость уже в канале! Подробности по ссылке ниже.\n\n[Читать]({link})"

def fetch_news():
    query = "politics OR music OR influencers OR USA OR hollywood"
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&sortBy=publishedAt&pageSize=15&apiKey={NEWS_API_KEY}"
    
    try:
        articles = requests.get(url).json().get("articles", [])
    except: return

    processed = get_processed_links()
    posted = 0
    
    for article in articles:
        if posted >= 2: break
        link = article["url"]
        
        if link not in processed:
            title = article["title"]
            full_content = get_full_article_text(link)
            content_to_use = full_content if full_content and len(full_content) > 400 else article["description"]
            
            final_post = rewrite_text_and_format(title, content_to_use, link)
            img = article.get("urlToImage")
            
            try:
                if img and img.startswith("http"):
                    bot.send_photo(CHANNEL_ID, img, caption=final_post, parse_mode='Markdown')
                else:
                    bot.send_message(CHANNEL_ID, final_post, parse_mode='Markdown')
                
                save_link(link)
                posted += 1
                time.sleep(10)
            except:
                continue

if __name__ == "__main__":
    fetch_news()
