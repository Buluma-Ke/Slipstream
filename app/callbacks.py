import fastf1
import pandas as pd
from data.loader import get_session, get_laps
from data.store import save_laps, query_laps
from dash.exceptions import PreventUpdate
from dash import Input, Output, State, callback, no_update, html, ALL



TEAM_COLORS = {
    'Red Bull Racing': '#3671C6',
    'Ferrari': '#E8002D',
    'Mercedes': '#27F4D2',
    'McLaren': '#FF8000',
    'Aston Martin': '#229971',
    'Alpine': '#FF87BC',
    'Williams': '#64C4FF',
    'RB': '#6692FF',
    'Kick Sauber': '#52E252',
    'Haas F1 Team': '#B6BABD',
    'Toro Rosso':  '#6692FF',
    'AlphaTauri':  '#6692FF',
    'RB':          '#6692FF',
    'Alfa Romeo':  '#52E252',
    'Racing Point': '#229971',
    'Force India':  '#229971',
    'Renault':  '#FF87BC',
    'Visa Cash App RB': '#6692FF',
    'Visa Cash App RB Formula One Team': '#6692FF',
    'RB Formula One Team': '#6692FF',
}

TEAM_LOGOS = {
    'Red Bull Racing':  'rbr-normalized-logo',
    'Ferrari':          'ferrari-normalized-logo',
    'Mercedes':         '2026-mercedes-normalized-logo',
    'McLaren':          'mclaren-normalized-logo',
    'Aston Martin':     'aston-martin-normalized-logo',
    'Alpine':           'alpine-normalized-logo',
    'Williams':         '2026-williams-normalized-logo',
    'RB':               'rb-normalized-logo',
    'Kick Sauber':      'kick-sauber-normalized-logo',
    'Haas F1 Team':     'haas-normalized-logo',
    'Audi':             'audi-normalized-logo',
    'Cadillac':         'cadillac-normalized-logo',
    'Toro Rosso':  'rb-normalized-logo',
    'AlphaTauri':  'rb-normalized-logo',
    'RB':          'rb-normalized-logo',
    'Alfa Romeo':  'kick-sauber-normalized-logo',
    'Racing Point': 'aston-martin-normalized-logo',
    'Force India':  'aston-martin-normalized-logo',
    'Renault':  'alpine-normalized-logo',
    'Visa Cash App RB': 'rb-normalized-logo',
    'Visa Cash App RB Formula One Team': 'rb-normalized-logo',
    'RB Formula One Team': 'rb-normalized-logo',
}


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
    from io import StringIO
    laps = pd.read_json(StringIO(laps_json), orient='split')
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
    from io import StringIO
    from app.components.charts import make_lap_time_dist
    laps = pd.read_json(StringIO(laps_json), orient='split')
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
    Output('sidebar-toggle-icon', 'icon'),
    Input('sidebar-toggle', 'n_clicks'),
    State('sidebar', 'className'),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks, current_class):
    if 'collapsed' in current_class:
        return 'sidebar expanded', 'main-content', 'tabler:chevrons-left'
    return 'sidebar collapsed', 'main-content expanded', 'tabler:chevrons-right'



# --- Page routing ---
@callback(
    Output('page-content', 'children'),
    Output('store-page', 'data'),
    [Input(f'nav-{page_id}', 'n_clicks')
     for page_id, _, _ in [
         ('home', '', ''), ('schedule', '', ''), ('driver-standings', '', ''),
         ('constructor-standings', '', ''), ('races', '', ''), ('drivers', '', ''), 
         ('teams', '', ''), ('telemetry', '', ''), ('predictions', '', ''),
     ]],
    prevent_initial_call=True,
)
def route_page(*args):
    from dash import ctx
    from app.pages import (home, races, schedule, standings, 
                           drivers, teams, telemetry, predictions, 
                           driver_standings, constructor_standings)

    page_map = {
        'nav-home':                     (home.layout(),                     'home'),
        'nav-schedule':                 (schedule.layout(),                 'schedule'),
        'nav-driver-standings':         (driver_standings.layout(),         'driver-standings'),
        'nav-constructor-standings':    (constructor_standings.layout(),    'constructor-standings'),
        'nav-races':                    (races.layout(),                    'races'),
        'nav-drivers':                  (drivers.layout(),                  'drivers'),
        'nav-teams':                    (teams.layout(),                    'teams'),
        'nav-telemetry':                (telemetry.layout(),                'telemetry'),
        'nav-predictions':              (predictions.layout(),              'predictions'),
    }

    triggered = ctx.triggered_id
    if triggered in page_map:
        return page_map[triggered]
    return home.layout(), 'home'


# --- Home page ---
@callback(
    Output('home-stat-champion', 'children'),
    Output('home-stat-champion-pts', 'children'),
    Output('home-stat-constructor', 'children'),
    Output('home-stat-constructor-pts', 'children'),
    Output('home-stat-races', 'children'),
    Output('home-fact-mostwins', 'children'),
    Output('home-fact-mostwins-sub', 'children'),
    Output('home-fact-poles', 'children'),
    Output('home-fact-poles-sub', 'children'),
    Output('home-fact-closest', 'children'),
    Output('home-fact-closest-sub', 'children'),
    Output('home-fact-dnf', 'children'),
    Output('home-fact-dnf-sub', 'children'),
    Output('home-drivers-table', 'children'),
    Output('home-constructors-table', 'children'),
    Input('home-store-year', 'data'),
)



def update_home(year):
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        races = schedule[schedule['EventFormat'] != 'testing']
        total_races = len(races)

        results_list = []

        for _, event in races.iterrows():
            try:
                session = fastf1.get_session(year, event['RoundNumber'], 'R')
                # Only load results — no laps, no telemetry, no weather
                session.load(
                    laps=False,
                    telemetry=False,
                    weather=False,
                    messages=False,
                )
                res = session.results
                if res is None or len(res) == 0:
                    continue
                res = res.copy()
                res['EventName'] = event['EventName']
                results_list.append(res)
            except Exception:
                continue

        if not results_list:
            return ('—',) * 15 

        all_results = pd.concat(results_list, ignore_index=True)

        # Champion
        driver_pts = all_results.groupby('Abbreviation')['Points'].sum().sort_values(ascending=False)
        champion = driver_pts.index[0] if len(driver_pts) > 0 else '—'
        champion_pts = int(driver_pts.iloc[0]) if len(driver_pts) > 0 else 0

        # Constructor
        team_pts = all_results.groupby('TeamName')['Points'].sum().sort_values(ascending=False)
        constructor = team_pts.index[0] if len(team_pts) > 0 else '—'
        constructor_pts = int(team_pts.iloc[0]) if len(team_pts) > 0 else 0

        # Most wins
        wins = all_results[all_results['Position'] == 1].groupby(
            'Abbreviation').size().sort_values(ascending=False)
        most_wins_driver = wins.index[0] if len(wins) > 0 else '—'
        most_wins_count = int(wins.iloc[0]) if len(wins) > 0 else 0

        # Poles — from results GridPosition == 1
        poles = all_results[all_results['GridPosition'] == 1].groupby(
            'Abbreviation').size().sort_values(ascending=False)
        most_poles = poles.index[0] if len(poles) > 0 else '—'
        most_poles_count = int(poles.iloc[0]) if len(poles) > 0 else 0

        # Closest finish
        closest_gap = None
        closest_event = '—'
        for res_df in results_list:
            p1 = res_df[res_df['Position'] == 1]
            p2 = res_df[res_df['Position'] == 2]
            if len(p1) > 0 and len(p2) > 0:
                t1 = p1.iloc[0].get('Time')
                t2 = p2.iloc[0].get('Time')
                if pd.notna(t1) and pd.notna(t2):
                    gap = abs(t2.total_seconds() - t1.total_seconds()) \
                        if hasattr(t1, 'total_seconds') else None
                    if gap and (closest_gap is None or gap < closest_gap):
                        closest_gap = gap
                        closest_event = res_df.iloc[0]['EventName']

        closest_str = f'{closest_gap:.3f}s' if closest_gap else '—'

        # DNFs
        dnfs = all_results[all_results['Status'].str.contains(
            'DNF|Retired|Accident|Engine|Mechanical', case=False, na=False)]
        dnf_by_driver = dnfs.groupby('Abbreviation').size().sort_values(ascending=False)
        most_dnf = dnf_by_driver.index[0] if len(dnf_by_driver) > 0 else '—'
        most_dnf_count = int(dnf_by_driver.iloc[0]) if len(dnf_by_driver) > 0 else 0

        # Driver championship table
        driver_standings = all_results.groupby(
            ['Abbreviation', 'FullName', 'TeamName']
        )['Points'].sum().reset_index().sort_values('Points', ascending=False)
        driver_standings['Pos'] = range(1, len(driver_standings) + 1)

        driver_rows = []
        for _, row in driver_standings.iterrows():
            team_color = TEAM_COLORS.get(row['TeamName'], '#444')
            logo_file = TEAM_LOGOS.get(row['TeamName'], None)
            pos = int(row['Pos'])
            driver_rows.append(
                html.Tr([
                    html.Td(str(pos), className='pos'),
                    html.Td(
                        html.Img(
                            src=f'/assets/logos/{logo_file}.avif',
                            style={'height': '16px', 'width': '28px',
                                'objectFit': 'contain'},
                        ) if logo_file else html.Div(
                            style={'width': '4px', 'height': '100%',
                                'background': team_color}
                        ),
                        style={'width': '32px', 'padding': '0 4px'},
                    ),
                    html.Td(row['Abbreviation'], className='driver-abbr'),
                    html.Td(row['FullName'], className='driver-name'),
                    html.Td(f"{int(row['Points'])}", className='pts'),
                ], className='p1' if pos == 1 else '')
            )
 

        drivers_table = html.Table([
            html.Thead(html.Tr([
                html.Th('POS'), html.Th(''),
                html.Th('DRV'), html.Th('NAME'), html.Th('PTS'),
            ])),
            html.Tbody(driver_rows),
        ], className='champ-table')

        # Constructor championship table
        constructor_standings = all_results.groupby(
            'TeamName'
        )['Points'].sum().reset_index().sort_values('Points', ascending=False)
        constructor_standings['Pos'] = range(1, len(constructor_standings) + 1)

        constructor_rows = []
        for _, row in constructor_standings.iterrows():
            team_color = TEAM_COLORS.get(row['TeamName'], '#444')
            logo_file = TEAM_LOGOS.get(row['TeamName'], None)
            pos = int(row['Pos'])
            constructor_rows.append(
                html.Tr([
                    html.Td(str(pos), className='pos'),
                    html.Td(
                        html.Img(
                            src=f'/assets/logos/{logo_file}.avif',
                            style={'height': '16px', 'width': '28px',
                                'objectFit': 'contain'},
                        ) if logo_file else html.Div(
                            style={'width': '4px', 'height': '100%',
                                'background': team_color}
                        ),
                        style={'width': '32px', 'padding': '0 4px'},
                    ),
                    html.Td(row['TeamName']),
                    html.Td(f"{int(row['Points'])}", className='pts'),
                ], className='p1' if pos == 1 else '')
            )

        constructors_table = html.Table([
            html.Thead(html.Tr([
                html.Th('POS'), html.Th(''),
                html.Th('TEAM'), html.Th('PTS'),
            ])),
            html.Tbody(constructor_rows),
        ], className='champ-table')

        return (
            champion,
            f'{champion_pts} pts',
            constructor,
            f'{constructor_pts} pts',
            str(total_races),
            str(most_wins_count),
            most_wins_driver,
            str(most_poles_count),
            most_poles,
            closest_str,
            closest_event,
            str(most_dnf_count),
            most_dnf,
            drivers_table,
            constructors_table,
        )

    except Exception as e:
        print(f'Home error: {e}')
        return ('—',) * 15 
    

# --- Home year pill toggle ---
@callback(
    Output('year-pill-dropdown', 'style', allow_duplicate=True),
    Output('year-pill-overlay', 'style', allow_duplicate=True),
    Input('year-pill-toggle', 'n_clicks'),
    State('year-pill-dropdown', 'style'),
    prevent_initial_call=True,
)
def toggle_year_dropdown(n_clicks, current_style):
    if isinstance(current_style, dict) and current_style.get('display') == 'none':
        return {'display': 'block'}, {'display': 'block'}
    return {'display': 'none'}, {'display': 'none'}


# --- Home year pill select ---
@callback(
    Output('home-store-year', 'data'),
    Output('pill-year-display', 'children'),
    Output('year-pill-dropdown', 'style', allow_duplicate=True),
    Input({'type': 'year-pill', 'index': ALL}, 'n_clicks'),
    State({'type': 'year-pill', 'index': ALL}, 'id'),
    prevent_initial_call=True,
)
def select_year(n_clicks, ids):
    from dash import ctx
    triggered = ctx.triggered_id
    if not triggered:
        return 2025, '2025', {'display': 'none'}
    selected = triggered['index']
    return selected, str(selected), {'display': 'none'}

# --- Close dropdown on outside click ---
@callback(
    Output('year-pill-dropdown', 'style', allow_duplicate=True),
    Output('year-pill-overlay', 'style'),
    Input('year-pill-overlay', 'n_clicks'),
    prevent_initial_call=True,
)
def close_on_outside(n_clicks):
    return {'display': 'none'}, {'display': 'none'}


# ── Schedule page ─────────────────────────────────────────────────────────────
@callback(
    Output('schedule-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('schedule-year-overlay', 'style', allow_duplicate=True),
    Input('schedule-year-pill-toggle', 'n_clicks'),
    State('schedule-year-pill-dropdown', 'style'),
    prevent_initial_call=True,
)
def toggle_schedule_year(n_clicks, current_style):
    if isinstance(current_style, dict) and current_style.get('display') == 'none':
        return {'display': 'block'}, {'display': 'block'}
    return {'display': 'none'}, {'display': 'none'}


@callback(
    Output('schedule-store-year', 'data'),
    Output('schedule-pill-year-display', 'children'),
    Output('schedule-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('schedule-year-overlay', 'style', allow_duplicate=True),
    Input({'type': 'schedule-year-pill', 'index': ALL}, 'n_clicks'),
    State({'type': 'schedule-year-pill', 'index': ALL}, 'id'),
    prevent_initial_call=True,
)
def select_schedule_year(n_clicks, ids):
    from dash import ctx
    triggered = ctx.triggered_id
    if not triggered:
        return 2025, '2025', {'display': 'none'}, {'display': 'none'}
    selected = triggered['index']
    return selected, str(selected), {'display': 'none'}, {'display': 'none'}


@callback(
    Output('schedule-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('schedule-year-overlay', 'style', allow_duplicate=True),
    Input('schedule-year-overlay', 'n_clicks'),
    prevent_initial_call=True,
)
def close_schedule_dropdown(n_clicks):
    return {'display': 'none'}, {'display': 'none'}


@callback(
    Output('schedule-cards', 'children'),
    Input('schedule-store-year', 'data'),
)
def update_schedule(year):
    from app.pages.schedule import make_race_card
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventFormat'] != 'testing']
        cards = []
        for _, event in schedule.iterrows():
            session_types = [
                event.get('Session1', ''),
                event.get('Session2', ''),
                event.get('Session3', ''),
                event.get('Session4', ''),
                event.get('Session5', ''),
            ]
            card = make_race_card(
                round_num=event['RoundNumber'],
                event_name=event['EventName'],
                country=event['Country'],
                date_start=event['Session1Date'],
                date_end=event['Session5Date'],
                session_types=session_types,
                year=year,
            )
            cards.append(card)
        return cards
    except Exception as e:
        print(f'Schedule error: {e}')
        return [html.Div(f'Error loading schedule: {e}')]

@callback(
    Output('store-page', 'data', allow_duplicate=True),
    Output('page-content', 'children', allow_duplicate=True),
    Input({'type': 'race-card', 'year': ALL, 'event': ALL}, 'n_clicks'),
    State({'type': 'race-card', 'year': ALL, 'event': ALL}, 'id'),
    prevent_initial_call=True,
)
def race_card_click(n_clicks, ids):
    from dash import ctx
    from app.pages import races
    triggered = ctx.triggered_id
    if not triggered or not any(n for n in n_clicks if n):
        return no_update, no_update
    return 'races', races.layout()


# ── Driver standings page ─────────────────────────────────────────────────────
@callback(
    Output('drv-standings-year-dropdown', 'style', allow_duplicate=True),
    Output('drv-standings-year-overlay', 'style', allow_duplicate=True),
    Input('drv-standings-year-toggle', 'n_clicks'),
    State('drv-standings-year-dropdown', 'style'),
    prevent_initial_call=True,
)
def toggle_drv_standings_year(n_clicks, current_style):
    if isinstance(current_style, dict) and current_style.get('display') == 'none':
        return {'display': 'block'}, {'display': 'block'}
    return {'display': 'none'}, {'display': 'none'}


@callback(
    Output('drv-standings-store-year', 'data'),
    Output('drv-standings-pill-year', 'children'),
    Output('drv-standings-year-dropdown', 'style', allow_duplicate=True),
    Output('drv-standings-year-overlay', 'style', allow_duplicate=True),
    Input({'type': 'drv-standings-year-pill', 'index': ALL}, 'n_clicks'),
    State({'type': 'drv-standings-year-pill', 'index': ALL}, 'id'),
    prevent_initial_call=True,
)
def select_drv_standings_year(n_clicks, ids):

    from dash import ctx

    triggered = ctx.triggered_id
    if not triggered:
        return 2025, '2025', {'display': 'none'}, {'display': 'none'}
    selected = triggered['index']
    return selected, str(selected), {'display': 'none'}, {'display': 'none'}


@callback(
    Output('drv-standings-year-dropdown', 'style', allow_duplicate=True),
    Output('drv-standings-year-overlay', 'style', allow_duplicate=True),
    Input('drv-standings-year-overlay', 'n_clicks'),
    prevent_initial_call=True,
)
def close_drv_standings_dropdown(n_clicks):
    return {'display': 'none'}, {'display': 'none'}


@callback(
    Output('drv-standings-content', 'children'),
    Output('drv-points-evolution', 'figure'),
    Output('drv-ranking-evolution', 'figure'),
    Output('drv-stats-chart', 'figure'),
    Output('drv-points-distribution', 'figure'),
    Input('drv-standings-store-year', 'data'),
)
def update_driver_standings_all(year):
    import fastf1
    import pandas as pd
    import plotly.graph_objects as go

    TRANSPARENT = dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FBF9E4', family='Titillium Web'),
    )
    AXIS = dict(
        gridcolor='rgba(0,0,0,0)',
        title='',
        showline=False,
        zeroline=False,
        tickfont=dict(color='#444'),
    )
    empty = go.Figure().update_layout(**TRANSPARENT)

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        races = schedule[schedule['EventFormat'] != 'testing'].reset_index(drop=True)
        results_list = []

        for _, event in races.iterrows():
            try:
                session = fastf1.get_session(year, event['RoundNumber'], 'R')
                session.load(telemetry=False, weather=False, messages=False)
                res = session.results
                if res is None or len(res) == 0:
                    continue
                res = res.copy()
                res['RoundNumber'] = event['RoundNumber']
                res['EventName'] = event['EventName']
                results_list.append(res)
            except Exception:
                continue

        if not results_list:
            err = html.Div('No data.', className='standings-empty')
            return err, empty, empty, empty, empty

        all_results = pd.concat(results_list, ignore_index=True)
        rounds = sorted(all_results['RoundNumber'].unique())

        # ── Driver standings table ──
        driver_standings = all_results.groupby(
            ['Abbreviation', 'FullName', 'TeamName']
        )['Points'].sum().reset_index().sort_values('Points', ascending=False)
        driver_standings['Pos'] = range(1, len(driver_standings) + 1)
        wins = all_results[all_results['Position'] == 1]\
            .groupby('Abbreviation').size()

        rows = []
        for _, row in driver_standings.iterrows():
            logo_file = TEAM_LOGOS.get(row['TeamName'], None)
            team_color = TEAM_COLORS.get(row['TeamName'], '#444')
            pos = int(row['Pos'])
            w = wins.get(row['Abbreviation'], 0)
            rows.append(html.Tr([
                html.Td(str(pos), className='pos'),
                html.Td(
                    html.Img(src=f'/assets/logos/{logo_file}.avif',
                             style={'height': '16px', 'width': '28px',
                                    'objectFit': 'contain'})
                    if logo_file else html.Div(
                        style={'width': '4px', 'background': team_color}),
                    style={'width': '36px', 'padding': '0 4px'},
                ),
                html.Td(row['Abbreviation'], className='driver-abbr'),
                html.Td(row['FullName'], className='driver-name'),
                html.Td(str(int(w)), className='driver-name',
                        style={'textAlign': 'center'}),
                html.Td(f"{int(row['Points'])}", className='pts'),
            ], className='p1' if pos == 1 else ''))


        # ── Hero card ──
        leader = driver_standings.iloc[0]
        leader_team = leader['TeamName']
        leader_color = TEAM_COLORS.get(leader_team, '#444')
        leader_logo = TEAM_LOGOS.get(leader_team, None)

        hero = html.Div([
            html.Div([
                html.Div(f'{year} Championship Leader',
                         style={'fontSize': '0.6rem', 'color': '#888',
                                'letterSpacing': '0.15em',
                                'textTransform': 'uppercase',
                                'fontFamily': 'Titillium Web, sans-serif',
                                'marginBottom': '8px'}),
                html.Div(leader['FullName'].split()[-1],
                         style={'fontFamily': 'Titillium Web, sans-serif',
                                'fontSize': '2rem', 'fontWeight': '900',
                                'color': leader_color, 'lineHeight': '1'}),
                html.Div(f"{int(leader['Points'])} pts",
                         style={'fontSize': '0.7rem', 'color': '#888',
                                'fontFamily': 'Titillium Web, sans-serif',
                                'marginTop': '4px'}),
            ], style={'flex': '1'}),
            html.Div(
                html.Img(src=f'/assets/logos/{leader_logo}.avif',
                         style={'height': '32px', 'objectFit': 'contain'})
                if leader_logo else html.Div(),
                style={'display': 'flex', 'alignItems': 'center'},
            ),
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'background': f'linear-gradient(135deg, rgba(0,0,0,0.8), {leader_color}22)',
            'border': f'1px solid {leader_color}44',
            'borderLeft': f'3px solid {leader_color}',
            'borderRadius': '6px',
            'padding': '14px 16px',
            'marginBottom': '16px',
           
        })

        # ── Table ──
        table = html.Div([
            hero,
            html.Table([
                html.Thead(html.Tr([
                    html.Th('POS'), html.Th(''),
                    html.Th('DRV'), html.Th('NAME'),
                    html.Th('WINS', style={'textAlign': 'center'}),
                    html.Th('PTS'),
                ])),
                html.Tbody(rows),
            ], className='champ-table standings-full-table'),
        ])

        drivers = driver_standings['Abbreviation'].tolist()

        # ── Points evolution ──
        fig1 = go.Figure()
        for drv in drivers:
            drv_data = all_results[all_results['Abbreviation'] == drv]\
                .sort_values('RoundNumber')
            team = drv_data.iloc[0]['TeamName'] if len(drv_data) > 0 else ''
            color = TEAM_COLORS.get(team, '#444')
            cumpts = drv_data.set_index('RoundNumber')['Points']\
                .reindex(rounds).fillna(0).cumsum()
            fig1.add_trace(go.Scatter(
                x=list(cumpts.index), y=list(cumpts.values),
                name=drv, line=dict(color=color, width=1.5),
                mode='lines+markers', marker=dict(size=4),
            ))
        fig1.update_layout(
            **TRANSPARENT,
            autosize=True,
            title=dict(text='Driver Standings Evolution', font=dict(color='#444', size=13)),
            xaxis=AXIS | dict(
                range=[1, 24],          # Force the view to end exactly at 24
                autorange=False,         # Stop Plotly from adding extra padding
                showgrid=False,
                # 'constrained' ensures the axis line matches the data range
                constrain='domain'
            ),
            yaxis=AXIS | dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=True, zerolinecolor='white'),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=20),
        )

        # ── Ranking evolution ──
        fig2 = go.Figure()

        valid_drivers = set(driver_standings['Abbreviation'])

        for drv in drivers:
            drv_data = all_results[all_results['Abbreviation'] == drv]
            team = drv_data.iloc[0]['TeamName'] if len(drv_data) > 0 else ''
            color = TEAM_COLORS.get(team, '#444')

            rankings = []

            for r in rounds:
                up_to = all_results[all_results['RoundNumber'] <= r]

                pts = (
                    up_to.groupby('Abbreviation')['Points']
                    .sum()
                    .loc[lambda x: x.index.isin(valid_drivers)]
                    .sort_values(ascending=False)
                )
                rank = list(pts.index).index(drv) + 1 \
                    if drv in pts.index else None
                
                if drv in pts.index:
                    rank = list(pts.index).index(drv) + 1
                elif rankings:
                    rank = rankings[-1]  # 👈 carry previous rank forward
                else:
                    rank = None

                rankings.append(rank)

            # Add lead-in (flat start)
            x_vals = [rounds[0] - 0.5] + rounds
            y_vals = [rankings[0]] + rankings

            fig2.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                name=drv,
                line=dict(color=color, width=1.5, shape='spline', smoothing=0.9),
                mode='lines+markers',
                marker=dict(size=2),
            ))

            # Driver label on right
            final_rank = rankings[-1] if rankings else None
            if final_rank:
                fig2.add_annotation(
                    x=rounds[-1], y=final_rank, text=drv,
                    xanchor='left', showarrow=False,
                    font=dict(color=color, size=9,
                              family='Titillium Web'),
                    xshift=6,
                )

        actual_max = len(valid_drivers)


        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FBF9E4', family='Titillium Web'),
            autosize=True,
            title=dict(text='Driver Ranking Evolution', font=dict(color='#444', size=13)),

            xaxis=dict(
                gridcolor='rgba(0,0,0,0)',
                title='',
                showline=False,
                zeroline=False,
                tickfont=dict(color='#444'),
                tickvals=rounds,
                range=[rounds[0] - 1, rounds[-1]],
            ),
            yaxis=AXIS | dict(
                title='',
                showline=False,
                tickfont=dict(color='#444'),
                # Keep your custom range and tick logic
                dtick=1,
                range=[actual_max, 1],
                tickvals=list(range(1, actual_max + 1)),
                # New "Ghost" Grid lines
                showgrid=True, 
                gridcolor='rgba(255, 255, 255, 0.05)', 
                gridwidth=1,
                zeroline=True,
                zerolinecolor='rgba(255, 255, 255, 0.1)'
            ),
            showlegend=False,
            margin=dict(l=40, r=60, t=40, b=20),
        )


        # ── Stats ──
        podiums = all_results[all_results['Position'] <= 3]\
            .groupby('Abbreviation').size()
        points_finishes = all_results[all_results['Points'] > 0]\
            .groupby('Abbreviation').size()
        
        poles = all_results[all_results['GridPosition'] == 1]\
            .groupby('Abbreviation').size()

        dnfs = all_results[all_results['Status'].str.contains(
            'DNF|Retired|Accident|Engine|Mechanical|Disqualified|DNS',
            case=False, na=False)].groupby('Abbreviation').size()

        fig3 = go.Figure()

        # Wins - Gold
        fig3.add_trace(go.Bar(
            name='Wins', x=drivers,
            y=[wins.get(d, 0) for d in drivers],
            marker=dict(color='#6C5FA7', line=dict(color='#6C5FA7', width=1)), 
        ))

        # Podiums - Blue
        fig3.add_trace(go.Bar(
            name='Podiums', x=drivers,
            y=[podiums.get(d, 0) for d in drivers],
            marker=dict(color='#6B3779', line=dict(color='#6B3779', width=1)),
        ))

        # Finish in points - Silver
        fig3.add_trace(go.Bar(
            name='Finish in points', x=drivers,
            y=[points_finishes.get(d, 0) for d in drivers],
            marker=dict(color='#B24968', line=dict(color='#B24968', width=1))
        ))

        # Pole positions - Purple
        fig3.add_trace(go.Bar(
            name='Pole positions', x=drivers,
            y=[poles.get(d, 0) for d in drivers],
            marker=dict(color='#b33dc6', line=dict(color='#b33dc6', width=1))
        ))

        # DNF/DNS/DSQ - Red
        fig3.add_trace(go.Bar(
            name='DNF/DNS/DSQ', x=drivers,
            y=[-dnfs.get(d, 0) for d in drivers],
            marker=dict(color='#FA8573', line=dict(color='#FA8573', width=1))
        ))

        fig3.update_layout(
            **TRANSPARENT,
            autosize=True,
            title=dict(text='Season Statistics', font=dict(color='#444', size=13)),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            # Using your standard AXIS dict (no lines/borders)
            xaxis=AXIS, 
            yaxis=AXIS | dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=True, zerolinecolor='rgba(255, 255, 255, 0.1)'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(0,0,0,0)',
                font=dict(color='#444', size=10)
            ),
            margin=dict(l=40, r=40, t=60, b=20),
        )


        # ── Points distribution ──
        fig4 = go.Figure()

        for _, event in races.iterrows():
            event_results = all_results[all_results['RoundNumber'] == event['RoundNumber']]\
                .sort_values('Position')
            event_name = event['EventName'].replace(' Grand Prix', '')
            flag = ''

            for _, driver_row in event_results.iterrows():
                if driver_row['Points'] <= 0:
                    continue
                team = driver_row['TeamName']
                color = TEAM_COLORS.get(team, '#444')
                fig4.add_trace(go.Bar(
                    name=driver_row['Abbreviation'],
                    y=[event_name],
                    x=[driver_row['Points']],
                    orientation='h',
                    marker=dict(color=color, line=dict(color=color, width=1)),
                    showlegend=False,
                    hovertemplate=f"{driver_row['Abbreviation']} — {int(driver_row['Points'])} pts<extra></extra>",
                ))

        fig4.update_layout(
            **TRANSPARENT,
            autosize=True,
            title=dict(text='Points Distribution', font=dict(color='#444', size=13)),
            barmode='stack',
            xaxis=dict(
                gridcolor='rgba(0,0,0,0)',
                title='',
                showline=False,
                zeroline=False,
                tickfont=dict(color='#444'),
            ),
            yaxis=dict(
                gridcolor='rgba(0,0,0,0)',
                title='',
                showline=False,
                zeroline=False,
                tickfont=dict(color='#444', size=10),
                autorange='reversed',
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            height=600,
)

        return table, fig1, fig2, fig3, fig4

    except Exception as e:
        print(f'Driver standings error: {e}')
        err = html.Div(f'Error: {e}', className='standings-empty')
        return err, empty, empty, empty, empty


# ── Constructor standings page ────────────────────────────────────────────────
@callback(
    Output('con-standings-year-dropdown', 'style', allow_duplicate=True),
    Output('con-standings-year-overlay', 'style', allow_duplicate=True),
    Input('con-standings-year-toggle', 'n_clicks'),
    State('con-standings-year-dropdown', 'style'),
    prevent_initial_call=True,
)
def toggle_con_standings_year(n_clicks, current_style):
    if isinstance(current_style, dict) and current_style.get('display') == 'none':
        return {'display': 'block'}, {'display': 'block'}
    return {'display': 'none'}, {'display': 'none'}


@callback(
    Output('con-standings-store-year', 'data'),
    Output('con-standings-pill-year', 'children'),
    Output('con-standings-year-dropdown', 'style', allow_duplicate=True),
    Output('con-standings-year-overlay', 'style', allow_duplicate=True),
    Input({'type': 'con-standings-year-pill', 'index': ALL}, 'n_clicks'),
    State({'type': 'con-standings-year-pill', 'index': ALL}, 'id'),
    prevent_initial_call=True,
)
def select_con_standings_year(n_clicks, ids):

    from dash import ctx

    triggered = ctx.triggered_id
    if not triggered:
        return 2025, '2025', {'display': 'none'}, {'display': 'none'}
    selected = triggered['index']
    return selected, str(selected), {'display': 'none'}, {'display': 'none'}


@callback(
    Output('con-standings-year-dropdown', 'style', allow_duplicate=True),
    Output('con-standings-year-overlay', 'style', allow_duplicate=True),
    Input('con-standings-year-overlay', 'n_clicks'),
    prevent_initial_call=True,
)
def close_con_standings_dropdown(n_clicks):
    return {'display': 'none'}, {'display': 'none'}

@callback(
    Output('con-standings-content', 'children'),
    Output('const-points-evolution', 'figure'),
    Output('const-ranking-evolution', 'figure'),
    Output('const-stats-chart', 'figure'),
    Output('const-points-distribution', 'figure'),
    Input('con-standings-store-year', 'data'),
)
def update_constructor_standings(year):

    import fastf1
    import pandas as pd
    import plotly.graph_objects as go

    TRANSPARENT = dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FBF9E4', family='Titillium Web'),
    )
    AXIS = dict(
        gridcolor='rgba(0,0,0,0)',
        title='',
        showline=False,
        zeroline=False,
        tickfont=dict(color='#444'),
    )
    empty = go.Figure().update_layout(**TRANSPARENT)

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        races = schedule[schedule['EventFormat'] != 'testing'].reset_index(drop=True)
        results_list = []

        for _, event in races.iterrows():
            try:
                session = fastf1.get_session(year, event['RoundNumber'], 'R')
                session.load(telemetry=False, weather=False, messages=False)
                res = session.results
                if res is None or len(res) == 0:
                    continue
                res = res.copy()
                res['RoundNumber'] = event['RoundNumber']
                res['EventName'] = event['EventName']
                results_list.append(res)
            except Exception:
                continue

        if not results_list:
            err = html.Div('No data available.', className='standings-empty')
            return err, empty, empty, empty, []

        all_results = pd.concat(results_list, ignore_index=True)
        rounds = sorted(all_results['RoundNumber'].unique())

        # ── Constructor standings table ──
        constructor_standings = all_results.groupby(
            'TeamName'
        )['Points'].sum().reset_index().sort_values('Points', ascending=False)
        constructor_standings['Pos'] = range(1, len(constructor_standings) + 1)

        wins = all_results[all_results['Position'] == 1]\
            .groupby('TeamName').size()

        rows = []
        for _, row in constructor_standings.iterrows():
            logo_file = TEAM_LOGOS.get(row['TeamName'], None)
            team_color = TEAM_COLORS.get(row['TeamName'], '#444')
            pos = int(row['Pos'])
            w = wins.get(row['TeamName'], 0)
            rows.append(html.Tr([
                html.Td(str(pos), className='pos'),
                html.Td(
                    html.Img(src=f'/assets/logos/{logo_file}.avif',
                             style={'height': '16px', 'width': '28px',
                                    'objectFit': 'contain'})
                    if logo_file else html.Div(
                        style={'width': '4px', 'background': team_color}),
                    style={'width': '36px', 'padding': '0 4px'},
                ),
                html.Td(row['TeamName']),
                html.Td(str(int(w)), className='driver-name',
                        style={'textAlign': 'center'}),
                html.Td(f"{int(row['Points'])}", className='pts'),
            ], className='p1' if pos == 1 else ''))

        # ── Hero card ──
        leader = constructor_standings.iloc[0]
        leader_team = leader['TeamName']
        leader_color = TEAM_COLORS.get(leader_team, '#444')
        leader_logo = TEAM_LOGOS.get(leader_team, None)

        hero = html.Div([
            html.Div([
                html.Div(f'{year} Constructors Champion',
                         style={'fontSize': '0.6rem', 'color': '#888',
                                'letterSpacing': '0.15em',
                                'textTransform': 'uppercase',
                                'fontFamily': 'Titillium Web, sans-serif',
                                'marginBottom': '8px'}),
                html.Div(leader_team,
                         style={'fontFamily': 'Titillium Web, sans-serif',
                                'fontSize': '2rem', 'fontWeight': '900',
                                'color': leader_color, 'lineHeight': '1'}),
                html.Div(f"{int(leader['Points'])} pts",
                         style={'fontSize': '0.7rem', 'color': '#888',
                                'fontFamily': 'Titillium Web, sans-serif',
                                'marginTop': '4px'}),
            ], style={'flex': '1'}),
            html.Div(
                html.Img(src=f'/assets/logos/{leader_logo}.avif',
                         style={'height': '32px', 'objectFit': 'contain'})
                if leader_logo else html.Div(),
                style={'display': 'flex', 'alignItems': 'center'},
            ),
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'background': f'linear-gradient(135deg, rgba(0,0,0,0.8), {leader_color}22)',
            'border': f'1px solid {leader_color}44',
            'borderLeft': f'3px solid {leader_color}',
            'borderRadius': '6px',
            'padding': '14px 16px',
            'marginBottom': '16px',
        })

        # ── Table ──
        table = html.Div([
            hero,
            html.Table([
                html.Thead(html.Tr([
                    html.Th('POS'), html.Th(''),
                    html.Th('TEAM'),
                    html.Th('WINS', style={'textAlign': 'center'}),
                    html.Th('PTS'),
                ])),
                html.Tbody(rows),
            ], className='champ-table standings-full-table'),
        ])

        constructors = constructor_standings['TeamName'].tolist()

        # ── Points evolution ──
        fig1 = go.Figure()
        for team in constructors:
            team_data = all_results[all_results['TeamName'] == team]\
                .groupby('RoundNumber')['Points'].sum()
            color = TEAM_COLORS.get(team, '#444')
            cumpts = team_data.reindex(rounds).fillna(0).cumsum()
            fig1.add_trace(go.Scatter(
                x=list(cumpts.index), y=list(cumpts.values),
                name=team, line=dict(color=color, width=1.5),
                mode='lines+markers', marker=dict(size=4),
            ))
        fig1.update_layout(
            **TRANSPARENT,
            autosize=True,
            title=dict(text='Constructor Standings Evolution', font=dict(color='#444', size=13)),
            xaxis=AXIS | dict(
                range=[1, 24],
                autorange=False,
                showgrid=False,
                constrain='domain',
            ),
            yaxis=AXIS | dict(
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.05)',
                zeroline=True,
                zerolinecolor='white',
            ),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=20),
        )

        # ── Ranking evolution ──
        fig2 = go.Figure()
        valid_constructors = set(constructor_standings['TeamName'])

        for team in constructors:
            color = TEAM_COLORS.get(team, '#444')
            rankings = []

            for r in rounds:
                up_to = all_results[all_results['RoundNumber'] <= r]
                pts = (
                    up_to.groupby('TeamName')['Points']
                    .sum()
                    .loc[lambda x: x.index.isin(valid_constructors)]
                    .sort_values(ascending=False)
                )
                if team in pts.index:
                    rank = list(pts.index).index(team) + 1
                elif rankings:
                    rank = rankings[-1]
                else:
                    rank = None
                rankings.append(rank)

            x_vals = [rounds[0] - 0.5] + rounds
            y_vals = [rankings[0]] + rankings

            fig2.add_trace(go.Scatter(
                x=x_vals, y=y_vals,
                name=team,
                line=dict(color=color, width=1.5, shape='spline', smoothing=0.9),
                mode='lines+markers',
                marker=dict(size=2),
            ))

            final_rank = rankings[-1] if rankings else None
            if final_rank:
                # Shorten long team names for the label
                short_name = team.split()[-1] if len(team) > 12 else team
                fig2.add_annotation(
                    x=rounds[-1], y=final_rank, text=short_name,
                    xanchor='left', showarrow=False,
                    font=dict(color=color, size=9, family='Titillium Web'),
                    xshift=6,
                )

        actual_max = len(valid_constructors)
        fig2.update_layout(
            **TRANSPARENT,
            autosize=True,
            title=dict(text='Constructor Ranking Evolution', font=dict(color='#444', size=13)),
            xaxis=AXIS | dict(
                tickvals=rounds,
                range=[rounds[0] - 1, rounds[-1]],
            ),
            yaxis=AXIS | dict(
                dtick=1,
                range=[actual_max, 1],
                tickvals=list(range(1, actual_max + 1)),
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.05)',
                gridwidth=1,
                zeroline=True,
                zerolinecolor='rgba(255, 255, 255, 0.1)',
            ),
            showlegend=False,
            margin=dict(l=40, r=80, t=40, b=20),
        )

        # ── Stats ──
        podiums = all_results[all_results['Position'] <= 3]\
            .groupby('TeamName').size()
        points_finishes = all_results[all_results['Points'] > 0]\
            .groupby('TeamName').size()
        poles = all_results[all_results['GridPosition'] == 1]\
            .groupby('TeamName').size()
        dnfs = all_results[all_results['Status'].str.contains(
            'DNF|Retired|Accident|Engine|Mechanical|Disqualified|DNS',
            case=False, na=False)].groupby('TeamName').size()

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name='Wins', x=constructors,
            y=[wins.get(t, 0) for t in constructors],
            marker=dict(color='#6C5FA7', line=dict(color='#6C5FA7', width=1)),
        ))
        fig3.add_trace(go.Bar(
            name='Podiums', x=constructors,
            y=[podiums.get(t, 0) for t in constructors],
            marker=dict(color='#6B3779', line=dict(color='#6B3779', width=1)),
        ))
        fig3.add_trace(go.Bar(
            name='Finish in points', x=constructors,
            y=[points_finishes.get(t, 0) for t in constructors],
            marker=dict(color='#B24968', line=dict(color='#B24968', width=1)),
        ))
        fig3.add_trace(go.Bar(
            name='Pole positions', x=constructors,
            y=[poles.get(t, 0) for t in constructors],
            marker=dict(color='#b33dc6', line=dict(color='#b33dc6', width=1)),
        ))
        fig3.add_trace(go.Bar(
            name='DNF/DNS/DSQ', x=constructors,
            y=[-dnfs.get(t, 0) for t in constructors],
            marker=dict(color='#FA8573', line=dict(color='#FA8573', width=1)),
        ))
        fig3.update_layout(
            **TRANSPARENT,
            autosize=True,
            title=dict(text='Season Statistics', font=dict(color='#444', size=13)),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            xaxis=AXIS | dict(
                tickvals=list(range(len(constructors))),
                ticktext=[''] * len(constructors),  # hide text labels
            ),
            yaxis=AXIS | dict(
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.05)',
                zeroline=True,
                zerolinecolor='rgba(255, 255, 255, 0.1)',
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(0,0,0,0)',
                font=dict(color='#444', size=10),
            ),
            margin=dict(l=40, r=40, t=60, b=60),
        )

        # Place logos along x-axis
        images = []
        for i, team in enumerate(constructors):
            logo_file = TEAM_LOGOS.get(team)
            if logo_file:
                images.append(dict(
                    source=f'/assets/logos/{logo_file}.avif',
                    xref='x', yref='paper',
                    x=i, y=-0.02,
                    sizex=0.6, sizey=0.08,
                    xanchor='center', yanchor='top',
                    layer='above',
                ))

        fig3.update_layout(
                images=images,
                margin=dict(l=40, r=40, t=60, b=80),  # keep enough room for logos
        )

        # ── Points distribution (stacked bar per race, one bar per team) ──
        fig4 = go.Figure()
        for _, event in races.iterrows():
            event_results = all_results[all_results['RoundNumber'] == event['RoundNumber']]
            team_pts = event_results.groupby('TeamName')['Points'].sum()
            event_name = event['EventName'].replace(' Grand Prix', '')

            for team, pts in team_pts.items():
                if pts <= 0:
                    continue
                color = TEAM_COLORS.get(team, '#444')
                fig4.add_trace(go.Bar(
                    name=team,
                    y=[event_name],
                    x=[pts],
                    orientation='h',
                    marker=dict(color=color, line=dict(color=color, width=1)),
                    showlegend=False,
                    hovertemplate=f"{team} — {int(pts)} pts<extra></extra>",
                ))

        fig4.update_layout(
            **TRANSPARENT,
            autosize=True,
            title=dict(text='Points Distribution', font=dict(color='#444', size=13)),
            barmode='stack',
            xaxis=AXIS,
            yaxis=dict(
                gridcolor='rgba(0,0,0,0)',
                title='',
                showline=False,
                zeroline=False,
                tickfont=dict(color='#444', size=10),
                autorange='reversed',
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            height=600,
        )


        return table, fig1, fig2, fig3, fig4 #points_dist_child

    except Exception as e:
        print(f'Constructor standings error: {e}')
        err = html.Div(f'Error: {e}', className='standings-empty')
        return err, empty, empty, empty, []
    



# ──────────────────── Races page ────────────────────

    
@callback(
    Output('races-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('races-year-overlay', 'style', allow_duplicate=True),
    Input('races-year-pill-toggle', 'n_clicks'),
    State('races-year-pill-dropdown', 'style'),
    prevent_initial_call=True,
)
def toggle_races_year(n_clicks, current_style):
    if isinstance(current_style, dict) and current_style.get('display') == 'none':
        return {'display': 'block'}, {'display': 'block'}
    return {'display': 'none'}, {'display': 'none'}


@callback(
    Output('races-store-year', 'data'),
    Output('races-pill-year-display', 'children'),
    Output('races-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('races-year-overlay', 'style', allow_duplicate=True),
    Input({'type': 'races-year-pill', 'index': ALL}, 'n_clicks'),
    State({'type': 'races-year-pill', 'index': ALL}, 'id'),
    prevent_initial_call=True,
)
def select_races_year(n_clicks, ids):
    from dash import ctx
    triggered = ctx.triggered_id
    if not triggered:
        return 2025, '2025', {'display': 'none'}, {'display': 'none'}
    selected = triggered['index']
    return selected, str(selected), {'display': 'none'}, {'display': 'none'}


@callback(
    Output('races-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('races-year-overlay', 'style', allow_duplicate=True),
    Input('races-year-overlay', 'n_clicks'),
    prevent_initial_call=True,
)
def close_races_year_dropdown(n_clicks):
    return {'display': 'none'}, {'display': 'none'}


@callback(
    Output('races-race-pill-dropdown', 'children'),
    Output('races-race-pill-dropdown', 'style', allow_duplicate=True),
    Output('races-race-overlay', 'style', allow_duplicate=True),
    Input('races-race-pill-toggle', 'n_clicks'),
    State('races-store-year', 'data'),
    State('races-race-pill-dropdown', 'style'),
    prevent_initial_call=True,
)
def toggle_races_race(n_clicks, year, current_style):
    if isinstance(current_style, dict) and current_style.get('display') != 'none':
        return no_update, {'display': 'none'}, {'display': 'none'}
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    schedule = schedule[schedule['EventFormat'] != 'testing']
    items = [
        html.Div(
            row['EventName'].replace(' Grand Prix', ''),
            id={'type': 'races-race-pill', 'index': int(row['RoundNumber'])},
            className='year-dropdown-item'
        )
        for _, row in schedule.iterrows()
    ]
    return items, {'display': 'block'}, {'display': 'block'}


# @callback(
#     Output('races-store-race', 'data'),
#     Output('races-pill-race-display', 'children'),
#     Output('races-race-pill-dropdown', 'style', allow_duplicate=True),
#     Output('races-race-overlay', 'style', allow_duplicate=True),
#     Input({'type': 'races-race-pill', 'index': ALL}, 'n_clicks'),
#     State({'type': 'races-race-pill', 'index': ALL}, 'id'),
#     prevent_initial_call=True,
# )
# def select_races_race(n_clicks, ids):
#     from dash import ctx
    
#     # Check if the callback was triggered by a specific button click
#     if not ctx.triggered or not isinstance(ctx.triggered_id, dict):
#         return no_update, no_update, no_update, no_update

#     triggered_id = ctx.triggered_id
#     selected_index = triggered_id['index']
    
#     # Find the label for the selected index
#     # (Using the year/schedule might be safer than relying on IDs)
#     return selected_index, f"Round {selected_index}", {'display': 'none'}, {'display': 'none'}


@callback(
    Output('races-store-race', 'data'),
    Output('races-pill-race-display', 'children'),
    Output('races-race-pill-dropdown', 'style', allow_duplicate=True),
    Output('races-race-overlay', 'style', allow_duplicate=True),
    Input({'type': 'races-race-pill', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def select_races_race(n_clicks):
    from dash import ctx
    # If no button in the pattern-match was actually clicked, don't close the menu
    if not ctx.triggered_id or all(n is None for n in n_clicks):
        raise PreventUpdate

    selected = ctx.triggered_id['index']
    return selected, f"Round {selected}", {'display': 'none'}, {'display': 'none'}

@callback(
    Output('races-race-pill-dropdown', 'style', allow_duplicate=True),
    Output('races-race-overlay', 'style', allow_duplicate=True),
    Input('races-race-overlay', 'n_clicks'),
    prevent_initial_call=True,
)
def close_races_race_dropdown(n_clicks):
    return {'display': 'none'}, {'display': 'none'}


@callback(
    Output('races-content', 'children'),
    Output('races-pace-evolution', 'figure'),
    Input('races-store-race', 'data'),
    Input('races-store-year', 'data'),
)
def update_races_content(round_number, year):
    import plotly.graph_objects as go

    TRANSPARENT = dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FBF9E4', family='Titillium Web'),
    )
    AXIS = dict(
        gridcolor='rgba(0,0,0,0)',
        title='',
        showline=False,
        zeroline=False,
        tickfont=dict(color='#444'),
    )
    empty = go.Figure().update_layout(**TRANSPARENT)

    if not year:
        return html.Div('Select a season.'), empty
    if not round_number:
        round_number = 1

    try:
        session = fastf1.get_session(year, round_number, 'R')
        session.load(telemetry=False, weather=False, messages=False)

        results = session.results
        laps = session.laps.copy()
        laps = laps.dropna(subset=['LapTime'])
        laps['LapTimeSec'] = laps['LapTime'].dt.total_seconds()

        # ── Fastest laps table ──
        fastest = laps.groupby('Driver')['LapTimeSec'].min().reset_index()
        fastest = fastest.sort_values('LapTimeSec').head(20)
        fastest['Pos'] = range(1, len(fastest) + 1)
        driver_team = results[['Abbreviation', 'TeamName']].copy()
        fastest = fastest.merge(driver_team, left_on='Driver',
                                right_on='Abbreviation', how='left')

        def fmt_time(secs):
            m = int(secs // 60)
            s = secs % 60
            return f"{m}:{s:06.3f}"

        fastest['LapTimeStr'] = fastest['LapTimeSec'].apply(fmt_time)

        rows = []
        for _, row in fastest.iterrows():
            logo_file = TEAM_LOGOS.get(row['TeamName'], None)
            team_color = TEAM_COLORS.get(row['TeamName'], '#444')
            pos = int(row['Pos'])
            rows.append(html.Tr([
                html.Td(str(pos), className='pos'),
                html.Td(
                    html.Img(src=f'/assets/logos/{logo_file}.avif',
                             style={'height': '16px', 'width': '28px',
                                    'objectFit': 'contain'})
                    if logo_file else html.Div(
                        style={'width': '4px', 'background': team_color}),
                    style={'width': '36px', 'padding': '0 4px'},
                ),
                html.Td(row['Driver'], className='driver-abbr'),
                html.Td(row['LapTimeStr'], className='pts'),
            ], className='p1' if pos == 1 else ''))

        table = html.Div([
            html.Div(f'{year} — {session.event["EventName"]}',
                     style={'fontSize': '0.6rem', 'color': '#888',
                            'letterSpacing': '0.15em', 'textTransform': 'uppercase',
                            'fontFamily': 'Titillium Web', 'marginBottom': '12px'}),
            html.Div('Fastest Laps', className='home-section-title',
                     style={'marginBottom': '8px'}),
            html.Table([
                html.Thead(html.Tr([
                    html.Th('POS'), html.Th(''),
                    html.Th('DRIVER'), html.Th('FASTEST LAP'),
                ])),
                html.Tbody(rows),
            ], className='champ-table standings-full-table'),
        ])

        # ── Race pace evolution ──
        fig = go.Figure()
        drivers = laps['Driver'].unique()

        # Filter out slow laps — pit laps, SC laps
        fastest_lap_time = laps['LapTimeSec'].min()
        clean_laps = laps[laps['LapTimeSec'] < fastest_lap_time * 1.07]

        for drv in drivers:
            drv_laps = clean_laps[clean_laps['Driver'] == drv]\
                .sort_values('LapNumber')
            if len(drv_laps) == 0:
                continue
            team = drv_laps.iloc[0].get('Team', '')
            color = TEAM_COLORS.get(team, '#444')

            # Format y-axis as MM:SS.mmm
            y_vals = drv_laps['LapTimeSec'].tolist()
            x_vals = drv_laps['LapNumber'].tolist()

            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                name=drv,
                line=dict(color=color, width=1.2),
                mode='lines+markers',
                marker=dict(size=3),
                hovertemplate=f'<b>{drv}</b><br>Lap %{{x}}<br>%{{text}}<extra></extra>',
                text=[fmt_time(t) for t in y_vals],
            ))

        # Format y-axis ticks as MM:SS
        min_time = clean_laps['LapTimeSec'].min() if len(clean_laps) > 0 else 60
        max_time = clean_laps['LapTimeSec'].max() if len(clean_laps) > 0 else 120

        tick_vals = [min_time + i * 2 for i in range(
            int((max_time - min_time) / 2) + 2)]
        tick_text = [fmt_time(t) for t in tick_vals]

        fig.update_layout(
            **TRANSPARENT,
            autosize=True,
            title=dict(text='Race Pace Evolution',
                       font=dict(color='#444', size=13)),
            xaxis=dict(**AXIS, title='Lap'),
            yaxis=dict(
                **AXIS,
                tickvals=tick_vals,
                ticktext=tick_text,
                autorange=True,
            ),
            showlegend=False,
            margin=dict(l=80, r=20, t=40, b=20),
        )

        return table, fig

    except Exception as e:
        print(f'Races content error: {e}')
        err = html.Div(f'Error: {e}', className='standings-empty')
        return err, empty