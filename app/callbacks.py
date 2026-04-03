import pandas as pd
from dash import Input, Output, State, callback, no_update, html
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
        # Lowercase columns so all charts get consistent names
        laps.columns = [c.lower() for c in laps.columns]
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
        return (
            [html.Div('Fastest Lap', className='label'), html.Div('—', className='value')],
            [html.Div('Total Laps', className='label'), html.Div('—', className='value')],
            [html.Div('Drivers', className='label'), html.Div('—', className='value')],
            [html.Div('Fastest Team', className='label'), html.Div('—', className='value')],
        )
    from io import StringIO
    laps = pd.read_json(StringIO(laps_json), orient='split')
    fastest_idx = laps['laptimesec'].idxmin()
    fastest_driver = laps.loc[fastest_idx, 'driver']
    fastest_time = laps['laptimesec'].min()
    total_laps = len(laps)
    drivers = laps['driver'].nunique()
    fastest_team = laps.loc[fastest_idx, 'team']
    return (
        [html.Div('Fastest Lap', className='label'),
         html.Div(f'{fastest_driver} — {fastest_time:.3f}s', className='value')],
        [html.Div('Total Laps', className='label'),
         html.Div(str(total_laps), className='value')],
        [html.Div('Drivers', className='label'),
         html.Div(str(drivers), className='value')],
        [html.Div('Fastest Team', className='label'),
         html.Div(fastest_team, className='value')],
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



# --- 6. Lap time distribution chart ---
@callback(
    Output('chart-lap-dist', 'figure'),
    Input('store-laps', 'data'),
)
def update_lap_dist(laps_json):
    if not laps_json:
        return {}
    laps = pd.read_json(laps_json, orient='split')
    print("Columns:", laps.columns.tolist())
    from app.components.charts import make_lap_time_dist
    return make_lap_time_dist(laps)


# --- 7. Strategy strip chart ---
@callback(
    Output('chart-strategy', 'figure'),
    Input('store-laps', 'data'),
)
def update_strategy(laps_json):
    if not laps_json:
        return {}
    from io import StringIO
    from app.components.charts import make_strategy_strip
    laps = pd.read_json(StringIO(laps_json), orient='split')
    return make_strategy_strip(laps)


# --- 8. Populate delta driver dropdowns ---
@callback(
    Output('dd-delta-a', 'options'),
    Output('dd-delta-a', 'value'),
    Output('dd-delta-b', 'options'),
    Output('dd-delta-b', 'value'),
    Input('store-laps', 'data'),
)
def update_delta_dropdowns(laps_json):
    if not laps_json:
        return [], None, [], None
    from io import StringIO
    laps = pd.read_json(StringIO(laps_json), orient='split')
    drivers = sorted(laps['driver'].unique())
    opts = [{'label': d, 'value': d} for d in drivers]
    a = drivers[0] if len(drivers) > 0 else None
    b = drivers[1] if len(drivers) > 1 else None
    return opts, a, opts, b


# --- 9. Delta chart ---
@callback(
    Output('chart-delta', 'figure'),
    Input('store-laps', 'data'),
    Input('dd-delta-a', 'value'),
    Input('dd-delta-b', 'value'),
)
def update_delta(laps_json, driver_a, driver_b):
    if not laps_json or not driver_a or not driver_b or driver_a == driver_b:
        return {}
    from io import StringIO
    from app.components.charts import make_lap_delta
    laps = pd.read_json(StringIO(laps_json), orient='split')
    return make_lap_delta(laps, driver_a, driver_b)


# --- 10. Populate telemetry driver dropdown ---
@callback(
    Output('dd-tel-driver', 'options'),
    Output('dd-tel-driver', 'value'),
    Input('store-laps', 'data'),
)
def update_tel_driver(laps_json):
    if not laps_json:
        return [], None
    from io import StringIO
    laps = pd.read_json(StringIO(laps_json), orient='split')
    drivers = sorted(laps['driver'].unique())
    opts = [{'label': d, 'value': d} for d in drivers]
    return opts, drivers[0] if drivers else None


# --- 11. Populate telemetry lap dropdown ---
@callback(
    Output('dd-tel-lap', 'options'),
    Output('dd-tel-lap', 'value'),
    Input('store-laps', 'data'),
    Input('dd-tel-driver', 'value'),
)
def update_tel_laps(laps_json, driver):
    if not laps_json or not driver:
        return [], None
    from io import StringIO
    laps = pd.read_json(StringIO(laps_json), orient='split')
    driver_laps = sorted(laps[laps['driver'] == driver]['lapnumber'].unique())
    opts = [{'label': f'Lap {int(n)}', 'value': int(n)} for n in driver_laps]
    return opts, int(driver_laps[0]) if driver_laps else None


# --- 12. Telemetry chart ---
@callback(
    Output('chart-telemetry', 'figure'),
    Input('dd-tel-driver', 'value'),
    Input('dd-tel-lap', 'value'),
    State('dd-year', 'value'),
    State('dd-event', 'value'),
    State('dd-session', 'value'),
)
def update_telemetry(driver, lap_number, year, event, session_type):
    if not all([driver, lap_number, year, event, session_type]):
        return {}
    try:
        from app.components.charts import make_speed_trace
        session = get_session(year, event, session_type)
        lap = session.laps.pick_driver(driver).pick_lap(lap_number)
        tel = lap.get_car_data().add_distance()
        return make_speed_trace(tel, f'{driver} — Lap {lap_number}')
    except Exception as e:
        print(f'Telemetry error: {e}')
        return {}
    



# --- 13. Populate map driver dropdown ---
@callback(
    Output('dd-map-driver', 'options'),
    Output('dd-map-driver', 'value'),
    Input('store-laps', 'data'),
)
def update_map_driver(laps_json):
    if not laps_json:
        return [], None
    from io import StringIO
    laps = pd.read_json(StringIO(laps_json), orient='split')
    drivers = sorted(laps['driver'].unique())
    opts = [{'label': d, 'value': d} for d in drivers]
    return opts, drivers[0] if drivers else None


# --- 14. Populate map lap dropdown ---
@callback(
    Output('dd-map-lap', 'options'),
    Output('dd-map-lap', 'value'),
    Input('store-laps', 'data'),
    Input('dd-map-driver', 'value'),
)
def update_map_laps(laps_json, driver):
    if not laps_json or not driver:
        return [], None
    from io import StringIO
    laps = pd.read_json(StringIO(laps_json), orient='split')
    driver_laps = sorted(laps[laps['driver'] == driver]['lapnumber'].unique())
    opts = [{'label': f'Lap {int(n)}', 'value': int(n)} for n in driver_laps]
    return opts, int(driver_laps[0]) if driver_laps else None


# --- 15. Track map chart ---
@callback(
    Output('chart-map', 'figure'),
    Input('dd-map-driver', 'value'),
    Input('dd-map-lap', 'value'),
    State('dd-year', 'value'),
    State('dd-event', 'value'),
    State('dd-session', 'value'),
)
def update_map(driver, lap_number, year, event, session_type):
    if not all([driver, lap_number, year, event, session_type]):
        return {}
    try:
        from app.components.charts import make_track_map
        session = get_session(year, event, session_type)
        lap = session.laps.pick_driver(driver).pick_lap(lap_number)
        tel = lap.get_car_data().add_distance()
        pos = lap.get_pos_data()
        merged = tel.merge_channels(pos)
        return make_track_map(merged)
    except Exception as e:
        print(f'Map error: {e}')
        return {}
    

# --- Sidebar toggle ---
@callback(
    Output('sidebar', 'className'),
    Output('main-content', 'className'),
    Output('sidebar-toggle-icon', 'children'),
    Input('sidebar-toggle', 'n_clicks'),
    State('sidebar', 'className'),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks, current_class):
    if 'collapsed' in current_class:
        return 'sidebar expanded', 'main-content', '◀'
    return 'sidebar collapsed', 'main-content expanded', '▶'


# --- Page routing ---
@callback(
    Output('page-content', 'children'),
    Output('store-page', 'data'),
    [Input(f'nav-{page_id}', 'n_clicks')
     for page_id, _, _ in [
         ('home', '', ''), ('schedule', '', ''), ('standings', '', ''),
         ('races', '', ''), ('drivers', '', ''), ('teams', '', ''),
         ('telemetry', '', ''), ('predictions', '', ''),
     ]],
    prevent_initial_call=True,
)
def route_page(*args):
    from dash import ctx
    from app.pages import home, races, schedule, standings, drivers, teams, telemetry, predictions

    page_map = {
        'nav-home':        (home.layout(),        'home'),
        'nav-schedule':    (schedule.layout(),    'schedule'),
        'nav-standings':   (standings.layout(),   'standings'),
        'nav-races':       (races.layout(),       'races'),
        'nav-drivers':     (drivers.layout(),     'drivers'),
        'nav-teams':       (teams.layout(),       'teams'),
        'nav-telemetry':   (telemetry.layout(),   'telemetry'),
        'nav-predictions': (predictions.layout(), 'predictions'),
    }

    triggered = ctx.triggered_id
    if triggered in page_map:
        return page_map[triggered]
    return home.layout(), 'home'