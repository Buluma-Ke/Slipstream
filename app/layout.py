from dash import dcc, html
import dash_bootstrap_components as dbc
from app.components.sidebar import build_sidebar


def build_layout():
    return html.Div([

        dcc.Store(id='store-laps', storage_type='memory'),
        dcc.Store(id='store-page', data='home', storage_type='memory'),

        # Sidebar
        build_sidebar(),

        # Main content
        html.Div([
            # Top bar — stat pills
            html.Div([
                html.Div('F1 ANALYTICS', style={
                    'fontSize': '0.55rem',
                    'color': '#E8002D',
                    'letterSpacing': '0.3em',
                    'fontFamily': 'Barlow Condensed, sans-serif',
                }),
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
            ], className='top-bar'),

                # Page content — home loads by default
                html.Div(id='page-content', className='page-content',
                        children=__import__('app.pages.home', fromlist=['layout']).layout()),

        ], id='main-content', className='main-content'),

    ], style={'height': '100vh', 'overflow': 'hidden'})