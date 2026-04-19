from dash import html, dcc
from dash_iconify import DashIconify


def layout():
    return html.Div([
        html.Div([
            html.Div('Constructor Standings', className='home-page-title'),
            html.Div([
                html.Div([
                    DashIconify(icon='tabler:flag', width=13,
                                style={'marginRight': '5px', 'color': '#E8002D'}),
                    html.Span('Season', className='pill-label',
                              style={'marginBottom': '0', 'marginRight': '6px'}),
                    html.Span(id='con-standings-pill-year', children='2025'),
                ], className='year-pill-single', id='con-standings-year-toggle'),
                html.Div(
                    [html.Div(str(y),
                              id={'type': 'con-standings-year-pill', 'index': y},
                              className='year-dropdown-item')
                     for y in range(2025, 2017, -1)],
                    id='con-standings-year-dropdown',
                    className='year-pill-menu',
                    style={'display': 'none'},
                ),
                html.Div(id='con-standings-year-overlay',
                         className='year-pill-overlay',
                         style={'display': 'none'}, n_clicks=0),
            ], style={'position': 'relative', 'display': 'flex',
                      'alignItems': 'center', 'gap': '8px'}),
        ], className='home-top-row'),

        #Main Layout Grid
        html.Div([
            dcc.Store(id='const-standings-data'),

            #Left - Standings table
            html.Div(
                html.Div(id='con-standings-content'), 
                className='standings-table-wrapper',
            ),

             # Right — evolution charts stacked
            dcc.Loading(
                type='circle', 
                color='#E8002D', 
                children=[
                    html.Div([
                        dcc.Graph(
                            id='const-points-evolution',
                            config={'displayModeBar': False, 'responsive': True},
                            style={'height': '400px', 'marginBottom': '8px', 'width': '100%'}
                        ),
                        dcc.Graph(
                            id='const-ranking-evolution',
                            config={'displayModeBar': False, 'responsive': True},
                            style={'height': '500px', 'marginBottom': '8px', 'width': '100%'}
                        ),
                    ], className='const-right'),
                ]
            ),

            # Bottom — Full width stats chart
            html.Div([
                dcc.Graph(
                    id='const-stats-chart',
                    config={'displayModeBar': False, 'responsive': True},
                    style={'height': '500px', 'width': '100%'}
                ),
                dcc.Graph(id='const-points-distribution',
                    config={'displayModeBar': False, 'responsive': True},
                    style={'height': '600px', 'width': '100%'}), 
            ], className='const-stats-full'
            ),

        ], className='const-standings-layout'),

    ], className='home-wrapper')
           