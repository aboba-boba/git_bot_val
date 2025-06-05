import time
import aiohttp
from config.settings import AGENT_API_URL, CACHE_TTL, logger

# Простой in-memory кэш
_cache = {
    "agents": None,
    "ts": 0.0,
}

async def fetch_agents():
    # I'll be back (api cache)
    now = time.time()
    if _cache["agents"] is not None and now - _cache["ts"] < CACHE_TTL:
        return _cache["agents"]

    logger.info("🛰 Запрашиваю список агентов…")
    async with aiohttp.ClientSession() as session:
        async with session.get(AGENT_API_URL, timeout=10) as resp:
            resp.raise_for_status()
            data = await resp.json()
            agents = data.get("data", [])
            _cache["agents"] = agents
            _cache["ts"] = now
            return agents

async def get_agent_info(name: str) -> str:
    #I'll find you, my pretty(agent finder))
    agents = await fetch_agents()
    search = name.lower()

    for a in agents:
        display = a.get("displayName", "")
        if search in display.lower():
            role = a.get("role", {}).get("displayName", "—")
            desc = a.get("description", "—")
            abilities = a.get("abilities", [])

            lines = [
                f"🎭 *{display}*",
                f"_{role}_",
                "",
                desc,
                "",
                "*Умения:*"
            ]
            emoji_map = {
                "Ability1": "E",
                "Ability2": "Q",
                "Grenade": "C",
                "Ultimate": "X"
            }
            for ab in abilities:
                slot = ab.get("slot", "")
                title = ab.get("displayName", "")
                txt = ab.get("description", "")
                icon = emoji_map.get(slot, "")
                lines.append(f"{icon} *{title}* — {txt}")

            return "\n".join(lines)

    raise ValueError(f"Не найден агент «{name}». Попробуйте другое имя.")

