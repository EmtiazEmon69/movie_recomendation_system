import sqlite3

# Connect to database
conn = sqlite3.connect('users.db')
cur = conn.cursor()

# Create ratings table
cur.execute('''
    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        movie_title TEXT,
        rating INTEGER
    )
''')

conn.commit()
conn.close()

print("✅ Ratings table created successfully.")
