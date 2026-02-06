import random
import re

HOOKS = [
    "🔥 В музыкальной индустрии снова шум.",
    "👀 Фанаты активно обсуждают эту новость.",
    "🎵 Похоже, это станет громким событием.",
    "😱 Новость, мимо которой не пройти."
]

def summarize(text, min_len=300, max_len=500):

    text = re.sub(r"\s+", " ", text).strip()

    sentences = re.split(r'(?<=[.!?]) +', text)

    summary = ""
    for s in sentences:
        if len(summary) + len(s) <= max_len:
            summary += s + " "
        if len(summary) >= min_len:
            break

    if not summary:
        summary = text[:max_len]

    hook = random.choice(HOOKS)
    return f"{hook}\n\n{summary.strip()}…"