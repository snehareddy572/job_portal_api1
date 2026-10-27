
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from database import get_connection

app = FastAPI(title="Job Portal API")


class Candidate(BaseModel):
    name: str
    email: EmailStr
    skills: str


@app.get("/")
def home():
    return {"message": "Job Portal API is running"}


@app.post("/candidates")
def add_candidate(candidate: Candidate):
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO candidates (name, email, skills)
            VALUES (?, ?, ?)
            """,
            (candidate.name, candidate.email, candidate.skills)
        )

        conn.commit()

        return {
            "message": "Candidate added successfully",
            "candidate_id": cursor.lastrowid,
            "name": candidate.name,
            "email": candidate.email,
            "skills": candidate.skills
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        conn.close()


@app.get("/candidates")
def get_candidates():
    conn = get_connection()

    try:
        candidates = conn.execute(
            "SELECT * FROM candidates"
        ).fetchall()

        return [dict(candidate) for candidate in candidates]

    finally:
        conn.close()

@app.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: int):
    conn = get_connection()

    try:
        candidate = conn.execute(
            "SELECT * FROM candidates WHERE id = ?",
            (candidate_id,)
        ).fetchone()

        if candidate is None:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )

        return dict(candidate)

    finally:
        conn.close()

@app.put("/candidates/{candidate_id}")
def update_candidate(candidate_id: int, candidate: Candidate):
    conn = get_connection()

    try:
        existing = conn.execute(
            "SELECT * FROM candidates WHERE id = ?",
            (candidate_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )

        conn.execute(
            """
            UPDATE candidates
            SET name = ?, email = ?, skills = ?
            WHERE id = ?
            """,
            (
                candidate.name,
                candidate.email,
                candidate.skills,
                candidate_id
            )
        )

        conn.commit()

        return {
            "message": "Candidate updated successfully",
            "candidate_id": candidate_id,
            "name": candidate.name,
            "email": candidate.email,
            "skills": candidate.skills
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@app.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int):
    conn = get_connection()

    try:
        existing = conn.execute(
            "SELECT * FROM candidates WHERE id = ?",
            (candidate_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )

        conn.execute(
            "DELETE FROM candidates WHERE id = ?",
            (candidate_id,)
        )

        conn.commit()

        return {
            "message": "Candidate deleted successfully",
            "candidate_id": candidate_id
        }

    except HTTPException:
        raise

    except Exception:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail="An internal database error occurred"
        )

    finally:
        conn.close()
