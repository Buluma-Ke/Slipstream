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
    'HARD': '#ABABAB',
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


def make_track_map(telemetry):
    """
    Circuit map coloured by speed.
    Uses X/Y position data merged with car speed.

    Args:
        telemetry: DataFrame from get_car_data().add_distance()
                   must also contain X and Y columns — use merge_channels()

    Returns:
        plotly Figure
    """
    fig = px.scatter(
        telemetry,
        x='X',
        y='Y',
        color='Speed',
        color_continuous_scale='RdYlGn',
        labels={'Speed': 'Speed (km/h)'},
        title='Track map — speed heatmap',
    )
    fig.update_traces(marker=dict(size=4))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, scaleanchor='x'),
        coloraxis_colorbar=dict(title='km/h'),
    )
    return fig


def make_strategy_strip(laps):
    """
    Horizontal bar chart showing each driver's tyre stint timeline.
    Each bar represents one stint, coloured by compound.

    Args:
        laps: DataFrame from query_laps()

    Returns:
        plotly Figure
    """
    # Detect stint boundaries — when compound changes for a driver
    laps = laps.sort_values(['driver', 'lap_number']).copy()
    laps['stint_id'] = (
        laps.groupby('driver')['compound']
        .transform(lambda x: (x != x.shift()).cumsum())
    )

    # Group into stints
    stints = laps.groupby(['driver', 'stint_id', 'compound']).agg(
        start_lap=('lap_number', 'min'),
        end_lap=('lap_number', 'max'),
    ).reset_index()

    stints['duration'] = stints['end_lap'] - stints['start_lap'] + 1

    fig = px.bar(
        stints,
        x='duration',
        y='driver',
        color='compound',
        base='start_lap',
        orientation='h',
        color_discrete_map=COMPOUND_COLORS,
        labels={
            'duration': 'Laps',
            'driver': 'Driver',
            'compound': 'Compound'
        },
        title='Tyre strategy',
        )
    
    fig.update_layout(
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='#ffffff'),
        xaxis=dict(
            title='Lap number',
            gridcolor='#333333',
        ),
        yaxis=dict(
            gridcolor='#333333',
        ),
        bargap=0.2,
        legend=dict(
            bgcolor='#1a1a1a',
        )
    )
    return fig


def make_lap_delta(laps, driver_a, driver_b):
    """
    Cumulative time delta between two drivers across all laps.
    Positive = driver_a is losing time to driver_b.
    Negative = driver_a is gaining on driver_b.

    Args:
        laps:     DataFrame from query_laps()
        driver_a: Driver code string e.g. 'VER'
        driver_b: Driver code string e.g. 'LEC'

    Returns:
        plotly Figure
    """
    a = laps[laps['driver'] == driver_a][['lap_number', 'lap_time_sec']].set_index('lap_number')
    b = laps[laps['driver'] == driver_b][['lap_number', 'lap_time_sec']].set_index('lap_number')

    delta = (a['lap_time_sec'] - b['lap_time_sec']).cumsum().reset_index()
    delta.columns = ['lap_number', 'delta']

    fig = px.line(
        delta,
        x='lap_number',
        y='delta',
        title=f'Cumulative delta — {driver_a} vs {driver_b}',
        labels={'delta': 'Delta (s)', 'lap_number': 'Lap'},
        color_discrete_sequence=['#E8002D'],
    )
    fig.add_hline(y=0, line_dash='dash', line_color='gray')
    fig.update_layout(
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='#ffffff'),
        xaxis=dict(gridcolor='#333333'),
        yaxis=dict(gridcolor='#333333'),
    )
    return fig


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    from data.store import query_laps
    from data.loader import get_session

    laps = query_laps(year=2023, event_name='Bahrain Grand Prix', session_type='R')
    session = get_session(2023, 'Bahrain', 'R')
    ver_lap = session.laps.pick_driver('VER').pick_lap(10)

    tel = ver_lap.get_car_data().add_distance()
    pos = ver_lap.get_pos_data()
    merged = tel.merge_channels(pos)

    # Chart 1
    fig1 = make_lap_time_dist(laps)
    fig1.show()

    # Chart 2
    fig2 = make_speed_trace(tel, 'VER — Lap 10')
    fig2.show()

    # Chart 3
    fig3 = make_track_map(merged)
    fig3.show()

    # Chart 4
    fig4 = make_strategy_strip(laps)
    fig4.show()

    # Chart 5
    fig5 = make_lap_delta(laps, 'VER', 'PER')
    fig5.show()