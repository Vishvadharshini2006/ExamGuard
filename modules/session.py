import sqlite3
import os



BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE = os.path.join(
    BASE_DIR,
    "exam.db"
)


def create_connection():

    return sqlite3.connect(DATABASE)



def get_exam_session(session_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            session_id,
            candidate_id,
            start_time,
            end_time,
            status,
            integrity_score
        FROM exam_session
        WHERE session_id=?
    """, (session_id,))

    session_data = cursor.fetchone()

    conn.close()

    return session_data



def get_session_events(session_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            event_type,
            timestamp,
            details
        FROM event_log
        WHERE session_id=?
        ORDER BY timestamp
    """, (session_id,))

    events = cursor.fetchall()

    conn.close()

    return events



def get_session_responses(session_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            response_id,
            question_id,
            selected_option
        FROM candidate_response
        WHERE session_id=?
    """, (session_id,))

    responses = cursor.fetchall()

    conn.close()

    return responses



def get_session_summary(session_id):

    session_data = get_exam_session(
        session_id
    )

    if session_data is None:

        return None

    events = get_session_events(
        session_id
    )

    responses = get_session_responses(
        session_id
    )

    return {

        "session": session_data,

        "events": events,

        "responses": responses

    }
    


def analyze_exam_session(
    session_id,
    exam_duration_seconds,
    face_absent_seconds=0
):

    from modules.scoring import analyze_session

    # Get events from database
    events = get_session_events(session_id)

    # Send events to scoring module
    result = analyze_session(
        events,
        exam_duration_seconds,
        face_absent_seconds
    )

    return result


def get_latest_session(candidate_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT session_id
        FROM exam_session
        WHERE candidate_id=?
        ORDER BY session_id DESC
        LIMIT 1
    """, (candidate_id,))

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None