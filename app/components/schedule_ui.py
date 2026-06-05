# app/components/schedule_ui.py
import os
from dash import html
from dash_iconify import DashIconify

TRACK_IMAGE_MAP = {
    'bahrain': 'bahrain', 'saudi': 'saudi-arabia', 'australian': 'australia',
    'japanese': 'japan', 'chinese': 'china', 'miami': 'miami',
    'emilia': 'emilia-romagna', 'monaco': 'monaco', 'canadian': 'canada',
    'spanish': 'spain', 'austria': 'austria', 'styria': 'styria',
    'britain': 'britain', 'british': 'britain', 'belgian': 'belgium',
    'hungarian': 'hungary', 'netherlands': 'netherlands', 'dutch': 'netherlands',
    'italy': 'italy', 'italian': 'italy', 'azerbaijan': 'azerbaijan',
    'singapore': 'singapore', 'united states': 'united-states', 'mexican': 'mexico',
    'são paulo': 'brazil', 'sao paulo': 'brazil', 'brazil': 'brazil',
    'brazilian': 'brazil', 'las vegas': 'las-vegas', 'mexico city': 'mexico',
    'abu dhabi': 'abu-dhabi', 'qatar': 'qatar', 'portugal': 'portugal',
    'france': 'france', 'turkey': 'turkey', 'tuscany': 'tuscany',
    'eifel': 'eifel', 'russia': 'russia', 'germany': 'germany',
}

COUNTRY_FLAGS = {
    'Bahrain': '🇧🇭', 'Saudi Arabia': '🇸🇦', 'Australia': '🇦🇺', 'Japan': '🇯🇵',
    'China': '🇨🇳', 'United States': '🇺🇸', 'Italy': '🇮🇹', 'Monaco': '🇲🇨',
    'Canada': '🇨🇦', 'Spain': '🇪🇸', 'Austria': '🇦🇹', 'United Kingdom': '🇬🇧',
    'Belgium': '🇧🇪', 'Hungary': '🇭🇺', 'Netherlands': '🇳🇱', 'Azerbaijan': '🇦🇿',
    'Singapore': '🇸🇬', 'Mexico': '🇲🇽', 'Brazil': '🇧🇷', 'Qatar': '🇶🇦',
    'United Arab Emirates': '🇦🇪', 'Portugal': '🇵🇹', 'France': '🇫🇷',
    'Turkey': '🇹🇷', 'Germany': '🇩🇪', 'Russia': '🇷🇺',
}

def get_track_image(event_name):
    """Safely looks up a matching racetrack diagram from assets."""
    name_lower = event_name.lower()
    for keyword, filename in TRACK_IMAGE_MAP.items():
        if keyword in name_lower:
            for ext in ['avif', 'png', 'jpg', 'webp']:
                path = f'assets/tracks/{filename}.{ext}'
                if os.path.exists(path):
                    return f'/assets/tracks/{filename}.{ext}'
    return None

def make_race_card(race_dict, year):
    """Constructs a clean structural grid layout cell card for a weekend."""
    event_name = race_dict['event_name']
    img_path = get_track_image(event_name)
    flag = COUNTRY_FLAGS.get(race_dict['country'], '🏁')

    try:
        start_str = race_dict['date_start'].strftime('%d %b')
        end_str = race_dict['date_end'].strftime('%d %b %Y')
        date_str = f'{start_str} – {end_str}'
    except Exception:
        date_str = str(race_dict['date_start'])

    has_sprint = any('sprint' in s.lower() for s in race_dict['session_types'])

    badges = [html.Span(f"R{race_dict['round_num']}", className='round-badge')]
    if has_sprint:
        badges.append(html.Span('SPRINT', className='session-badge sprint'))

    return html.Div([
        # Left Panel content metadata
        html.Div([
            html.Div(badges, className='card-badges'),
            html.Div([
                html.Span(flag, style={'fontSize': '1.2rem', 'marginRight': '8px'}),
                html.Span(event_name.replace(' Grand Prix', ''), className='race-card-name'),
            ], className='race-card-title'),
            html.Div(date_str, className='race-card-date'),
        ], className='race-card-left'),

        # Right Panel track vector image display
        html.Div(
            html.Img(src=img_path, className='track-img') if img_path else html.Div(
                DashIconify(icon='tabler:road', width=40, color='#2a2a2a'),
                className='track-img-placeholder',
            ),
            className='race-card-right',
        ),
    ], className='race-card', id={'type': 'race-card', 'year': int(year), 'event': event_name}, n_clicks=0)
