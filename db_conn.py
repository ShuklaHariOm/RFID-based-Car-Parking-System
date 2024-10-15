import sqlite3

conn = sqlite3.connect('parking.db')

cursor = conn.cursor()

# Add the status column to track entry/exit status
cursor.execute('''
CREATE TABLE IF NOT EXISTS parking_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_number TEXT,
    in_time TEXT,
    out_time TEXT,
    slot_number INTEGER,
    status TEXT
)
''')

conn.commit()
conn.close()
