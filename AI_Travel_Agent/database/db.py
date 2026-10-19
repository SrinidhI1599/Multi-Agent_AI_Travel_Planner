import sqlite3

conn = sqlite3.connect(
    "travel.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS trips(
id INTEGER PRIMARY KEY,
destination TEXT,
days INTEGER,
budget INTEGER
)
""")

conn.commit()