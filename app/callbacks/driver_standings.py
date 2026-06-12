# app/callbacks/driver_standings.py
import dash
from dash import html, callback, Output, Input, State, ALL, ctx
from app.analytics.driver_standings import fetch_season_results, process_driver_metrics
import app.components.driver_standings_ui as ui

# ... (Keep your dropdown toggle callbacks here as they are) ...

@callback(
    Output('drv-standings-content', 'children'),
    Output('drv-points-evolution', 'figure'),
    Output('drv-ranking-evolution', 'figure'),
    Output('drv-stats-chart', 'figure'),
    Output('drv-points-distribution', 'figure'),
    Input('drv-standings-store-year', 'data'),
)
def update_driver_standings_all(year):
    # Initialize our fallback object
    fallback_fig = ui.get_empty_fallback()

    # 1. Fetch raw rows
    all_results = fetch_season_results(year)

    # Path A: Handle empty or missing frames cleanly with a 5-element tuple
    if all_results is None or all_results.empty:
        err_view = html.Div('No data found for this season windows layout.', className='standings-empty')
        return err_view, fallback_fig, fallback_fig, fallback_fig, fallback_fig

    # 2. Extract metrics arrays
    standings, wins, rounds = process_driver_metrics(all_results)
    drivers = standings['Abbreviation'].tolist()

    # 3. Construct elements using the layout component engine
    table_layout = ui.build_standings_table(standings, wins, year)

    fig_points = ui.make_points_evolution_chart(all_results, drivers, rounds)
    fig_ranking = ui.make_ranking_evolution_chart(all_results, drivers, rounds, max_drivers=len(standings))
    fig_stats = ui.make_season_stats_chart(all_results, drivers, wins)
    fig_distribution = ui.make_points_distribution_chart(all_results)

    # Path B: The successful path must also return exactly 5 elements
    return table_layout, fig_points, fig_ranking, fig_stats, fig_distribution
