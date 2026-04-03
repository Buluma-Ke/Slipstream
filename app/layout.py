import dash_bootstrap_components as dbc
from dash import dcc, html


def build_layout():
    return html.Div([

        dcc.Store(id='store-laps', storage_type='memory'),

        # Navbar
        dbc.Navbar(
            dbc.Container([
                html.Span('SLIPSTREAM', className='navbar-brand'),
                html.Span('F1 ANALYTICS', className='nav-subtitle ms-3'),
            ], fluid=True),
            className='mb-2',
        ),

        dbc.Container([

            # Session selector
            dbc.Card(dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div('Year', className='selector-label'),
                        dcc.Dropdown(
                            id='dd-year',
                            options=[{'label': y, 'value': y} for y in range(2025, 2017, -1)],
                            value=2023,
                            clearable=False,
                        ),
                    ], md=2),
                    dbc.Col([
                        html.Div('Event', className='selector-label'),
                        dcc.Dropdown(id='dd-event', clearable=False),
                    ], md=5),
                    dbc.Col([
                        html.Div('Session', className='selector-label'),
                        dcc.Dropdown(
                            id='dd-session',
                            options=[
                                {'label': 'Race', 'value': 'R'},
                                {'label': 'Qualifying', 'value': 'Q'},
                                {'label': 'Sprint', 'value': 'S'},
                                {'label': 'Sprint Qualifying', 'value': 'SQ'},
                                {'label': 'FP1', 'value': 'FP1'},
                                {'label': 'FP2', 'value': 'FP2'},
                                {'label': 'FP3', 'value': 'FP3'},
                            ],
                            value='R',
                            clearable=False,
                        ),
                    ], md=2),
                    dbc.Col([
                        html.Div('\u00a0', className='selector-label'),
                        dbc.Button('LOAD', id='btn-load', className='w-100'),
                    ], md=2),
                ], align='end'),
                dbc.Row([
                    dbc.Col(html.Div(id='selection-display', className='mt-1'), md=8),
                    dbc.Col(html.Div(id='session-status', className='mt-1 text-end'), md=4),
                ]),
                dbc.Alert(id='session-confirm', color='success', className='mt-2 py-1 mb-0', is_open=False),
            ]), className='mb-2'),

            # Stat cards
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div('Fastest Lap', className='stat-label'),
                    html.Div('—', className='stat-value', id='stat-fastest'),
                ], className='stat-card'), md=3),
                dbc.Col(html.Div([
                    html.Div('Total Laps', className='stat-label'),
                    html.Div('—', className='stat-value', id='stat-laps'),
                ], className='stat-card'), md=3),
                dbc.Col(html.Div([
                    html.Div('Drivers', className='stat-label'),
                    html.Div('—', className='stat-value', id='stat-drivers'),
                ], className='stat-card'), md=3),
                dbc.Col(html.Div([
                    html.Div('Fastest Team', className='stat-label'),
                    html.Div('—', className='stat-value', id='stat-team'),
                ], className='stat-card'), md=3),
            ], className='mb-2 g-2'),

            # Chart tabs
            dbc.Tabs([
                dbc.Tab(
                    dcc.Graph(id='chart-lap-dist', config={'displayModeBar': False},
                              style={'height': '60vh'}),
                    label='Lap Times',
                ),
                dbc.Tab(
                    dcc.Graph(id='chart-strategy', config={'displayModeBar': False},
                              style={'height': '60vh'}),
                    label='Strategy',
                ),
                dbc.Tab(
                    dbc.Row([
                        dbc.Col([
                            html.Div('Driver A', className='selector-label mt-2'),
                            dcc.Dropdown(id='dd-delta-a', clearable=False),
                            html.Div('Driver B', className='selector-label mt-2'),
                            dcc.Dropdown(id='dd-delta-b', clearable=False),
                        ], md=2),
                        dbc.Col(
                            dcc.Graph(id='chart-delta', config={'displayModeBar': False},
                                      style={'height': '60vh'}),
                            md=10
                        ),
                    ]),
                    label='Delta',
                ),
                dbc.Tab(
                    dbc.Row([
                        dbc.Col([
                            html.Div('Driver', className='selector-label mt-2'),
                            dcc.Dropdown(id='dd-tel-driver', clearable=False),
                            html.Div('Lap', className='selector-label mt-2'),
                            dcc.Dropdown(id='dd-tel-lap', clearable=False),
                        ], md=2),
                        dbc.Col(
                            dcc.Graph(id='chart-telemetry', config={'displayModeBar': False},
                                      style={'height': '60vh'}),
                            md=10
                        ),
                    ]),
                    label='Telemetry',
                ),
                dbc.Tab(
                    dbc.Row([
                        dbc.Col([
                            html.Div('Driver', className='selector-label mt-2'),
                            dcc.Dropdown(id='dd-map-driver', clearable=False),
                            html.Div('Lap', className='selector-label mt-2'),
                            dcc.Dropdown(id='dd-map-lap', clearable=False),
                        ], md=2),
                        dbc.Col(
                            dcc.Graph(id='chart-map', config={'displayModeBar': False},
                                      style={'height': '60vh'}),
                            md=10
                        ),
                    ]),
                    label='Track Map',
                ),
            ]),

        ], fluid=True),
    ])