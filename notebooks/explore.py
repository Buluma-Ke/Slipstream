import sys
sys.path.insert(0, '.')

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