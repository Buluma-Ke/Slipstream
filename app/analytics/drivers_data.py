# app/analytics/drivers_data.py
import pandas as pd
from data.store import get_connection

def fetch_available_drivers(year: int) -> pd.DataFrame:
    """Fetches unique drivers stored in the DB for a given year."""
    if not year:
        return pd.DataFrame()

    con = get_connection(read_only=True)
    df = con.execute("""
        SELECT DISTINCT driver, full_name
        FROM race_results
        WHERE year = ?
        ORDER BY driver ASC
    """, [int(year)]).df()
    con.close()
    return df

def fetch_driver_season_results(year: int, driver_code: str) -> pd.DataFrame:
    """
    Fetches full season analytics results for a specific driver,
    dynamically applying a chronological round index using DENSE_RANK.
    """
    if not year or not driver_code:
        return pd.DataFrame()

    con = get_connection(read_only=True)
    df = con.execute("""
        WITH ranked_events AS (
            SELECT *,
                   DENSE_RANK() OVER (ORDER BY event_name) AS round_number
            FROM race_results
            WHERE year = ?
        )
        SELECT
            year,
            event_name AS EventName,
            round_number AS RoundNumber,
            driver AS Driver,
            full_name AS FullName,
            team AS Team,
            position AS Position,
            points AS Points,
            grid_position AS GridPosition,
            status AS Status
        FROM ranked_events
        WHERE driver = ?
        ORDER BY round_number ASC
    """, [int(year), str(driver_code)]).df()
    con.close()
    return df
