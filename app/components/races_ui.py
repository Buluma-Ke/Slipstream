# app/components/races_ui.py
from dash import html
import plotly.graph_objects as go
import pandas as pd

TRANSPARENT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#FBF9E4', family='Titillium Web'),
)

AXIS = dict(
    gridcolor='rgba(0,0,0,0)',
    title='',
    showline=False,
    zeroline=False,
    tickfont=dict(color='#444'),
)

def fmt_time(secs):
    m = int(secs // 60)
    s = secs % 60
    return f"{m}:{s:06.3f}"

def hex_to_rgba(hex_color, alpha=0.3):
    if not hex_color or not isinstance(hex_color, str):
        return f'rgba(128,128,128,{alpha})'
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return f'rgba(128,128,128,{alpha})'
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f'rgba({r},{g},{b},{alpha})'
    except ValueError:
        return f'rgba(128,128,128,{alpha})'


def build_fastest_laps_view(fastest_df: pd.DataFrame, session: object, year: int, TEAM_COLORS: dict, TEAM_LOGOS: dict) -> html.Div:
    if fastest_df.empty or not session:
        return html.Div('No telemetry matches found.', className='standings-empty')

    rows = []
    for _, row in fastest_df.iterrows():
        logo_file = TEAM_LOGOS.get(row['TeamName'], None)
        team_color = TEAM_COLORS.get(row['TeamName'], '#444')
        pos = int(row['Pos'])
        lap_str = fmt_time(row['LapTimeSec'])

        rows.append(html.Tr([
            html.Td(str(pos), className='pos'),
            html.Td(
                html.Img(src=f'/assets/logos/{logo_file}.avif', style={'height': '16px', 'width': '28px', 'objectFit': 'contain'})
                if logo_file else html.Div(style={'width': '4px', 'background': team_color}),
                style={'width': '36px', 'padding': '0 4px'},
            ),
            html.Td(row['Driver'], className='driver-abbr'),
            html.Td(lap_str, className='pts'),
        ], className='p1' if pos == 1 else ''))

    return html.Div([
        html.Div(f'{year} — {session.event["EventName"]}',
                 style={'fontSize': '0.6rem', 'color': '#888', 'letterSpacing': '0.15em', 'textTransform': 'uppercase', 'marginBottom': '12px'}),
        html.Div('Fastest Laps', className='home-section-title', style={'marginBottom': '8px'}),
        html.Table([
            html.Thead(html.Tr([html.Th('POS'), html.Th(''), html.Th('DRIVER'), html.Th('FASTEST LAP')])),
            html.Tbody(rows),
        ], className='champ-table standings-full-table'),
    ])


def make_pace_evolution_chart(clean_laps: pd.DataFrame, max_laps: int, TEAM_COLORS: dict) -> go.Figure:
    fig = go.Figure()
    if clean_laps.empty: return fig.update_layout(**TRANSPARENT)

    for drv in clean_laps['Driver'].unique():
        drv_laps = clean_laps[clean_laps['Driver'] == drv].sort_values('LapNumber')
        if drv_laps.empty: continue

        team = drv_laps.iloc[0].get('Team', '')
        color = TEAM_COLORS.get(team, '#444')
        y_vals = drv_laps['LapTimeSec'].tolist()

        fig.add_trace(go.Scatter(
            x=drv_laps['LapNumber'].tolist(), y=y_vals, name=drv,
            line=dict(color=color, width=1.2), mode='lines+markers', marker=dict(size=3),
            hovertemplate=f'<b>{drv}</b><br>Lap %{{x}}<br>%{{text}}<extra></extra>',
            text=[fmt_time(t) for t in y_vals],
        ))

    min_t, max_t = clean_laps['LapTimeSec'].min(), clean_laps['LapTimeSec'].max()
    ticks = [min_t + i * 2 for i in range(int((max_t - min_t) / 2) + 2)]

    return fig.update_layout(
        **TRANSPARENT, autosize=True,
        title=dict(text='Race Pace Evolution', font=dict(color='#444', size=13)),
        xaxis=AXIS | dict(range=[1, max_laps + 1]),
        yaxis=AXIS | dict(tickvals=ticks, ticktext=[fmt_time(t) for t in ticks], autorange=True),
        showlegend=False, margin=dict(l=80, r=20, t=40, b=20),
    )


def make_pace_box_chart(clean_laps: pd.DataFrame, driver_order: list, TEAM_COLORS: dict) -> go.Figure:
    fig_box = go.Figure()
    if clean_laps.empty: return fig_box.update_layout(**TRANSPARENT)

    for drv in driver_order:
        drv_laps = clean_laps[clean_laps['Driver'] == drv]['LapTimeSec']
        if drv_laps.empty: continue

        team = clean_laps[clean_laps['Driver'] == drv].iloc[0].get('Team', '')
        color = TEAM_COLORS.get(team, '#444')

        fig_box.add_trace(go.Box(
            y=drv_laps.tolist(), name=drv, marker_color=color, line_color=color,
            fillcolor=hex_to_rgba(color, 0.3), boxpoints=False, showlegend=False,
        ))

    ticks = list(range(int(clean_laps['LapTimeSec'].min()) - 1, int(clean_laps['LapTimeSec'].max()) + 2))
    return fig_box.update_layout(
        **TRANSPARENT, autosize=True,
        title=dict(text='Race Pace Distribution', font=dict(color='#444', size=13)),
        xaxis=AXIS | dict(tickfont=dict(color='#888', size=10)),
        yaxis=AXIS | dict(tickvals=ticks, ticktext=[fmt_time(t) for t in ticks]),
        margin=dict(l=80, r=20, t=40, b=20),
    )


def make_lap_times_strip_chart(clean_laps: pd.DataFrame, driver_order: list, TEAM_COLORS: dict) -> go.Figure:
    fig_strip = go.Figure()
    if clean_laps.empty: return fig_strip.update_layout(**TRANSPARENT)

    for drv in driver_order:
        drv_laps = clean_laps[clean_laps['Driver'] == drv]
        if drv_laps.empty: continue

        team = drv_laps.iloc[0].get('Team', '')
        color = TEAM_COLORS.get(team, '#444')
        y_vals = drv_laps['LapTimeSec'].tolist()

        fig_strip.add_trace(go.Scatter(
            x=[drv] * len(drv_laps), y=y_vals, mode='markers', name=drv,
            marker=dict(color=color, size=6, opacity=0.7), showlegend=False,
            hovertemplate=f'<b>{drv}</b><br>%{{text}}<extra></extra>', text=[fmt_time(t) for t in y_vals],
        ))

    ticks = list(range(int(clean_laps['LapTimeSec'].min()) - 1, int(clean_laps['LapTimeSec'].max()) + 2))
    return fig_strip.update_layout(
        **TRANSPARENT, autosize=True,
        title=dict(text='Lap Times Spread', font=dict(color='#444', size=13)),
        xaxis=AXIS | dict(tickfont=dict(color='#888', size=10)),
        yaxis=AXIS | dict(tickvals=ticks, ticktext=[fmt_time(t) for t in ticks]),
        margin=dict(l=80, r=20, t=40, b=20),
    )


def make_position_evolution_chart(laps: pd.DataFrame, TEAM_COLORS: dict) -> go.Figure:
    fig_pos = go.Figure()
    pos_laps = laps.dropna(subset=['Position']).copy()
    if pos_laps.empty: return fig_pos.update_layout(**TRANSPARENT)

    pos_laps['Position'] = pos_laps['Position'].astype(int)
    total_max_laps = pos_laps['LapNumber'].max()
    pos_counts = {}

    for drv in pos_laps['Driver'].unique():
        drv_data = pos_laps[pos_laps['Driver'] == drv].sort_values('LapNumber')
        if drv_data.empty: continue

        team = drv_data.iloc[0].get('Team', '')
        color = TEAM_COLORS.get(team, '#444')
        final_pos = int(drv_data.iloc[-1]['Position'])

        offset = pos_counts.get(final_pos, 0)
        pos_counts[final_pos] = offset + 1

        fig_pos.add_trace(go.Scatter(
            x=drv_data['LapNumber'].tolist(), y=drv_data['Position'].tolist(), name=drv,
            line=dict(color=color, width=1.5, shape='spline', smoothing=0.9),
            mode='lines+markers', marker=dict(size=2), showlegend=False,
        ))

        fig_pos.add_annotation(
            x=total_max_laps, y=final_pos + (offset * 0.3), text=drv,
            xanchor='left', showarrow=False, font=dict(color=color, size=9, family='Titillium Web'), xshift=6,
        )

    max_pos = int(pos_laps['Position'].max())
    return fig_pos.update_layout(
        **TRANSPARENT, autosize=True,
        title=dict(text='Position Evolution', font=dict(color='#444', size=13)),
        xaxis=AXIS | dict(range=[1, total_max_laps + 1]),
        yaxis=AXIS | dict(autorange=False, range=[max_pos + 0.3, 0.7], dtick=1, tick0=1, tickmode='linear'),
        margin=dict(l=40, r=60, t=40, b=20),
    )


def make_speed_trap_heatmap(laps: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    speed_data = laps.dropna(subset=['SpeedST']).copy()
    if speed_data.empty: return fig.update_layout(**TRANSPARENT)

    speed_data['SpeedST'] = speed_data['SpeedST'].astype(int)
    speed_data['SpeedRank'] = speed_data.groupby('Driver')['SpeedST'].rank(method='first', ascending=False)

    top_20_speeds = speed_data[speed_data['SpeedRank'] <= 20].copy()
    speed_pivot = top_20_speeds.pivot(index='Driver', columns='SpeedRank', values='SpeedST')

    driver_best = speed_pivot[1.0].sort_values(ascending=False)
    speed_pivot = speed_pivot.reindex(driver_best.index)

    fig.add_trace(go.Heatmap(
        z=speed_pivot.values, x=speed_pivot.columns, y=speed_pivot.index,
        colorscale='Reds', showscale=False, text=speed_pivot.values,
        texttemplate="%{text}", textfont={"size": 10, "family": "Titillium Web"},
        hoverongaps=False, xgap=1, ygap=1
    ))

    return fig.update_layout(
        **TRANSPARENT, height=500, width=800,
        title=dict(text='Top 20 Speed Trap Speeds per Driver (km/h)', font=dict(color='#444', size=13)),
        xaxis=dict(visible=False),
        yaxis=AXIS | dict(autorange='reversed', tickfont=dict(color='#444', size=10)),
        margin=dict(l=50, r=10, t=30, b=10),
    )
