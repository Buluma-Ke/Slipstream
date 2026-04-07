from dash import html, dcc, callback, Output, Input
from dash_iconify import DashIconify

def layout():
    return html.Div([

        # Header row
        html.Div([
            html.Div('Standings', className='home-page-title'),
            html.Div([
                html.Div([
                    DashIconify(icon='tabler:flag', width=13,
                                style={'marginRight': '5px', 'color': '#E8002D'}),
                    html.Span('Season', className='pill-label',
                              style={'marginBottom': '0', 'marginRight': '6px'}),
                    html.Span(id='standings-pill-year-display', children='2025'),
                ], className='year-pill-single', id='standings-year-pill-toggle'),
                html.Div(
                    [html.Div(str(y),
                              id={'type': 'standings-year-pill', 'index': y},
                              className='year-dropdown-item')
                     for y in range(2025, 2017, -1)],
                    id='standings-year-pill-dropdown',
                    className='year-pill-menu',
                    style={'display': 'none'},
                ),
                html.Div(
                    id='standings-year-overlay',
                    className='year-pill-overlay',
                    style={'display': 'none'},
                    n_clicks=0,
                ),
            ], style={'position': 'relative', 'display': 'flex',
                      'alignItems': 'center', 'gap': '8px'}),
        ], className='home-top-row'),

        # Two tabs — Drivers / Constructors
        dcc.Tabs([
            dcc.Tab(
                html.Div(id='standings-drivers-content',
                         className='standings-table-wrapper'),
                label='Drivers',
                className='standings-tab',
                selected_className='standings-tab-active',
            ),
            dcc.Tab(
                html.Div(id='standings-constructors-content',
                         className='standings-table-wrapper'),
                label='Constructors',
                className='standings-tab',
                selected_className='standings-tab-active',
            ),
        ], className='standings-tabs'),

    ], className='home-wrapper')