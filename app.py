import dash
import dash_bootstrap_components as dbc
from app.layout import build_layout
import app.callbacks

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title='Slipstream',
    suppress_callback_exceptions=True,
)

app.layout = build_layout()

if __name__ == '__main__':
    app.run(debug=True, port=8050)