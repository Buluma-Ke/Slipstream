# app/components/driver_standings_ui.py
from dash import html
import plotly.graph_objects as go
from app.constants import TEAM_COLORS, TEAM_LOGOS

THEME_TRANSPARENT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#FBF9E4', family='Titillium Web'),
)

AXIS_BLANK = dict(
    gridcolor='rgba(0,0,0,0)',
    title='',
    showline=False,
    zeroline=False,
    tickfont=dict(color='#444'),
)

def get_empty_fallback():
    return go.Figure().update_layout(**THEME_TRANSPARENT)

def build_hero_leader_card(leader, year: int):
    """Renders the featured showcase component for the top driver."""
    leader_team = leader['TeamName']
    leader_color = TEAM_COLORS.get(leader_team, '#444')
    leader_logo = TEAM_LOGOS.get(leader_team, None)

    return html.Div([
        html.Div([
            html.Div(f'{year} Championship Leader', style={'fontSize': '0.6rem', 'color': '#888', 'letterSpacing': '0.15em', 'textTransform': 'uppercase', 'fontFamily': 'Titillium Web, sans-serif', 'marginBottom': '8px'}),
            html.Div(leader['FullName'].split()[-1], style={'fontFamily': 'Titillium Web, sans-serif', 'fontSize': '2rem', 'fontWeight': '900', 'color': leader_color, 'lineHeight': '1'}),
            html.Div(f"{int(leader['Points'])} pts", style={'fontSize': '0.7rem', 'color': '#888', 'fontFamily': 'Titillium Web, sans-serif', 'marginTop': '4px'}),
        ], style={'flex': '1'}),
        html.Div(
            html.Img(src=f'/assets/logos/{leader_logo}.avif', style={'height': '32px', 'objectFit': 'contain'}) if leader_logo else html.Div(),
            style={'display': 'flex', 'alignItems': 'center'},
        ),
    ], style={
        'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
        'background': f'linear-gradient(135deg, rgba(0,0,0,0.8), {leader_color}22)',
        'border': f'1px solid {leader_color}44', 'borderLeft': f'3px solid {leader_color}',
        'borderRadius': '6px', 'padding': '14px 16px', 'marginBottom': '16px',
    })

def build_standings_table(standings, wins, year: int):
    """Constructs HTML markup table items."""
    rows = []
    for _, row in standings.iterrows():
        logo_file = TEAM_LOGOS.get(row['TeamName'], None)
        team_color = TEAM_COLORS.get(row['TeamName'], '#444')
        pos = int(row['Pos'])
        w = wins.get(row['Abbreviation'], 0)

        rows.append(html.Tr([
            html.Td(str(pos), className='pos'),
            html.Td(
                html.Img(src=f'/assets/logos/{logo_file}.avif', style={'height': '16px', 'width': '28px', 'objectFit': 'contain'})
                if logo_file else html.Div(style={'width': '4px', 'background': team_color}),
                style={'width': '36px', 'padding': '0 4px'},
            ),
            html.Td(row['Abbreviation'], className='driver-abbr'),
            html.Td(row['FullName'], className='driver-name'),
            html.Td(str(int(w)), className='driver-name', style={'textAlign': 'center'}),
            html.Td(f"{int(row['Points'])}", className='pts'),
        ], className='p1' if pos == 1 else ''))

    return html.Div([
        build_hero_leader_card(standings.iloc[0], year),
        html.Table([
            html.Thead(html.Tr([
                html.Th('POS'), html.Th(''), html.Th('DRV'), html.Th('NAME'),
                html.Th('WINS', style={'textAlign': 'center'}), html.Th('PTS'),
            ])),
            html.Tbody(rows),
        ], className='champ-table standings-full-table'),
    ])

# ── Figure Generation Handlers ──

def make_points_evolution_chart(all_results, drivers, rounds):
    fig = go.Figure()
    for drv in drivers:
        drv_data = all_results[all_results['Abbreviation'] == drv].sort_values('RoundNumber')
        team = drv_data.iloc[0]['TeamName'] if len(drv_data) > 0 else ''
        color = TEAM_COLORS.get(team, '#444')
        cumpts = drv_data.set_index('RoundNumber')['Points'].reindex(rounds).fillna(0).cumsum()

        fig.add_trace(go.Scatter(
            x=list(cumpts.index), y=list(cumpts.values), name=drv,
            line=dict(color=color, width=1.5), mode='lines+markers', marker=dict(size=4),
        ))
    return fig.update_layout(
        **THEME_TRANSPARENT, autosize=True,
        title=dict(text='Driver Standings Evolution', font=dict(color='#444', size=13)),
        xaxis=AXIS_BLANK | dict(range=[1, 24], autorange=False, showgrid=False, constrain='domain'),
        yaxis=AXIS_BLANK | dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=True, zerolinecolor='white'),
        showlegend=False, margin=dict(l=40, r=40, t=40, b=20),
    )

def make_ranking_evolution_chart(all_results, drivers, rounds, max_drivers):
    fig = go.Figure()
    valid_drivers = set(drivers)

    for drv in drivers:
        rankings = []
        for r in rounds:
            up_to = all_results[all_results['RoundNumber'] <= r]
            pts = up_to.groupby('Abbreviation')['Points'].sum().loc[lambda x: x.index.isin(valid_drivers)].sort_values(ascending=False)

            if drv in pts.index:
                rank = list(pts.index).index(drv) + 1
            elif rankings:
                rank = rankings[-1]
            else:
                rank = None
            rankings.append(rank)

        x_vals = [rounds[0] - 0.5] + rounds
        y_vals = [rankings[0]] + rankings

        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals, name=drv,
            line=dict(color=TEAM_COLORS.get(all_results[all_results['Abbreviation'] == drv].iloc[0]['TeamName'], '#444'), width=1.5, shape='spline', smoothing=0.9),
            mode='lines+markers', marker=dict(size=2),
        ))

        final_rank = rankings[-1] if rankings else None
        if final_rank:
            fig.add_annotation(
                x=rounds[-1], y=final_rank, text=drv, xanchor='left', showarrow=False,
                font=dict(color=TEAM_COLORS.get(all_results[all_results['Abbreviation'] == drv].iloc[0]['TeamName'], '#444'), size=9, family='Titillium Web'), xshift=6,
            )

    return fig.update_layout(
        **THEME_TRANSPARENT, autosize=True,
        title=dict(text='Driver Ranking Evolution', font=dict(color='#444', size=13)),
        xaxis=AXIS_BLANK | dict(tickvals=rounds, range=[rounds[0] - 1, rounds[-1]]),
        yaxis=AXIS_BLANK | dict(dtick=1, range=[max_drivers, 1], tickvals=list(range(1, max_drivers + 1)), showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)'),
        showlegend=False, margin=dict(l=40, r=60, t=40, b=20),
    )

def make_season_stats_chart(all_results, drivers, wins):
    podiums = all_results[all_results['Position'] <= 3].groupby('Abbreviation').size()
    points_finishes = all_results[all_results['Points'] > 0].groupby('Abbreviation').size()
    poles = all_results[all_results['GridPosition'] == 1].groupby('Abbreviation').size()
    dnfs = all_results[all_results['Status'].str.contains('DNF|Retired|Accident|Engine|Mechanical|Disqualified|DNS', case=False, na=False)].groupby('Abbreviation').size()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Wins', x=drivers, y=[wins.get(d, 0) for d in drivers], marker=dict(color='#6C5FA7')))
    fig.add_trace(go.Bar(name='Podiums', x=drivers, y=[podiums.get(d, 0) for d in drivers], marker=dict(color='#6B3779')))
    fig.add_trace(go.Bar(name='Finish in points', x=drivers, y=[points_finishes.get(d, 0) for d in drivers], marker=dict(color='#B24968')))
    fig.add_trace(go.Bar(name='Pole positions', x=drivers, y=[poles.get(d, 0) for d in drivers], marker=dict(color='#b33dc6')))
    fig.add_trace(go.Bar(name='DNF/DNS/DSQ', x=drivers, y=[-dnfs.get(d, 0) for d in drivers], marker=dict(color='#FA8573')))

    return fig.update_layout(
        **THEME_TRANSPARENT, autosize=True, title=dict(text='Season Statistics', font=dict(color='#444', size=13)),
        barmode='group', bargap=0.15, bargroupgap=0.1, xaxis=AXIS_BLANK,
        yaxis=AXIS_BLANK | dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)', font=dict(color='#444', size=10)),
        margin=dict(l=40, r=40, t=60, b=20),
    )

def make_points_distribution_chart(all_results):
    fig = go.Figure()
    unique_events = all_results[['RoundNumber', 'EventName']].drop_duplicates().sort_values('RoundNumber')

    for _, event in unique_events.iterrows():
        event_results = all_results[all_results['RoundNumber'] == event['RoundNumber']].sort_values('Position')
        event_clean_name = event['EventName'].replace(' Grand Prix', '')

        for _, driver_row in event_results.iterrows():
            if driver_row['Points'] <= 0:
                continue
            color = TEAM_COLORS.get(driver_row['TeamName'], '#444')
            fig.add_trace(go.Bar(
                name=driver_row['Abbreviation'], y=[event_clean_name], x=[driver_row['Points']],
                orientation='h', marker=dict(color=color, line=dict(color=color, width=1)),
                showlegend=False, hovertemplate=f"{driver_row['Abbreviation']} — {int(driver_row['Points'])} pts<extra></extra>",
            ))

    return fig.update_layout(
        **THEME_TRANSPARENT, autosize=True, title=dict(text='Points Distribution', font=dict(color='#444', size=13)),
        barmode='stack', xaxis=AXIS_BLANK,
        yaxis=dict(gridcolor='rgba(0,0,0,0)', title='', showline=False, zeroline=False, tickfont=dict(color='#444', size=10), autorange='reversed'),
        margin=dict(l=20, r=20, t=40, b=20), height=600,
    )
