import sqlite3

def criar_banco_de_dados():
    conn = sqlite3.connect('database/users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    criar_banco_de_dados()
