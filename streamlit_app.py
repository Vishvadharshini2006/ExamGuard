import streamlit as st
import sqlite3
import pandas as pd

from config import DATABASE

from modules.analytics import (
    analyze_session_risk,
    get_face_presence_percentage,
    get_event_frequency,
    get_category_frequency,
    get_integrity_timeline
)

from modules.ai_report import generate_session_ai_report

from modules.export_manager import (
    export_csv,
    export_complete_session,
    get_session_summary_data,
    get_event_logs,
    get_incident_logs
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ExamGuard Dashboard",
    page_icon="🛡️",
    layout="wide"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    return sqlite3.connect(DATABASE)


# =========================================================
# GET ALL SESSIONS
# =========================================================

def get_sessions():

    conn = get_connection()

    query = """
        SELECT
            session_id,
            candidate_id,
            start_time,
            end_time,
            status,
            integrity_score
        FROM exam_session
        ORDER BY session_id DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# =========================================================
# GET EVENTS
# =========================================================

def get_session_events(session_id):

    conn = get_connection()

    query = """
        SELECT
            event_id,
            event_type,
            timestamp,
            details
        FROM event_log
        WHERE session_id = ?
        ORDER BY timestamp
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(session_id,)
    )

    conn.close()

    return df


# =========================================================
# GET INCIDENTS
# =========================================================

def get_session_incidents(session_id):

    conn = get_connection()

    query = """
        SELECT
            incident_id,
            event_type,
            timestamp,
            severity,
            details,
            evidence_path,
            status
        FROM incident
        WHERE session_id = ?
        ORDER BY timestamp
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(session_id,)
    )

    conn.close()

    return df


# =========================================================
# GET RISK DATA
# =========================================================

def get_risk_data():

    try:

        result = analyze_session_risk()

        if result is None:
            return pd.DataFrame()

        if isinstance(result, pd.DataFrame):

            return result

        return pd.DataFrame(result)

    except Exception:

        return pd.DataFrame()


# =========================================================
# PAGE HEADER
# =========================================================

st.title("🛡️ ExamGuard")

st.subheader(
    "Online Examination Monitoring & Analytics Dashboard"
)

st.divider()


# =========================================================
# LOAD SESSIONS
# =========================================================

sessions = get_sessions()

if sessions.empty:

    st.warning(
        "No examination sessions found."
    )

    st.stop()


# =========================================================
# SESSION SELECTOR
# =========================================================

session_ids = sessions["session_id"].tolist()

selected_session = st.selectbox(
    "Select Examination Session",
    session_ids
)


# =========================================================
# SELECTED SESSION
# =========================================================

session = sessions[
    sessions["session_id"] == selected_session
].iloc[0]


# =========================================================
# LOAD EVENTS
# =========================================================

events = get_session_events(
    selected_session
)


# =========================================================
# LOAD INCIDENTS
# =========================================================

incidents = get_session_incidents(
    selected_session
)


# =========================================================
# RISK INFORMATION
# =========================================================

risk_level = "Not Available"
cluster = "Not Available"

risk_data = get_risk_data()


if not risk_data.empty:

    if "session_id" in risk_data.columns:

        risk_rows = risk_data[
            risk_data["session_id"] == selected_session
        ]

        if not risk_rows.empty:

            if "risk_level" in risk_rows.columns:

                risk_level = risk_rows.iloc[0][
                    "risk_level"
                ]

            if "cluster" in risk_rows.columns:

                cluster = risk_rows.iloc[0][
                    "cluster"
                ]


# =========================================================
# FACE PRESENCE
# =========================================================

try:

    face_presence = get_face_presence_percentage(
        selected_session
    )

except Exception:

    face_presence = 0


# =========================================================
# SESSION OVERVIEW
# =========================================================

st.subheader("Session Overview")

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Session ID",
        session["session_id"]
    )


with col2:

    st.metric(
        "Integrity Score",
        f"{session['integrity_score']}%"
    )


with col3:

    st.metric(
        "Risk Level",
        risk_level
    )


with col4:

    st.metric(
        "Violations",
        len(events)
    )


with col5:

    st.metric(
        "Face Presence",
        f"{face_presence:.1f}%"
    )


# =========================================================
# MONITORING SUMMARY
# =========================================================

st.divider()

st.subheader("Monitoring Summary")

monitor_col1, monitor_col2, monitor_col3 = st.columns(3)


with monitor_col1:

    st.info(
        f"**Monitoring Events:** {len(events)}"
    )


with monitor_col2:

    st.warning(
        f"**Incidents:** {len(incidents)}"
    )


with monitor_col3:

    st.info(
        f"**K-Means Cluster:** {cluster}"
    )


# =========================================================
# SESSION INFORMATION
# =========================================================

st.divider()

st.subheader("Session Information")

info_col1, info_col2 = st.columns(2)


with info_col1:

    st.write(
        "**Session ID:**",
        session["session_id"]
    )

    st.write(
        "**Candidate ID:**",
        session["candidate_id"]
    )

    st.write(
        "**Status:**",
        session["status"]
    )


with info_col2:

    st.write(
        "**Start Time:**",
        session["start_time"]
    )

    st.write(
        "**End Time:**",
        session["end_time"]
    )

    st.write(
        "**Integrity Score:**",
        f"{session['integrity_score']}%"
    )


# =========================================================
# DATA SCIENCE ANALYTICS
# =========================================================

st.divider()

st.header("Data Science Analytics")


# =========================================================
# 1. INTEGRITY TIMELINE
# =========================================================

st.subheader("Integrity Score Timeline")

try:

    timeline = get_integrity_timeline(
        selected_session
    )

    # Existing function returns a LIST
    if timeline:

        timeline_df = pd.DataFrame(
            timeline
        )

        # If the function returns dictionaries
        if not timeline_df.empty:

            # Try to identify useful columns
            if (
                "timestamp" in timeline_df.columns
                and "integrity_score" in timeline_df.columns
            ):

                timeline_df["timestamp"] = pd.to_datetime(
                    timeline_df["timestamp"]
                )

                timeline_df = timeline_df.set_index(
                    "timestamp"
                )

                st.line_chart(
                    timeline_df["integrity_score"]
                )

            elif "integrity_score" in timeline_df.columns:

                st.line_chart(
                    timeline_df["integrity_score"]
                )

            else:

                st.dataframe(
                    timeline_df,
                    use_container_width=True,
                    hide_index=True
                )

        else:

            st.info(
                "No integrity timeline data available."
            )

    else:

        st.info(
            "No integrity timeline data available."
        )

except Exception as e:

    st.warning(
        f"Integrity timeline could not be generated: {e}"
    )


# =========================================================
# 2. EVENT FREQUENCY
# =========================================================

st.subheader("Event Frequency")

try:

    event_frequency = get_event_frequency(
        selected_session
    )

    # Existing function returns a DICTIONARY
    if event_frequency:

        event_df = pd.DataFrame(
            list(event_frequency.items()),
            columns=[
                "Event",
                "Count"
            ]
        )

        event_df = event_df.set_index(
            "Event"
        )

        st.bar_chart(
            event_df
        )

    else:

        st.info(
            "No event frequency data available."
        )

except Exception as e:

    st.warning(
        f"Event frequency could not be generated: {e}"
    )


# =========================================================
# 3. VIOLATION CATEGORY DISTRIBUTION
# =========================================================

st.subheader(
    "Violation Category Distribution"
)

try:

    category_frequency = get_category_frequency(
        selected_session
    )

    # Existing function returns a DICTIONARY
    if category_frequency:

        category_df = pd.DataFrame(
            list(category_frequency.items()),
            columns=[
                "Category",
                "Count"
            ]
        )

        category_df = category_df.set_index(
            "Category"
        )

        st.bar_chart(
            category_df
        )

    else:

        st.info(
            "No category data available."
        )

except Exception as e:

    st.warning(
        f"Category analysis could not be generated: {e}"
    )


# =========================================================
# 4. K-MEANS RISK ANALYSIS
# =========================================================

st.subheader(
    "K-Means Risk Analysis"
)


if not risk_data.empty:

    display_columns = []

    possible_columns = [
        "session_id",
        "integrity_score",
        "total_events",
        "cluster",
        "risk_level"
    ]

    for column in possible_columns:

        if column in risk_data.columns:

            display_columns.append(
                column
            )


    if display_columns:

        st.dataframe(
            risk_data[display_columns],
            use_container_width=True,
            hide_index=True
        )


    if (
        "integrity_score" in risk_data.columns
        and "total_events" in risk_data.columns
    ):

        st.write(
            "**Integrity Score vs Total Events**"
        )

        chart_data = risk_data[
            [
                "integrity_score",
                "total_events"
            ]
        ].copy()

        chart_data = chart_data.rename(
            columns={
                "integrity_score":
                    "Integrity Score",
                "total_events":
                    "Total Events"
            }
        )

        st.scatter_chart(
            chart_data,
            x="Total Events",
            y="Integrity Score"
        )

else:

    st.info(
        "K-Means analysis requires at least "
        "3 examination sessions."
    )


# =========================================================
# 5. MONITORING EVENTS
# =========================================================

st.divider()

st.subheader(
    "Selected Session Events"
)


if events.empty:

    st.success(
        "No monitoring events recorded."
    )

else:

    st.dataframe(
        events,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 6. INCIDENTS
# =========================================================

st.subheader(
    "Selected Session Incidents"
)


if incidents.empty:

    st.success(
        "No incidents recorded."
    )

else:

    st.dataframe(
        incidents,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 7. AI GENERATED REPORT
# =========================================================

st.divider()

st.header(
    "AI-Generated Session Report"
)

st.write(
    "Generate an objective AI-assisted summary "
    "of the selected examination session."
)


if st.button(
    "Generate AI Report",
    type="primary"
):

    with st.spinner(
        "Generating AI report..."
    ):

        try:

            report, report_data = (
                generate_session_ai_report(
                    selected_session
                )
            )

            st.session_state[
                "ai_report"
            ] = report

            st.session_state[
                "ai_report_data"
            ] = report_data

            st.success(
                "AI report generated successfully."
            )

        except Exception as e:

            st.error(
                f"AI report generation failed: {e}"
            )


if "ai_report" in st.session_state:

    st.markdown(
        st.session_state["ai_report"]
    )


# =========================================================
# 8. EXPORT SECTION
# =========================================================

st.divider()

st.header(
    "Export Session Data"
)

st.write(
    "Download session logs, incidents, "
    "risk information and AI-generated reports."
)


export_col1, export_col2, export_col3, export_col4 = (
    st.columns(4)
)


# =========================================================
# SESSION CSV
# =========================================================

with export_col1:

    if st.button(
        "Export Session CSV"
    ):

        filepath = export_csv(
            get_session_summary_data(
                selected_session
            ),
            f"session_{selected_session}_summary.csv"
        )

        with open(
            filepath,
            "rb"
        ) as file:

            st.download_button(
                label="Download Session CSV",
                data=file.read(),
                file_name=(
                    f"session_{selected_session}_summary.csv"
                ),
                mime="text/csv"
            )


# =========================================================
# EVENTS CSV
# =========================================================

with export_col2:

    if st.button(
        "Export Events CSV"
    ):

        event_data = get_event_logs(
            selected_session
        )

        filepath = export_csv(
            event_data,
            f"session_{selected_session}_events.csv"
        )

        with open(
            filepath,
            "rb"
        ) as file:

            st.download_button(
                label="Download Events CSV",
                data=file.read(),
                file_name=(
                    f"session_{selected_session}_events.csv"
                ),
                mime="text/csv"
            )


# =========================================================
# INCIDENTS CSV
# =========================================================

with export_col3:

    if st.button(
        "Export Incidents CSV"
    ):

        incident_data = get_incident_logs(
            selected_session
        )

        filepath = export_csv(
            incident_data,
            f"session_{selected_session}_incidents.csv"
        )

        with open(
            filepath,
            "rb"
        ) as file:

            st.download_button(
                label="Download Incidents CSV",
                data=file.read(),
                file_name=(
                    f"session_{selected_session}_incidents.csv"
                ),
                mime="text/csv"
            )


# =========================================================
# COMPLETE JSON
# =========================================================

with export_col4:

    if st.button(
        "Export Complete JSON"
    ):

        ai_report = st.session_state.get(
            "ai_report",
            None
        )

        filepath = export_complete_session(
            selected_session,
            risk_level=risk_level,
            cluster=cluster,
            ai_report=ai_report
        )

        with open(
            filepath,
            "rb"
        ) as file:

            st.download_button(
                label="Download Complete JSON",
                data=file.read(),
                file_name=(
                    f"session_{selected_session}_complete.json"
                ),
                mime="application/json"
            )


# =========================================================
# ALL EXAMINATION SESSIONS
# =========================================================

st.divider()

st.subheader(
    " All Examination Sessions"
)

st.dataframe(
    sessions,
    use_container_width=True,
    hide_index=True
)