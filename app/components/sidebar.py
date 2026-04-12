from dash import html
from dash_iconify import DashIconify

NAV_ITEMS = [
    ('home',                     'tabler:layout-2',         'Home'),
    ('schedule',                 'tabler:calendar-event',   'Schedule'),
    ('driver-standings',         'tabler:trophy',           'Driver Standings'),
    ('constructor-standings',    'tabler:building-factory', 'Constructor'),
    ('races',                    'tabler:steering-wheel',   'Races'),
    ('drivers',                  'tabler:helmet',           'Drivers'),
    ('teams',                    'tabler:users-group',      'Teams'),
    ('telemetry',                'tabler:activity',         'Telemetry'),
    ('predictions',              'tabler:chart-dots',       'Predictions'),
]

def build_sidebar():
    nav_links = []
    for page_id, icon, label in NAV_ITEMS:
        nav_links.append(
            html.Div(
                id=f'nav-{page_id}',
                className='nav-item',
                children=[
                    DashIconify(icon=icon, width=18, className='nav-icon'),
                    html.Span(label, className='nav-label'),
                ],
                **{'data-page': page_id},
            )
        )

    return html.Div([
        html.Div([
            html.Div('S', className='sidebar-logo-icon'),
            html.Div('SLIPSTREAM', className='sidebar-logo-text'),
        ], className='sidebar-logo'),

        html.Div(nav_links, className='sidebar-nav'),

        html.Div([
            DashIconify(icon='tabler:chevrons-left', width=18,
                        id='sidebar-toggle-icon'),
            html.Span('Collapse', className='nav-label'),
        ], id='sidebar-toggle', className='sidebar-toggle nav-item'),

    ], id='sidebar', className='sidebar expanded')