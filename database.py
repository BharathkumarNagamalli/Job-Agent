import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "jobs.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    # Applications tracker
    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            salary TEXT,
            job_type TEXT,
            description TEXT,
            apply_url TEXT,
            status TEXT DEFAULT 'saved',
            notes TEXT,
            date_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_applied TIMESTAMP,
            date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User profile
    c.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            location TEXT,
            skills TEXT,
            experience TEXT,
            education TEXT,
            linkedin TEXT,
            github TEXT,
            portfolio TEXT,
            summary TEXT,
            resume_text TEXT,
            resume_filename TEXT
        )
    """)

    # Check for new columns and add them if missing
    try:
        c.execute("ALTER TABLE profile ADD COLUMN resume_text TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        c.execute("ALTER TABLE profile ADD COLUMN resume_filename TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Insert default profile if not exists
    c.execute("SELECT COUNT(*) FROM profile")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO profile (id, name, email, skills, experience, education, github)
            VALUES (1, 'BharathKumar', '', 'Python, Flask, JavaScript, React, HTML/CSS, SQL',
                   'Web Development Intern at Brainwave Matrix Solutions',
                   'B.Tech CSE - Malla Reddy Institute of Engineering and Technology, Hyderabad',
                   'https://github.com/BharathkumarNagamalli')
        """)

    conn.commit()
    conn.close()
