from dash import html, dcc
import dash_bootstrap_components as dbc


def layout():
    return html.Div([

        # Selector row
        html.Div([
            html.Div([
                html.Div('Year', className='selector-label'),
                dcc.Dropdown(
                    id='dd-year',
                    options=[{'label': y, 'value': y} for y in range(2025, 2017, -1)],
                    value=2023,
                    clearable=False,
                ),
            ], className='selector-col year'),
            html.Div([
                html.Div('Event', className='selector-label'),
                dcc.Dropdown(id='dd-event', clearable=False),
            ], className='selector-col event'),
            html.Div([
                html.Div('Session', className='selector-label'),
                dcc.Dropdown(
                    id='dd-session',
                    options=[
                        {'label': 'Race',              'value': 'R'},
                        {'label': 'Qualifying',        'value': 'Q'},
                        {'label': 'Sprint',            'value': 'S'},
                        {'label': 'Sprint Qualifying', 'value': 'SQ'},
                        {'label': 'FP1',               'value': 'FP1'},
                        {'label': 'FP2',               'value': 'FP2'},
                        {'label': 'FP3',               'value': 'FP3'},
                    ],
                    value='R',
                    clearable=False,
                ),
            ], className='selector-col session'),
            html.Div([
                html.Div('\u00a0', className='selector-label'),
                dbc.Button('LOAD', id='btn-load'),
            ], className='selector-col btn'),
            html.Div([
                html.Div(id='selection-display'),
                html.Div(id='session-status'),
                dbc.Alert(
                    id='session-confirm',
                    color='success',
                    is_open=False,
                    className='mb-0',
                ),
            ], className='selector-col status'),

            # Stat pills — right side of selector row
            html.Div([
                html.Div(id='stat-fastest', className='stat-pill',
                         children=[html.Div('Fastest Lap', className='label'),
                                   html.Div('—', className='value')]),
                html.Div(id='stat-laps', className='stat-pill',
                         children=[html.Div('Total Laps', className='label'),
                                   html.Div('—', className='value')]),
                html.Div(id='stat-drivers', className='stat-pill',
                         children=[html.Div('Drivers', className='label'),
                                   html.Div('—', className='value')]),
                html.Div(id='stat-team', className='stat-pill',
                         children=[html.Div('Fastest Team', className='label'),
                                   html.Div('—', className='value')]),
            ], style={'display': 'flex', 'marginLeft': 'auto', 'alignItems': 'center'}),

        ], className='selector-row'),

        # Chart tabs
        dbc.Tabs([
            dbc.Tab(
                dcc.Graph(id='chart-lap-dist',
                          config={'displayModeBar': False},
                          style={'height': '73vh'}),
                label='Lap Times',
            ),
            dbc.Tab(
                dcc.Graph(id='chart-strategy',
                          config={'displayModeBar': False},
                          style={'height': '73vh'}),
                label='Strategy',
            ),
            dbc.Tab(
                html.Div([
                    html.Div([
                        html.Div('Driver A', className='selector-label mt-2'),
                        dcc.Dropdown(id='dd-delta-a', clearable=False),
                        html.Div('Driver B', className='selector-label mt-2'),
                        dcc.Dropdown(id='dd-delta-b', clearable=False),
                    ], className='tab-sidebar',
                       style={'width': '140px', 'display': 'inline-block',
                              'verticalAlign': 'top'}),
                    html.Div(
                        dcc.Graph(id='chart-delta',
                                  config={'displayModeBar': False},
                                  style={'height': '73vh'}),
                        style={'display': 'inline-block',
                               'width': 'calc(100% - 148px)',
                               'verticalAlign': 'top'}),
                ]),
                label='Delta',
            ),
            dbc.Tab(
                html.Div([
                    html.Div([
                        html.Div('Driver', className='selector-label mt-2'),
                        dcc.Dropdown(id='dd-tel-driver', clearable=False),
                        html.Div('Lap', className='selector-label mt-2'),
                        dcc.Dropdown(id='dd-tel-lap', clearable=False),
                    ], className='tab-sidebar',
                       style={'width': '140px', 'display': 'inline-block',
                              'verticalAlign': 'top'}),
                    html.Div(
                        dcc.Graph(id='chart-telemetry',
                                  config={'displayModeBar': False},
                                  style={'height': '73vh'}),
                        style={'display': 'inline-block',
                               'width': 'calc(100% - 148px)',
                               'verticalAlign': 'top'}),
                ]),
                label='Telemetry',
            ),
            dbc.Tab(
                html.Div([
                    html.Div([
                        html.Div('Driver', className='selector-label mt-2'),
                        dcc.Dropdown(id='dd-map-driver', clearable=False),
                        html.Div('Lap', className='selector-label mt-2'),
                        dcc.Dropdown(id='dd-map-lap', clearable=False),
                    ], className='tab-sidebar',
                       style={'width': '140px', 'display': 'inline-block',
                              'verticalAlign': 'top'}),
                    html.Div(
                        dcc.Graph(id='chart-map',
                                  config={'displayModeBar': False},
                                  style={'height': '73vh'}),
                        style={'display': 'inline-block',
                               'width': 'calc(100% - 148px)',
                               'verticalAlign': 'top'}),
                ]),
                label='Track Map',
            ),
        ]),
    ])