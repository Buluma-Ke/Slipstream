from dash import html

def layout():
    return html.Div([
        html.Div('PREDICTIONS', style={
            'fontFamily': 'Barlow Condensed, sans-serif',
            'fontSize': '3rem',
            'color': '#E8002D',
            'padding': '40px',
            'letterSpacing': '0.3em',
        }),
        html.Div('Season overview coming soon.', style={
            'color': '#666',
            'fontFamily': 'DM Mono, monospace',
            'fontSize': '0.8rem',
            'paddingLeft': '40px',
        }),
    ])