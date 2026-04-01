import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# F1 team colours 2024
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
}

COMPOUND_COLORS = {
    'SOFT': '#E8002D',
    'MEDIUM': '#FFF200',
    'HARD': '#FFFFFF',
    'INTERMEDIATE': '#39B54A',
    'WET': '#0067FF',
}



def make_lap_time_dist(laps):
    """
    Box plot of lap times per driver for a session.
    Drivers sorted fastest to slowest by median lap time.

    Args:
        laps: DataFrame from query_laps() or get_laps()

    Returns:
        plotly Figure
    """
    # Sort drivers by median lap time
    order = (
        laps.groupby('driver')['lap_time_sec']
        .median()
        .sort_values()
        .index.tolist()
    )

    fig = px.box(
        laps,
        x='driver',
        y='lap_time_sec',
        color='team',
        color_discrete_map=TEAM_COLORS,
        category_orders={'driver': order},
        labels={
            'lap_time_sec': 'Lap time (s)',
            'driver': 'Driver',
            'team': 'Team'
        },
        title='Lap time distribution — Bahrain 2023',
    )
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def make_speed_trace(telemetry, driver_label=''):
    """
    Four stacked subplots showing speed, throttle, brake and gear vs distance.

    Args:
        telemetry:    DataFrame from get_car_data().add_distance()
        driver_label: String shown in the chart title e.g. 'VER — Lap 10'

    Returns:
        plotly Figure
    """
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        subplot_titles=['Speed (km/h)', 'Throttle (%)', 'Brake', 'Gear'],
        vertical_spacing=0.06,
    )

    fig.add_trace(go.Scatter(
        x=telemetry['Distance'], y=telemetry['Speed'],
        name='Speed', line=dict(color='#E8002D', width=1.5)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=telemetry['Distance'], y=telemetry['Throttle'],
        name='Throttle', line=dict(color='#27F4D2', width=1)
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=telemetry['Distance'], y=telemetry['Brake'].astype(int),
        name='Brake', fill='tozeroy', line=dict(color='#FF8000', width=0.5)
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=telemetry['Distance'], y=telemetry['nGear'],
        name='Gear', line=dict(color='#FFD700', width=1), mode='lines'
    ), row=4, col=1)

    fig.update_layout(
        title=f'Telemetry — {driver_label}',
        showlegend=False,
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_xaxes(title_text='Distance (m)', row=4, col=1)
    fig.update_yaxes(tickvals=list(range(1, 9)), row=4, col=1)
    return fig


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    from data.store import query_laps
    from data.loader import get_session

    laps = query_laps(year=2023, event_name='Bahrain Grand Prix', session_type='R')

    # Chart 1 — lap time distribution
    fig1 = make_lap_time_dist(laps)
    fig1.show()

    # Chart 2 — speed trace
    session = get_session(2023, 'Bahrain', 'R')
    ver_lap = session.laps.pick_driver('VER').pick_lap(10)
    tel = ver_lap.get_car_data().add_distance()
    fig2 = make_speed_trace(tel, 'VER — Lap 10')
    fig2.show()