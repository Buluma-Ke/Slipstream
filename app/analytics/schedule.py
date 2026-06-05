# app/analytics/schedule.py
import fastf1
import pandas as pd

def get_season_schedule(year: int):
    """
    Fetches the calendar configuration framework for a specific F1 season.
    Returns a cleaned list of dict entries or an empty list if loading fails.
    """
    try:
        year = int(year)
        # FastF1 uses local cached assets if run_ingestion has already warm-cached it
        schedule = fastf1.get_event_schedule(year)

        # Eliminate non-championship events (pre-season testing sessions)
        races = schedule[schedule['EventFormat'] != 'testing'].copy()

        schedule_data = []
        for _, row in races.iterrows():
            # Gather unique session types available for the weekend framework
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
