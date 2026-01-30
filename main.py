import os
import telebot
import requests
import re
import random
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916" 
CHANNEL_ID = "@SUP_V_BotK"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def get_posted_data():
    if not os.path.exists(DB_FILE): return set()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())

def save_posted_data(link, title):
    clean_title = re.sub(r'[^\w\s]', '', title).lower().strip()
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(f"{link}\n{clean_title}\n")

def get_full_article(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']): s.decompose()
        
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text()) > 40]
        text = " ".join(paragraphs)
        
        # Вырезаем мусор и тех-инфу
        text = re.sub(r'(Copyright|©|Адрес для связи|info@|Выделите текст|Ошибка|Поиск по сайту).*', '', text, flags=re.IGNORECASE)
        return text[:2500]
    except:
        return None

def rewrite_text(title, content):
    prompt = (
        f"Ты — профессиональный редактор новостей. Сделай пост в стиле 'карточки'.\n\n"
        f"ТЕМА: {title}\n"
        f"ИНФО: {content}\n\n"
        f"СТРУКТУРА ПОСТА:\n"
        f"1. ⚡️ Жирный заголовок: отрази главную суть.\n\n"
        f"2. Короткий абзац (2 предложения): разъясни, что произошло.\n\n"
        f"3. Список ключевых цифр или фактов через буллиты (•).\n\n"
        f"4. Блок 'Главное для читателя': дай практический совет или вывод.\n\n"
        f"5. В конце добавь 3 тематических хештега.\n\n"
        f"ЗАПРЕТ: Не используй фразы 'в тексте говорится', 'коротко: важное обновление'. "
        f"Пиши только факты. Максимум 500 знаков. Закончи мысль полностью."
    )
    try:
        with DDGS() as ddgs:
            response = ddgs.chat(prompt, model='gpt-4o-mini')
            res = response.strip()
            # Убираем возможный префикс ИИ
            res = re.sub(r'^.*?новостной пост:|^.*?пересказ:', '', res, flags=re.IGNORECASE).strip()
            
            last_mark = max(res.rfind('.'), res.rfind('!'), res.rfind('?'))
            if last_mark != -1: res = res[:last_mark + 1]
            return res
    except:
        return None

def run():
    url = f"https://newsapi.org/v2/everything?q=(IT OR нейросети OR технологии OR выплаты OR законы)&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        articles = requests.get(url).json().get('articles', [])
    except: return

    posted_data = get_posted_data()
    random.shuffle(articles)

    for art in articles:
        link = art['url']
        title = art['title']
        clean_title = re.sub(r'[^\w\s]', '', title).lower().strip()
        
        if link in posted_data or clean_title in posted_data: continue
        
        raw_text = get_full_article(link)
        content = raw_text if (raw_text and len(raw_text) > 300) else art.get('description', "")
        
        if not content or "Copyright" in content: continue

        final_post = rewrite_text(title, content)
        
        if not final_post or len(final_post) < 150 or "обновление в сфере" in final_post:
            continue

        caption = f"{final_post}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if art.get('urlToImage'):
                bot.send_photo(CHANNEL_ID, art['urlToImage'], caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_data(link, title)
            break
        except: continue

if __name__ == "__main__":
    run()
