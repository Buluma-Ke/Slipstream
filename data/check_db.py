# check_db.py
from store import get_connection

con = get_connection(read_only=True)

print("--- Database Summary ---")
# Check table row counts
tables = ['race_results', 'laps', 'sessions_loaded']

for table in tables:
    try:
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"Table '{table}': {count} rows")
    except Exception as e:
        print(f"Table '{table}': Error (likely doesn't exist yet) - {e}")

# If race_results has data, show the first 3 rows to verify the year
if con.execute("SELECT COUNT(*) FROM race_results").fetchone()[0] > 0:
    print("\n--- Sample Data (race_results) ---")
    print(con.execute("SELECT year, event_name, driver, time_seconds FROM race_results LIMIT 3").df())

con.close()
