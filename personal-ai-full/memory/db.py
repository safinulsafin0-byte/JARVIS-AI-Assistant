import sqlite3
from pathlib import Path
from config import MEMORY_DB

MEMORY_DB.parent.mkdir(parents=True, exist_ok=True)

def init_db():
    with sqlite3.connect(MEMORY_DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS memories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_text TEXT,
            assistant_text TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS facts(
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")

def add_memory(user_text, assistant_text):
    with sqlite3.connect(MEMORY_DB) as c:
        c.execute("INSERT INTO memories(user_text,assistant_text) VALUES(?,?)",
                  (user_text, assistant_text))

def recent(limit=10):
    with sqlite3.connect(MEMORY_DB) as c:
        return c.execute(
            "SELECT user_text,assistant_text,created_at FROM memories ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()

def set_fact(key, value):
    with sqlite3.connect(MEMORY_DB) as c:
        c.execute("""INSERT INTO facts(key,value) VALUES(?,?)
                     ON CONFLICT(key) DO UPDATE SET value=excluded.value,
                     updated_at=CURRENT_TIMESTAMP""", (key, value))

def facts():
    with sqlite3.connect(MEMORY_DB) as c:
        return c.execute("SELECT key,value FROM facts").fetchall()
