import hashlib, json, os

FILE = "posted.json"

def _load():
    if not os.path.exists(FILE):
        return set()
    return set(json.load(open(FILE)))

def _save(data):
    json.dump(list(data), open(FILE, "w"), indent=2)

def is_duplicate(url, title):
    h = hashlib.sha256(f"{url}{title}".encode()).hexdigest()
    return h in _load()

def mark_posted(url, title):
    data = _load()
    data.add(hashlib.sha256(f"{url}{title}".encode()).hexdigest())
    _save(data)