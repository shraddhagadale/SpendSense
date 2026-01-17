import sqlite3
from pathlib import Path

DB_PATH = Path('spendsense.db')

def get_db_connections():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            imported_at TEXT NOT NULL,
            UNIQUE(date,description,amount)
        );
        """
    )
    conn.commit()
    return conn 