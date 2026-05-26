# app/analytics/home.py
import pandas as pd
from store import get_connection

def get_season_overview_stats(year: int) -> dict:
    """
    Calculates high-level season metrics directly from the local DuckDB cache.
    Returns a clean dictionary ready for Dash UI cards.
    """
    con = get_connection(read_only=True)

    # 1. Total unique races run so far
    total_races = con.execute("""
        SELECT COUNT(DISTINCT event_name)
        FROM race_results
        WHERE year = ?
    """, [year]).fetchone()[0]

    if total_races == 0:
        con.close()
        return {
            "total_races": 0,
            "driver_leader": "—",
            "driver_points": 0,
            "team_leader": "—",
            "team_points": 0,
            "most_wins_driver": "—",
            "most_wins_count": 0,
            "most_poles_driver": "—",
            "most_poles_count": 0
        }

    # 2. Top Driver Standings Leader
    driver_leader = con.execute("""
        SELECT driver, SUM(points) as total_pts
        FROM race_results
        WHERE year = ?
        GROUP BY driver
        ORDER BY total_pts DESC
        LIMIT 1
    """, [year]).fetchone()

    # 3. Top Constructor Standings Leader
    team_leader = con.execute("""
        SELECT team, SUM(points) as total_pts
        FROM race_results
        WHERE year = ?
        GROUP BY team
        ORDER BY total_pts DESC
        LIMIT 1
    """, [year]).fetchone()

    # 4. Driver with the most Grand Prix wins (Position = 1)
    most_wins = con.execute("""
        SELECT driver, COUNT(*) as win_count
        FROM race_results
        WHERE year = ? AND position = 1
        GROUP BY driver
        ORDER BY win_count DESC
        LIMIT 1
    """, [year]).fetchone()

    # 5. Driver with the most Pole Positions (GridPosition = 1 from laps or results)
    most_poles = con.execute("""
        SELECT driver, COUNT(*) as pole_count
        FROM race_results
        WHERE year = ? AND grid_position = 1
        GROUP BY driver
        ORDER BY pole_count DESC
        LIMIT 1
    """, [year]).fetchone()

    con.close()

    return {
        "total_races": total_races,
        "driver_leader": driver_leader[0] if driver_leader else "—",
        "driver_points": round(driver_leader[1], 1) if driver_leader else 0,
        "team_leader": team_leader[0] if team_leader else "—",
        "team_points": round(team_leader[1], 1) if team_leader else 0,
        "most_wins_driver": most_wins[0] if most_wins else "—",
        "most_wins_count": most_wins[1] if most_wins else 0,
        "most_poles_driver": most_poles[0] if most_poles else "—",
        "most_poles_count": most_poles[1] if most_poles else 0
    }


def get_season_pace_ranking(year: int) -> pd.DataFrame:
    """
    Computes an aggregated season-long pace ranking using median lap times
    across normal track conditions, returning a lightweight summary DataFrame.
    """
    con = get_connection(read_only=True)

    # Run a clean columnar aggregation across all cached laps for the season
    # We filter out slow laps (> 100 seconds is an easy threshold, or use median bounds)
    df_pace = con.execute("""
        SELECT
            driver,
            team,
            COUNT(lap_number) as total_laps_analyzed,
            ROUND(MEDIAN(lap_time_sec), 3) as median_lap_time
        FROM laps
        WHERE year = ? AND lap_time_sec IS NOT NULL AND lap_time_sec < 120
        GROUP BY driver, team
        ORDER BY median_lap_time ASC
    """, [year]).df()

    con.close()
    return df_pace
