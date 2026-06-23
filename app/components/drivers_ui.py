# app/components/drivers_ui.py
from dash import html, dcc

import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Assume your shared layout dictionaries are imported here
TRANSPARENT = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

def render_driver_hero(year: int, full_name: str, team: str, team_color: str, logo_file: str) -> html.Div:
    return html.Div([
        html.Div([
            html.Div(f'{year} Season', style={'fontSize': '0.6rem', 'color': '#888', 'letterSpacing': '0.15em',
                                              'textTransform': 'uppercase', 'fontFamily': 'Titillium Web', 'marginBottom': '4px'}),
            html.Div(full_name, style={'fontFamily': 'Titillium Web', 'fontSize': '1.8rem', 'fontWeight': '900',
                                        'color': team_color, 'lineHeight': '1'}),
            html.Div(team, style={'fontSize': '0.7rem', 'color': '#888', 'fontFamily': 'Titillium Web', 'marginTop': '4px'}),
        ], style={'flex': '1'}),
        html.Div(
            html.Img(src=f'/assets/logos/{logo_file}.avif', style={'height': '36px', 'objectFit': 'contain'}) if logo_file else html.Div(),
            style={'display': 'flex', 'alignItems': 'center'},
        ),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
              'background': f'linear-gradient(135deg, rgba(0,0,0,0.8), {team_color}22)', 'border': f'1px solid {team_color}44',
              'borderLeft': f'3px solid {team_color}', 'borderRadius': '6px', 'padding': '14px 16px', 'marginBottom': '16px'})


def make_stat_card(label: str, value: any, sub: str = '', team_color: str = '#FBF9E4', accent: bool = False) -> html.Div:

    return html.Div([
        html.Div([
            html.Div(label, className='card-label'),
            html.Div(str(value), className='card-value', style={'color': team_color if accent else '#FBF9E4'}),
            html.Div(sub, className='card-sub') if sub else None,
        ]),
    ], className='info-card')


def make_radial_bar_chart(drv_results: pd.DataFrame, wins: int, podiums: int, dnfs: int, team_color: str):
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
            line=dict(color='#111827', width=10),
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
                    width=10,
                    shape='spline' # ⚡ Removed 'cmid=0' clean here
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


def make_distribution_chart(drv_results: pd.DataFrame, team_color: str) -> go.Figure:
    pos_counts = drv_results['Position'].value_counts().sort_index()
    fig = go.Figure(go.Bar(
        y=[f"P{i}" for i in range(1, 21)],
        x=[pos_counts.get(i, 0) for i in range(1, 21)],
        orientation='h',
        marker=dict(color=[team_color if pos_counts.get(i, 0) > 0 else '#222' for i in range(1, 21)])
    ))
    return fig.update_layout(margin=dict(l=40, r=10, t=30, b=10), height=500,
                             yaxis=dict(autorange="reversed", color='#888'), xaxis=dict(visible=False), **TRANSPARENT)

def make_points_donut(drv_results: pd.DataFrame, team_color: str) -> go.Figure:
    in_pts = len(drv_results[drv_results['Points'] > 0])
    total = len(drv_results)
    pts_pct = round((in_pts / total) * 100, 1) if total > 0 else 0
    fig = go.Figure(data=[go.Pie(labels=['Points', 'No Points'], values=[in_pts, total - in_pts], hole=.7, marker=dict(colors=[team_color, '#222']), textinfo='none')])

    return fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=30, b=10), height=250, annotations=[dict(text=f'{pts_pct}%',
                                                                                                                  x=0.5, y=0.5,
                                                                                                                  font_size=20,
                                                                                                                  font_family="Titillium Web",
                                                                                                                  font_color="white",
                                                                                                                  showarrow=False)], **TRANSPARENT)

def make_points_evolution(drv_results: pd.DataFrame, team_color: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=drv_results['RoundNumber'], y=drv_results['Points'].cumsum(), mode='lines+markers', line=dict(color=team_color)))

    return fig.update_layout(margin=dict(l=40, r=10, t=30, b=30), height=300, **TRANSPARENT)
