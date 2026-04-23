from dash import dcc, html
import dash_bootstrap_components as dbc
from app.components.sidebar import build_sidebar


def build_layout():
    return html.Div([

        dcc.Store(id='store-laps', storage_type='memory'),
        dcc.Store(id='store-page', data='home', storage_type='memory'),
        dcc.Store(id='home-store-year', data=2025),
        dcc.Store(id='schedule-store-year', data=2025),
        dcc.Store(id='standings-store-year', data=2025),
        dcc.Store(id='drv-standings-store-year', data=2025),
        dcc.Store(id='con-standings-store-year', data=2025),
        dcc.Store(id='races-store-year', data=2025),
        dcc.Store(id='races-store-race', data=None),

        # Sidebar
        build_sidebar(),  

        # Main content
        html.Div([
                # Page content — home loads by default
                html.Div(id='page-content', className='page-content',
                        children=__import__('app.pages.home', fromlist=['layout']).layout()),

        ], id='main-content', className='main-content expanded'),

    ], style={'height': '100vh', 'overflow': 'hidden'})