import sqlite3

conn = sqlite3.connect('missing_artworks.db')
c = conn.cursor()

# Add 'admin' column to users table if it doesn't exist
c.execute("PRAGMA table_info(users)")
columns = [col[1] for col in c.fetchall()]
if 'admin' not in columns:
    c.execute('ALTER TABLE users ADD COLUMN admin BOOLEAN DEFAULT 0')
    print("'admin' column added to users table.")
else:
    print("'admin' column already exists.")

conn.commit()
conn.close()
