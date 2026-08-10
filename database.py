import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATA_DIR / "angie.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def execute(query, params=()):
    conn = get_connection()
    try:
        cur = conn.execute(query, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def fetch_one(query, params=()):
    conn = get_connection()
    try:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def fetch_all(query, params=()):
    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def _ensure_column(table_name, column_name, column_def):
    conn = get_connection()
    try:
        columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})")}
        if column_name not in columns:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
            conn.commit()
    finally:
        conn.close()


def initialize_database():
    execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT DEFAULT '',
            language TEXT DEFAULT 'English',
            voice TEXT DEFAULT 'female',
            theme TEXT DEFAULT 'light',
            wallpaper TEXT DEFAULT 'dawn',
            voice_reply INTEGER DEFAULT 0,
            daily_quotes INTEGER DEFAULT 1,
            scripture INTEGER DEFAULT 1,
            notifications INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    _ensure_column("users", "full_name", "TEXT DEFAULT ''")
    _ensure_column("users", "language", "TEXT DEFAULT 'English'")
    _ensure_column("users", "voice", "TEXT DEFAULT 'female'")
    _ensure_column("users", "theme", "TEXT DEFAULT 'light'")
    _ensure_column("users", "wallpaper", "TEXT DEFAULT 'dawn'")
    _ensure_column("users", "voice_reply", "INTEGER DEFAULT 0")
    _ensure_column("users", "daily_quotes", "INTEGER DEFAULT 1")
    _ensure_column("users", "scripture", "INTEGER DEFAULT 1")
    _ensure_column("users", "notifications", "INTEGER DEFAULT 1")

    execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    execute("""
        CREATE TABLE IF NOT EXISTS moods(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mood TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    execute("""
        CREATE TABLE IF NOT EXISTS journal_entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entry TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    execute("CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id, topic)")
    execute("CREATE INDEX IF NOT EXISTS idx_moods_user ON moods(user_id)")
    execute("CREATE INDEX IF NOT EXISTS idx_journal_user ON journal_entries(user_id)")


# ==========================================================
# USERS
# ==========================================================

def create_user(username, email, password_hash, full_name=""):
    return execute(
        """
        INSERT INTO users(username, email, password_hash, full_name)
        VALUES(?,?,?,?)
        """,
        (username, email, password_hash, full_name),
    )


def get_user_by_email(email):
    return fetch_one("SELECT * FROM users WHERE email=?", (email,))


def get_user_by_username(username):
    return fetch_one("SELECT * FROM users WHERE username=?", (username,))


def get_user(user_id):
    return fetch_one("SELECT * FROM users WHERE id=?", (user_id,))


def update_preferences(user_id, **fields):
    if not fields:
        return
    allowed = {
        "language", "voice", "theme", "wallpaper", "voice_reply",
        "daily_quotes", "scripture", "notifications", "full_name",
    }
    keys = [k for k in fields.keys() if k in allowed]
    if not keys:
        return
    set_clause = ", ".join(f"{k}=?" for k in keys)
    values = [fields[k] for k in keys]
    values.append(user_id)
    execute(f"UPDATE users SET {set_clause} WHERE id=?", values)


def delete_user(user_id):
    execute("DELETE FROM users WHERE id=?", (user_id,))


# ==========================================================
# MESSAGES
# ==========================================================

def save_message(user_id, topic, sender, message):
    execute(
        """
        INSERT INTO messages(user_id, topic, sender, message)
        VALUES(?,?,?,?)
        """,
        (user_id, topic, sender, message),
    )


def load_messages(user_id, topic, limit=50):
    rows = fetch_all(
        """
        SELECT * FROM messages
        WHERE user_id=? AND topic=?
        ORDER BY id ASC
        LIMIT ?
        """,
        (user_id, topic, limit),
    )
    return rows


def delete_all_messages(user_id):
    execute("DELETE FROM messages WHERE user_id=?", (user_id,))


# ==========================================================
# MOODS
# ==========================================================

def save_mood(user_id, mood):
    execute(
        "INSERT INTO moods(user_id, mood) VALUES(?,?)",
        (user_id, mood),
    )


def load_moods(user_id, limit=20):
    return fetch_all(
        """
        SELECT * FROM moods
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )


# ==========================================================
# JOURNAL
# ==========================================================

def save_journal_entry(user_id, entry):
    execute(
        "INSERT INTO journal_entries(user_id, entry) VALUES(?,?)",
        (user_id, entry),
    )


def load_journal_entries(user_id, limit=100):
    return fetch_all(
        """
        SELECT * FROM journal_entries
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )


def delete_journal_entry(entry_id, user_id):
    execute(
        "DELETE FROM journal_entries WHERE id=? AND user_id=?",
        (entry_id, user_id),
    )
