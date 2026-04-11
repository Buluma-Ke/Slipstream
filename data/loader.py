import fastf1
from pathlib import Path

# Tell FastF1 where to save downloaded sessions
CACHE_DIR = Path("./data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))


def get_session(year, event, session_type="R"):
    # Fetch -> load -> return
    session = fastf1.get_session(year, event, session_type)
    session.load()

    return session


def get_laps(session):
    """
    Return cleaned lap data from a session.
    Converts timedelta columns to seconds and removes laps with no recorded time.

    Args:
        session: A loaded FastF1 session object

    Returns:
        pandas DataFrame of cleaned laps
    """
    laps = session.laps.copy()
    laps = laps.dropna(subset=['LapTime'])
    laps['LapTimeSec'] = laps['LapTime'].dt.total_seconds()
    return laps