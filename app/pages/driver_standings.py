from dash import html, dcc
from dash_iconify import DashIconify

def layout():
    return html.Div([
        # Header Row
        html.Div([
            html.Div('Driver Standings', className='home-page-title'),
            html.Div([
                html.Div([
                    DashIconify(icon='tabler:flag', width=13,
                                style={'marginRight': '5px', 'color': '#E8002D'}),
                    html.Span('Season', className='pill-label',
                              style={'marginBottom': '0', 'marginRight': '6px'}),
                    html.Span(id='drv-standings-pill-year', children='2025'),
                ], className='year-pill-single', id='drv-standings-year-toggle'),
                
                html.Div(
                    [html.Div(str(y),
                              id={'type': 'drv-standings-year-pill', 'index': y},
                              className='year-dropdown-item')
                     for y in range(2025, 2017, -1)],
                    id='drv-standings-year-dropdown',
                    className='year-pill-menu',
                    style={'display': 'none'},
                ),
                
                html.Div(id='drv-standings-year-overlay',
                         className='year-pill-overlay',
                         style={'display': 'none'}, n_clicks=0),
            ], style={'position': 'relative', 'display': 'flex',
                      'alignItems': 'center', 'gap': '8px'}),
        ], className='home-top-row'),

        # Main Layout Grid
        html.Div([
            dcc.Store(id='drv-standings-data'),
            
            # Left — standings table
            html.Div(
                html.Div(id='drv-standings-content'),
                className='drv-left',
            ),

            # Right — evolution charts stacked
            dcc.Loading(
                type='circle', 
                color='#E8002D', 
                children=[
                    html.Div([
                        dcc.Graph(
                            id='drv-points-evolution',
                            config={'displayModeBar': False, 'responsive': True},
                            style={'height': '400px', 'marginBottom': '8px', 'width': '100%'}
                        ),
                        dcc.Graph(
                            id='drv-ranking-evolution',
                            config={'displayModeBar': False, 'responsive': True},
                            style={'height': '500px', 'marginBottom': '8px', 'width': '100%'}
                        ),
                    ], className='drv-right'),
                ]
            ),

            # Bottom — Full width stats chart
            html.Div([
                dcc.Graph(
                    id='drv-stats-chart',
                    config={'displayModeBar': False, 'responsive': True},
                    style={'height': '500px', 'width': '100%'}
                ),
                dcc.Graph(id='drv-points-distribution',
                    config={'displayModeBar': False, 'responsive': True},
                    style={'height': '600px', 'width': '100%'}), 
            ], className='drv-stats-full'
            ),

        ], className='drv-standings-layout'),

    ], className='home-wrapper')