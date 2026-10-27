


from database import get_connection

conn = get_connection()

conn.execute(
    """
    INSERT INTO candidates (name, email, skills)
    VALUES (?, ?, ?)
    """,
    ("Sneha", "sneha@example.com", "Python, SQLite, FastAPI")
)

conn.commit()

print("Candidate inserted successfully!")

candidates = conn.execute(
    "SELECT * FROM candidates"
).fetchall()

for candidate in candidates:
    print(dict(candidate))

conn.close()

