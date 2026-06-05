
from app.analytics.home import get_homepage_data
from app.components.tables import build_driver_table, build_team_table
from dash import callback, Output, Input, State, ALL


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
    data = get_homepage_data(year)

    if not data:
        # Return the "Empty State" tuple
        return (
            '—', '0 pts', '—', '0 pts', '0',
            '0', '—',
            '0', '—',
            '—', '—',
            '0', '—',
            [], [])

    # Format Champion/Constructor cards
    champion_name = data['champion'].get('Abbreviation', '—')
    champion_pts = f"{int(data['champion'].get('Points', 0))} pts"

    team_name = data['constructor'].get('TeamName', '—')
    team_pts = f"{int(data['constructor'].get('Points', 0))} pts"

    # Build Tables (Use your existing row-building logic here)
    # Just pass data['driver_standings'] and data['team_standings'] to your helper functions
    drivers_table = build_driver_table(data['driver_standings'])
    constructors_table = build_team_table(data['team_standings'])

    return (
            champion_name,
            f'{champion_pts}',
            team_name,
            f'{team_pts} pts',
            str(data['total_races']),
            str(data['wins'][1]), data['wins'][0],  # Most wins count and driver
            str(data['poles'][1]), data['poles'][0], # Most poles count and driver
            data.get('closest_gap', '—'),            # Closest finish string
            data.get('closest_event', '—'),     # Closest event name
            str(data['dnfs'][1]), data['dnfs'][0],  # Most DNFs count and driver
            drivers_table,
            constructors_table,
        )
