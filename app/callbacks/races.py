# app/callbacks/races.py
import fastf1
from dash import html, callback, Output, Input, State, ALL, ctx, no_update
from dash.exceptions import PreventUpdate

import app.analytics.races_data as data
import app.components.races_ui as ui
from app.constants import TEAM_COLORS, TEAM_LOGOS


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
    prevent_initial_call=True,
)
def select_races_year(n_clicks):
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


@callback(
    Output('races-store-race', 'data'),
    Output('races-pill-race-display', 'children'),
    Output('races-race-pill-dropdown', 'style', allow_duplicate=True),
    Output('races-race-overlay', 'style', allow_duplicate=True),
    Input({'type': 'races-race-pill', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def select_races_race(n_clicks):
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
    Output('races-pace-boxplot', 'figure'),
    Output('races-lap-times-strip', 'figure'),
    Output('races-position-evolution', 'figure'),
    Output('races-speed-heatmap', 'figure'),
    Input('races-store-race', 'data'),
    Input('races-store-year', 'data'),
)
def update_races_content(round_number, year):
    empty_fig = go.Figure().update_layout(**ui.TRANSPARENT)

    if not year:
        return html.Div('Select a season.'), empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    round_number = round_number or 1

    try:
        # 1. Pipeline pull from Data Extraction Layer
        results, laps, session = data.fetch_race_session_data(year, round_number)

        if laps.empty:
            err_view = html.Div('Telemetry data unavailable for this event.', className='standings-empty')
            return err_view, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

        # 2. Extract calculations & apply statistical data filters
        clean_laps = data.process_clean_race_laps(laps)
        fastest_df = data.generate_fastest_laps_table(laps, results)

        max_laps = int(laps['LapNumber'].max())
        driver_order = clean_laps.groupby('Driver')['LapTimeSec'].median().sort_values().index.tolist()

        # 3. UI Component generation using the layout engine
        table_layout = ui.build_fastest_laps_view(fastest_df, session, year, TEAM_COLORS, TEAM_LOGOS)
        fig_pace = ui.make_pace_evolution_chart(clean_laps, max_laps, TEAM_COLORS)
        fig_box = ui.make_pace_box_chart(clean_laps, driver_order, TEAM_COLORS)
        fig_strip = ui.make_lap_times_strip_chart(clean_laps, driver_order, TEAM_COLORS)
        fig_pos = ui.make_position_evolution_chart(laps, TEAM_COLORS)
        fig_heatmap = ui.make_speed_trap_heatmap(laps)

        return table_layout, fig_pace, fig_box, fig_strip, fig_pos, fig_heatmap

    except Exception as e:
        print(f'❌ Layout rendering route crash: {e}')
        err_view = html.Div(f'Layout Error: {e}', className='standings-empty')
        return err_view, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig
