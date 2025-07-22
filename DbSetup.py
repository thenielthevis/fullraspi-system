import sqlite3

# Database file path
db_path = 'arpi.sqlite'

# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# SQL statement to create a table
create_table_sql = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    uid TEXT NOT NULL UNIQUE,
    credit INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0
);
'''

# Execute the SQL statement
cursor.execute(create_table_sql)

# Commit changes and close connection
conn.commit()
conn.close()

print("Table 'users' created successfully.")

def add_credit(uid, amount=1):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET credit = credit + ? WHERE uid = ?", (amount, uid))
    conn.commit()
    conn.close()

def claim_points(uid, points):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET points = points + ? WHERE uid = ?", (points, uid))
    conn.commit()
    conn.close()

def insert_user(name, uid, credit, points):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, uid, credit, points) VALUES (?, ?, ?, ?)", (name, uid, credit, points))
    conn.commit()
    conn.close()

def user_exists(uid):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE uid = ?", (uid,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

if __name__ == "__main__":
    insert_user("eli", "336ACDA6", 3, 1000)
    print("Inserted user: eli, 336ACDA6, 3, 1000")