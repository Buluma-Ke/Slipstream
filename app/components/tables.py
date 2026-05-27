# app/components/tables.py
from dash import html

# Assuming you have these dictionaries defined in your constants or config
TEAM_COLORS = {
    'Mercedes': '#27F4D2', 'Red Bull Racing': '#3671C6', 'Ferrari': '#E80020',
    'McLaren': '#FF8000', 'Aston Martin': '#229971', 'Alpine': '#0093CC',
    'Williams': '#64C4FF', 'RB': '#6692FF', 'Sauber': '#52E252', 'Haas F1 Team': '#B6BABD'
}

TEAM_LOGOS = {
    'Mercedes': 'mercedes', 'Red Bull Racing': 'redbull', 'Ferrari': 'ferrari',
    'McLaren': 'mclaren', 'Aston Martin': 'aston', 'Alpine': 'alpine',
    'Williams': 'williams', 'RB': 'rb', 'Sauber': 'sauber', 'Haas F1 Team': 'haas'
}

def build_driver_table(df):
    """
    Transforms a DuckDB DataFrame into a Dash HTML Table.
    """
    if df is None or df.empty:
        return html.Div("No driver data available for this season.", className='no-data-msg')

    # Add Position column based on the sorted Points
    df = df.copy()
    df['Pos'] = range(1, len(df) + 1)

    driver_rows = []
    for _, row in df.iterrows():
        team_name = row['TeamName']
        team_color = TEAM_COLORS.get(team_name, '#444')
        logo_file = TEAM_LOGOS.get(team_name, None)
        pos = int(row['Pos'])

        driver_rows.append(
            html.Tr([
                # Position
                html.Td(str(pos), className='pos'),

                # Team Identity (Logo or Color Bar)
                html.Td(
                    html.Img(
                        src=f'/assets/logos/{logo_file}.avif',
                        style={'height': '16px', 'width': '28px', 'objectFit': 'contain'}
                    ) if logo_file else html.Div(
                        style={'width': '4px', 'height': '20px', 'background': team_color, 'margin': '0 auto'}
                    ),
                    style={'width': '32px', 'padding': '0 4px'},
                ),

                # Driver Info
                html.Td(row['Abbreviation'], className='driver-abbr'),
                html.Td(row['FullName'], className='driver-name'),

                # Points
                html.Td(f"{int(row['Points'])}", className='pts'),
            ],
            # Apply a special class to the leader
            className='p1-row' if pos == 1 else 'standard-row')
        )

    return html.Table([
        html.Thead(html.Tr([
            html.Th('POS'),
            html.Th(''),
            html.Th('DRV'),
            html.Th('NAME'),
            html.Th('PTS'),
        ])),
        html.Tbody(driver_rows),
    ], className='champ-table')
