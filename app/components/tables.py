# # app/components/tables.py
# from dash import html

# # Assuming you have these dictionaries defined in your constants or config
# TEAM_COLORS = {
#     'Mercedes': '#27F4D2', 'Red Bull Racing': '#3671C6', 'Ferrari': '#E80020',
#     'McLaren': '#FF8000', 'Aston Martin': '#229971', 'Alpine': '#0093CC',
#     'Williams': '#64C4FF', 'RB': '#6692FF', 'Sauber': '#52E252', 'Haas F1 Team': '#B6BABD'
# }

# TEAM_LOGOS = {
#     'Mercedes': 'mercedes', 'Red Bull Racing': 'redbull', 'Ferrari': 'ferrari',
#     'McLaren': 'mclaren', 'Aston Martin': 'aston', 'Alpine': 'alpine',
#     'Williams': 'williams', 'RB': 'rb', 'Sauber': 'sauber', 'Haas F1 Team': 'haas'
# }

# def build_driver_table(df):
#     """
#     Transforms a DuckDB DataFrame into a Dash HTML Table.
#     """
#     if df is None or df.empty:
#         return html.Div("No driver data available for this season.", className='no-data-msg')

#     # Add Position column based on the sorted Points
#     df = df.copy()
#     df['Pos'] = range(1, len(df) + 1)

#     driver_rows = []
#     for _, row in df.iterrows():
#         team_name = row['TeamName']
#         team_color = TEAM_COLORS.get(team_name, '#444')
#         logo_file = TEAM_LOGOS.get(team_name, None)
#         pos = int(row['Pos'])

#         driver_rows.append(
#             html.Tr([
#                 # Position
#                 html.Td(str(pos), className='pos'),

#                 # Team Identity (Logo or Color Bar)
#                 html.Td(
#                     html.Img(
#                         src=f'/assets/logos/{logo_file}.avif',
#                         style={'height': '16px', 'width': '28px', 'objectFit': 'contain'}
#                     ) if logo_file else html.Div(
#                         style={'width': '4px', 'height': '20px', 'background': team_color, 'margin': '0 auto'}
#                     ),
#                     style={'width': '32px', 'padding': '0 4px'},
#                 ),

#                 # Driver Info
#                 html.Td(row['Abbreviation'], className='driver-abbr'),
#                 html.Td(row['FullName'], className='driver-name'),

#                 # Points
#                 html.Td(f"{int(row['Points'])}", className='pts'),
#             ],
#             # Apply a special class to the leader
#             className='p1-row' if pos == 1 else 'standard-row')
#         )

#     return html.Table([
#         html.Thead(html.Tr([
#             html.Th('POS'),
#             html.Th(''),
#             html.Th('DRV'),
#             html.Th('NAME'),
#             html.Th('PTS'),
#         ])),
#         html.Tbody(driver_rows),
#     ], className='champ-table')


# # app/components/tables.py (continued)

# def build_team_table(df):
#     """
#     Transforms the team standings DataFrame into a Dash HTML Table.
#     """
#     if df is None or df.empty:
#         return html.Div("No constructor data available.", className='no-data-msg')

#     # Ensure sorting and add rank
#     df = df.copy()
#     df['Pos'] = range(1, len(df) + 1)

#     team_rows = []
#     for _, row in df.iterrows():
#         team_name = row['TeamName']
#         team_color = TEAM_COLORS.get(team_name, '#444')
#         logo_file = TEAM_LOGOS.get(team_name, None)
#         pos = int(row['Pos'])

#         team_rows.append(
#             html.Tr([
#                 # Position
#                 html.Td(str(pos), className='pos'),

#                 # Team Logo
#                 html.Td(
#                     html.Img(
#                         src=f'/assets/logos/{logo_file}.avif',
#                         style={'height': '16px', 'width': '28px', 'objectFit': 'contain'}
#                     ) if logo_file else html.Div(
#                         style={'width': '4px', 'height': '20px', 'background': team_color, 'margin': '0 auto'}
#                     ),
#                     style={'width': '32px', 'padding': '0 4px'},
#                 ),

#                 # Team Name
#                 html.Td(team_name, className='team-name-cell'),

#                 # Points
#                 html.Td(f"{int(row['Points'])}", className='pts'),
#             ],
#             className='p1-row' if pos == 1 else 'standard-row')
#         )

#     return html.Table([
#         html.Thead(html.Tr([
#             html.Th('POS'),
#             html.Th(''),
#             html.Th('TEAM'),
#             html.Th('PTS'),
#         ])),
#         html.Tbody(team_rows),
#     ], className='champ-table')






from dash import html
from app.constants import get_team_assets

def build_driver_table(df):
    if df is None or df.empty:
        return html.Div("No driver standings available.", className='table-empty-state')

    table_rows = []

    # Enumerate helps us capture the mathematical rank safely
    for idx, row in df.iterrows():
        pos = idx + 1
        team_name = row.get('TeamName', '—')

        # 1. Pull the custom asset configurations safely
        team_color, logo_url = get_team_assets(team_name)

        # Give a custom class to P1 for styling highlights
        row_class = 'p1-row' if pos == 1 else 'standard-row'

        row_element = html.Tr([
            html.Td(str(pos), className='pos'),

            # 2. Render the normalized team logo asset
            html.Td(
                html.Img(src=logo_url, style={'height': '16px', 'width': '28px', 'objectFit': 'contain'}),
                style={'width': '32px', 'padding': '0 4px'}
            ),

            html.Td(str(row.get('Abbreviation', '—')), className='driver-abbr'),

            # 3. Dynamic border accent left using the hex team color
            html.Td(
                str(row.get('FullName', '—')),
                className='driver-name',
                style={'borderLeft': f'4px solid {team_color}', 'paddingLeft': '8px'}
            ),

            html.Td(str(int(row.get('Points', 0))), className='pts')
        ], className=row_class)

        table_rows.append(row_element)

    return html.Table([
        html.Thead(html.Tr([html.Th('POS'), html.Th(''), html.Th('DRV'), html.Th('NAME'), html.Th('PTS')])),
        html.Tbody(table_rows)
    ], className='champ-table')


def build_team_table(df):
    if df is None or df.empty:
        return html.Div("No constructor standings available.", className='table-empty-state')

    table_rows = []

    for idx, row in df.iterrows():
        pos = idx + 1
        team_name = row.get('TeamName', '—')

        # Pull asset values
        team_color, logo_url = get_team_assets(team_name)
        row_class = 'p1-row' if pos == 1 else 'standard-row'

        row_element = html.Tr([
            html.Td(str(pos), className='pos'),

            html.Td(
                html.Img(src=logo_url, style={'height': '16px', 'width': '28px', 'objectFit': 'contain'}),
                style={'width': '32px', 'padding': '0 4px'}
            ),

            html.Td(
                team_name,
                className='team-name-cell',
                style={'borderLeft': f'4px solid {team_color}', 'paddingLeft': '8px'}
            ),

            html.Td(str(int(row.get('Points', 0))), className='pts')
        ], className=row_class)

        table_rows.append(row_element)

    return html.Table([
        html.Thead(html.Tr([html.Th('POS'), html.Th(''), html.Th('TEAM'), html.Th('PTS')])),
        html.Tbody(table_rows)
    ], className='champ-table')
