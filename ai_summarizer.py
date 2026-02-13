import re

def summarize(text):
    if not text:
        return ""
    text = re.sub("<.*?>", "", text)
    text = text.replace("\n", " ").strip()
    return text[:200] + "..."