import sys
sys.path.insert(0, '.')

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from data.loader import get_session


# --- 1. Load session ---
print("Loading 2023 Bahrain Race...")
session = get_session(2023, 'Bahrain', 'R')

print("Done!")
print(f"Session: {session.event['EventName']} {session.event.year}")


# --- 2. Inspect raw lap data ---
laps = session.laps
print(f"\nTotal laps: {len(laps)}")
print(f"\nColumns: {laps.columns.tolist()}")
print(f"\nFirst 5 rows:")
print(laps.head())


# --- 3. Verstappen laps ---
print("\n--- Key columns for one driver ---")
ver_laps = laps[laps['Driver'] == 'VER']
print(ver_laps[['LapNumber', 'LapTime', 'Compound', 'TyreLife', 'IsPersonalBest']].to_string())


# --- 4. Clean laps + average pace ---
print("\n--- Cleaned average lap time per driver (seconds) ---")

# Convert LapTime to seconds
laps['LapTimeSec'] = laps['LapTime'].dt.total_seconds()

# Filter out slow laps (pit laps, SC laps, formation lap)
fastest_lap = laps['LapTimeSec'].min()
clean_laps = laps[laps['LapTimeSec'] < fastest_lap * 1.07]

avg_pace = clean_laps.groupby('Driver')['LapTimeSec'].mean().sort_values()
print(avg_pace.to_string())


# --- 5. Driver list ---
print("\n--- All drivers in the session ---")
print(sorted(laps['Driver'].unique()))



# --- 6. Tyre strategy ---
print("\n--- Tyre compounds used per driver ---")
compounds = clean_laps.groupby(['Driver', 'Compound'])['LapNumber'].count().unstack(fill_value=0)
print(compounds.to_string())



# --- 7. Telemetry for one lap ---
print("\n--- Fetching telemetry for VER lap 10 ---")
ver_lap = clean_laps[(clean_laps['Driver'] == 'VER') & (clean_laps['LapNumber'] == 10)].iloc[0]
telemetry = ver_lap.get_car_data().add_distance()

print(f"Rows: {len(telemetry)}")
print(f"Columns: {telemetry.columns.tolist()}")
print(telemetry[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear']].head(10))



# --- 8. Plot speed trace with throttle and brake ---
fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    subplot_titles=['Speed (km/h)', 'Throttle (%)', 'Brake'],
    vertical_spacing=0.08
)

fig.add_trace(go.Scatter(x=telemetry['Distance'], y=telemetry['Speed'], name='Speed', line=dict(color='#E8002D')), row=1, col=1)
fig.add_trace(go.Scatter(x=telemetry['Distance'], y=telemetry['Throttle'], name='Throttle', line=dict(color='#27F4D2')), row=2, col=1)
fig.add_trace(go.Scatter(x=telemetry['Distance'], y=telemetry['Brake'].astype(int), name='Brake', fill='tozeroy', line=dict(color='#FF8000')), row=3, col=1)

fig.update_layout(title='VER Lap 10 — Telemetry (Bahrain 2023)', showlegend=False, height=600)
fig.update_xaxes(title_text='Distance (m)', row=3, col=1)

fig.show()



# --- 9. Track map coloured by speed ---
pos = ver_lap.get_pos_data()
tel = ver_lap.get_car_data().add_distance()

# Merge position and telemetry on time
from fastf1 import plotting
merged = tel.merge_channels(pos)

fig = px.scatter(
    merged,
    x='X',
    y='Y',
    color='Speed',
    color_continuous_scale='RdYlGn',
    title='VER Lap 10 — Speed map (Bahrain 2023)',
    labels={'Speed': 'Speed (km/h)'}
)
fig.update_traces(marker=dict(size=4))
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False, scaleanchor='x')
)
fig.show()