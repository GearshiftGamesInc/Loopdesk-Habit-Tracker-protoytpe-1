import sqlite3

DB = "habits.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    total_completed INTEGER DEFAULT 0,
    last_completed DATE
)
""")

cursor.execute("""
CREATE TABLE player (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1
)
""")

cursor.execute("INSERT INTO player (id, xp, level) VALUES (1, 0, 1)")

conn.commit()
conn.close()

print("🔥 Fresh gamified database created!")
