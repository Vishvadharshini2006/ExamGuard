from modules.export_manager import (
    get_session_summary_data,
    get_event_logs,
    get_incident_logs,
    export_csv,
    export_complete_session
)
from modules.analytics import analyze_session_risk
from modules.ai_report import generate_session_ai_report

print("Testing session data...")

sessions = get_session_summary_data()

print("Sessions:", len(sessions))


print("Testing event logs...")

events = get_event_logs()

print("Events:", len(events))


print("Testing incidents...")

incidents = get_incident_logs()

print("Incidents:", len(incidents))


if sessions:

    session_id = sessions[0]["session_id"]

    print("Testing session:", session_id)
    
    print("Getting risk information...")

    risk_result = analyze_session_risk()

    risk_level = None
    cluster = None

    if risk_result is not None and not risk_result.empty:

        session_rows = risk_result[
        risk_result["session_id"] == session_id
        ]

    if not session_rows.empty:

        risk_level = session_rows.iloc[0]["risk_level"]

        cluster = int(
            session_rows.iloc[0]["cluster"]
        )

    print("Risk Level:", risk_level)
    print("Cluster:", cluster)
    
    print("Generating AI report...")

ai_report = None

try:

    ai_report, session_data = generate_session_ai_report(
        session_id
    )

    print("AI report generated successfully.")

except Exception as e:

    print("AI report generation failed:")
    print(e)

    export_csv(
        get_session_summary_data(session_id),
        f"session_{session_id}_summary.csv"
    )

    export_csv(
    get_incident_logs(session_id),
    f"session_{session_id}_incidents.csv",
    fieldnames=[
        "incident_id",
        "session_id",
        "candidate_id",
        "event_type",
        "timestamp",
        "severity",
        "details",
        "evidence_path",
        "status",
        "created_at"
    ]
)

   

    export_complete_session(
    session_id,
    risk_level=risk_level,
    cluster=cluster,
    ai_report=ai_report
)
    

    print("Export completed successfully.")

else:

    print("No sessions found in database.")