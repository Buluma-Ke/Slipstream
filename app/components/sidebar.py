from dash import html
import dash_bootstrap_components as dbc

# Nav items — (id, icon, label)
NAV_ITEMS = [
    ('home',        '⊞',  'Home'),
    ('schedule',    '◎',  'Schedule'),
    ('standings',   '🏆', 'Standings'),
    ('races',       '🏎', 'Races'),
    ('drivers',     '👤', 'Drivers'),
    ('teams',       '🏗', 'Teams'),
    ('telemetry',   '📡', 'Telemetry'),
    ('predictions', '🔮', 'Predictions'),
]


def build_sidebar():
    nav_links = []
    for page_id, icon, label in NAV_ITEMS:
        nav_links.append(
            html.Div(
                id=f'nav-{page_id}',
                className='nav-item',
                children=[
                    html.Span(icon, className='nav-icon'),
                    html.Span(label, className='nav-label'),
                ],
                **{'data-page': page_id},
            )
        )

    return html.Div([
        # Logo area
        html.Div([
            html.Div('S', className='sidebar-logo-icon'),
            html.Div('SLIPSTREAM', className='sidebar-logo-text'),
        ], className='sidebar-logo'),

        # Nav links
        html.Div(nav_links, className='sidebar-nav'),

        # Collapse toggle at bottom
        html.Div(
            html.Span('◀', id='sidebar-toggle-icon'),
            id='sidebar-toggle',
            className='sidebar-toggle',
        ),

    ], id='sidebar', className='sidebar expanded')