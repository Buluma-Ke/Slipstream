# app/analytics/driver_standings.py
import pandas as pd
from data.store import get_connection

def fetch_season_results(year: int) -> pd.DataFrame:
    """
    Checks local DB for race results. Dynamically generates
    a chronological RoundNumber using a window function over event_name.
    """
    year = int(year)

    try:
        con = get_connection(read_only=True)

        # DENSE_RANK() dynamically forces a sequential order to track chart evolution
        db_df = con.execute("""
            WITH ordered_events AS (
                SELECT
                    driver AS abbreviation,
                    full_name,
                    team,
                    points,
                    position,
                    grid_position,
                    status,
                    event_name,
                    DENSE_RANK() OVER (ORDER BY event_name) AS generated_round
                FROM race_results
                WHERE year = ?
            )
            SELECT
                abbreviation,
                full_name,
                team,
                points,
                position,
                grid_position,
                status,
                generated_round,
                event_name
            FROM ordered_events
        """, [year]).df()
        con.close()

        if not db_df.empty:
            print(f"⚡ [DATABASE HIT] Loaded data rows for the {year} season.")
            # Map column outputs smoothly to the expected interface names
            db_df.columns = ['Abbreviation', 'FullName', 'TeamName', 'Points', 'Position', 'GridPosition', 'Status', 'RoundNumber', 'EventName']
            return db_df

    except Exception as e:
        print(f"❌ Database Query Failed: {e}")

    # Return empty DataFrame immediately if DB pull fails or has no rows
    return pd.DataFrame()


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
