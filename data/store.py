import duckdb
from pathlib import Path

DB_PATH = Path("./data/f1.duckdb")




def get_connection():
    """Return a DuckDB connection to the local database file."""
    return duckdb.connect(str(DB_PATH))



def init_db():
    """
    Create the core tables if they don't exist.
    Run this once before using any other function.

    Tables created:
        laps            — one row per lap per driver per session
        sessions_loaded — tracks which sessions have been persisted
    """
    con = get_connection()
    con.execute("""
        CREATE TABLE IF NOT EXISTS laps (
            year         INTEGER,
            event_name   VARCHAR,
            session_type VARCHAR,
            driver       VARCHAR,
            team         VARCHAR,
            lap_number   INTEGER,
            lap_time_sec DOUBLE,
            s1_sec       DOUBLE,
            s2_sec       DOUBLE,
            s3_sec       DOUBLE,
            compound     VARCHAR,
            tyre_life    INTEGER,
            is_personal_best BOOLEAN
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS sessions_loaded (
            year         INTEGER,
            event_name   VARCHAR,
            session_type VARCHAR,
            PRIMARY KEY (year, event_name, session_type)
        )
    """)
    con.close()
    print("Database ready.")




def save_laps(laps, year, event_name, session_type):
    """
    Persist a session's lap data to DuckDB.
    Skips silently if this session is already stored.

    Args:
        laps:         DataFrame returned by loader.get_laps()
        year:         Season year, e.g. 2023
        event_name:   Full event name, e.g. 'Bahrain Grand Prix'
        session_type: 'R', 'Q', 'SQ', 'S', 'FP1', 'FP2', 'FP3'
    """

    con = get_connection()

    # Check if we already have this session
    already = con.execute("""
        SELECT 1 FROM sessions_loaded
        WHERE year=? AND event_name=? AND session_type=?
    """, [year, event_name, session_type]).fetchone()

    if already:
        print(f"Already stored: {year} {event_name} {session_type}")
        con.close()
        return

    # Build a clean DataFrame to insert
    import pandas as pd
    insert_df = pd.DataFrame({
        'year': year,
        'event_name': event_name,
        'session_type': session_type,
        'driver': laps['Driver'],
        'team': laps['Team'],
        'lap_number': laps['LapNumber'],
        'lap_time_sec': laps['LapTimeSec'],
        's1_sec': laps['Sector1Time'].dt.total_seconds(),
        's2_sec': laps['Sector2Time'].dt.total_seconds(),
        's3_sec': laps['Sector3Time'].dt.total_seconds(),
        'compound': laps['Compound'],
        'tyre_life': laps['TyreLife'],
        'is_personal_best': laps['IsPersonalBest'],
    })

    con.execute("INSERT INTO laps SELECT * FROM insert_df")
    con.execute("""
        INSERT INTO sessions_loaded (year, event_name, session_type)
        VALUES (?, ?, ?)
    """, [year, event_name, session_type])

    con.close()
    print(f"Saved {len(insert_df)} laps for {year} {event_name} {session_type}")




def query_laps(year=None, event_name=None, session_type=None, driver=None):
    """
    Query lap data from DuckDB with optional filters.
    All parameters are optional — omit any to get broader results.

    Args:
        year:         Filter by season, e.g. 2023
        event_name:   Filter by event, e.g. 'Bahrain Grand Prix'
        session_type: Filter by session, e.g. 'R', 'Q', 'S', 'SQ', 'FP1', 'FP2', 'FP3'
        driver:       Filter by driver code, e.g. 'VER'

    Returns:
        pandas DataFrame of matching laps
    """
    con = get_connection()

    clauses = ["1=1"]
    params = []

    if year:
        clauses.append("year = ?")
        params.append(year)
    if event_name:
        clauses.append("event_name = ?")
        params.append(event_name)
    if session_type:
        clauses.append("session_type = ?")
        params.append(session_type)
    if driver:
        clauses.append("driver = ?")
        params.append(driver)

    where = " AND ".join(clauses)
    df = con.execute(f"SELECT * FROM laps WHERE {where}", params).df()
    con.close()
    return df




if __name__ == "__main__":
    init_db()

    # Load session from FastF1
    import sys
    sys.path.insert(0, '.')
    from data.loader import get_session, get_laps

    print("\nLoading session from FastF1...")
    session = get_session(2023, 'Bahrain', 'R')
    laps = get_laps(session)

    # Save to DuckDB
    print("\nSaving to DuckDB...")
    save_laps(laps, 2023, 'Bahrain Grand Prix', 'R')

    # Read back from DuckDB
    print("\nQuerying from DuckDB...")
    stored = query_laps(year=2023, event_name='Bahrain Grand Prix', session_type='R')
    print(f"Rows returned: {len(stored)}")
    print(stored[['driver', 'lap_number', 'lap_time_sec', 'compound']].head(10))