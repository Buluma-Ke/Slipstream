# run_ingestion.py
import store
from loader import get_session

def populate_season(year):
    print(f"🚀 Starting ingestion for the {year} season...")

    # 1. Initialize the DB structure (just in case)
    store.init_db()

    # 2. Get the season schedule
    import fastf1
    schedule = fastf1.get_event_schedule(year)

    # Filter for races that have already happened
    # (FastF1 'EventFormat' excludes testing; we check for completed races)
    races = schedule[schedule['EventFormat'] != 'testing']

    for _, event in races.iterrows():
        event_name = event['EventName']

        # Check if we already have this in our DB to save time/API calls
        if store.is_session_loaded(year, event_name, "R"):
            print(f"⏩ Skipping {event_name} - already in database.")
            continue

        try:
            print(f"🏁 Loading {event_name}...")
            # Use your loader.py to fetch and load the session
            session = get_session(year, event_name, "R")

            # Use your store.py to save the results and laps
            store.save_session_data(
                year=year,
                event_name=event_name,
                session_type="R",
                laps_df=session.laps,
                results_df=session.results
            )
        except Exception as e:
            print(f"❌ Failed to load {event_name}: {e}")

if __name__ == "__main__":
    # Run this for the 2025 season
    populate_season(2025)
