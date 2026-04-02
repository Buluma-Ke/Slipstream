import dash_bootstrap_components as dbc
from dash import dcc, html


def build_layout():
    return html.Div([

        # Session store — holds lap data in memory across callbacks
        dcc.Store(id='store-laps', storage_type='memory'),

        # Navbar
        dbc.Navbar(
            dbc.Container([
                html.Span('🏎 Slipstream', className='navbar-brand fw-bold fs-4'),
                html.Span('F1 Analytics', className='text-muted small ms-2'),
            ]),
            color='dark', dark=True, className='mb-4',
        ),

        dbc.Container([

            # Session selector
            dbc.Card(dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label('Year', className='fw-semibold small'),
                        dcc.Dropdown(
                            id='dd-year',
                            options=[{'label': y, 'value': y} for y in range(2025, 2017, -1)],
                            value=2023,
                            clearable=False,
                        ),
                    ], md=3),
                    dbc.Col([
                        html.Label('Event', className='fw-semibold small'),
                        dcc.Dropdown(id='dd-event', clearable=False),
                    ], md=6),
                    dbc.Col([
                        html.Label('Session', className='fw-semibold small'),
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
                    ], md=3),
                ]),
                dbc.Row(dbc.Col(
                    html.Div(id='selection-display', className='text-muted small mt-2'),
                )),
                dbc.Row(dbc.Col(
                    dbc.Button('Load session', id='btn-load', color='danger', className='mt-3'),
                )),
                html.Div(id='session-status', className='text-muted small mt-2'),
                dbc.Alert(id='session-confirm', color='success', className='mt-2 py-2', is_open=False),
            ]), className='mb-4'),

            # Stat cards
            dbc.Row([
                dbc.Col(dbc.Card([
                    html.P('Fastest lap', className='text-muted small mb-1'),
                    html.H5(id='stat-fastest', children='—'),
                ], body=True), md=3),
                dbc.Col(dbc.Card([
                    html.P('Total laps', className='text-muted small mb-1'),
                    html.H5(id='stat-laps', children='—'),
                ], body=True), md=3),
                dbc.Col(dbc.Card([
                    html.P('Drivers', className='text-muted small mb-1'),
                    html.H5(id='stat-drivers', children='—'),
                ], body=True), md=3),
                dbc.Col(dbc.Card([
                    html.P('Fastest team', className='text-muted small mb-1'),
                    html.H5(id='stat-team', children='—'),
                ], body=True), md=3),
            ], className='mb-4'),

            # Chart tabs
            dbc.Tabs([
                dbc.Tab(
                    dcc.Graph(id='chart-lap-dist', config={'displayModeBar': False}),
                    label='Lap times',
                ),
                dbc.Tab(
                    dcc.Graph(id='chart-strategy', config={'displayModeBar': False}),
                    label='Strategy',
                ),
                dbc.Tab(
                    dbc.Row([
                        dbc.Col([
                            html.Label('Driver A', className='fw-semibold small mt-3'),
                            dcc.Dropdown(id='dd-delta-a', clearable=False),
                            html.Label('Driver B', className='fw-semibold small mt-2'),
                            dcc.Dropdown(id='dd-delta-b', clearable=False),
                        ], md=3),
                        dbc.Col(
                            dcc.Graph(id='chart-delta', config={'displayModeBar': False}),
                            md=9
                        ),
                    ]),
                    label='Delta',
                ),
                dbc.Tab(
                    dbc.Row([
                        dbc.Col([
                            html.Label('Driver', className='fw-semibold small mt-3'),
                            dcc.Dropdown(id='dd-tel-driver', clearable=False),
                            html.Label('Lap', className='fw-semibold small mt-2'),
                            dcc.Dropdown(id='dd-tel-lap', clearable=False),
                        ], md=3),
                        dbc.Col(
                            dcc.Graph(id='chart-telemetry', config={'displayModeBar': False}),
                            md=9
                        ),
                    ]),
                    label='Telemetry',
                ),
                dbc.Tab(
                    dbc.Row([
                        dbc.Col([
                            html.Label('Driver', className='fw-semibold small mt-3'),
                            dcc.Dropdown(id='dd-map-driver', clearable=False),
                            html.Label('Lap', className='fw-semibold small mt-2'),
                            dcc.Dropdown(id='dd-map-lap', clearable=False),
                        ], md=3),
                        dbc.Col(
                            dcc.Graph(id='chart-map', config={'displayModeBar': False}),
                            md=9
                        ),
                    ]),
                    label='Track map',
                ),
            ]),

        ]),
    ])