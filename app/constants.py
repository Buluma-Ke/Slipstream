# app/constants.py

TEAM_COLORS = {
    'Red Bull Racing': '#3671C6',
    'Ferrari': '#E8002D',
    'Mercedes': '#27F4D2',
    'McLaren': '#FF8000',
    'Aston Martin': '#229971',
    'Alpine': '#FF87BC',
    'Williams': '#64C4FF',
    'RB': '#6692FF',
    'Kick Sauber': '#52E252',
    'Haas F1 Team': '#B6BABD',
    'Toro Rosso': '#6692FF',
    'AlphaTauri': '#6692FF',
    'Alfa Romeo': '#52E252',
    'Racing Point': '#229971',
    'Force India': '#229971',
    'Renault': '#FF87BC',
    'Visa Cash App RB': '#6692FF',
    'Visa Cash App RB Formula One Team': '#6692FF',
    'RB Formula One Team': '#6692FF',
}

TEAM_LOGOS = {
    'Red Bull Racing': 'rbr-normalized-logo',
    'Ferrari': 'ferrari-normalized-logo',
    'Mercedes': '2026-mercedes-normalized-logo',
    'McLaren': 'mclaren-normalized-logo',
    'Aston Martin': 'aston-martin-normalized-logo',
    'Alpine': 'alpine-normalized-logo',
    'Williams': '2026-williams-normalized-logo',
    'RB': 'rb-normalized-logo',
    'Kick Sauber': 'kick-sauber-normalized-logo',
    'Haas F1 Team': 'haas-normalized-logo',
    'Audi': 'audi-normalized-logo',
    'Cadillac': 'cadillac-normalized-logo',
    'Toro Rosso': 'rb-normalized-logo',
    'AlphaTauri': 'rb-normalized-logo',
    'Alfa Romeo': 'kick-sauber-normalized-logo',
    'Racing Point': 'aston-martin-normalized-logo',
    'Force India': 'aston-martin-normalized-logo',
    'Renault': 'alpine-normalized-logo',
    'Visa Cash App RB': 'rb-normalized-logo',
    'Visa Cash App RB Formula One Team': 'rb-normalized-logo',
    'RB Formula One Team': 'rb-normalized-logo',
}

# -- How to Use Them Later --
# from app.constants import TEAM_COLORS, TEAM_LOGOS

def get_team_assets(team_name):
    """
    Safely retrieves the accent color and logo path for any given team name.
    Includes fallbacks for unknown or unmapped teams.
    """
    if not team_name:
        return '#B6BABD', '/assets/logos/default.avif'

    name_clean = str(team_name).strip()

    # Safe lookups with default fallbacks
    color = TEAM_COLORS.get(name_clean, '#B6BABD') # Default gray if not found
    logo_file = TEAM_LOGOS.get(name_clean, 'default-logo')

    # Assuming your logos use a standard format like .avif or .png in assets
    logo_path = f"/assets/logos/{logo_file}.avif"

    return color, logo_path
