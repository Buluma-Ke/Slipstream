# In your callbacks file
from app.analytics.home import get_homepage_data
from dash import callback, Output, Input, State, ctx

@callback(
    Output('home-stat-champion', 'children'),
    Output('home-stat-champion-pts', 'children'),
    Output('home-stat-constructor', 'children'),
    Output('home-stat-constructor-pts', 'children'),
    Output('home-stat-races', 'children'),
    Output('home-fact-mostwins', 'children'),
    Output('home-fact-mostwins-sub', 'children'),
    Output('home-fact-poles', 'children'),
    Output('home-fact-poles-sub', 'children'),
    Output('home-fact-dnf', 'children'),
    Output('home-fact-dnf-sub', 'children'),
    Output('home-drivers-table', 'children'),
    Output('home-constructors-table', 'children'),
    Input('home-store-year', 'data'),
)


def update_home(year):
    data = get_homepage_data(year)

    if not data:
        # Return the "Empty State" tuple
        return ('—', '0 pts', '—', '0 pts', '0', '0', '—', '0', '—', '—', '—', [], [])

    # Format Champion/Constructor cards
    champion_name = data['champion'].get('Abbreviation', '—')
    champion_pts = f"{int(data['champion'].get('Points', 0))} pts"

    team_name = data['constructor'].get('TeamName', '—')
    team_pts = f"{int(data['constructor'].get('Points', 0))} pts"

    # Build Tables (Use your existing row-building logic here)
    # Just pass data['driver_standings'] and data['team_standings'] to your helper functions
    drivers_table = build_driver_table(data['driver_standings'])
    teams_table = build_team_table(data['team_standings'])

    return (
        champion_name, champion_pts,
        team_name, team_pts,
        str(data['total_races']),
        str(data['wins'][1]), data['wins'][0],
        str(data['poles'][1]), data['poles'][0],
        str(data['dnfs'][1]), data['dnfs'][0],
        drivers_table,
        teams_table
    )
