# app/callbacks/teams.py
import plotly.graph_objects as go
from dash import callback, Output, Input, State, html, ctx, no_update, ALL
from app.analytics.teams_data import fetch_available_teams, fetch_team_season_results
from app.components.teams_ui import (
    render_team_hero, make_stat_card, make_radial_bar_chart,
    make_distribution_chart, make_points_donut, make_points_evolution
)

TEAM_COLORS = {}
TEAM_LOGOS = {}


# Toggle Year Dropdown
@callback(
    Output('teams-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('teams-year-overlay', 'style', allow_duplicate=True),
    Input('teams-year-pill-toggle', 'n_clicks'),
    State('teams-year-pill-dropdown', 'style'),
    prevent_initial_call=True,
)
def toggle_teams_year(n_clicks, current_style):
    if isinstance(current_style, dict) and current_style.get('display') == 'none':
        return {'display': 'block'}, {'display': 'block'}
    return {'display': 'none'}, {'display': 'none'}


# Select Year From Dropdown
@callback(
    Output('teams-store-year', 'data'),
    Output('teams-pill-year-display', 'children'),
    Output('teams-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('teams-year-overlay', 'style', allow_duplicate=True),
    Input({'type': 'teams-year-pill', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def select_teams_year(n_clicks):
    triggered = ctx.triggered_id
    if not triggered:
        return 2025, '2025', {'display': 'none'}, {'display': 'none'}
    selected = triggered['index']
    return selected, str(selected), {'display': 'none'}, {'display': 'none'}


# Close Year Dropdown via Overlay
@callback(
    Output('teams-year-pill-dropdown', 'style', allow_duplicate=True),
    Output('teams-year-overlay', 'style', allow_duplicate=True),
    Input('teams-year-overlay', 'n_clicks'),
    prevent_initial_call=True,
)
def close_teams_year(n_clicks):
    return {'display': 'none'}, {'display': 'none'}


# Toggle Team Dropdown
@callback(
    Output('teams-team-pill-dropdown', 'children'),
    Output('teams-team-pill-dropdown', 'style', allow_duplicate=True),
    Output('teams-team-overlay', 'style', allow_duplicate=True),
    Input('teams-team-pill-toggle', 'n_clicks'),
    State('teams-store-year', 'data'),
    State('teams-team-pill-dropdown', 'style'),
    prevent_initial_call=True,
)
def toggle_teams_team(n_clicks, year, current_style):
    if isinstance(current_style, dict) and current_style.get('display') == 'block':
        return no_update, {'display': 'none'}, {'display': 'none'}

    if not year:
        return [html.Div("Select a year first", className='year-dropdown-item')], {'display': 'block'}, {'display': 'block'}

    teams_df = fetch_available_teams(year)
    if teams_df.empty:
        return [html.Div("No team data loaded", className='year-dropdown-item')], {'display': 'block'}, {'display': 'block'}

    items = [
        html.Div(
            f"{row['team']}",
            id={'type': 'teams-team-pill', 'index': row['team']},
            className='year-dropdown-item',
            n_clicks=0
        )
        for _, row in teams_df.iterrows()
    ]
    return items, {'display': 'block'}, {'display': 'block'}


# Select Team From Dropdown
@callback(
    Output('teams-store-team', 'data'),
    Output('teams-pill-team-display', 'children'),
    Output('teams-team-pill-dropdown', 'style', allow_duplicate=True),
    Output('teams-team-overlay', 'style', allow_duplicate=True),
    Input({'type': 'teams-team-pill', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def select_teams_team(n_clicks):
    triggered = ctx.triggered_id
    if not triggered or not ctx.triggered[0]['value']:
        return no_update, no_update, no_update, no_update

    selected = triggered['index']
    return selected, selected, {'display': 'none'}, {'display': 'none'}


# Close Team Dropdown via Overlay
@callback(
    Output('teams-team-pill-dropdown', 'style', allow_duplicate=True),
    Output('teams-team-overlay', 'style', allow_duplicate=True),
    Input('teams-team-overlay', 'n_clicks'),
    prevent_initial_call=True,
)
def close_teams_team(n_clicks):
    return {'display': 'none'}, {'display': 'none'}


# Update Dashboard Analytics and Charts Content
@callback(
    Output('teams-hero-content', 'children'),
    Output('teams-stats-cards', 'children'),
    Output('teams-graph-radial', 'figure'),
    Output('teams-radial-legend-container', 'children'),
    Output('teams-graph-dist', 'figure'),
    Output('teams-graph-donut', 'figure'),
    Output('teams-graph-evo', 'figure'),
    Output('teams-graphs-grid', 'style'),
    Input('teams-store-team', 'data'),
    Input('teams-store-year', 'data'),
)
def update_teams_content(team, year):
    if not team or not year:
        fallback_msg = html.Div('Select a season and team.', style={'color': '#555', 'fontFamily': 'Titillium Web', 'fontSize': '0.8rem', 'padding': '20px'})
        return fallback_msg, None, go.Figure(), None, go.Figure(), go.Figure(), go.Figure(), {'display': 'none'}

    try:
        tm_results = fetch_team_season_results(year, team)

        if tm_results.empty:
            return html.Div(f'No data for {team} in {year}.'), None, go.Figure(), None, go.Figure(), go.Figure(), go.Figure(), {'display': 'none'}

        # Calculate metrics using aggregated structure or handling grouped strings
        def count_positions(pos_series, condition):
            count = 0
            for val in pos_series.dropna():
                count += sum(1 for p in str(val).split(',') if p.strip().isdigit() and condition(int(p.strip())))
            return count

        wins = count_positions(tm_results['Positions'], lambda p: p == 1)
        podiums = count_positions(tm_results['Positions'], lambda p: p <= 3)
        poles = count_positions(tm_results['GridPositions'], lambda p: p == 1)

        points = int(tm_results['Points'].sum())
        races_count = len(tm_results)
        avg_pts = round(points / races_count, 1) if races_count > 0 else 0

        dnfs = 0
        for val in tm_results['Positions'].dropna():
            dnfs += sum(1 for p in str(val).split(',') if 'DNF' in p.upper() or 'R' in p.upper())

        hero_node = render_team_hero(year, team)

        cards_grid = html.Div([
            make_stat_card('Grand Prix Wins', wins, team, 'Sprint wins not included', accent=True),
            make_stat_card('Podiums', podiums, team, 'Sprint podiums not included'),
            make_stat_card('Season Points', points, team, f'Avg. {avg_pts} per race'),
            make_stat_card('Pole Positions', poles, team),
            make_stat_card('Races', races_count, team),
            make_stat_card('DNFs', dnfs, team),
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gap': '10px', 'marginBottom': '16px'})

        fig_radial, radial_legend = make_radial_bar_chart(tm_results, wins, podiums, dnfs, team)
        fig_dist = make_distribution_chart(tm_results, team)
        fig_donut = make_points_donut(tm_results, team)
        fig_evo = make_points_evolution(tm_results, team)

        return hero_node, cards_grid, fig_radial, radial_legend, fig_dist, fig_donut, fig_evo, {'display': 'flex', 'gap': '15px', 'marginTop': '16px'}

    except Exception as e:
        print(f'❌ Teams content runtime error: {e}')
        return html.Div(f'Error processing data: {e}'), None, go.Figure(), None, go.Figure(), go.Figure(), go.Figure(), {'display': 'none'}
