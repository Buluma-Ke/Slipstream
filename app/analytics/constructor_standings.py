# app/analytics/constructor_standings.py
import pandas as pd
from data.store import get_connection

def fetch_constructor_season_results(year: int) -> pd.DataFrame:
    """
    Queries local DB for race results. Dynamically generates
    a sequential RoundNumber using a DENSE_RANK() window function.
    """
    year = int(year)

    try:
        con = get_connection(read_only=True)
        db_df = con.execute("""
            WITH ordered_events AS (
                SELECT
                    team AS team_name,
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
                team_name,
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
            # Standardize columns to match downstream API properties seamlessly
            db_df.columns = ['TeamName', 'Points', 'Position', 'GridPosition', 'Status', 'RoundNumber', 'EventName']
            return db_df

    except Exception as e:
        print(f"❌ Constructor DB Query Failed: {e}")

    return pd.DataFrame()


def process_constructor_metrics(all_results: pd.DataFrame):
    """Processes aggregated metrics, standings tables, wins, and round keys."""
    if all_results.empty:
        return pd.DataFrame(), pd.Series(dtype=int), []

    rounds = sorted(all_results['RoundNumber'].unique())

    # Aggregate total point standings
    standings = all_results.groupby('TeamName')['Points'].sum().reset_index()
    standings = standings.sort_values('Points', ascending=False).reset_index(drop=True)
    standings['Pos'] = range(1, len(standings) + 1)

    # Calculate wins per team
    wins = all_results[all_results['Position'] == 1].groupby('TeamName').size()

    return standings, wins, rounds
