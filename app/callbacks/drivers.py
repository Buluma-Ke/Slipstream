# app/callbacks/drivers.py
import plotly.graph_objects as go

from dash import callback, Output, Input, State, html, ctx, no_update, ALL
from app.analytics.drivers_data import fetch_available_drivers, fetch_driver_season_results
from app.components.drivers_ui import (
    render_driver_hero, make_stat_card, make_radial_bar_chart,
    make_distribution_chart, make_points_donut, make_points_evolution
)

# Placeholders for dictionary maps managed by your global configs
TEAM_COLORS = {}
TEAM_LOGOS = {}

@callback(
    Output('drivers-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('drivers-year-overlay', 'style', allow_duplicate=True),
    Input('drivers-year-pill-toggle', 'n_clicks'),
    State('drivers-year-pill-dropdown', 'style'),
    prevent_initial_call=True,
)
def toggle_drivers_year(n_clicks, current_style):
    if isinstance(current_style, dict) and current_style.get('display') == 'none':
        return {'display': 'block'}, {'display': 'block'}
    return {'display': 'none'}, {'display': 'none'}

@callback(
    Output('drivers-store-year', 'data'),
    Output('drivers-pill-year-display', 'children'),
    Output('drivers-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('drivers-year-overlay', 'style', allow_duplicate=True),
    Input({'type': 'drivers-year-pill', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def select_drivers_year(n_clicks):
    triggered = ctx.triggered_id
    if not triggered:
        return 2025, '2025', {'display': 'none'}, {'display': 'none'}
    selected = triggered['index']
    return selected, str(selected), {'display': 'none'}, {'display': 'none'}

@callback(
    Output('drivers-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('drivers-year-overlay', 'style', allow_duplicate=True),
    Input('drivers-year-overlay', 'n_clicks'),
    prevent_initial_call=True,
)
def close_drivers_year(n_clicks):
    return {'display': 'none'}, {'display': 'none'}

@callback(
    Output('drivers-driver-pill-dropdown', 'children'),
    Output('drivers-driver-pill-dropdown', 'style', allow_duplicate=True),
    Output('drivers-driver-overlay', 'style', allow_duplicate=True),
    Input('drivers-driver-pill-toggle', 'n_clicks'),
    State('drivers-store-year', 'data'),
    State('drivers-driver-pill-dropdown', 'style'),
    prevent_initial_call=True,
)
def toggle_drivers_driver(n_clicks, year, current_style):
    if isinstance(current_style, dict) and current_style.get('display') == 'block':
        return no_update, {'display': 'none'}, {'display': 'none'}

    if not year:
        return [html.Div("Select a year first", className='year-dropdown-item')], {'display': 'block'}, {'display': 'block'}

    drivers_df = fetch_available_drivers(year)
    if drivers_df.empty:
        return [html.Div("No driver data loaded", className='year-dropdown-item')], {'display': 'block'}, {'display': 'block'}

    items = [
        html.Div(
            f"{row['driver']} — {row['full_name']}",
            id={'type': 'drivers-driver-pill', 'index': row['driver']},
            className='year-dropdown-item',
            n_clicks=0
        )
        for _, row in drivers_df.iterrows()
    ]
    return items, {'display': 'block'}, {'display': 'block'}

@callback(
    Output('drivers-store-driver', 'data'),
    Output('drivers-pill-driver-display', 'children'),
    Output('drivers-driver-pill-dropdown', 'style', allow_duplicate=True),
    Output('drivers-driver-overlay', 'style', allow_duplicate=True),
    Input({'type': 'drivers-driver-pill', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def select_drivers_driver(n_clicks):
    triggered = ctx.triggered_id
    if not triggered or not ctx.triggered[0]['value']:
        return no_update, no_update, no_update, no_update

    selected = triggered['index']
    return selected, selected, {'display': 'none'}, {'display': 'none'}

@callback(
    Output('drivers-driver-pill-dropdown', 'style', allow_duplicate=True),
    Output('drivers-driver-overlay', 'style', allow_duplicate=True),
    Input('drivers-driver-overlay', 'n_clicks'),
    prevent_initial_call=True,
)
def close_drivers_driver(n_clicks):
    return {'display': 'none'}, {'display': 'none'}

@callback(
    Output('drivers-hero-content', 'children'),
    Output('drivers-stats-cards', 'children'),
    Output('graph-radial', 'figure'),
    Output('graph-dist', 'figure'),
    Output('graph-donut', 'figure'),
    Output('graph-evo', 'figure'),
    Output('drivers-graphs-grid', 'style'),
    Input('drivers-store-driver', 'data'),
    Input('drivers-store-year', 'data'),
)
def update_drivers_content(driver, year):
    if not driver or not year:
        fallback_msg = html.Div('Select a season and driver.', style={'color': '#555', 'fontFamily': 'Titillium Web', 'fontSize': '0.8rem', 'padding': '20px'})
        return fallback_msg, None, go.Figure(), go.Figure(), go.Figure(), go.Figure(), {'display': 'none'}

    try:
        drv_results = fetch_driver_season_results(year, driver)
        if drv_results.empty:
            return html.Div(f'No data for {driver} in {year}.'), None, go.Figure(), go.Figure(), go.Figure(), go.Figure(), {'display': 'none'}

        team = drv_results.iloc[-1]['Team']
        full_name = drv_results.iloc[-1]['FullName']
        team_color = TEAM_COLORS.get(team, '#444')
        logo_file = TEAM_LOGOS.get(team, None)

        # Performance Calculations
        wins = len(drv_results[drv_results['Position'] == 1])
        podiums = len(drv_results[drv_results['Position'] <= 3])
        points = int(drv_results['Points'].sum())
        races_count = len(drv_results)
        avg_pts = round(points / races_count, 1) if races_count > 0 else 0
        dnfs = len(drv_results[drv_results['Status'].str.contains('DNF|Retired|Accident|Engine|Mechanical', case=False, na=False)])
        poles = len(drv_results[drv_results['GridPosition'] == 1])
        best_finish = int(drv_results['Position'].min()) if len(drv_results) > 0 else '—'
        avg_finish = round(drv_results['Position'].mean(), 1)

        # UI Layout Construction
        hero_node = render_driver_hero(year, full_name, team, team_color, logo_file)

        cards_grid = html.Div([
            make_stat_card('Grand Prix Wins', wins, 'Sprint wins not included', team_color, accent=True),
            make_stat_card('Podiums', podiums, 'Sprint podiums not included'),
            make_stat_card('Season Points', points, f'Avg. {avg_pts} per race'),
            make_stat_card('Pole Positions', poles),
            make_stat_card('Best Finish', f'P{best_finish}'),
            make_stat_card('Avg Finish', f'P{avg_finish}'),
            make_stat_card('DNFs', dnfs),
            make_stat_card('Races', races_count),
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '10px', 'marginBottom': '16px'})

        # Graphic Assemblies
        fig_radial = make_radial_bar_chart(drv_results, wins, podiums, dnfs, team_color)
        fig_dist = make_distribution_chart(drv_results, team_color)
        fig_donut = make_points_donut(drv_results, team_color)
        fig_evo = make_points_evolution(drv_results, team_color)

        return hero_node, cards_grid, fig_radial, fig_dist, fig_donut, fig_evo, {'display': 'flex', 'gap': '15px', 'marginTop': '16px'}

    except Exception as e:
        print(f'❌ Drivers content runtime error: {e}')
        return html.Div(f'Error processing data: {e}'), None, go.Figure(), go.Figure(), go.Figure(), go.Figure(), {'display': 'none'}
