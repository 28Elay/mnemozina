import sqlite3
from datetime import datetime, timedelta

DB = "mnemozina.db"

def get_db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = lambda cur, row: {d[0]: row[i] for i, d in enumerate(cur.description)}
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        scheduled_at TEXT NOT NULL,
        done INTEGER DEFAULT 0,
        priority INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS settings (
        k TEXT PRIMARY KEY,
        v TEXT
    );
    """)
    conn.commit()
    conn.close()

def setting(k, v=None):
    conn = get_db()
    if v is not None:
        conn.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (k, v))
        conn.commit()
        conn.close()
        return v
    r = conn.execute("SELECT v FROM settings WHERE k = ?", (k,)).fetchone()
    conn.close()
    return r["v"] if r else None

def add_task(title, description, scheduled_at, priority=0):
    conn = get_db()
    conn.execute(
        "INSERT INTO tasks (title, description, scheduled_at, done, priority) VALUES (?, ?, ?, 0, ?)",
        (title, description, scheduled_at, priority)
    )
    conn.commit()
    conn.close()

def get_active_tasks():
    conn = get_db()
    tasks = conn.execute("""
        SELECT * FROM tasks WHERE done = 0 ORDER BY datetime(scheduled_at) ASC
    """).fetchall()
    conn.close()
    return tasks

def get_tasks_by_filter(filter_type):
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    query = "SELECT * FROM tasks WHERE done = 0"
    params = ()
    
    if filter_type == "today":
        query += " AND scheduled_at LIKE ?"
        params = (f"{today}%",)
    elif filter_type == "tomorrow":
        query += " AND scheduled_at LIKE ?"
        params = (f"{tomorrow}%",)
        
    query += " ORDER BY datetime(scheduled_at) ASC"
    tasks = conn.execute(query, params).fetchall()
    conn.close()
    return tasks

def get_due_tasks():
    conn = get_db()
    tasks = conn.execute("""
        SELECT * FROM tasks 
        WHERE done = 0 AND datetime(scheduled_at) <= datetime('now', 'localtime')
    """).fetchall()
    conn.close()
    return tasks

def mark_done(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def update_priority(task_id, priority):
    conn = get_db()
    conn.execute("UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id))
    conn.commit()
    conn.close()