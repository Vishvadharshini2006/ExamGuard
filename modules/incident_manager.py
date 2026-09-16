"""
ExamGuard Incident Management

This module converts suspicious examination
events into structured incidents.

Important:
Incident severity is independent from
Integrity Score deduction.
"""


from datetime import datetime

from database import create_incident


# =========================================================
# EVENT SEVERITY
# =========================================================

EVENT_SEVERITY = {

    # Browser events
    "Tab Switched": "Medium",

    "Right Click": "Low",

    "Copy Attempt": "Medium",

    "Paste Attempt": "Medium",

    "F12 Pressed": "High",

    "Developer Tools Attempt": "High",

    "Developer Tools": "High",

    "View Source Attempt": "High",

    # Face monitoring
    "Face Missing": "Medium",

    "Multiple Faces": "High",

    "Camera Covered": "High"
}


# =========================================================
# EVENTS THAT CREATE INCIDENTS
# =========================================================

INCIDENT_EVENTS = {

    "Tab Switched",

    "Right Click",

    "Copy Attempt",

    "Paste Attempt",

    "F12 Pressed",

    "Developer Tools Attempt",

    "Developer Tools",

    "View Source Attempt",

    "Face Missing",

    "Multiple Faces",

    "Camera Covered"
}


# =========================================================
# GET SEVERITY
# =========================================================

def get_event_severity(event_type):

    return EVENT_SEVERITY.get(
        event_type,
        "Low"
    )


# =========================================================
# SHOULD CREATE INCIDENT?
# =========================================================

def should_create_incident(event_type):

    return event_type in INCIDENT_EVENTS


# =========================================================
# REGISTER INCIDENT
# =========================================================

def register_incident(
    session_id,
    candidate_id,
    event_type,
    details=None,
    evidence_path=None,
    timestamp=None
):

    if not should_create_incident(event_type):

        return None

    if timestamp is None:

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    severity = get_event_severity(
        event_type
    )

    incident_id = create_incident(

        session_id=session_id,

        candidate_id=candidate_id,

        event_type=event_type,

        timestamp=timestamp,

        severity=severity,

        details=details,

        evidence_path=evidence_path
    )

    return incident_id


# =========================================================
# INCIDENT SUMMARY
# =========================================================

def get_incident_summary(incidents):

    summary = {

        "total": 0,

        "high": 0,

        "medium": 0,

        "low": 0,

        "pending": 0,

        "reviewed": 0,

        "dismissed": 0
    }


    for incident in incidents:

        summary["total"] += 1


        severity = incident.get(
            "severity",
            ""
        ).lower()


        status = incident.get(
            "status",
            ""
        ).lower()


        if severity == "high":

            summary["high"] += 1

        elif severity == "medium":

            summary["medium"] += 1

        elif severity == "low":

            summary["low"] += 1


        if status == "pending":

            summary["pending"] += 1

        elif status == "reviewed":

            summary["reviewed"] += 1

        elif status == "dismissed":

            summary["dismissed"] += 1


    return summary
