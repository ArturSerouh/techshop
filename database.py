import sqlite3

DB = "store.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS products ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "title TEXT NOT NULL, "
        "description TEXT, "
        "price REAL NOT NULL, "
        "image_url TEXT, "
        "category_id INTEGER, "
        "in_stock INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    conn.close()

init_db()