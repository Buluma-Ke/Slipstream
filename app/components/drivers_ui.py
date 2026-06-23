# app/components/drivers_ui.py
from dash import html
import plotly.graph_objects as go
import pandas as pd

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

def make_radial_bar_chart(drv_results: pd.DataFrame, wins: int, podiums: int, dnfs: int, team_color: str) -> go.Figure:
    total_races = len(drv_results)
    pts_finishes = len(drv_results[drv_results['Points'] > 0])
    perf_metrics = {'Wins': {'val': wins, 'color': '#FFD700'}, 'Podiums': {'val': podiums, 'color': team_color},
                    'In Points': {'val': pts_finishes, 'color': '#22D3EE'}, 'DNF/DSQ': {'val': dnfs, 'color': '#EF4444'}}

    fig = go.Figure()
    for i, (label, data) in enumerate(perf_metrics.items()):
        r_val = 100 - (i * 20)
        fig.add_trace(go.Scatterpolar(r=[r_val, r_val], theta=[0, 360], mode='lines', line=dict(color='#222', width=12), hoverinfo='skip'))
        percentage = (data['val'] / total_races) * 360 if total_races > 0 else 0
        fig.add_trace(go.Scatterpolar(r=[r_val, r_val], theta=[0, percentage], mode='lines', line=dict(color=data['color'], width=12, shape='spline'), name=label))

    return fig.update_layout(polar=dict(hole=0.4, bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False),
                                        angularaxis=dict(visible=False)), showlegend=False, margin=dict(l=10, r=10, t=30, b=10), height=300, **TRANSPARENT)

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
