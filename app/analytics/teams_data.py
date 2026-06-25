# app/analytics/teams_data.py

import pandas as pd
from data.store import get_connection

def fetch_available_teams(year: int) -> pd.DataFrame:
    """Fetches unique teams stored in the DB for a given year."""
    if not year:
        return pd.DataFrame()

    con = get_connection(read_only=True)
    df = con.execute("""
        SELECT DISTINCT team
        FROM race_results
        WHERE year = ?
        ORDER BY team ASC
    """, [int(year)]).df()
    con.close()
    return df

def fetch_team_season_results(year: int, team_name: str) -> pd.DataFrame:
    """
    Fetches full season analytics results for a specific team,
    aggregating individual driver rows to calculate collective team points per event.
    """
    if not year or not team_name:
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
            team AS Team,
            SUM(points) AS Points,
            GROUP_CONCAT(position, ', ') AS Positions,
            GROUP_CONCAT(grid_position, ', ') AS GridPositions
        FROM ranked_events
        WHERE team = ?
        GROUP BY year, event_name, round_number, team
        ORDER BY round_number ASC
    """, [int(year), str(team_name)]).df()
    con.close()
    return df
