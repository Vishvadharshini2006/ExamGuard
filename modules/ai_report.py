import os
import json

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from modules.analytics import (
    get_session_analytics,
    get_event_frequency,
    get_face_presence_percentage,
    get_category_frequency,
    analyze_session_risk
)

from database import (
    get_incidents
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not configured. "
        "Please add it to the .env file."
    )

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

REPORT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are the AI Integrity Assessment Analyst for ExamGuard,
an online examination proctoring and integrity monitoring system.

Your task is to analyze the structured examination data supplied
by ExamGuard and produce a professional, objective, evidence-based
integrity assessment for an examination administrator.

The report must be factual, neutral, concise, and suitable for
official examination review.

============================================================
STRICT DATA INTEGRITY RULES
============================================================

1. Use ONLY the information provided in the supplied session data.
...
[The rest of the system prompt remains unchanged]
"""
    ),
    (
        "human",
        """
Analyze the following REAL ExamGuard examination session.

Use only the supplied information.

SESSION DATA:

{session_data}
"""
    )
])

def get_session_risk_level(session_id):
    try:
        risk_dataframe = analyze_session_risk()
        if (
            risk_dataframe is None
            or risk_dataframe.empty
        ):
            return "Not Available"

        session_rows = risk_dataframe[
            risk_dataframe["session_id"] == session_id
        ]

        if session_rows.empty:
            return "Not Available"

        risk_level = session_rows.iloc[0].get(
            "risk_level"
        )

        if risk_level is None:
            return "Not Available"

        return str(risk_level)

    except Exception as e:
        print(
            "RISK ANALYSIS ERROR:",
            str(e)
        )
        return "Not Available"

def get_ai_session_data(session_id):
    session_data = get_session_analytics(
        session_id
    )

    if session_data is None:
        return None

    event_frequency = get_event_frequency(
        session_id
    )

    category_frequency = get_category_frequency(
        session_id
    )

    face_presence_percentage = (
        get_face_presence_percentage(
            session_id
        )
    )

    incidents = get_incidents(
        session_id
    )

    risk_level = get_session_risk_level(
        session_id
    )

    formatted_incidents = []
    evidence_count = 0

    for incident in incidents:
        evidence_available = bool(
            incident.get(
                "evidence_path"
            )
        )

        if evidence_available:
            evidence_count += 1

        formatted_incidents.append({
            "incident_id":
                incident.get(
                    "incident_id"
                ),
            "event_type":
                incident.get(
                    "event_type"
                ),
            "timestamp":
                incident.get(
                    "timestamp"
                ),
            "severity":
                incident.get(
                    "severity"
                ),
            "details":
                incident.get(
                    "details"
                ),
            "evidence_available":
                evidence_available,
            "status":
                incident.get(
                    "status"
                )
        })

    browser_events = {}
    face_events = {}
    camera_events = {}
    multiple_face_events = {}

    for event, count in event_frequency.items():
        if event in {
            "Tab Switched",
            "Right Click",
            "Copy Attempt",
            "Paste Attempt",
            "F12 Pressed",
            "Developer Tools Attempt",
            "Developer Tools",
            "View Source Attempt"
        }:
            browser_events[event] = count

        elif event in {
            "Face Missing",
            "Face Detected"
        }:
            face_events[event] = count

        elif event == "Camera Covered":
            camera_events[event] = count

        elif event in {
            "Multiple Faces",
            "Multiple Faces Detected"
        }:
            multiple_face_events[event] = count

    ai_data = {
        "session_information": {
            "session_id":
                session_data.get(
                    "session_id"
                ),
            "candidate_id":
                session_data.get(
                    "candidate_id"
                ),
            "start_time":
                session_data.get(
                    "start_time"
                ),
            "end_time":
                session_data.get(
                    "end_time"
                ),
            "status":
                session_data.get(
                    "status"
                )
        },
        "official_integrity_score":
            session_data.get(
                "integrity_score"
            ),
        "risk_level":
            risk_level,
        "total_events":
            session_data.get(
                "total_events"
            ),
        "event_frequency":
            event_frequency,
        "browser_events":
            browser_events,
        "face_events":
            face_events,
        "camera_events":
            camera_events,
        "multiple_face_events":
            multiple_face_events,
        "event_categories":
            category_frequency,
        "face_presence_percentage":
            face_presence_percentage,
        "incident_count":
            len(incidents),
        "incidents":
            formatted_incidents,
        "evidence_summary": {
            "total_incidents":
                len(incidents),
            "incidents_with_evidence":
                evidence_count,
            "evidence_available":
                evidence_count > 0
        }
    }

    return ai_data

def generate_ai_report(session_data):
    try:
        formatted_data = json.dumps(
            session_data,
            indent=4,
            default=str
        )

        prompt = REPORT_PROMPT.format_messages(
            session_data=formatted_data
        )

        response = llm.invoke(
            prompt
        )

        return response.content

    except Exception as e:
        print(
            "AI REPORT ERROR:",
            str(e)
        )
        return None

def generate_session_ai_report(
    session_id
):
    session_data = get_ai_session_data(
        session_id
    )

    if session_data is None:
        return None, None

    report = generate_ai_report(
        session_data
    )

    return report, session_data

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("EXAMGUARD LANGCHAIN TEST")
    print("=" * 70)

    try:
        session_id = int(
            input(
                "Enter Session ID to analyze: "
            )
        )

        print()
        print(
            "Collecting ExamGuard session data..."
        )

        report, session_data = (
            generate_session_ai_report(
                session_id
            )
        )

        if session_data is None:
            print()
            print(
                "Session not found."
            )

        elif report is None:
            print()
            print(
                "AI report generation failed."
            )

        else:
            print()
            print(
                "REAL SESSION DATA:"
            )

            print(
                json.dumps(
                    session_data,
                    indent=4,
                    default=str
                )
            )

            print()
            print("=" * 70)
            print(
                "EXAMGUARD AI INTEGRITY REPORT"
            )
            print("=" * 70)
            print()

            print(
                report
            )

            print()
            print("=" * 70)

    except ValueError:
        print(
            "Please enter a valid numeric session ID."
        )
