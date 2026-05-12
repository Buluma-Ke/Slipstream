from dash import html, dcc
from dash_iconify import DashIconify


def layout():
    return html.Div([

        # Header row
        html.Div([
            html.Div('Drivers', className='home-page-title'),
            html.Div([
                # Season pill
                html.Div([
                    DashIconify(icon='tabler:flag', width=13,
                                style={'marginRight': '5px', 'color': '#E8002D'}),
                    html.Span('Season', className='pill-label',
                              style={'marginBottom': '0', 'marginRight': '6px'}),
                    html.Span(id='drivers-pill-year-display', children='2025'),
                ], className='year-pill-single', id='drivers-year-pill-toggle'),
                html.Div(
                    [html.Div(str(y),
                              id={'type': 'drivers-year-pill', 'index': y},
                              className='year-dropdown-item')
                     for y in range(2025, 2017, -1)],
                    id='drivers-year-pill-dropdown',
                    className='year-pill-menu',
                    style={'display': 'none'},
                ),
                html.Div(id='drivers-year-overlay', className='year-pill-overlay',
                         style={'display': 'none'}, n_clicks=0),

                # Driver pill
                html.Div([
                    DashIconify(icon='tabler:helmet', width=13,
                                style={'marginRight': '5px', 'color': '#E8002D'}),
                    html.Span('Driver', className='pill-label',
                              style={'marginBottom': '0', 'marginRight': '6px'}),
                    html.Span(id='drivers-pill-driver-display', children='Select'),
                ], className='year-pill-single', id='drivers-driver-pill-toggle',
                   style={'marginLeft': '8px'}),
                html.Div(
                    id='drivers-driver-pill-dropdown',
                    className='year-pill-menu',
                    style={'display': 'none'},
                ),
                html.Div(id='drivers-driver-overlay', className='year-pill-overlay',
                         style={'display': 'none'}, n_clicks=0),

            ], style={'position': 'relative', 'display': 'flex',
                      'alignItems': 'center', 'gap': '4px'}),
        ], className='home-top-row'),

        # Content
        dcc.Loading(type='circle', color='#E8002D',
                    children=html.Div(id='drivers-content')),
        dcc.Loading(type='circle', color='#E8002D', children=[
            html.Div(id='drivers-hero-container'),
            html.Div(id='drivers-stats-cards-container'),

            # The Graph Grid Structure
            html.Div([
                # Left Column
                html.Div([
                    html.Div([
                        html.Div("Season Performance", className='card-label'),
                        dcc.Graph(id='graph-radial', config={'displayModeBar': False})
                    ], className='info-card', style={'marginBottom': '10px'}),

                    html.Div([
                        html.Div("Finish Positions in Points", className='card-label'),
                        dcc.Graph(id='graph-donut', config={'displayModeBar': False})
                    ], className='info-card'),
                ], style={'flex': '1'}),

                # Right Column
                html.Div([
                    html.Div([
                        html.Div("Finish Positions Distribution", className='card-label'),
                        dcc.Graph(id='graph-dist', config={'displayModeBar': False})
                    ], className='info-card', style={'marginBottom': '10px'}),

                    html.Div([
                        html.Div("Points Evolution", className='card-label'),
                        dcc.Graph(id='graph-evo', config={'displayModeBar': False})
                    ], className='info-card'),
                ], style={'flex': '1.5'})
            ], id='drivers-graphs-container', style={'display': 'none', 'gap': '10px', 'marginTop': '16px'})
        ]),

    ], className='home-wrapper')
