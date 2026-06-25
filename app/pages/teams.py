from dash import html, dcc
from dash_iconify import DashIconify


def layout():
    return html.Div([

        # Header row
        html.Div([
            html.Div('Teams', className='home-page-title'),
            html.Div([
                # Season pill
                html.Div([
                    DashIconify(icon='tabler:flag', width=13,
                                style={'marginRight': '5px', 'color': '#E8002D'}),
                    html.Span('Season', className='pill-label',
                              style={'marginBottom': '0', 'marginRight': '6px'}),
                    html.Span(id='teams-pill-year-display', children='2025'),
                ], className='year-pill-single', id='teams-year-pill-toggle'),
                html.Div(
                    [html.Div(str(y),
                              id={'type': 'teams-year-pill', 'index': y},
                              className='year-dropdown-item')
                     for y in range(2025, 2017, -1)],
                    id='teams-year-pill-dropdown',
                    className='year-pill-menu',
                    style={'display': 'none'},
                ),
                html.Div(id='teams-year-overlay', className='year-pill-overlay',
                         style={'display': 'none'}, n_clicks=0),

                # Team pill
                html.Div([
                    DashIconify(icon='tabler:users', width=13,
                                style={'marginRight': '5px', 'color': '#E8002D'}),
                    html.Span('Team', className='pill-label',
                              style={'marginBottom': '0', 'marginRight': '6px'}),
                    html.Span(id='teams-pill-team-display', children='Select'),
                ], className='year-pill-single', id='teams-team-pill-toggle',
                   style={'marginLeft': '8px'}),
                html.Div(
                    id='teams-team-pill-dropdown',
                    className='year-pill-menu',
                    style={'display': 'none'},
                ),
                html.Div(id='teams-team-overlay', className='year-pill-overlay',
                         style={'display': 'none'}, n_clicks=0),

            ], style={'position': 'relative', 'display': 'flex',
                      'alignItems': 'center', 'gap': '4px'}),
        ], className='home-top-row'),

        # Content Loader Wrapper Container
        dcc.Loading(type='circle', color='#E8002D', children=[
            # Hero and Stats section
            html.Div(id='teams-hero-content'),
            html.Div(id='teams-stats-cards'),

            # Graphs Grid (Controlled by callback style)
            html.Div([
                # Column 1
                html.Div([
                    html.Div([
                        html.Div("Season Performance", className='card-label'),
                        html.Div([
                            dcc.Graph(id='teams-graph-radial', config={'displayModeBar': False}, style={'width': '260px'}),
                            html.Div(id='teams-radial-legend-container')
                        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'width': '100%'})
                    ], className='info-card', style={'marginBottom': '10px'}),

                    html.Div([html.Div("Finish Positions in Points", className='card-label'), dcc.Graph(id='teams-graph-donut', config={'displayModeBar': False})], className='info-card'),
                ], style={'flex': '1'}),

                # Column 2
                html.Div([
                    html.Div([html.Div("Finish Positions Distribution", className='card-label'), dcc.Graph(id='teams-graph-dist', config={'displayModeBar': False})], className='info-card', style={'marginBottom': '10px'}),
                    html.Div([html.Div("Points Evolution", className='card-label'), dcc.Graph(id='teams-graph-evo', config={'displayModeBar': False})], className='info-card'),
                ], style={'flex': '1.5'})
            ], id='teams-graphs-grid', style={'display': 'none'})
        ]),

    ], className='home-wrapper')
