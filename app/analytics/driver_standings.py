# app/analytics/driver_standings.py
import fastf1
import pandas as pd
from data.store import get_connection

def fetch_season_results(year: int) -> pd.DataFrame:
    """
    Checks local DB for race results first. Falls back to FastF1
    if local telemetry datasets are not loaded for the selected season.
    """
    year = int(year)

    # 1. Attempt to resolve via local data storage first
    try:
        con = get_connection(read_only=True)
        db_df = con.execute("""
            SELECT abbreviation, full_name, team_name, points, position, grid_position, status, round_number, event_name
            FROM race_results
            WHERE year = ?
        """, [year]).df()
        con.close()

        if not db_df.empty:
            # Rename columns to match existing downstream API properties seamlessly
            db_df.columns = ['Abbreviation', 'FullName', 'TeamName', 'Points', 'Position', 'GridPosition', 'Status', 'RoundNumber', 'EventName']
            return db_df
    except Exception as e:
        print(f"⚠️ Local DB standings query bypassed: {e}")

    # 2. Cache-First fallback path via FastF1 API
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    races = schedule[schedule['EventFormat'] != 'testing'].reset_index(drop=True)
    results_list = []

    for _, event in races.iterrows():
        try:
            session = fastf1.get_session(year, event['RoundNumber'], 'R')
            session.load(telemetry=False, weather=False, messages=False)
            res = session.results
            if res is None or len(res) == 0:
                continue
            res = res.copy()
            res['RoundNumber'] = event['RoundNumber']
            res['EventName'] = event['EventName']
            results_list.append(res)
        except Exception:
            continue

    return pd.concat(results_list, ignore_index=True) if results_list else pd.DataFrame()


def process_driver_metrics(all_results: pd.DataFrame):
    """Processes aggregated metrics, standings, wins, and round keys."""
    if all_results.empty:
        return None, None, []

    rounds = sorted(all_results['RoundNumber'].unique())

    # Aggregate points metrics
    standings = all_results.groupby(
        ['Abbreviation', 'FullName', 'TeamName']
    )['Points'].sum().reset_index().sort_values('Points', ascending=False)
    standings['Pos'] = range(1, len(standings) + 1)

    # Calculate round-level win tallies
    wins = all_results[all_results['Position'] == 1].groupby('Abbreviation').size()

    return standings, wins, rounds
