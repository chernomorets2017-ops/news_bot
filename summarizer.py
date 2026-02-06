import random
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

HOOKS = [
    "🔥 В индустрии снова шум.",
    "🎵 Фанаты уже обсуждают.",
    "😱 Это обсуждают все.",
    "👀 Кажется, нас ждёт хит."
]

def summarize(text, max_len=500):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    sentences = summarizer(parser.document, 4)

    summary = " ".join(str(s) for s in sentences)
    summary = summary[:max_len].rsplit(" ", 1)[0]

    hook = random.choice(HOOKS)
    return f"{hook}\n\n{summary}…"