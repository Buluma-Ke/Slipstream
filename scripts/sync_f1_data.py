# scripts/sync_f1_data.py

import sys
import os
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

import fastf1
from data.store import save_session_data, is_session_loaded



def sync_season(year):
    print(f"🏁 Syncing Season {year}...")

    # 1. Get the race schedule
    schedule = fastf1.get_event_schedule(year)
    # Filter for completed races only
    races = schedule[schedule['EventFormat'] != 'testing']

    for _, event in races.iterrows():
        event_name = event['EventName']

        # 2. CHECK if we already have it (Optimization)
        if is_session_loaded(year, event_name, 'R'):
            print(f"⏩ Skipping {event_name} (Already in DB)")
            continue

        try:
            print(f"📥 Loading {event_name} from FastF1...")
            session = fastf1.get_session(year, event['RoundNumber'], 'R')

            # This loads from your local FastF1 cache folder automatically
            session.load(laps=True, telemetry=False)

            # 3. CALL YOUR STORE FUNCTION
            save_session_data(
                year=year,
                event_name=event_name,
                session_type='R',
                laps_df=session.laps,
                results_df=session.results
            )
        except Exception as e:
            print(f"⚠️ Error syncing {event_name}: {e}")

if __name__ == "__main__":
    sync_season(2025)
