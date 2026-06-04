# app/db/store.py
import os
import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = Path("./data/f1.duckdb")

def get_connection(read_only=False):
    """
    Return a DuckDB connection.
    Use read_only=True inside Dash callbacks to prevent file-locking conflicts.
    """
    # Ensure the data directory directory exists safely
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH), read_only=read_only)


def init_db():
    """Initializes tables for laps, final race results, and loading logs."""
    con = get_connection(read_only=False)

    # 1. Procedural Laps Table
    con.execute("""
        CREATE TABLE IF NOT EXISTS laps (
            year             INTEGER,
            event_name       VARCHAR,
            session_type     VARCHAR,
            driver           VARCHAR,
            team             VARCHAR,
            lap_number       INTEGER,
            lap_time_sec     DOUBLE,
            s1_sec           DOUBLE,
            s2_sec           DOUBLE,
            s3_sec           DOUBLE,
            compound         VARCHAR,
            tyre_life        INTEGER,
            is_personal_best BOOLEAN,
            UNIQUE (year, event_name, session_type, driver, lap_number)
        )
    """)

    # 2. Race Results Table (Essential for Standings, Home, & Analytics)
    con.execute("""
        CREATE TABLE IF NOT EXISTS race_results (
            year          INTEGER,
            event_name    VARCHAR,
            driver        VARCHAR,
            full_name     VARCHAR,
            team          VARCHAR,
            position      INTEGER,
            points        DOUBLE,
            grid_position INTEGER,
            status        VARCHAR,
            time_seconds  DOUBLE,
            UNIQUE (year, event_name, driver)
        )
    """)

    # 3. Cache Directory Index Log
    con.execute("""
        CREATE TABLE IF NOT EXISTS sessions_loaded (
            year         INTEGER,
            event_name   VARCHAR,
            session_type VARCHAR,
            PRIMARY KEY (year, event_name, session_type)
        )
    """)
    con.close()
    print("Database structures verified and ready.")


def is_session_loaded(year, event_name, session_type):
    """Safely checks if a specific session layout is already present in cache."""
    con = get_connection(read_only=True)
    already = con.execute("""
        SELECT 1 FROM sessions_loaded
        WHERE year=? AND event_name=? AND session_type=?
    """, [year, event_name, session_type]).fetchone()
    con.close()
    return already is not None


def save_session_data(year, event_name, session_type, laps_df=None, results_df=None):
    """
    Saves a session's lap metrics and final results down to the local file engine.
    Safely wraps formatting transforms to isolate the interface.
    """
    if is_session_loaded(year, event_name, session_type):
        print(f"⏩ Already stored: {year} {event_name} {session_type}")
        return

    con = get_connection(read_only=False)

    try:
        # Step A: Parse and Append Laps data if available
        if laps_df is not None and not laps_df.empty:
            # Safe parsing transformations for timedelta to numeric floats
            lap_time_converted = (laps_df['LapTime'].dt.total_seconds()
                                  if 'LapTime' in laps_df.columns else laps_df.get('LapTimeSec'))

            insert_laps = pd.DataFrame({
                'year': int(year),
                'event_name': str(event_name),
                'session_type': str(session_type),
                'driver': laps_df['Driver'].astype(str),
                'team': laps_df['Team'].astype(str),
                'lap_number': laps_df['LapNumber'].astype(int),
                'lap_time_sec': pd.to_numeric(lap_time_converted, errors='coerce'),
                's1_sec': pd.to_numeric(laps_df['Sector1Time'].dt.total_seconds(), errors='coerce'),
                's2_sec': pd.to_numeric(laps_df['Sector2Time'].dt.total_seconds(), errors='coerce'),
                's3_sec': pd.to_numeric(laps_df['Sector3Time'].dt.total_seconds(), errors='coerce'),
                'compound': laps_df['Compound'].astype(str),
                'tyre_life': laps_df['TyreLife'].fillna(0).astype(int),
                'is_personal_best': laps_df['IsPersonalBest'].fillna(False).astype(bool),
            })
            con.execute("INSERT INTO laps SELECT * FROM insert_laps")

        # Step B: Parse and Append Results data if available (Crucial for Home Page/Standings)
        if results_df is not None and not results_df.empty:

            # Safe parsing transformations for race final time delta to float seconds
            res_time_converted = (
                results_df['Time'].dt.total_seconds()
                if 'Time' in results_df.columns and hasattr(results_df['Time'], 'dt')
                else pd.to_timedelta(results_df.get('Time')).dt.total_seconds()
            )

            insert_results = pd.DataFrame({
                'year': int(year),
                'event_name': str(event_name),
                'driver': results_df['Abbreviation'].astype(str),
                'full_name': results_df['FullName'].astype(str),
                'team': results_df['TeamName'].astype(str),
                'position': pd.to_numeric(results_df['Position'], errors='coerce').fillna(99).astype(int),
                'points': pd.to_numeric(results_df['Points'], errors='coerce').fillna(0.0).astype(float),
                'grid_position': pd.to_numeric(results_df['GridPosition'], errors='coerce').fillna(0).astype(int),
                'status': results_df['Status'].astype(str),
                'time_seconds': pd.to_numeric(res_time_converted, errors='coerce'),
            })
            con.execute("INSERT INTO race_results SELECT * FROM insert_results")

        # Step C: Log successful process completion inside track index
        con.execute("""
            INSERT INTO sessions_loaded (year, event_name, session_type)
            VALUES (?, ?, ?)
        """, [year, event_name, session_type])
        print(f"✅ Successfully written: {year} {event_name} ({session_type})")

    except Exception as e:
        print(f"❌ Transaction failure occurred during session insertion: {e}")
    finally:
        con.close()


def query_race_results(year=None, event_name=None):
    """Retrieves fast, read-only historical race outcome frameworks."""
    con = get_connection(read_only=True)
    clauses, params = ["1=1"], []

    if year:
        clauses.append("year = ?"), params.append(int(year))
    if event_name:
        clauses.append("event_name = ?"), params.append(str(event_name))

    df = con.execute(f"SELECT * FROM race_results WHERE {' AND '.join(clauses)}", params).df()
    con.close()
    return df


def query_laps(year=None, event_name=None, session_type=None, driver=None):
    """Queries structural lap historical arrays using lightweight file connection locks."""
    con = get_connection(read_only=True)
    clauses, params = ["1=1"], []

    if year:
        clauses.append("year = ?"), params.append(int(year))
    if event_name:
        clauses.append("event_name = ?"), params.append(str(event_name))
    if session_type:
        clauses.append("session_type = ?"), params.append(str(session_type))
    if driver:
        clauses.append("driver = ?"), params.append(str(driver))

    df = con.execute(f"SELECT * FROM laps WHERE {' AND '.join(clauses)}", params).df()
    con.close()
    return df
