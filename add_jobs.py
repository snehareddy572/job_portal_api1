
from database import get_connection, create_table

# Make sure all tables exist
create_table()

conn = get_connection()

jobs = [
    (
        "Python Developer",
        "ABC Technologies",
        "Hyderabad",
        "4-6 LPA",
        "Develop Python applications and REST APIs."
    ),
    (
        "Data Analyst",
        "XYZ Solutions",
        "Bengaluru",
        "5-7 LPA",
        "Analyze data and prepare reports using SQL and Python."
    ),
    (
        "Software Engineer",
        "Tech Solutions",
        "Chennai",
        "6-8 LPA",
        "Develop and maintain software applications."
    ),
    (
        "Machine Learning Intern",
        "AI Innovations",
        "Hyderabad",
        "15,000 per month",
        "Assist with machine learning models and data preparation."
    ),
    (
        "Backend Developer",
        "Digital Systems",
        "Pune",
        "5-8 LPA",
        "Build backend services using Python and databases."
    )
]

for job in jobs:
    conn.execute(
        """
        INSERT INTO jobs
        (title, company, location, salary, description)
        SELECT ?, ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM jobs
            WHERE title = ? AND company = ?
        )
        """,
        job + (job[0], job[1])
    )

conn.commit()

print("Sample jobs added successfully!")

# Display all jobs
results = conn.execute("SELECT * FROM jobs").fetchall()

for result in results:
    print(dict(result))

conn.close()
