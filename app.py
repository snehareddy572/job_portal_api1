




import streamlit as st
import hashlib
import secrets
from database import get_connection, create_table

# Create database tables
create_table()

st.set_page_config(
    page_title="Job Portal",
    page_icon="💼",
    layout="wide"
)


# ---------------- PASSWORD FUNCTIONS ----------------

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(password, stored_hash):
    try:
        salt, original_hash = stored_hash.split("$", 1)
        new_hash = hash_password(password, salt)
        calculated_hash = new_hash.split("$", 1)[1]

        return secrets.compare_digest(
            calculated_hash,
            original_hash
        )
    except (ValueError, AttributeError):
        return False


# ---------------- SESSION STATE ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_role" not in st.session_state:
    st.session_state.user_role = ""


# ---------------- NAVIGATION ----------------

st.title("💼 Job Portal")
st.write("Find jobs, apply for opportunities, and manage your career.")

pages = ["Home", "Find Jobs", "Register", "Login"]

if st.session_state.logged_in:
    pages.append("My Account")

    if st.session_state.user_role == "Job Seeker":
        pages.append("My Applications")

    elif st.session_state.user_role == "Employer":
        pages.append("Post a Job")
        pages.append("Manage Applications")

page = st.sidebar.selectbox("Choose a page", pages)


# ---------------- HOME PAGE ----------------

if page == "Home":
    st.header("Welcome to Job Portal")

    st.write(
        "Explore job opportunities and take the next step in your career."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.info("🔍 Search for available jobs.")

    with col2:
        st.info("📄 Apply for jobs and track applications.")


# ---------------- FIND JOBS PAGE ----------------

elif page == "Find Jobs":
    st.header("Find Available Jobs")

    title_search = st.text_input("Search by job title")
    location_search = st.text_input("Search by location")

    conn = get_connection()

    jobs = conn.execute(
        """
        SELECT * FROM jobs
        WHERE LOWER(title) LIKE LOWER(?)
        AND LOWER(location) LIKE LOWER(?)
        ORDER BY id DESC
        """,
        (f"%{title_search}%", f"%{location_search}%")
    ).fetchall()

    conn.close()

    st.write(f"Jobs found: {len(jobs)}")

    if jobs:
        for job in jobs:
            with st.container(border=True):
                st.subheader(job["title"])
                st.write(f"**Company:** {job['company']}")
                st.write(f"**Location:** {job['location']}")
                st.write(f"**Salary:** {job['salary'] or 'Not specified'}")
                st.write(
                    f"**Description:** "
                    f"{job['description'] or 'No description'}"
                )

                if not st.session_state.logged_in:
                    st.info("Log in as a Job Seeker to apply.")

                elif st.session_state.user_role != "Job Seeker":
                    st.info("Only Job Seekers can apply for jobs.")

                else:
                    if st.button("Apply Now", key=f"apply_{job['id']}"):
                        conn = get_connection()

                        try:
                            conn.execute(
                                """
                                INSERT INTO applications
                                (candidate_id, job_id, status)
                                VALUES (?, ?, 'Pending')
                                """,
                                (
                                    st.session_state.user_id,
                                    job["id"]
                                )
                            )

                            conn.commit()
                            st.success("Application submitted successfully!")

                        except Exception as e:
                            if "UNIQUE constraint failed" in str(e):
                                st.warning(
                                    "You have already applied for this job."
                                )
                            else:
                                st.error(
                                    f"Could not submit application: {e}"
                                )

                        finally:
                            conn.close()
    else:
        st.warning("No matching jobs found. Try another search.")


# ---------------- REGISTRATION PAGE ----------------

elif page == "Register":
    st.header("Create an Account")

    role = st.selectbox(
        "Register as",
        ["Job Seeker", "Employer"]
    )

    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    skills = ""

    if role == "Job Seeker":
        skills = st.text_input("Skills (e.g. Python, SQL)")

    if st.button("Register"):
        if not name.strip() or not email.strip() or not password:
            st.error("Please fill in all required fields.")

        elif "@" not in email or "." not in email.split("@")[-1]:
            st.error("Please enter a valid email address.")

        elif len(password) < 8:
            st.error("Password must contain at least 8 characters.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        else:
            conn = get_connection()

            try:
                password_hash = hash_password(password)

                conn.execute(
                    """
                    INSERT INTO candidates
                    (name, email, skills, password_hash, role)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        name.strip(),
                        email.strip().lower(),
                        skills.strip(),
                        password_hash,
                        role
                    )
                )

                conn.commit()

                st.success(
                    "Registration successful! Please go to Login."
                )

            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    st.error("This email is already registered.")
                else:
                    st.error(f"Registration failed: {e}")

            finally:
                conn.close()


# ---------------- LOGIN PAGE ----------------

elif page == "Login":
    st.header("Login to Your Account")

    email = st.text_input("Email Address", key="login_email")
    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button("Login"):
        if not email.strip() or not password:
            st.error("Please enter your email and password.")

        else:
            conn = get_connection()

            user = conn.execute(
                """
                SELECT * FROM candidates
                WHERE email = ?
                """,
                (email.strip().lower(),)
            ).fetchone()

            conn.close()

            if (
                user
                and user["password_hash"]
                and verify_password(password, user["password_hash"])
            ):
                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.user_name = user["name"]
                st.session_state.user_role = (
                    user["role"] or "Job Seeker"
                )

                st.success(f"Welcome, {user['name']}!")
                st.rerun()

            else:
                st.error("Invalid email or password.")


# ---------------- MY ACCOUNT PAGE ----------------

elif page == "My Account":
    st.header("My Account")

    st.write(f"**Name:** {st.session_state.user_name}")
    st.write(f"**User ID:** {st.session_state.user_id}")
    st.write(f"**Role:** {st.session_state.user_role}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.session_state.user_role = ""
        st.rerun()


# ---------------- POST A JOB PAGE ----------------

elif page == "Post a Job":
    if (
        st.session_state.logged_in
        and st.session_state.user_role == "Employer"
    ):
        st.header("Post a New Job")

        title = st.text_input("Job Title")
        company = st.text_input("Company Name")
        location = st.text_input("Job Location")
        salary = st.text_input("Salary")
        description = st.text_area("Job Description")

        if st.button("Publish Job"):
            if (
                not title.strip()
                or not company.strip()
                or not location.strip()
            ):
                st.error(
                    "Please enter the job title, company, and location."
                )

            else:
                conn = get_connection()

                try:
                    conn.execute(
                        """
                        INSERT INTO jobs
                        (title, company, location, salary, description)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            title.strip(),
                            company.strip(),
                            location.strip(),
                            salary.strip(),
                            description.strip()
                        )
                    )

                    conn.commit()
                    st.success("Job posted successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Could not post job: {e}")

                finally:
                    conn.close()
    else:
        st.error("Only logged-in employers can post jobs.")


# ---------------- MY APPLICATIONS PAGE ----------------

elif page == "My Applications":
    if (
        st.session_state.logged_in
        and st.session_state.user_role == "Job Seeker"
    ):
        st.header("My Applications")

        conn = get_connection()

        applications = conn.execute(
            """
            SELECT
                applications.id,
                jobs.title,
                jobs.company,
                jobs.location,
                jobs.salary,
                applications.status
            FROM applications
            JOIN jobs
                ON applications.job_id = jobs.id
            WHERE applications.candidate_id = ?
            ORDER BY applications.id DESC
            """,
            (st.session_state.user_id,)
        ).fetchall()

        conn.close()

        if applications:
            for application in applications:
                with st.container(border=True):
                    st.subheader(application["title"])
                    st.write(f"**Company:** {application['company']}")
                    st.write(f"**Location:** {application['location']}")
                    st.write(
                        f"**Salary:** "
                        f"{application['salary'] or 'Not specified'}"
                    )
                    st.write(
                        f"**Application Status:** {application['status']}"
                    )
        else:
            st.info("You have not applied for any jobs yet.")

    else:
        st.error("This page is only for logged-in Job Seekers.")


# ---------------- MANAGE APPLICATIONS PAGE ----------------

elif page == "Manage Applications":
    if (
        st.session_state.logged_in
        and st.session_state.user_role == "Employer"
    ):
        st.header("Manage Applications")

        conn = get_connection()

        applications = conn.execute(
            """
            SELECT
                applications.id AS application_id,
                candidates.name AS candidate_name,
                candidates.email AS candidate_email,
                candidates.skills AS candidate_skills,
                jobs.title AS job_title,
                jobs.company AS company,
                applications.status AS application_status
            FROM applications
            JOIN candidates
                ON applications.candidate_id = candidates.id
            JOIN jobs
                ON applications.job_id = jobs.id
            ORDER BY applications.id DESC
            """
        ).fetchall()

        conn.close()

        if applications:
            st.write(f"Total applications: {len(applications)}")

            for application in applications:
                with st.container(border=True):
                    st.subheader(application["job_title"])

                    st.write(
                        f"**Candidate:** {application['candidate_name']}"
                    )
                    st.write(
                        f"**Email:** {application['candidate_email']}"
                    )
                    st.write(
                        f"**Skills:** "
                        f"{application['candidate_skills'] or 'Not provided'}"
                    )
                    st.write(f"**Company:** {application['company']}")
                    st.write(
                        f"**Current Status:** "
                        f"{application['application_status']}"
                    )

                    statuses = ["Pending", "Shortlisted", "Rejected"]
                    current_status = application["application_status"]

                    status_index = (
                        statuses.index(current_status)
                        if current_status in statuses
                        else 0
                    )

                    new_status = st.selectbox(
                        "Update application status",
                        statuses,
                        index=status_index,
                        key=f"status_{application['application_id']}"
                    )

                    if st.button(
                        "Save Status",
                        key=f"save_{application['application_id']}"
                    ):
                        conn = get_connection()

                        try:
                            conn.execute(
                                """
                                UPDATE applications
                                SET status = ?
                                WHERE id = ?
                                """,
                                (
                                    new_status,
                                    application["application_id"]
                                )
                            )

                            conn.commit()
                            st.success("Application status updated!")
                            st.rerun()

                        except Exception as e:
                            st.error(
                                f"Could not update application: {e}"
                            )

                        finally:
                            conn.close()

        else:
            st.info("No job applications have been received yet.")

    else:
        st.error("Only logged-in employers can manage applications.")
