# nuke_and_pave.py
import os
from store import get_connection, init_db

def reset_database_infrastructure():
    print("⚠️  Preparing to drop old database engine tables...")
    con = get_connection(read_only=False)

    try:
        # Drop tables to eliminate old structural layout schemas
        con.execute("DROP TABLE IF EXISTS race_results;")
        con.execute("DROP TABLE IF EXISTS laps;")
        con.execute("DROP TABLE IF EXISTS sessions_loaded;")
        print("🔥 Existing tables dropped successfully.")
    except Exception as e:
        print(f"❌ Error during dropping sequence: {e}")
    finally:
        con.close()

    print("🛠️ Re-initializing pristine database structures...")
    # This automatically calls your updated store.py layout to build them properly
    init_db()
    print("✨ Database reset complete! It is now safe to run your pipeline scripts.")

if __name__ == "__main__":
    reset_database_infrastructure()
