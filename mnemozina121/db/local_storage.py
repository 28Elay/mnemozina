import sqlite3,json
from datetime import datetime,timedelta

DB="tasks.db"

def db():
    c=sqlite3.connect(DB,check_same_thread=False)
    c.row_factory=lambda cur,row:{d[0]:row[i] for i,d in enumerate(cur.description)}
    return c

def init_db():
    x=db()
    x.executescript("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        explanation TEXT,
        scheduled_at TEXT,
        done INTEGER DEFAULT 0,
        critical INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS sync_queue(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        payload TEXT
    );
    CREATE TABLE IF NOT EXISTS settings(
        k TEXT PRIMARY KEY,
        v TEXT
    );
    """)
    x.commit()

def setting(k,v=None):
    x=db()
    if v is not None:
        x.execute("INSERT OR REPLACE INTO settings VALUES(?,?)",(k,v))
        x.commit()
        return v
    r=x.execute("SELECT v FROM settings WHERE k=?",(k,)).fetchone()
    return r["v"] if r else None

def queue(action,payload):
    x=db()
    x.execute("INSERT INTO sync_queue(action,payload) VALUES(?,?)",(action,json.dumps(payload)))
    x.commit()

def tasks(limit=5):
    return db().execute("""
    SELECT * FROM tasks
    WHERE done=0
    ORDER BY datetime(scheduled_at)
    LIMIT ?
    """,(limit,)).fetchall()

def due_tasks():
    return db().execute("""
    SELECT * FROM tasks
    WHERE done=0
    AND datetime(scheduled_at)<=datetime('now','localtime')
    """).fetchall()

def done(task_id):
    x=db()
    x.execute("UPDATE tasks SET done=1 WHERE id=?",(task_id,))
    x.commit()
    queue("done",{"task_id":task_id})

def snooze(task_id):
    dt=(datetime.now()+timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
    x=db()
    x.execute("UPDATE tasks SET scheduled_at=? WHERE id=?",(dt,task_id))
    x.commit()
    queue("snooze",{"task_id":task_id,"scheduled_at":dt})

def sync_rows():
    return db().execute("SELECT * FROM sync_queue").fetchall()

def clear_sync():
    x=db()
    x.execute("DELETE FROM sync_queue")
    x.commit()