import os
import csv
import json
import sqlite3

from config import DATABASE


EXPORT_DIR = "exports"


def create_export_directory():
    os.makedirs(EXPORT_DIR, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------
# SESSION SUMMARY
# ---------------------------------------------------------

def get_session_summary_data(session_id=None):

    conn = get_connection()

    if session_id is not None:

        query = """
            SELECT
                es.session_id,
                es.candidate_id,
                es.start_time,
                es.end_time,
                es.status,
                es.integrity_score
            FROM exam_session es
            WHERE es.session_id = ?
        """

        rows = conn.execute(query, (session_id,)).fetchall()

    else:

        query = """
            SELECT
                es.session_id,
                es.candidate_id,
                es.start_time,
                es.end_time,
                es.status,
                es.integrity_score
            FROM exam_session es
            ORDER BY es.session_id
        """

        rows = conn.execute(query).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ---------------------------------------------------------
# EVENT LOGS
# ---------------------------------------------------------

def get_event_logs(session_id=None):

    conn = get_connection()

    if session_id is not None:

        query = """
            SELECT
                event_id,
                session_id,
                event_type,
                timestamp,
                details
            FROM event_log
            WHERE session_id = ?
            ORDER BY timestamp
        """

        rows = conn.execute(query, (session_id,)).fetchall()

    else:

        query = """
            SELECT
                event_id,
                session_id,
                event_type,
                timestamp,
                details
            FROM event_log
            ORDER BY timestamp
        """

        rows = conn.execute(query).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ---------------------------------------------------------
# INCIDENTS
# ---------------------------------------------------------

def get_incident_logs(session_id=None):

    conn = get_connection()

    if session_id is not None:

        query = """
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
            ORDER BY timestamp
        """

        rows = conn.execute(query, (session_id,)).fetchall()

    else:

        query = """
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
            ORDER BY timestamp
        """

        rows = conn.execute(query).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ---------------------------------------------------------
# CSV EXPORT
# ---------------------------------------------------------

def export_csv(data, filename, fieldnames=None):

    create_export_directory()

    filepath = os.path.join(EXPORT_DIR, filename)

    if not data and fieldnames is None:
        return filepath

    if fieldnames is None:
        fieldnames = data[0].keys()

    with open(filepath, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        if data:
            writer.writerows(data)

    return filepath


# ---------------------------------------------------------
# JSON EXPORT
# ---------------------------------------------------------

def export_json(data, filename):

    create_export_directory()

    filepath = os.path.join(EXPORT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=4,
            default=str
        )

    return filepath


# ---------------------------------------------------------
# COMPLETE SESSION EXPORT
# ---------------------------------------------------------

def export_complete_session(session_id, risk_level=None,
                            cluster=None, ai_report=None):

    session_data = get_session_summary_data(session_id)
    events = get_event_logs(session_id)
    incidents = get_incident_logs(session_id)

    complete_data = {

        "session": session_data,

        "risk_level": risk_level,

        "cluster": cluster,

        "events": events,

        "incidents": incidents,

        "ai_report": ai_report

    }

    filename = f"session_{session_id}_complete.json"

    return export_json(
        complete_data,
        filename
    )