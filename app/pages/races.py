from dash import html, dcc
from dash_iconify import DashIconify


def layout():
    return html.Div([

        # Header row
        html.Div([
            html.Div('Races', className='home-page-title'),
            html.Div([
                html.Div([
                    DashIconify(icon='tabler:flag', width=13,
                                style={'marginRight': '5px', 'color': '#E8002D'}),
                    html.Span('Season', className='pill-label',
                              style={'marginBottom': '0', 'marginRight': '6px'}),
                    html.Span(id='races-pill-year-display', children='2025'),
                ], className='year-pill-single', id='races-year-pill-toggle'),
                html.Div(
                    [html.Div(str(y),
                              id={'type': 'races-year-pill', 'index': y},
                              className='year-dropdown-item')
                     for y in range(2025, 2017, -1)],
                    id='races-year-pill-dropdown',
                    className='year-pill-menu',
                    style={'display': 'none'},
                ),
                html.Div(id='races-year-overlay', className='year-pill-overlay',
                         style={'display': 'none'}, n_clicks=0),

                html.Div([
                    DashIconify(icon='tabler:steering-wheel', width=13,
                                style={'marginRight': '5px', 'color': '#E8002D'}),
                    html.Span('Race', className='pill-label',
                              style={'marginBottom': '0', 'marginRight': '6px'}),
                    html.Span(id='races-pill-race-display', children='Select'),
                ], className='year-pill-single', id='races-race-pill-toggle',
                   style={'marginLeft': '8px'}),
                html.Div(
                    id='races-race-pill-dropdown',
                    className='year-pill-menu',
                    style={'display': 'none'},
                ),
                html.Div(id='races-race-overlay', className='year-pill-overlay',
                         style={'display': 'none'}, n_clicks=0),

            ], style={'position': 'relative', 'display': 'flex',
                      'alignItems': 'center', 'gap': '4px'}),
        ], className='home-top-row'),

        # Two column layout
        dcc.Loading(type='circle', color='#E8002D', children=
            html.Div([
                # Left — fastest laps table
                html.Div(
                    html.Div(id='races-content'),
                    className='drv-left',
                ),
                # Right — race pace evolution
                html.Div(
                    dcc.Graph(id='races-pace-evolution',
                              config={'displayModeBar': False, 'responsive': True},
                              style={'height': '85vh', 'width': '100%'}),
                    className='drv-right',
                ),
            ], className='drv-standings-layout'),
        ),
        dcc.Graph(id='races-pace-boxplot',
            config={'displayModeBar': False, 'responsive': True},
            style={'height': '400px', 'width': '100%', 'marginTop': '8px'}),

    ], className='home-wrapper', style={'paddingBottom': '0'})