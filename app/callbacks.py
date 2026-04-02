import pandas as pd
from dash import Input, Output, State, callback, no_update
from data.loader import get_session, get_laps
from data.store import save_laps, query_laps
import fastf1


# --- 1. Populate event dropdown when year changes ---
@callback(
    Output('dd-event', 'options'),
    Output('dd-event', 'value'),
    Input('dd-year', 'value'),
)
def update_events(year):
    schedule = fastf1.get_event_schedule(year)
    options = [
        {'label': row['EventName'], 'value': row['EventName']}
        for _, row in schedule.iterrows()
    ]
    first = options[0]['value'] if options else None
    return options, first


# --- 2. Load session on button click ---
@callback(
    Output('store-laps', 'data'),
    Output('session-status', 'children'),
    Input('btn-load', 'n_clicks'),
    State('dd-year', 'value'),
    State('dd-event', 'value'),
    State('dd-session', 'value'),
    prevent_initial_call=True,
)
def load_session(n_clicks, year, event, session_type):
    if not all([year, event, session_type]):
        return no_update, 'Please select year, event and session.'
    try:
        session = get_session(year, event, session_type)
        laps = get_laps(session)
        save_laps(laps, year, event, session_type)
        laps_json = laps.to_json(date_format='iso', orient='split')
        return laps_json, f'✅ Loaded {len(laps)} laps — {event} {year}'
    except Exception as e:
        return no_update, f'❌ Error: {e}'
    

# --- 3. Update stat cards ---
@callback(
    Output('stat-fastest', 'children'),
    Output('stat-laps', 'children'),
    Output('stat-drivers', 'children'),
    Output('stat-team', 'children'),
    Input('store-laps', 'data'),
)
def update_stats(laps_json):
    if not laps_json:
        return '—', '—', '—', '—'
    laps = pd.read_json(laps_json, orient='split')
    fastest_driver = laps.loc[laps['LapTimeSec'].idxmin(), 'Driver']
    fastest_time = laps['LapTimeSec'].min()
    total_laps = len(laps)
    drivers = laps['Driver'].nunique()
    fastest_team = laps.loc[laps['LapTimeSec'].idxmin(), 'Team']
    return (
        f"{fastest_driver} — {fastest_time:.3f}s",
        str(total_laps),
        str(drivers),
        fastest_team,
    )



# --- 4. Session confirmation banner ---
@callback(
    Output('session-confirm', 'children'),
    Output('session-confirm', 'is_open'),
    Input('store-laps', 'data'),
    State('dd-year', 'value'),
    State('dd-event', 'value'),
    State('dd-session', 'value'),
)
def confirm_session(laps_json, year, event, session_type):
    if not laps_json:
        return '', False
    laps = pd.read_json(laps_json, orient='split')
    return f'📌 {year} — {event} — {session_type} — {len(laps)} laps loaded', True


# --- 5. Show current selection as user picks ---
@callback(
    Output('selection-display', 'children'),
    Input('dd-year', 'value'),
    Input('dd-event', 'value'),
    Input('dd-session', 'value'),
)
def show_selection(year, event, session_type):
    parts = []
    if year:
        parts.append(str(year))
    if event:
        parts.append(event)
    if session_type:
        labels = {
            'R': 'Race', 'Q': 'Qualifying', 'S': 'Sprint',
            'SQ': 'Sprint Qualifying', 'FP1': 'FP1', 'FP2': 'FP2', 'FP3': 'FP3'
        }
        parts.append(labels.get(session_type, session_type))
    return '📌 ' + ' — '.join(parts) if parts else ''