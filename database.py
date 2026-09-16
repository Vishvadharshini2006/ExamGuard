import sqlite3
from werkzeug.security import generate_password_hash
from config import DATABASE

DATABASE_NAME = DATABASE


# ---------------- DATABASE CONNECTION ---------------- #

def create_connection():

    conn = sqlite3.connect(DATABASE_NAME)
    return conn


# ---------------- CREATE TABLES ---------------- #

def create_tables():

    conn = create_connection()
    cursor = conn.cursor()

    # ---------------- Candidate Table ---------------- #

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS candidate(

        candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,

        full_name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password_hash TEXT NOT NULL,

        photo_path TEXT,

        govt_id_path TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # ---------------- Exam Session ---------------- #

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS exam_session(

        session_id INTEGER PRIMARY KEY AUTOINCREMENT,

        candidate_id INTEGER,

        start_time TEXT,

        end_time TEXT,

        status TEXT,

        integrity_score INTEGER DEFAULT 100,
        

        FOREIGN KEY(candidate_id)

        REFERENCES candidate(candidate_id)

    )

    """)

    # ---------------- Event Log ---------------- #

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS event_log(

        event_id INTEGER PRIMARY KEY AUTOINCREMENT,

        session_id INTEGER,

        event_type TEXT,

        timestamp TEXT,

        details TEXT,

        FOREIGN KEY(session_id)

        REFERENCES exam_session(session_id)

    )

    """)

    # ---------------- Question Table ---------------- #

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS question(

        question_id INTEGER PRIMARY KEY AUTOINCREMENT,

        question TEXT NOT NULL,

        option1 TEXT,

        option2 TEXT,

        option3 TEXT,

        option4 TEXT,

        correct_answer TEXT

    )

    """)

    # ---------------- Candidate Response ---------------- #

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS candidate_response(

        response_id INTEGER PRIMARY KEY AUTOINCREMENT,

        session_id INTEGER,

        question_id INTEGER,

        selected_option TEXT,

        FOREIGN KEY(session_id)

        REFERENCES exam_session(session_id),

        FOREIGN KEY(question_id)

        REFERENCES question(question_id)

    )

    """)
    
    
    # ---------------- INCIDENT TABLE ---------------- #

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident(
            incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            candidate_id INTEGER,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            severity TEXT NOT NULL,
            details TEXT,
            evidence_path TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(session_id)
                REFERENCES exam_session(session_id),

            FOREIGN KEY(candidate_id)
                REFERENCES candidate(candidate_id)
        )
    """)



    conn.commit()
    conn.close()
    
# ---------------- ADD CANDIDATE ---------------- #

def add_candidate(full_name, email, password):

    conn = create_connection()
    cursor = conn.cursor()

    password_hash = generate_password_hash(password)

    cursor.execute("""

        INSERT INTO candidate(

            full_name,
            email,
            password_hash

        )

        VALUES(?,?,?)

    """,(full_name,email,password_hash))

    conn.commit()
    conn.close()


# ---------------- GET CANDIDATE ---------------- #

def get_candidate_by_email(email):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM candidate

        WHERE email=?

    """,(email,))

    candidate = cursor.fetchone()

    conn.close()

    return candidate


# ---------------- START EXAM SESSION ---------------- #

def start_exam_session(candidate_id, start_time):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO exam_session(

            candidate_id,
            start_time,
            status,
            integrity_score

        )

        VALUES(?,?,?,?)

    """,(candidate_id,start_time,"Started",100))

    conn.commit()

    session_id = cursor.lastrowid

    conn.close()

    return session_id


# ---------------- UPDATE SESSION STATUS ---------------- #

def update_session_status(session_id, status):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE exam_session

        SET status=?

        WHERE session_id=?

    """,(status,session_id))

    conn.commit()
    conn.close()


# ---------------- END EXAM SESSION ---------------- #

def end_exam_session(session_id, end_time):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE exam_session

        SET

            end_time=?,
            status=?

        WHERE session_id=?

    """,(end_time,"Submitted",session_id))

    conn.commit()
    conn.close()


def update_candidate_photo(candidate_id, photo_path):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE candidate
        SET photo_path = ?
        WHERE candidate_id = ?
    """, (photo_path, candidate_id))

    conn.commit()
    conn.close()
# ---------------- UPDATE GOVERNMENT ID ---------------- #

def update_govt_id(candidate_id, govt_id_path):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE candidate

        SET govt_id_path=?

        WHERE candidate_id=?

    """,(govt_id_path,candidate_id))

    conn.commit()
    conn.close()


# ---------------- PAUSE EXAM ---------------- #

def pause_exam_session(session_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE exam_session

        SET status=?

        WHERE session_id=?

    """,("Paused",session_id))

    conn.commit()
    conn.close()


# ---------------- RESUME EXAM ---------------- #

def resume_exam_session(session_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE exam_session

        SET status=?

        WHERE session_id=?

    """,("Running",session_id))

    conn.commit()
    conn.close()
    
# ---------------- GET INTEGRITY SCORE ---------------- #

def get_integrity_score(session_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT integrity_score

        FROM exam_session

        WHERE session_id=?

    """,(session_id,))

    score = cursor.fetchone()

    conn.close()

    if score:
        return score[0]

    return 100


# =====================================================
# INTEGRITY SCORE
# =====================================================

def get_integrity_score(session_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT integrity_score
        FROM exam_session
        WHERE session_id=?
    """, (session_id,))

    result = cursor.fetchone()

    conn.close()

    if result and result[0] is not None:
        return result[0]

    return 100


def update_integrity_score(session_id, score):

    score = max(0, min(100, int(score)))

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE exam_session
        SET integrity_score=?
        WHERE session_id=?
    """, (score, session_id))

    conn.commit()
    conn.close()


def deduct_integrity_score(session_id, deduction):

    current_score = get_integrity_score(session_id)

    new_score = max(
        0,
        current_score - deduction
    )

    update_integrity_score(
        session_id,
        new_score
    )

    return new_score





# ---------------- LOG EVENTS ---------------- #

from datetime import datetime

def log_event(session_id, event_type, timestamp=None, details=None):

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if details is None:
        details = ""

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO event_log(

            session_id,
            event_type,
            timestamp,
            details

        )

        VALUES(?,?,?,?)

    """,(session_id,event_type,timestamp,details))

    conn.commit()
    conn.close()
    

# =========================================================
# INCIDENT MANAGEMENT
# =========================================================

def create_incident(
    session_id,
    candidate_id,
    event_type,
    timestamp,
    severity,
    details=None,
    evidence_path=None
):
    """
    Create a new incident record.
    """

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO incident (
            session_id,
            candidate_id,
            event_type,
            timestamp,
            severity,
            details,
            evidence_path,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        candidate_id,
        event_type,
        timestamp,
        severity,
        details,
        evidence_path,
        "Pending"
    ))

    incident_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return incident_id


def get_incidents(session_id=None):
    """
    Get incidents for one session.
    If session_id is None, return all incidents.
    """

    conn = create_connection()
    cursor = conn.cursor()

    if session_id is not None:

        cursor.execute("""
            SELECT
                incident_id,
                session_id,
                candidate_id,
                event_type,
                timestamp,
                severity,
                details,
                evidence_path,
                status,
                created_at
            FROM incident
            WHERE session_id = ?
            ORDER BY timestamp DESC
        """, (session_id,))

    else:

        cursor.execute("""
            SELECT
                incident_id,
                session_id,
                candidate_id,
                event_type,
                timestamp,
                severity,
                details,
                evidence_path,
                status,
                created_at
            FROM incident
            ORDER BY timestamp DESC
        """)

    rows = cursor.fetchall()

    conn.close()

    incidents = []

    for row in rows:

        incidents.append({
            "incident_id": row[0],
            "session_id": row[1],
            "candidate_id": row[2],
            "event_type": row[3],
            "timestamp": row[4],
            "severity": row[5],
            "details": row[6],
            "evidence_path": row[7],
            "status": row[8],
            "created_at": row[9]
        })

    return incidents


def get_incident(incident_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            incident_id,
            session_id,
            candidate_id,
            event_type,
            timestamp,
            severity,
            details,
            evidence_path,
            status,
            created_at
        FROM incident
        WHERE incident_id = ?
    """, (incident_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return {
        "incident_id": row[0],
        "session_id": row[1],
        "candidate_id": row[2],
        "event_type": row[3],
        "timestamp": row[4],
        "severity": row[5],
        "details": row[6],
        "evidence_path": row[7],
        "status": row[8],
        "created_at": row[9]
    }


def update_incident_status(incident_id, status):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE incident
        SET status = ?
        WHERE incident_id = ?
    """, (
        status,
        incident_id
    ))

    conn.commit()
    conn.close()


def update_incident_evidence(
    incident_id,
    evidence_path
):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE incident
        SET evidence_path = ?
        WHERE incident_id = ?
    """, (
        evidence_path,
        incident_id
    ))

    conn.commit()
    conn.close()


# ---------------- INSERT DEMO QUESTIONS ---------------- #

def insert_demo_questions():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT COUNT(*)

        FROM question

    """)

    count = cursor.fetchone()[0]

    if count == 0:

        questions = [

            (
                "What does AI stand for?",
                "Artificial Intelligence",
                "Automatic Internet",
                "Advanced Interface",
                "Artificial Integration",
                "Artificial Intelligence"
            ),

            (
                "Python is a...",
                "Programming Language",
                "Database",
                "Browser",
                "Operating System",
                "Programming Language"
            ),

            (
                "Which company developed Java?",
                "Microsoft",
                "Sun Microsystems",
                "Google",
                "Apple",
                "Sun Microsystems"
            ),

            (
                "Which SQL command retrieves data?",
                "SELECT",
                "INSERT",
                "UPDATE",
                "DELETE",
                "SELECT"
            ),

            (
                "Flask is a...",
                "Python Framework",
                "Database",
                "Compiler",
                "Browser",
                "Python Framework"
            )

        ]

        cursor.executemany("""

            INSERT INTO question(

                question,
                option1,
                option2,
                option3,
                option4,
                correct_answer

            )

            VALUES(?,?,?,?,?,?)

        """,questions)

    conn.commit()
    conn.close()
    
# ==========================================================
# GET TOTAL QUESTIONS
# ==========================================================

def get_total_questions():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT COUNT(*)

        FROM question

    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total


# ==========================================================
# GET QUESTION BY QUESTION NUMBER
# ==========================================================

def get_question(question_number):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM question

        ORDER BY question_id

        LIMIT 1 OFFSET ?

    """, (question_number - 1,))

    question = cursor.fetchone()

    conn.close()

    return question


# ==========================================================
# SAVE / UPDATE RESPONSE
# ==========================================================

def save_response(session_id, question_id, selected_option):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT response_id

        FROM candidate_response

        WHERE session_id=? AND question_id=?

    """, (session_id, question_id))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""

            UPDATE candidate_response

            SET selected_option=?

            WHERE session_id=? AND question_id=?

        """, (selected_option, session_id, question_id))

    else:

        cursor.execute("""

            INSERT INTO candidate_response(

                session_id,
                question_id,
                selected_option

            )

            VALUES(?,?,?)

        """, (session_id, question_id, selected_option))

    conn.commit()
    conn.close()


# ==========================================================
# GET SAVED RESPONSE
# ==========================================================

def get_saved_response(session_id, question_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT selected_option

        FROM candidate_response

        WHERE session_id=? AND question_id=?

    """, (session_id, question_id))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return None


# ==========================================================
# ATTEMPTED QUESTION COUNT
# ==========================================================

def get_attempted_count(session_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT COUNT(*)

        FROM candidate_response

        WHERE session_id=?

    """, (session_id,))

    attempted = cursor.fetchone()[0]

    conn.close()

    return attempted


# ==========================================================
# GET ALL QUESTIONS (for palette)
# ==========================================================

def get_all_questions():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM question

        ORDER BY question_id

    """)

    questions = cursor.fetchall()

    conn.close()

    return questions


# ==========================================================
# GET CANDIDATE RESPONSES
# ==========================================================

def get_candidate_responses(session_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT question_id, selected_option

        FROM candidate_response

        WHERE session_id=?

    """, (session_id,))

    responses = cursor.fetchall()

    conn.close()

    return responses



def get_session_report(session_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""

    SELECT

        c.full_name,

        e.session_id,

        e.start_time,

        e.end_time,

        e.integrity_score

    FROM exam_session e

    JOIN candidate c

    ON e.candidate_id=c.candidate_id

    WHERE e.session_id=?

    """,(session_id,))

    report = cursor.fetchone()

    conn.close()

    return report


def get_all_events(session_id):

    conn=create_connection()

    cursor=conn.cursor()

    cursor.execute("""

    SELECT

    event_type,

    timestamp

    FROM event_log

    WHERE session_id=?

    ORDER BY timestamp

    """,(session_id,))

    events=cursor.fetchall()

    conn.close()

    return events

# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    create_tables()

    insert_demo_questions()

    print("Database and tables created successfully.")