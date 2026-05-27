# app/analytics/home.py
import pandas as pd
from data.store import get_connection

def get_homepage_data(year):
    con = get_connection(read_only=True)
    year = int(year)

    try:
        # 1. Basic Counts
        total_races = con.execute("SELECT COUNT(DISTINCT event_name) FROM race_results WHERE year=?", [year]).fetchone()[0]

        if total_races == 0:
            return None

        # 2. Standings & Champions
        driver_standings = con.execute("""
            SELECT driver as Abbreviation, full_name as FullName, team as TeamName, SUM(points) as Points
            FROM race_results WHERE year=? GROUP BY 1, 2, 3 ORDER BY Points DESC
        """, [year]).df()

        team_standings = con.execute("""
            SELECT team as TeamName, SUM(points) as Points
            FROM race_results WHERE year=? GROUP BY 1 ORDER BY Points DESC
        """, [year]).df()

        # 3. Facts (Wins, Poles, DNFs)
        most_wins = con.execute("""
            SELECT driver, COUNT(*) as count FROM race_results
            WHERE year=? AND position=1 GROUP BY 1 ORDER BY count DESC LIMIT 1
        """, [year]).fetchone()

        most_poles = con.execute("""
            SELECT driver, COUNT(*) as count FROM race_results
            WHERE year=? AND grid_position=1 GROUP BY 1 ORDER BY count DESC LIMIT 1
        """, [year]).fetchone()

        most_dnfs = con.execute("""
            SELECT driver, COUNT(*) as count FROM race_results
            WHERE year=? AND status NOT IN ('Finished', '+1 Lap', '+2 Laps')
            GROUP BY 1 ORDER BY count DESC LIMIT 1
        """, [year]).fetchone()

        return {
            'total_races': total_races,
            'driver_standings': driver_standings,
            'team_standings': team_standings,
            'champion': driver_standings.iloc[0].to_dict() if not driver_standings.empty else {},
            'constructor': team_standings.iloc[0].to_dict() if not team_standings.empty else {},
            'wins': most_wins or ('—', 0),
            'poles': most_poles or ('—', 0),
            'dnfs': most_dnfs or ('—', 0)
        }
    finally:
        con.close()
