import sqlite3
import os
import faker

def init_database():
    db_path = os.getenv('DATABASE_PATH', '/data/test_users.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]

    if count == 0:
        users = [
            ('Anna Andersson', 'anna@test.se'),
            ('Bo Bengtsson', 'bo@test.se')
        ]
        cursor.executemany(
            'INSERT INTO users (name, email) VALUES (?, ?)', users
        )

    conn.commit()
    conn.close()

def display_users():
    db_path = os.getenv('DATABASE_PATH', '/data/test_users.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    for user in cursor.fetchall():
        print(user)

    conn.close()

def clear_test_data():
    db_path = os.getenv('DATABASE_PATH', '/data/test_users.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM users')
    conn.commit()
    conn.close()

def anonymize_data():
    db_path = os.getenv('DATABASE_PATH', '/data/test_users.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('UPDATE users SET name="Anonym Användare"')
    faker_instance = faker.Faker('sv_SE')
    cursor.execute('UPDATE users SET email=?', (faker_instance.email(),))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    display_users()
    print("Container running…")
    while True:
        pass
