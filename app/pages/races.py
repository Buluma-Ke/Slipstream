from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify


def layout():
    return html.Div([

        # Header row
        html.Div([
            html.Div('Races', className='home-page-title'),
            html.Div([
                # Season pill
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

                # Race pill
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

        # Content
        dcc.Loading(type='circle', color='#E8002D', children=
            html.Div(id='races-content', className='home-wrapper',
                     style={'paddingTop': '0'})
        ),

    ], className='home-wrapper', style={'paddingBottom': '0'})