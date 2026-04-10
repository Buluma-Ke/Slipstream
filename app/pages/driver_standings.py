from dash import html, dcc
from dash_iconify import DashIconify


def layout():
    return html.Div([
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

        html.Div(id='drv-standings-content', className='standings-table-wrapper'),

    ], className='home-wrapper')