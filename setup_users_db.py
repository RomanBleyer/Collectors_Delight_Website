import sqlite3

conn = sqlite3.connect('missing_artworks.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT
)
''')

conn.commit()
conn.close()

print("Users table created (if not exists).")
