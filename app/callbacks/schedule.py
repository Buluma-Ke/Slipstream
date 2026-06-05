# app/callbacks/schedule.py
import json
import dash
from dash import html, callback, Output, Input, State, ALL
from app.analytics.schedule import get_season_schedule
from app.components.schedule_ui import make_race_card

@callback(
    [Output('schedule-year-pill-dropdown', 'style'),
     Output('schedule-year-overlay', 'style')],
    [Input('schedule-year-pill-toggle', 'n_clicks'),
     Input('schedule-year-overlay', 'n_clicks'),
     Input({'type': 'schedule-year-pill', 'index': ALL}, 'n_clicks')],
    [State('schedule-year-pill-dropdown', 'style')],
    prevent_initial_call=True
)
def toggle_year_dropdown(toggle_clicks, overlay_clicks, pill_clicks, current_style):
    """Manages view block displays for the custom year selection component dropdown."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return {'display': 'none'}, {'display': 'none'}

    trigger_id = ctx.triggered[0]['prop_id']

    # Hide dropdown if background overlay layer or an item pill selection was fired
    if 'schedule-year-overlay' in trigger_id or 'schedule-year-pill' in trigger_id:
        return {'display': 'none'}, {'display': 'none'}

    # Toggle open/close visibility
    if current_style and current_style.get('display') == 'block':
        return {'display': 'none'}, {'display': 'none'}

    return {'display': 'block'}, {'display': 'block'}


@callback(
    [Output('schedule-active-year-store', 'data'),
     Output('schedule-pill-year-display', 'children')],
    Input({'type': 'schedule-year-pill', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_selected_year_state(pill_clicks):
    """Processes explicit year dropdown selections and saves them to local storage."""
    ctx = dash.callback_context
    if not ctx.triggered or not any(pill_clicks):
        return 2025, '2025'

    # Safely extract index parameter from the pattern-matching callback string
    trigger_raw = ctx.triggered[0]['prop_id'].split('.')[0]
    trigger_dict = json.loads(trigger_raw)
    selected_year = int(trigger_dict['index'])

    return selected_year, str(selected_year)


@callback(
    Output('schedule-cards', 'children'),
    Input('schedule-active-year-store', 'data')
)
def render_schedule_cards_grid(active_year):
    """Populates structural dashboard interface display cards based on selected year filter."""
    # 1. Ask engine for schedule metrics data array
    races_list = get_season_schedule(active_year)

    if not races_list:
        return html.Div("No schedule entries available for this season window.", className='table-empty-state')

    # 2. Feed raw metrics directly into your custom component card generators
    cards_layout = [make_race_card(race, active_year) for race in races_list]
    return cards_layout
