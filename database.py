



import sqlite3


# Connect to the SQLite database
def get_connection():
    conn = sqlite3.connect("job_portal.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create database tables
def create_table():
    conn = get_connection()

    # Candidates table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            skills TEXT,
            password_hash TEXT,
            role TEXT DEFAULT 'Job Seeker'
        )
    """)

    # Add new columns to an existing candidates table
    columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(candidates)"
        ).fetchall()
    ]

    if "password_hash" not in columns:
        conn.execute(
            "ALTER TABLE candidates ADD COLUMN password_hash TEXT"
        )

    if "role" not in columns:
        conn.execute(
            "ALTER TABLE candidates ADD COLUMN role TEXT DEFAULT 'Job Seeker'"
        )

    # Jobs table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            salary TEXT,
            description TEXT
        )
    """)

    # Applications table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (candidate_id) REFERENCES candidates(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            UNIQUE (candidate_id, job_id)
        )
    """)

    conn.commit()
    conn.close()


# Create tables when this file runs
if __name__ == "__main__":
    create_table()
    print("Database and tables created successfully!")
