from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

def summarize(text: str, min_len=300, max_len=500):
    parser = PlaintextParser.from_string(
        text,
        Tokenizer("russian")
    )

    summarizer = TextRankSummarizer()
    sentences = summarizer(parser.document, 5)

    summary = " ".join(str(s) for s in sentences)

    if len(summary) > max_len:
        summary = summary[:max_len].rsplit(" ", 1)[0] + "…"

    if len(summary) < min_len:
        summary += " Подробности в источнике."

    return summary