# app/callbacks/navigation.py
from dash import callback, Output, Input, State, ctx
from app.pages import (
    home, races, schedule, drivers, teams,
    telemetry, predictions, driver_standings, constructor_standings
)

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
