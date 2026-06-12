# app/analytics/races_data.py
import pandas as pd
from data.store import get_connection

class SimulatedSession:
    """Simulates the FastF1 session wrapper object for downstream layout components."""
    def __init__(self, event_name: str, year: int):
        self.event = {"EventName": event_name or f"Grand Prix {year}"}

def fetch_race_session_data(year: int, round_number: int) -> tuple[pd.DataFrame, pd.DataFrame, object]:
    """
    Queries local DB for complete race results and individual lap data.
    Eliminates live API network latency.
    """
    if not year or not round_number:
        return pd.DataFrame(), pd.DataFrame(), None

    try:
        con = get_connection(read_only=True)

        # 1. Pull race results summary
        results_df = con.execute("""
            SELECT
                driver_code AS Abbreviation,
                team AS TeamName,
                position AS Position,
                points AS Points,
                grid_position AS GridPosition,
                status AS Status
            FROM race_results
            WHERE year = ? AND round_number = ?
        """, [int(year), int(round_number)]).df()

        # 2. Pull detailed lap times telemetry data
        laps_df = con.execute("""
            SELECT
                driver_code AS Driver,
                team AS Team,
                lap_number AS LapNumber,
                lap_time_sec AS LapTimeSec,
                pit_in_time AS PitInTime,
                pit_out_time AS PitOutTime,
                position AS Position,
                speed_st AS SpeedST,
                event_name AS EventName
            FROM lap_times
            WHERE year = ? AND round_number = ?
        """, [int(year), int(round_number)]).df()

        con.close()

        if laps_df.empty:
            return results_df, pd.DataFrame(), None

        # Resolve the event name context safely for the UI header card
        raw_event = laps_df['EventName'].dropna().iloc[0] if 'EventName' in laps_df.columns and not laps_df['EventName'].dropna().empty else f"Round {round_number}"
        session_mock = SimulatedSession(raw_event, year)

        # Force valid numeric lap times explicitly
        laps_df = laps_df.dropna(subset=['LapTimeSec'])
        laps_df['LapTimeSec'] = laps_df['LapTimeSec'].astype(float)

        return results_df, laps_df, session_mock

    except Exception as e:
        print(f"❌ Backend Race DB Fetch Failure: {e}")
        return pd.DataFrame(), pd.DataFrame(), None


def process_clean_race_laps(laps: pd.DataFrame) -> pd.DataFrame:
    """Applies a robust median-based window filter to eliminate outlier lap times."""
    if laps.empty:
        return pd.DataFrame()

    median_lap = laps['LapTimeSec'].median()

    # Isolate active race runs: Filter pit windows and yellow/red flag anomalies
    clean_laps = laps[
        laps['PitInTime'].isna() &
        (laps['LapTimeSec'] < median_lap * 1.15) &
        (laps['LapNumber'] > 1)
    ].copy()

    return clean_laps


def generate_fastest_laps_table(laps: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
    """Aggregates absolute fastest lap times and joins driver team names."""
    if laps.empty or results.empty:
        return pd.DataFrame()

    fastest = laps.groupby('Driver')['LapTimeSec'].min().reset_index()
    fastest = fastest.sort_values('LapTimeSec').head(20)
    fastest['Pos'] = range(1, len(fastest) + 1)

    driver_team = results[['Abbreviation', 'TeamName']].copy()
    fastest = fastest.merge(driver_team, left_on='Driver', right_on='Abbreviation', how='left')

    return fastest
