import sqlite3 
from pathlib import Path 

DB_PATH = Path (__file__).resolve().parent.parent / "loan_emi.db"

def get_connection():
    """Open a raw sqlite3 connection with foreign keys enforced and
    rows returned as dict-like objects instead of plain tuples."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    """FastAPI dependency — opens one connection per request,
    hands it to the endpoint, and guarantees it gets closed after."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()