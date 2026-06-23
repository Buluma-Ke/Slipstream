# app/components/drivers_ui.py
from dash import html, dcc
from app.constants import TEAM_COLORS, TEAM_LOGOS

import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Shared layout settings
TRANSPARENT = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

# String normalization layer to bridge data frames to your constant files
TEAM_NAME_MAP = {
    'Scuderia Ferrari': 'Ferrari',
    'Ferrari Scuderia': 'Ferrari',
    'Oracle Red Bull Racing': 'Red Bull',
    'Red Bull Racing': 'Red Bull',
    'Mercedes-AMG PETRONAS F1 Team': 'Mercedes',
    'Mercedes AMG': 'Mercedes',
    'McLaren Formula 1 Team': 'McLaren',
    'Aston Martin Aramco F1 Team': 'Aston Martin',
    'Alpine F1 Team': 'Alpine',
    'Sauber F1 Team': 'Sauber',
    'Kick Sauber': 'Sauber',
    'Haas F1 Team': 'Haas',
    'MoneyGram Haas F1 Team': 'Haas',
    'Visa Cash App RB Formula One Team': 'RB',
    'Racing Bulls': 'RB'
}

def _get_team_assets(raw_team_string: str):
    """Helper method to look up and apply centralized colors and logos safely."""
    norm_name = TEAM_NAME_MAP.get(raw_team_string, raw_team_string)
    color = TEAM_COLORS.get(norm_name, '#E8002D')  # Default F1 Red fallback
    logo = TEAM_LOGOS.get(norm_name, None)
    return color, logo


def render_driver_hero(year: int, full_name: str, team: str) -> html.Div:
    # Look up variables directly from constants matching structural requirements
    team_color, team_logo = _get_team_assets(team)

    return html.Div([
        html.Div([
            html.Div(f'{year} Season', style={'fontSize': '0.6rem', 'color': '#888', 'letterSpacing': '0.15em',
                                              'textTransform': 'uppercase', 'fontFamily': 'Titillium Web', 'marginBottom': '4px'}),
            html.Div(full_name, style={'fontFamily': 'Titillium Web', 'fontSize': '1.8rem', 'fontWeight': '900',
                                        'color': team_color, 'lineHeight': '1'}),
            html.Div(team, style={'fontSize': '0.7rem', 'color': '#888', 'fontFamily': 'Titillium Web', 'marginTop': '4px'}),
        ], style={'flex': '1'}),
        html.Div(
            html.Img(src=f'/assets/logos/{team_logo}.avif', style={'height': '36px', 'objectFit': 'contain'}) if team_logo else html.Div(),
            style={'display': 'flex', 'alignItems': 'center'},
        ),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
              'background': f'linear-gradient(135deg, rgba(0,0,0,0.8), {team_color}22)', 'border': f'1px solid {team_color}44',
              'borderLeft': f'3px solid {team_color}', 'borderRadius': '6px', 'padding': '14px 16px', 'marginBottom': '16px'})


def make_stat_card(label: str, value: any, team: str, sub: str = '', accent: bool = False) -> html.Div:
    team_color, _ = _get_team_assets(team)

    return html.Div([
        html.Div([
            html.Div(label, className='card-label'),
            html.Div(str(value), className='card-value', style={'color': team_color if accent else '#FBF9E4'}),
            html.Div(sub, className='card-sub') if sub else None,
        ]),
    ], className='info-card')


def make_radial_bar_chart(drv_results: pd.DataFrame, wins: int, podiums: int, dnfs: int, team: str):
    total_races = len(drv_results)
    pts_finishes = len(drv_results[drv_results['Points'] > 0]) if not drv_results.empty else 0

    perf_metrics = [
        {'label': 'Wins', 'val': wins, 'color': '#FFD700', 'ring_level': 4},
        {'label': 'Podiums', 'val': podiums, 'color': '#2563EB', 'ring_level': 3},
        {'label': 'In Points', 'val': pts_finishes, 'color': '#CBD5E1', 'ring_level': 2},
        {'label': 'DNF/DSQ', 'val': dnfs, 'color': '#DC2626', 'ring_level': 1}
    ]

    fig = go.Figure()
    starting_angle = 90  # 12 o'clock position

    for metric in perf_metrics:
        r_radius = metric['ring_level']
        pct = (metric['val'] / total_races) if total_races > 0 else 0
        angular_width = pct * 360

        # 1. Background Track
        full_theta = np.linspace(0, 360, 100)
        fig.add_trace(go.Scatterpolar(
            r=[r_radius] * len(full_theta),
            theta=full_theta,
            mode='lines',
            line=dict(color='#111827', width=8),
            hoverinfo='skip',
            showlegend=False
        ))

        # 2. Foreground Performance Arc
        if metric['val'] > 0:
            end_angle = starting_angle - angular_width
            arc_theta = np.linspace(starting_angle, end_angle, max(2, int(angular_width)))

            fig.add_trace(go.Scatterpolar(
                r=[r_radius] * len(arc_theta),
                theta=arc_theta,
                mode='lines',
                line=dict(
                    color=metric['color'],
                    width=8,
                    shape='spline'
                ),
                hoverinfo='skip',
                showlegend=False
            ))

    fig.update_layout(
        polar=dict(
            hole=0.2,
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=False, range=[0.6, 4.3]),
            angularaxis=dict(visible=False, direction="clockwise", period=360)
        ),
        xaxis=dict(visible=False, showgrid=False, zeroline=False),
        yaxis=dict(visible=False, showgrid=False, zeroline=False),
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,
        width=260,
        **TRANSPARENT
    )

    # 3. Text Side-Legend Generation
    legend_items = html.Div([
        html.Div([
            html.Div(style={'width': '12px', 'height': '12px', 'borderRadius': '50%', 'backgroundColor': m['color'], 'marginRight': '8px'}),
            html.Span(f"{m['label']}: ", style={'color': '#888', 'fontSize': '0.85rem', 'fontFamily': 'Titillium Web'}),
            html.Span(str(m['val']), style={'color': '#FFF', 'fontWeight': 'bold', 'marginLeft': '4px', 'fontFamily': 'Titillium Web'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '6px'})
        for m in perf_metrics
    ], style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'paddingLeft': '20px'})

    return fig, legend_items


def make_distribution_chart(drv_results: pd.DataFrame, team: str) -> go.Figure:
    team_color, _ = _get_team_assets(team)
    pos_counts = drv_results['Position'].value_counts().sort_index()

    fig = go.Figure(go.Bar(
        y=[f"P{i}" for i in range(1, 21)],
        x=[pos_counts.get(i, 0) for i in range(1, 21)],
        orientation='h',
        marker=dict(color=[team_color if pos_counts.get(i, 0) > 0 else '#222' for i in range(1, 21)])
    ))
    return fig.update_layout(margin=dict(l=40, r=10, t=30, b=10), height=500,
                             yaxis=dict(autorange="reversed", color='#888'), xaxis=dict(visible=False), **TRANSPARENT)


# def make_points_donut(drv_results: pd.DataFrame, team: str) -> go.Figure:
#     team_color, _ = _get_team_assets(team)
#     in_pts = len(drv_results[drv_results['Points'] > 0])
#     total = len(drv_results)
#     pts_pct = round((in_pts / total) * 100, 1) if total > 0 else 0

#     fig = go.Figure(data=[go.Pie(labels=['Points', 'No Points'], values=[in_pts, total - in_pts], hole=.7, marker=dict(colors=[team_color, '#222']), textinfo='none')])

#     return fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=30, b=10), height=250, annotations=[dict(text=f'{pts_pct}%',
#                                                                                                                 x=0.5, y=0.5,
#                                                                                                                 font_size=20,
#                                                                                                                 font_family="Titillium Web",
#                                                                                                                 font_color="white"])

def make_points_donut(drv_results: pd.DataFrame, team: str) -> go.Figure:
    team_color, _ = _get_team_assets(team)
    in_pts = len(drv_results[drv_results['Points'] > 0])
    total = len(drv_results)
    pts_pct = round((in_pts / total) * 100, 1) if total > 0 else 0

    fig = go.Figure(data=[go.Pie(
        labels=['Points', 'No Points'],
        values=[in_pts, total - in_pts],
        hole=.7,
        marker=dict(colors=[team_color, '#222']),
        textinfo='none'
    )])

    return fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        height=250,
        annotations=[dict(
            text=f'{pts_pct}%',
            x=0.5,
            y=0.5,
            showarrow=False,  # ⚡ Prevents default arrow rendering inside the hole
            font=dict(        # ⚡ Standardized font property hierarchy block
                size=24,      # Slightly bumped to stand out inside the donut
                family="Titillium Web",
                color="white"
            )
        )],
        **TRANSPARENT
    )


def make_points_evolution(drv_results: pd.DataFrame, team: str) -> go.Figure:
    team_color, _ = _get_team_assets(team)
    fig = go.Figure()

    # Add the primary line + marker trace
    fig.add_trace(go.Scatter(
        x=drv_results['RoundNumber'],
        y=drv_results['Points'].cumsum(),
        mode='lines+markers',
        line=dict(color=team_color, width=2.5),
        marker=dict(size=6),
        hoverinfo='x+y'
    ))

    return fig.update_layout(
        margin=dict(l=40, r=15, t=30, b=30),
        height=300,
        # Clean up x-axis (No vertical gridlines, proper fonts nested in tickfont)
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            color='#666',
            tickfont=dict(family="Titillium Web"),
            tickmode='linear',
            dtick=5
        ),
        # Minimalist y-axis (Faint, ultra-thin horizontal rules)
        yaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='#222630',
            zeroline=False,
            color='#666',
            tickfont=dict(family="Titillium Web")   # ⚡ Fixed nested property path
        ),
        **TRANSPARENT
    )
