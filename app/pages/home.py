from dash import html, dcc, callback, Output, Input
import fastf1
import pandas as pd

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
}


def layout():
    return html.Div([

        # Top row — title + year selector
        html.Div([
            html.Div('Season Overview', className='home-page-title'),
            html.Div([
                html.Div('Season', className='home-year-label'),
                dcc.Dropdown(
                    id='home-dd-year',
                    options=[{'label': y, 'value': y} for y in range(2025, 2017, -1)],
                    value=2024,
                    clearable=False,
                    style={'width': '90px'},
                ),
                html.Div(id='home-loading-status'),
            ], className='home-year-selector'),
        ], className='home-top-row'),

        # Row 1 — headline cards
        html.Div([
            html.Div([
                html.Div('⚡', className='card-icon'),
                html.Div('Champion', className='card-label'),
                html.Div('—', className='card-value large', id='home-stat-champion'),
                html.Div('—', className='card-sub', id='home-stat-champion-pts'),
            ], className='info-card accent-gold'),

            html.Div([
                html.Div('🏗', className='card-icon'),
                html.Div('Winning Constructor', className='card-label'),
                html.Div('—', className='card-value', id='home-stat-constructor'),
                html.Div('—', className='card-sub', id='home-stat-constructor-pts'),
            ], className='info-card accent-red'),

            html.Div([
                html.Div('🏁', className='card-icon'),
                html.Div('Total Races', className='card-label'),
                html.Div('—', className='card-value large', id='home-stat-races'),
                html.Div('rounds completed', className='card-sub'),
            ], className='info-card accent-ocean'),
        ], className='cards-grid'),

        # Row 2 — fun fact cards
        html.Div([
            html.Div([
                html.Div('🏆', className='card-icon'),
                html.Div('Most Wins', className='card-label'),
                html.Div('—', className='card-value', id='home-fact-mostwins'),
                html.Div('—', className='card-sub', id='home-fact-mostwins-sub'),
            ], className='info-card'),

            html.Div([
                html.Div('🎯', className='card-icon'),
                html.Div('Most Pole Positions', className='card-label'),
                html.Div('—', className='card-value', id='home-fact-poles'),
                html.Div('—', className='card-sub', id='home-fact-poles-sub'),
            ], className='info-card'),

            html.Div([
                html.Div('⏱', className='card-icon'),
                html.Div('Closest Finish', className='card-label'),
                html.Div('—', className='card-value', id='home-fact-closest'),
                html.Div('—', className='card-sub', id='home-fact-closest-sub'),
            ], className='info-card accent-gold'),

            html.Div([
                html.Div('💀', className='card-icon'),
                html.Div('Most DNFs', className='card-label'),
                html.Div('—', className='card-value', id='home-fact-dnf'),
                html.Div('—', className='card-sub', id='home-fact-dnf-sub'),
            ], className='info-card'),
        ], className='cards-grid-2'),

        # Row 3 — championship tables
        html.Div([
            html.Div([
                html.Div([
                    html.Div('Drivers Championship', className='table-card-title'),
                ], className='table-card-header'),
                html.Div(id='home-drivers-table'),
            ], className='table-card'),

            html.Div([
                html.Div([
                    html.Div('Constructors Championship', className='table-card-title'),
                ], className='table-card-header'),
                html.Div(id='home-constructors-table'),
            ], className='table-card'),
        ], className='tables-row'),

    ], className='home-wrapper')