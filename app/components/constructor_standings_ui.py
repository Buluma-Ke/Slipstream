# app/components/constructor_standings_ui.py
from dash import html
import plotly.graph_objects as go
import pandas as pd

# Global styling configurations
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

def get_empty_fallback():
    return go.Figure().update_layout(**TRANSPARENT)

def build_constructor_table(standings: pd.DataFrame, wins: pd.Series, year: int, TEAM_COLORS: dict, TEAM_LOGOS: dict) -> html.Div:
    """Builds the Champion Hero Card and grid summary view."""
    if standings.empty:
        return html.Div('No data found for this season layout.', className='standings-empty')

    rows = []
    for _, row in standings.iterrows():
        logo_file = TEAM_LOGOS.get(row['TeamName'], None)
        team_color = TEAM_COLORS.get(row['TeamName'], '#444')
        pos = int(row['Pos'])
        w = wins.get(row['TeamName'], 0)

        rows.append(html.Tr([
            html.Td(str(pos), className='pos'),
            html.Td(
                html.Img(src=f'/assets/logos/{logo_file}.avif',
                         style={'height': '16px', 'width': '28px', 'objectFit': 'contain'})
                if logo_file else html.Div(style={'width': '4px', 'background': team_color}),
                style={'width': '36px', 'padding': '0 4px'},
            ),
            html.Td(row['TeamName']),
            html.Td(str(int(w)), className='driver-name', style={'textAlign': 'center'}),
            html.Td(f"{int(row['Points'])}", className='pts'),
        ], className='p1' if pos == 1 else ''))

    # Hero card assembly
    leader = standings.iloc[0]
    leader_team = leader['TeamName']
    leader_color = TEAM_COLORS.get(leader_team, '#444')
    leader_logo = TEAM_LOGOS.get(leader_team, None)

    hero = html.Div([
        html.Div([
            html.Div(f'{year} Constructors Champion',
                     style={'fontSize': '0.6rem', 'color': '#888', 'letterSpacing': '0.15em',
                            'textTransform': 'uppercase', 'fontFamily': 'Titillium Web, sans-serif', 'marginBottom': '8px'}),
            html.Div(leader_team,
                     style={'fontFamily': 'Titillium Web, sans-serif', 'fontSize': '2rem', 'fontWeight': '900',
                            'color': leader_color, 'lineHeight': '1'}),
            html.Div(f"{int(leader['Points'])} pts",
                     style={'fontSize': '0.7rem', 'color': '#888', 'fontFamily': 'Titillium Web, sans-serif', 'marginTop': '4px'}),
        ], style={'flex': '1'}),
        html.Div(
            html.Img(src=f'/assets/logos/{leader_logo}.avif', style={'height': '32px', 'objectFit': 'contain'})
            if leader_logo else html.Div(),
            style={'display': 'flex', 'alignItems': 'center'},
        ),
    ], style={
        'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
        'background': f'linear-gradient(135deg, rgba(0,0,0,0.8), {leader_color}22)',
        'border': f'1px solid {leader_color}44', 'borderLeft': f'3px solid {leader_color}',
        'borderRadius': '6px', 'padding': '14px 16px', 'marginBottom': '16px',
    })

    return html.Div([
        hero,
        html.Table([
            html.OnRead(html.Tr([
                html.Th('POS'), html.Th(''), html.Th('TEAM'),
                html.Th('WINS', style={'textAlign': 'center'}), html.Th('PTS'),
            ])),
            html.Tbody(rows),
        ], className='champ-table standings-full-table'),
    ])

def make_points_evolution_chart(all_results: pd.DataFrame, constructors: list, rounds: list, TEAM_COLORS: dict) -> go.Figure:
    fig = go.Figure()
    for team in constructors:
        team_data = all_results[all_results['TeamName'] == team].groupby('RoundNumber')['Points'].sum()
        color = TEAM_COLORS.get(team, '#444')
        cumpts = team_data.reindex(rounds).fillna(0).cumsum()
        fig.add_trace(go.Scatter(
            x=list(cumpts.index), y=list(cumpts.values),
            name=team, line=dict(color=color, width=1.5),
            mode='lines+markers', marker=dict(size=4),
        ))
    return fig.update_layout(
        **TRANSPARENT, autosize=True,
        title=dict(text='Constructor Standings Evolution', font=dict(color='#444', size=13)),
        xaxis=AXIS | dict(range=[1, max(rounds) if rounds else 24], autorange=False, showgrid=False, constrain='domain'),
        yaxis=AXIS | dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=True, zerolinecolor='white'),
        showlegend=False, margin=dict(l=40, r=40, t=40, b=20),
    )

def make_ranking_evolution_chart(all_results: pd.DataFrame, constructors: list, rounds: list, TEAM_COLORS: dict) -> go.Figure:
    fig = go.Figure()
    valid_constructors = set(constructors)

    for team in constructors:
        color = TEAM_COLORS.get(team, '#444')
        rankings = []

        for r in rounds:
            up_to = all_results[all_results['RoundNumber'] <= r]
            pts = up_to.groupby('TeamName')['Points'].sum().loc[lambda x: x.index.isin(valid_constructors)].sort_values(ascending=False)
            rank = list(pts.index).index(team) + 1 if team in pts.index else (rankings[-1] if rankings else None)
            rankings.append(rank)

        if not rankings or rankings[0] is None: continue
        x_vals = [rounds[0] - 0.5] + rounds
        y_vals = [rankings[0]] + rankings

        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals, name=team,
            line=dict(color=color, width=1.5, shape='spline', smoothing=0.9),
            mode='lines+markers', marker=dict(size=2),
        ))

        if rankings[-1]:
            short_name = team.split()[-1] if len(team) > 12 else team
            fig.add_annotation(
                x=rounds[-1], y=rankings[-1], text=short_name,
                xanchor='left', showarrow=False, font=dict(color=color, size=9, family='Titillium Web'), xshift=6,
            )

    actual_max = len(valid_constructors)
    return fig.update_layout(
        **TRANSPARENT, autosize=True,
        title=dict(text='Constructor Ranking Evolution', font=dict(color='#444', size=13)),
        xaxis=AXIS | dict(tickvals=rounds, range=[rounds[0] - 1, rounds[-1]] if rounds else [0, 24]),
        yaxis=AXIS | dict(dtick=1, range=[actual_max, 1], tickvals=list(range(1, actual_max + 1)),
                          showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=True, zerolinecolor='rgba(255, 255, 255, 0.1)'),
        showlegend=False, margin=dict(l=40, r=80, t=40, b=20),
    )

def make_season_stats_chart(all_results: pd.DataFrame, constructors: list, wins: pd.Series, TEAM_LOGOS: dict) -> go.Figure:
    podiums = all_results[all_results['Position'] <= 3].groupby('TeamName').size()
    points_finishes = all_results[all_results['Points'] > 0].groupby('TeamName').size()
    poles = all_results[all_results['GridPosition'] == 1].groupby('TeamName').size()
    dnfs = all_results[all_results['Status'].str.contains('DNF|Retired|Accident|Engine|Mechanical|Disqualified|DNS', case=False, na=False)].groupby('TeamName').size()

    fig = go.Figure()
    categories = [('Wins', wins, '#6C5FA7'), ('Podiums', podiums, '#6B3779'),
                  ('Finish in points', points_finishes, '#B24968'), ('Pole positions', poles, '#b33dc6')]

    for name, series, col in categories:
        fig.add_trace(go.Bar(name=name, x=constructors, y=[series.get(t, 0) for t in constructors], marker=dict(color=col)))

    fig.add_trace(go.Bar(name='DNF/DNS/DSQ', x=constructors, y=[-dnfs.get(t, 0) for t in constructors], marker=dict(color='#FA8573')))

    images = [dict(source=f'/assets/logos/{TEAM_LOGOS.get(t)}.avif', xref='x', yref='paper', x=i, y=-0.02,
                   sizex=0.6, sizey=0.08, xanchor='center', yanchor='top', layer='above')
              for i, t in enumerate(constructors) if TEAM_LOGOS.get(t)]

    return fig.update_layout(
        **TRANSPARENT, autosize=True, barmode='group', bargap=0.15, bargroupgap=0.1, images=images,
        title=dict(text='Season Statistics', font=dict(color='#444', size=13)),
        xaxis=AXIS | dict(tickvals=list(range(len(constructors))), ticktext=[''] * len(constructors)),
        yaxis=AXIS | dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=True, zerolinecolor='rgba(255, 255, 255, 0.1)'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)', font=dict(color='#444', size=10)),
        margin=dict(l=40, r=40, t=60, b=80),
    )

def make_points_distribution_chart(all_results: pd.DataFrame, TEAM_COLORS: dict) -> go.Figure:
    fig = go.Figure()
    unique_events = all_results[['RoundNumber', 'EventName']].drop_duplicates().sort_values('RoundNumber')

    for _, ev in unique_events.iterrows():
        event_results = all_results[all_results['RoundNumber'] == ev['RoundNumber']]
        team_pts = event_results.groupby('TeamName')['Points'].sum()
        event_name = ev['EventName'].replace(' Grand Prix', '')

        for team, pts in team_pts.items():
            if pts <= 0: continue
            color = TEAM_COLORS.get(team, '#444')
            fig.add_trace(go.Bar(
                name=team, y=[event_name], x=[pts], orientation='h',
                marker=dict(color=color, line=dict(color=color, width=1)),
                showlegend=False, hovertemplate=f"{team} — {int(pts)} pts<extra></extra>",
            ))

    return fig.update_layout(
        **TRANSPARENT, autosize=True, barmode='stack', xaxis=AXIS, height=600,
        title=dict(text='Points Distribution', font=dict(color='#444', size=13)),
        yaxis=dict(gridcolor='rgba(0,0,0,0)', title='', showline=False, zeroline=False, tickfont=dict(color='#444', size=10), autorange='reversed'),
        margin=dict(l=20, r=20, t=40, b=20),
    )
