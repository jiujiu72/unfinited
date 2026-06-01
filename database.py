import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.db")


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS highscores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER NOT NULL,
            level INTEGER NOT NULL,
            kills INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def save_score(score, level, kills):
    conn = _get_connection()
    conn.execute(
        "INSERT INTO highscores (score, level, kills) VALUES (?, ?, ?)",
        (score, level, kills)
    )
    conn.commit()
    conn.close()


def get_high_score():
    conn = _get_connection()
    cursor = conn.execute("SELECT MAX(score) FROM highscores")
    row = cursor.fetchone()
    conn.close()
    if row and row[0] is not None:
        return row[0]
    return 0


def get_top_scores(limit=5):
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT score, level, kills, timestamp FROM highscores ORDER BY score DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
