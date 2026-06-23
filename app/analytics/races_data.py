# app/analytics/races_data.py
import pandas as pd
from data.store import get_connection

class SimulatedSession:
    """Simulates the FastF1 session wrapper object for downstream layout components."""
    def __init__(self, event_name: str, year: int):
        self.event = {"EventName": event_name or f"Grand Prix {year}"}

def fetch_race_session_data(year: int, round_number: int) -> tuple[pd.DataFrame, pd.DataFrame, object]:
    """
    Queries local DB using your exact table structures and a dynamic DENSE_RANK
    to map integer requests to alphabetical event names.
    """
    if not year or not round_number:
        return pd.DataFrame(), pd.DataFrame(), None

    try:
        con = get_connection(read_only=True)

        # 1. Fetch from 'race_results'
        results_df = con.execute("""
            WITH ranked_results AS (
                SELECT *,
                       DENSE_RANK() OVER (ORDER BY event_name) AS dynamic_round
                FROM race_results
                WHERE year = ?
            )
            SELECT
                driver AS Abbreviation,
                team AS TeamName,
                position AS Position,
                points AS Points,
                grid_position AS GridPosition,
                status AS Status,
                event_name AS EventName
            FROM ranked_results
            WHERE dynamic_round = ?
        """, [int(year), int(round_number)]).df()

        # 2. Fetch from 'laps' (Filtering for Race session context and adding structural fallbacks)
        laps_df = con.execute("""
            WITH ranked_laps AS (
                SELECT *,
                       DENSE_RANK() OVER (ORDER BY event_name) AS dynamic_round
                FROM laps
                WHERE year = ? AND (session_type = 'Race' OR session_type = 'R')
            )
            SELECT
                driver AS Driver,
                team AS Team,
                lap_number AS LapNumber,
                lap_time_sec AS LapTimeSec,
                NULL AS PitInTime,      -- ⚡ Fallback: keeps your cleaning filter from crashing
                NULL AS PitOutTime,     -- ⚡ Fallback
                NULL AS Position,       -- ⚡ Fallback
                NULL AS SpeedST,        -- ⚡ Fallback
                event_name AS EventName
            FROM ranked_laps
            WHERE dynamic_round = ?
        """, [int(year), int(round_number)]).df()

        con.close()

        if laps_df.empty:
            return results_df, pd.DataFrame(), None

        # Resolve event name text from the database payload
        resolved_event_name = laps_df['EventName'].dropna().iloc[0] if 'EventName' in laps_df.columns and not laps_df['EventName'].dropna().empty else f"Round {round_number}"
        session_mock = SimulatedSession(resolved_event_name, year)

        laps_df = laps_df.dropna(subset=['LapTimeSec'])
        laps_df['LapTimeSec'] = laps_df['LapTimeSec'].astype(float)

        return results_df, laps_df, session_mock

    except Exception as e:
        print(f"❌ Backend Race DB Fetch Failure: {e}")
        return pd.DataFrame(), pd.DataFrame(), None


def process_clean_race_laps(laps: pd.DataFrame) -> pd.DataFrame:
    """
    Applies a robust median-based window filter to eliminate outlier lap times.
    """
    if laps.empty:
        return pd.DataFrame()

    median_lap = laps['LapTimeSec'].median()

    # Isolate active race runs: Filter out standard pace anomalies
    # Note: PitInTime fallback handles the missing schema column safely
    clean_laps = laps[
        (laps['LapTimeSec'] < median_lap * 1.15) &
        (laps['LapNumber'] > 1)
    ].copy()

    return clean_laps


def generate_fastest_laps_table(laps: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates absolute fastest lap times and joins driver team names.
    """
    if laps.empty or results.empty:
        return pd.DataFrame()

    fastest = laps.groupby('Driver')['LapTimeSec'].min().reset_index()
    fastest = fastest.sort_values('LapTimeSec').head(20)
    fastest['Pos'] = range(1, len(fastest) + 1)

    driver_team = results[['Abbreviation', 'TeamName']].copy()
    fastest = fastest.merge(driver_team, left_on='Driver', right_on='Abbreviation', how='left')

    return fastest
