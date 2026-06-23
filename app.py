import dash
import dash_bootstrap_components as dbc
from app.layout import build_layout
from data.store import init_db

# initialize db
init_db()

app = dash.Dash(
    __name__,
    external_stylesheets=[],
    title='Slipstream',
    suppress_callback_exceptions=True,
)

app.layout = build_layout()

from app.callbacks import homepage, schedule, navigation, driver_standings, constructor_standings, races, drivers

if __name__ == '__main__':
    app.run(debug=True, port=8050, use_reloader=False)
