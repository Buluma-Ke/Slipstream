import fastf1
from pathlib import Path

# Tell FastF1 where to save downloaded sessions
CACHE_DIR = Path("./data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))


def get_session(year, event, session_type="R"):
    session = fastf1.get_session(year, event, session_type)
    session.load()
    return session