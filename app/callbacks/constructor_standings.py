# app/callbacks/constructor_standings.py
from dash import html, callback, Output, Input, State, ALL, ctx
from app.analytics.constructor_standings import fetch_constructor_season_results, process_constructor_metrics
import app.components.constructor_standings_ui as ui
from  app.constants import TEAM_COLORS, TEAM_LOGOS

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
    fallback_fig = ui.get_empty_fallback()

    # 1. Pipeline pull directly from our database layer
    all_results = fetch_constructor_season_results(year)

    if all_results.empty:
        err_view = html.Div('No data available in local database.', className='standings-empty')
        return err_view, fallback_fig, fallback_fig, fallback_fig, fallback_fig

    # 2. Extract calculations
    standings, wins, rounds = process_constructor_metrics(all_results)
    constructors = standings['TeamName'].tolist()

    # 3. Component distribution generation
    table_layout = ui.build_constructor_table(standings, wins, year, TEAM_COLORS, TEAM_LOGOS)
    fig_points = ui.make_points_evolution_chart(all_results, constructors, rounds, TEAM_COLORS)
    fig_ranking = ui.make_ranking_evolution_chart(all_results, constructors, rounds, TEAM_COLORS)
    fig_stats = ui.make_season_stats_chart(all_results, constructors, wins, TEAM_LOGOS)
    fig_dist = ui.make_points_distribution_chart(all_results, TEAM_COLORS)

    return table_layout, fig_points, fig_ranking, fig_stats, fig_dist
