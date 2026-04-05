from dash import html, dcc, callback, Output, Input
from dash_iconify import DashIconify
import fastf1
import os

# Maps event name keywords to track image filenames
TRACK_IMAGE_MAP = {
    'bahrain':        'bahrain',
    'saudi':          'saudi-arabia',
    'australian':      'australia',
    'japanese':          'japan',
    'chinese':          'china',
    'miami':          'miami',
    'emilia':         'emilia-romagna',
    'monaco':         'monaco',
    'canadian':         'canada',
    'spanish':          'spain',
    'austria':        'austria',
    'styria':         'styria',
    'britain':        'britain',
    'british':        'britain',
    'belgian':        'belgium',
    'hungarian':        'hungary',
    'netherlands':    'netherlands',
    'dutch':          'netherlands',
    'italy':          'italy',
    'italian':        'italy',
    'azerbaijan':     'azerbaijan',
    'singapore':      'singapore',
    'united states':  'united-states',
    'mexican':         'mexico',
    'são paulo':         'brazil',
    'são paulo':  'brazil',
    'sao paulo':  'brazil',
    'brazil':     'brazil',
    'brazilian':  'brazil',
    'las vegas':      'las-vegas',
    'mexico city': 'mexico',
    'las vegas':   'las-vegas',
    'abu dhabi':   'abu-dhabi',
    'miami':       'miami',
    'monaco':      'monaco',
    'qatar':          'qatar',
    'abu dhabi':      'abu-dhabi',
    'portugal':       'portugal',
    'france':         'france',
    'turkey':         'turkey',
    'tuscany':        'tuscany',
    'eifel':          'eifel',
    'russia':         'russia',
    'germany':        'germany',
}

COUNTRY_FLAGS = {
    'Bahrain':        '🇧🇭',
    'Saudi Arabia':   '🇸🇦',
    'Australia':      '🇦🇺',
    'Japan':          '🇯🇵',
    'China':          '🇨🇳',
    'United States':  '🇺🇸',
    'Italy':          '🇮🇹',
    'Monaco':         '🇲🇨',
    'Canada':         '🇨🇦',
    'Spain':          '🇪🇸',
    'Austria':        '🇦🇹',
    'United Kingdom': '🇬🇧',
    'Belgium':        '🇧🇪',
    'Hungary':        '🇭🇺',
    'Netherlands':    '🇳🇱',
    'Azerbaijan':     '🇦🇿',
    'Singapore':      '🇸🇬',
    'Mexico':         '🇲🇽',
    'Brazil':         '🇧🇷',
    'Qatar':          '🇶🇦',
    'United Arab Emirates': '🇦🇪',
    'Portugal':       '🇵🇹',
    'France':         '🇫🇷',
    'Turkey':         '🇹🇷',
    'Germany':        '🇩🇪',
    'Russia':         '🇷🇺',
}


def get_track_image(event_name):
    """Return image path if file exists, else None."""
    name_lower = event_name.lower()
    for keyword, filename in TRACK_IMAGE_MAP.items():
        if keyword in name_lower:
            for ext in ['avif', 'png', 'jpg', 'webp']:
                path = f'assets/tracks/{filename}.{ext}'
                if os.path.exists(path):
                    return f'/assets/tracks/{filename}.{ext}'
    return None


def make_race_card(round_num, event_name, country, date_start, date_end,
                   session_types, year):
    """Build one race card."""
    img_path = get_track_image(event_name)
    flag = COUNTRY_FLAGS.get(country, '🏁')

    # Format dates
    try:
        start_str = date_start.strftime('%d %b')
        end_str = date_end.strftime('%d %b %Y')
        date_str = f'{start_str} – {end_str}'
    except Exception:
        date_str = str(date_start)

    # Session type badges
    has_sprint = any('sprint' in s.lower() for s in session_types)

    badges = [
        html.Span(f'R{round_num}', className='round-badge'),
    ]
    if has_sprint:
        badges.append(html.Span('SPRINT', className='session-badge sprint'))

    return html.Div([
        # Left content
        html.Div([
            html.Div(badges, className='card-badges'),
            html.Div([
                html.Span(flag, style={'fontSize': '1.2rem', 'marginRight': '8px'}),
                html.Span(event_name.replace(' Grand Prix', ''),
                          className='race-card-name'),
            ], className='race-card-title'),
            html.Div(date_str, className='race-card-date'),
        ], className='race-card-left'),

        # Right — track image
        html.Div(
            html.Img(
                src=img_path,
                className='track-img',
            ) if img_path else html.Div(
                DashIconify(icon='tabler:road', width=40, color='#2a2a2a'),
                className='track-img-placeholder',
            ),
            className='race-card-right',
        ),

    ], className='race-card',
       id={'type': 'race-card', 'year': year, 'event': event_name},
       n_clicks=0)


def layout():
    return html.Div([
        # Header row
        html.Div([
            html.Div('Race Calendar', className='home-page-title'),
            html.Div([
                html.Div([
                    DashIconify(icon='tabler:flag', width=13,
                                style={'marginRight': '5px', 'color': '#E8002D'}),
                    html.Span('Season', className='pill-label',
                            style={'marginBottom': '0', 'marginRight': '6px'}),
                    html.Span(id='schedule-pill-year-display', children='2025'),
                ], className='year-pill-single', id='schedule-year-pill-toggle'),
                html.Div(
                    [html.Div(str(y),
                            id={'type': 'schedule-year-pill', 'index': y},
                            className='year-dropdown-item')
                    for y in range(2025, 2017, -1)],
                    id='schedule-year-pill-dropdown',
                    className='year-pill-menu',
                    style={'display': 'none'},
                ),
                html.Div(
                    id='schedule-year-overlay',
                    className='year-pill-overlay',
                    style={'display': 'none'},
                    n_clicks=0,
                ),
            ], style={'position': 'relative', 'display': 'flex',
                    'alignItems': 'center', 'gap': '8px'}),
        ], className='home-top-row'),
       

        # Race cards grid
        html.Div(id='schedule-cards', className='schedule-grid'),

    ], className='home-wrapper')