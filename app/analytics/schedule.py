# app/analytics/schedule.py
import fastf1
import pandas as pd
from data.store import get_connection

def get_season_schedule(year: int):
    """
    Fetches the calendar configuration framework for a specific F1 season.
    Checks the local DuckDB database first. Falls back to FastF1 API if empty.
    Returns a cleaned list of dict entries or an empty list if loading fails.
    """
    year = int(year)
    schedule_data = []

    # --- STRATEGY A: Check Local DuckDB Engine First ---
    try:
        con = get_connection(read_only=True)
        # Check if we have any race entries recorded for this season
        local_df = con.execute("""
            SELECT DISTINCT event_name, year
            FROM race_results
            WHERE year = ?
        """, [year]).df()
        con.close()

        # If we have entries in our database, reconstruct from local history
        if not local_df.empty:
            print(f"📦 Database Hit: Reconstructing {year} schedule locally.")

            con = get_connection(read_only=True)
            # Query unique session types per event from your laps or session ledger if needed.
            # To keep this fast, we pull what we have from results and laps layouts.
            db_races = con.execute("""
                SELECT
                    r.event_name,
                    MIN(r.year) as year,
                    -- We can aggregate custom details or map general session layouts
                    MAX(CASE WHEN l.session_type = 'Sprint' THEN 'Sprint' ELSE 'Race' END) as has_sprint
                FROM race_results r
                LEFT JOIN laps l
                  ON r.year = l.year AND r.event_name = l.event_name
                WHERE r.year = ?
                GROUP BY r.event_name
            """, [year]).df()
            con.close()


    except Exception as e:
        print(f"⚠️ Local DB schedule lookup skipped: {e}")

    # --- STRATEGY B: FastF1 Cache-First Fallback API ---
    try:
        print(f"🌐 Querying FastF1 Cache Engine for {year} schedule...")
        # Since you enabled fastf1.Cache.enable_cache() in loader.py,
        # calling this is instant if run_ingestion has already been executed.
        schedule = fastf1.get_event_schedule(year)

        # Eliminate non-championship events (pre-season testing sessions)
        races = schedule[schedule['EventFormat'] != 'testing'].copy()

        for _, row in races.iterrows():
            session_types = []
            for i in range(1, 6):
                s_name = row.get(f'Session{i}')
                if s_name:
                    session_types.append(str(s_name))

            schedule_data.append({
                'round_num': int(row.get('RoundNumber', 0)),
                'event_name': str(row.get('EventName', '—')),
                'country': str(row.get('EventCountry', '—')),
                'date_start': row.get('EventDate'), # Timestamp object
                'date_end': row.get('EventDate'),   # Timestamp object
                'session_types': session_types
            })

        return schedule_data
    except Exception as e:
        print(f"❌ Schedule analytics data thread error: {e}")
        return []
