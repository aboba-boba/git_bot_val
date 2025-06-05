import json
import os
from datetime import datetime

BASE = os.path.dirname(__file__)
FOLDER = os.path.join(BASE, "..", "storage")
os.makedirs(FOLDER, exist_ok=True)
FILE = os.path.join(FOLDER, 'favorites.json')

def _load() -> dict:
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def _save(data: dict):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_favorites(user_id: int) -> list[str]:
    data = _load()
    user_data = data.get(str(user_id), None)
    if isinstance(user_data, dict):
        return user_data.get("favorites", [])
    elif isinstance(user_data, list):
        return user_data
    else:
        return []

def add_favorite(user_id: int, agent: str) -> bool:
    data = _load()
    user_key = str(user_id)
    favorites = data.get(user_key, [])
    if agent not in favorites:
        favorites.append(agent)
        data[user_key] = favorites
        _save(data)
        return True
    return False

def remove_favorite(user_id: int, agent: str) -> bool:
    data = _load()
    user_key = str(user_id)
    favorites = data.get(user_key, [])
    if agent in favorites:
        favorites.remove(agent)
        data[user_key] = favorites
        _save(data)
        return True
    return False