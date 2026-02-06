import hashlib
import json
import os

FILE_PATH = "posted.json"

def _load_hashes():
    if not os.path.exists(FILE_PATH):
        return set()
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return set(json.load(f))

def _save_hashes(hashes):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(list(hashes), f, ensure_ascii=False, indent=2)

def is_duplicate(url: str, title: str) -> bool:
    hashes = _load_hashes()
    raw = f"{url}{title}".encode("utf-8")
    article_hash = hashlib.sha256(raw).hexdigest()
    return article_hash in hashes

def mark_as_posted(url: str, title: str):
    hashes = _load_hashes()
    raw = f"{url}{title}".encode("utf-8")
    article_hash = hashlib.sha256(raw).hexdigest()
    hashes.add(article_hash)
    _save_hashes(hashes)