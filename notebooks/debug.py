import duckdb
con = duckdb.connect('./data/f1.duckdb')

# Do we have results for 2025?
print(con.execute("SELECT count(*) FROM race_results WHERE year = 2025").fetchone())

# Do we have laps for 2025?
print(con.execute("SELECT count(*) FROM laps WHERE year = 2025").fetchone())
con.close()
