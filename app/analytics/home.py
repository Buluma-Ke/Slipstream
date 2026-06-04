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

        # 4. Closest Finish Logic (Self-Join to compare P1 and P2)
        # This calculates the gap between P1 and P2 for each race and finds the minimum
        closest_finish = con.execute("""
            SELECT
                p1.event_name,
                (p2.time_seconds - p1.time_seconds) as gap
            FROM race_results p1
            JOIN race_results p2 ON p1.event_name = p2.event_name AND p1.year = p2.year
            WHERE p1.year = ?
              AND p1.position = 1
              AND p2.position = 2
              AND p1.time_seconds IS NOT NULL
              AND p2.time_seconds IS NOT NULL
            ORDER BY gap ASC
            LIMIT 1
        """, [year]).fetchone()

        # Extract values or defaults
        closest_event = closest_finish[0] if closest_finish else '—'
        closest_gap = f"{closest_finish[1]:.3f}s" if closest_finish else '—'

        return {
            'total_races': total_races,
            'driver_standings': driver_standings,
            'team_standings': team_standings,
            'champion': driver_standings.iloc[0].to_dict() if not driver_standings.empty else {},
            'constructor': team_standings.iloc[0].to_dict() if not team_standings.empty else {},
            'wins': most_wins or ('—', 0),
            'poles': most_poles or ('—', 0),
            'dnfs': most_dnfs or ('—', 0),
            'closest_gap': closest_gap,
            'closest_event': closest_event
        }
    finally:
        con.close()
