import sqlite3
import os

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from config import DATABASE


# =========================================================
# DATABASE
# =========================================================

DATABASE_NAME = DATABASE


def create_connection():

    return sqlite3.connect(
        DATABASE_NAME
    )


# =========================================================
# EVENT CATEGORIES
# =========================================================

BROWSER_EVENTS = {

    "Tab Switched",
    "Right Click",
    "Copy Attempt",
    "Paste Attempt",
    "F12 Pressed",
    "Developer Tools Attempt",
    "Developer Tools",
    "View Source Attempt"

}


FACE_EVENTS = {

    "Face Missing",
    "Face Detected"

}


CAMERA_EVENTS = {

    "Camera Covered"

}


MULTIPLE_FACE_EVENTS = {

    "Multiple Faces",
    "Multiple Faces Detected"

}


# =========================================================
# INTEGRITY DEDUCTIONS
# ONLY BROWSER EVENTS REDUCE INTEGRITY
# =========================================================

INTEGRITY_DEDUCTIONS = {

    "Tab Switched": 5,

    "Right Click": 2,

    "Copy Attempt": 3,

    "Paste Attempt": 3,

    "F12 Pressed": 5,

    "Developer Tools Attempt": 10,

    "Developer Tools": 10,

    "View Source Attempt": 5

}


# =========================================================
# EVENT CLASSIFICATION
# =========================================================

def classify_event(event):

    if event in BROWSER_EVENTS:

        return "Browser Activity"


    if event in FACE_EVENTS:

        return "Face Monitoring"


    if event in CAMERA_EVENTS:

        return "Camera"


    if event in MULTIPLE_FACE_EVENTS:

        return "Multiple Faces"


    return "Other"


# =========================================================
# EVENT DATAFRAME
# =========================================================

def create_event_dataframe(session_id):

    conn = create_connection()

    query = """

        SELECT

            event_type AS event,

            timestamp,

            details

        FROM event_log

        WHERE session_id=?

        ORDER BY timestamp

    """

    df = pd.read_sql_query(

        query,

        conn,

        params=(session_id,)

    )

    conn.close()


    if df.empty:

        return pd.DataFrame(

            columns=[
                "event",
                "timestamp",
                "details"
            ]

        )


    df["timestamp"] = pd.to_datetime(

        df["timestamp"],

        errors="coerce"

    )


    return df


# =========================================================
# CATEGORIZED EVENT DATAFRAME
# =========================================================

def create_categorized_event_dataframe(
    session_id
):

    df = create_event_dataframe(
        session_id
    )


    if df.empty:

        df["category"] = pd.Series(
            dtype=str
        )

        return df


    df["category"] = df[
        "event"
    ].apply(
        classify_event
    )


    return df


# =========================================================
# EVENT FREQUENCY
# =========================================================

def get_event_frequency(session_id):

    df = create_event_dataframe(
        session_id
    )


    if df.empty:

        return {}


    frequency = (

        df["event"]
        .value_counts()
        .to_dict()

    )


    return frequency


# =========================================================
# EVENT FREQUENCY PLOT
# =========================================================

def plot_event_frequency(
    session_id
):

    frequency = get_event_frequency(
        session_id
    )


    if not frequency:

        return None


    plt.figure(
        figsize=(10, 5)
    )


    plt.bar(

        list(
            frequency.keys()
        ),

        list(
            frequency.values()
        )

    )


    plt.title(
        "Event Frequency"
    )


    plt.xlabel(
        "Event"
    )


    plt.ylabel(
        "Occurrences"
    )


    plt.xticks(

        rotation=45,

        ha="right"

    )


    plt.tight_layout()


    path = save_analytics_plot(

        plt,

        f"event_frequency_{session_id}.png"

    )


    plt.close()


    return path


# =========================================================
# GET INTEGRITY SCORE
# =========================================================

def get_integrity_score(
    session_id
):

    conn = create_connection()

    cursor = conn.cursor()


    cursor.execute(

        """

        SELECT integrity_score

        FROM exam_session

        WHERE session_id=?

        """,

        (session_id,)

    )


    row = cursor.fetchone()


    conn.close()


    if row is None:

        return 100


    return row[0]


# =========================================================
# SESSION ANALYTICS
# =========================================================

def get_session_analytics(
    session_id
):

    conn = create_connection()

    cursor = conn.cursor()


    cursor.execute(

        """

        SELECT

            session_id,

            candidate_id,

            start_time,

            end_time,

            integrity_score,

            status

        FROM exam_session

        WHERE session_id=?

        """,

        (session_id,)

    )


    row = cursor.fetchone()


    conn.close()


    if row is None:

        return None


    df = create_event_dataframe(
        session_id
    )


    total_events = len(df)


    return {

        "session_id":
            row[0],

        "candidate_id":
            row[1],

        "start_time":
            row[2],

        "end_time":
            row[3],

        "integrity_score":
            row[4],

        "status":
            row[5],

        "total_events":
            total_events

    }


# =========================================================
# ALL INTEGRITY SCORES
# =========================================================

def get_all_integrity_scores():

    conn = create_connection()


    query = """

        SELECT

            session_id,

            integrity_score

        FROM exam_session

        ORDER BY session_id

    """


    df = pd.read_sql_query(

        query,

        conn

    )


    conn.close()


    return df


# =========================================================
# INTEGRITY DISTRIBUTION
# =========================================================

def plot_integrity_distribution():

    df = get_all_integrity_scores()


    if df.empty:

        return None


    plt.figure(
        figsize=(9, 5)
    )


    plt.hist(

        df["integrity_score"],

        bins=10

    )


    plt.title(
        "Integrity Score Distribution"
    )


    plt.xlabel(
        "Integrity Score"
    )


    plt.ylabel(
        "Number of Sessions"
    )


    plt.tight_layout()


    path = save_analytics_plot(

        plt,

        "integrity_distribution.png"

    )


    plt.close()


    return path


# =========================================================
# SESSION × EVENT MATRIX
# =========================================================

def get_session_event_matrix():

    conn = create_connection()


    query = """

        SELECT

            session_id,

            event_type

        FROM event_log

        ORDER BY session_id

    """


    df = pd.read_sql_query(

        query,

        conn

    )


    conn.close()


    if df.empty:

        return pd.DataFrame()


    matrix = pd.crosstab(

        df["session_id"],

        df["event_type"]

    )


    return matrix


# =========================================================
# EVENT FREQUENCY HEATMAP
# =========================================================

def plot_event_heatmap():

    matrix = get_session_event_matrix()


    if matrix.empty:

        return None


    plt.figure(

        figsize=(14, 7)

    )


    sns.heatmap(

        matrix,

        annot=True,

        fmt="d",

        cmap="YlOrRd",

        linewidths=0.5,

        cbar=True

    )


    plt.title(

        "Event Frequency Heatmap Across Exam Sessions"

    )


    plt.xlabel(

        "Event Type"

    )


    plt.ylabel(

        "Session ID"

    )


    plt.xticks(

        rotation=45,

        ha="right"

    )


    plt.yticks(

        rotation=0

    )


    plt.tight_layout()


    path = save_analytics_plot(

        plt,

        "event_heatmap.png"

    )


    plt.close()


    return path


# =========================================================
# SAVE ANALYTICS PLOTS
# =========================================================

def save_analytics_plot(
    figure,
    filename
):

    base_dir = os.path.dirname(

        os.path.dirname(

            os.path.abspath(__file__)

        )

    )


    analytics_dir = os.path.join(

        base_dir,

        "static",

        "analytics"

    )


    os.makedirs(

        analytics_dir,

        exist_ok=True

    )


    file_path = os.path.join(

        analytics_dir,

        filename

    )


    figure.savefig(

        file_path,

        dpi=150,

        bbox_inches="tight"

    )


    return file_path


# =========================================================
# FACE PRESENCE RATIO
# =========================================================

def get_face_presence_ratio(
    session_id
):

    conn = create_connection()

    cursor = conn.cursor()


    cursor.execute(

        """

        SELECT

            start_time,

            end_time

        FROM exam_session

        WHERE session_id=?

        """,

        (session_id,)

    )


    session_data = cursor.fetchone()


    conn.close()


    if session_data is None:

        return 0


    start_time = pd.to_datetime(

        session_data[0],

        errors="coerce"

    )


    end_time = pd.to_datetime(

        session_data[1],

        errors="coerce"

    )


    if pd.isna(start_time):

        return 0


    if pd.isna(end_time):

        end_time = pd.Timestamp.now()


    total_duration = (

        end_time - start_time

    ).total_seconds()


    if total_duration <= 0:

        return 0


    df = create_event_dataframe(

        session_id

    )


    if df.empty:

        return 1.0


    missing_events = df[

        df["event"] ==
        "Face Missing"

    ]


    if missing_events.empty:

        return 1.0


    missing_duration = 0


    missing_times = (

        missing_events[
            "timestamp"
        ]
        .dropna()
        .tolist()

    )


    for i, missing_start in enumerate(
        missing_times
    ):

        if i + 1 < len(
            missing_times
        ):

            next_time = missing_times[
                i + 1
            ]

        else:

            next_time = end_time


        duration = (

            pd.Timestamp(next_time)
            -
            pd.Timestamp(missing_start)

        ).total_seconds()


        if duration > 0:

            missing_duration += duration


    presence_duration = max(

        0,

        total_duration -
        missing_duration

    )


    ratio = (

        presence_duration /
        total_duration

    )


    return round(

        min(
            1,
            max(
                0,
                ratio
            )
        ),

        3

    )


def get_face_presence_percentage(
    session_id
):

    return round(

        get_face_presence_ratio(
            session_id
        ) * 100,

        2

    )


# =========================================================
# SESSION FEATURE DATAFRAME
# =========================================================

def create_session_feature_dataframe():

    conn = create_connection()


    sessions = pd.read_sql_query(

        """

        SELECT

            session_id,

            integrity_score

        FROM exam_session

        """,

        conn

    )


    events = pd.read_sql_query(

        """

        SELECT

            session_id,

            event_type

        FROM event_log

        """,

        conn

    )


    conn.close()


    if sessions.empty:

        return pd.DataFrame()


    result = sessions.copy()


    # -----------------------------------------------------
    # GENERAL
    # -----------------------------------------------------

    result["total_events"] = 0


    result["browser_activity"] = 0


    # -----------------------------------------------------
    # BROWSER
    # -----------------------------------------------------

    result["tab_switches"] = 0

    result["copy_attempts"] = 0

    result["paste_attempts"] = 0

    result["right_clicks"] = 0

    result["f12_presses"] = 0

    result["developer_tools"] = 0

    result["view_source"] = 0


    # -----------------------------------------------------
    # FACE / CAMERA
    # -----------------------------------------------------

    result["face_missing"] = 0

    result["face_detected"] = 0

    result["camera_covered"] = 0

    result["multiple_faces"] = 0


    if not events.empty:

        for session_id in result[
            "session_id"
        ]:

            session_events = events[

                events["session_id"]
                ==
                session_id

            ]["event_type"]


            # TOTAL

            result.loc[

                result["session_id"]
                ==
                session_id,

                "total_events"

            ] = len(
                session_events
            )


            # BROWSER

            result.loc[

                result["session_id"]
                ==
                session_id,

                "browser_activity"

            ] = session_events.isin(

                BROWSER_EVENTS

            ).sum()


            # TAB SWITCH

            result.loc[

                result["session_id"]
                ==
                session_id,

                "tab_switches"

            ] = (

                session_events ==
                "Tab Switched"

            ).sum()


            # COPY

            result.loc[

                result["session_id"]
                ==
                session_id,

                "copy_attempts"

            ] = (

                session_events ==
                "Copy Attempt"

            ).sum()


            # PASTE

            result.loc[

                result["session_id"]
                ==
                session_id,

                "paste_attempts"

            ] = (

                session_events ==
                "Paste Attempt"

            ).sum()


            # RIGHT CLICK

            result.loc[

                result["session_id"]
                ==
                session_id,

                "right_clicks"

            ] = (

                session_events ==
                "Right Click"

            ).sum()


            # F12

            result.loc[

                result["session_id"]
                ==
                session_id,

                "f12_presses"

            ] = (

                session_events ==
                "F12 Pressed"

            ).sum()


            # DEVELOPER TOOLS

            result.loc[

                result["session_id"]
                ==
                session_id,

                "developer_tools"

            ] = session_events.isin(

                [

                    "Developer Tools",

                    "Developer Tools Attempt"

                ]

            ).sum()


            # VIEW SOURCE

            result.loc[

                result["session_id"]
                ==
                session_id,

                "view_source"

            ] = (

                session_events ==
                "View Source Attempt"

            ).sum()


            # FACE MISSING

            result.loc[

                result["session_id"]
                ==
                session_id,

                "face_missing"

            ] = (

                session_events ==
                "Face Missing"

            ).sum()


            # FACE DETECTED

            result.loc[

                result["session_id"]
                ==
                session_id,

                "face_detected"

            ] = (

                session_events ==
                "Face Detected"

            ).sum()


            # CAMERA

            result.loc[

                result["session_id"]
                ==
                session_id,

                "camera_covered"

            ] = (

                session_events ==
                "Camera Covered"

            ).sum()


            # MULTIPLE FACES

            result.loc[

                result["session_id"]
                ==
                session_id,

                "multiple_faces"

            ] = session_events.isin(

                MULTIPLE_FACE_EVENTS

            ).sum()


    # -----------------------------------------------------
    # FACE PRESENCE RATIO
    # -----------------------------------------------------

    result["face_presence_ratio"] = (

        result["session_id"].apply(

            get_face_presence_ratio

        )

    )


    return result


# =========================================================
# K-MEANS
# =========================================================

def perform_kmeans_clustering(
    n_clusters=3
):

    df = create_session_feature_dataframe()


    if df.empty:

        return df


    if len(df) < n_clusters:

        return df


    features = [

        "integrity_score",

        "total_events",

        "browser_activity",

        "tab_switches",

        "copy_attempts",

        "paste_attempts",

        "right_clicks",

        "f12_presses",

        "developer_tools",

        "view_source",

        "face_missing",

        "face_detected",

        "face_presence_ratio",

        "camera_covered",

        "multiple_faces"

    ]


    X = df[
        features
    ].fillna(0)


    scaler = StandardScaler()


    X_scaled = scaler.fit_transform(
        X
    )


    model = KMeans(

        n_clusters=n_clusters,

        random_state=42,

        n_init=10

    )


    df["cluster"] = (

        model.fit_predict(
            X_scaled
        )

    )


    return df


# =========================================================
# RISK CLASSIFICATION
# =========================================================

def classify_risk_clusters(df):

    if df is None or df.empty:

        return df


    cluster_scores = (

        df.groupby("cluster")
        ["integrity_score"]
        .mean()
        .sort_values()

    )


    risk_labels = [

        "High Risk",

        "Medium Risk",

        "Low Risk"

    ]


    cluster_to_risk = {}


    for cluster, risk in zip(

        cluster_scores.index,

        risk_labels

    ):

        cluster_to_risk[
            cluster
        ] = risk


    df["risk_level"] = df[
        "cluster"
    ].map(
        cluster_to_risk
    )


    return df


# =========================================================
# COMPLETE RISK ANALYSIS
# =========================================================

def analyze_session_risk():

    df = perform_kmeans_clustering(
        n_clusters=3
    )


    if df is None or df.empty:

        return df


    if "cluster" not in df.columns:

        return df


    df = classify_risk_clusters(
        df
    )


    return df


# =========================================================
# COHORT RISK PROFILE
# =========================================================

def get_risk_profile(df):

    if df is None or df.empty:

        return pd.DataFrame()


    if "risk_level" not in df.columns:

        return pd.DataFrame()


    profile = (

        df.groupby(
            "risk_level"
        )

        .agg(

            sessions=(

                "session_id",

                "count"

            ),

            average_score=(

                "integrity_score",

                "mean"

            ),

            average_events=(

                "total_events",

                "mean"

            )

        )

        .reset_index()

    )


    return profile


# =========================================================
# K-MEANS PLOT
# =========================================================

def plot_kmeans_clusters(df):

    if df is None or df.empty:

        return None


    if "risk_level" not in df.columns:

        return None


    plt.figure(


        figsize=(10, 6)

    )


    for risk in [

        "Low Risk",

        "Medium Risk",

        "High Risk"

    ]:

        subset = df[

            df["risk_level"] ==
            risk

        ]


        if subset.empty:

            continue


        plt.scatter(

            subset["total_events"],

            subset["integrity_score"],

            label=risk,

            s=80

        )


    plt.title(

        "K-Means Session Risk Clustering"

    )


    plt.xlabel(

        "Total Events"

    )


    plt.ylabel(

        "Integrity Score"

    )


    plt.legend()


    plt.grid(
        alpha=0.3
    )


    plt.tight_layout()


    # path = save_analytics_plot(

    #     plt,

    #     "kmeans_clusters.png"

    # )
    plt.show()


    plt.close()


    #return path






# =========================================================
# RISK PROFILE PLOT
# =========================================================

def plot_risk_profile(df):

    if df is None or df.empty:

        return None


    profile = get_risk_profile(
        df
    )


    if profile.empty:

        return None


    plt.figure(

        figsize=(9, 5)

    )


    plt.bar(

        profile["risk_level"],

        profile["sessions"]

    )


    plt.title(

        "Cohort Risk Profile"

    )


    plt.xlabel(

        "Risk Level"

    )


    plt.ylabel(

        "Number of Sessions"

    )


    plt.tight_layout()


    path = save_analytics_plot(

        plt,

        "risk_profile.png"

    )


    plt.close()


    return path


# =========================================================
# CATEGORY FREQUENCY
# =========================================================

def get_category_frequency(
    session_id
):

    df = create_categorized_event_dataframe(

        session_id

    )


    categories = [

        "Face Monitoring",

        "Camera",

        "Multiple Faces",

        "Browser Activity"

    ]


    if df.empty:

        return {

            category: 0

            for category in categories

        }


    counts = (

        df["category"]
        .value_counts()
        .to_dict()

    )


    return {

        category:

            counts.get(
                category,
                0
            )

        for category in categories

    }


# =========================================================
# VIOLATION CATEGORIES
# =========================================================

def get_violation_categories(
    session_id
):

    return get_category_frequency(
        session_id
    )


# =========================================================
# INTEGRITY TIMELINE
# =========================================================

def get_integrity_timeline(
    session_id
):

    df = create_event_dataframe(
        session_id
    )


    if df.empty:

        return []


    score = 100


    timeline = []


    for _, row in df.iterrows():

        event = row["event"]


        deduction = (

            INTEGRITY_DEDUCTIONS.get(

                event,

                0

            )

        )


        affects_score = (

            deduction > 0

        )


        if affects_score:

            score = max(

                0,

                score - deduction

            )


        timeline.append(

            {

                "event":
                    event,

                "timestamp":
                    str(
                        row["timestamp"]
                    ),

                "score":
                    score,

                "deduction":
                    deduction,

                "affects_score":
                    affects_score

            }

        )


    return timeline


# =========================================================
# SYNTHETIC CORPUS VALIDATION
# =========================================================

def validate_synthetic_corpus():

    synthetic_data = [

        {

            "session_id": 1,

            "integrity_score": 95,

            "total_events": 1,

            "face_presence_ratio": 0.99

        },

        {

            "session_id": 2,

            "integrity_score": 90,

            "total_events": 2,

            "face_presence_ratio": 0.97

        },

        {

            "session_id": 3,

            "integrity_score": 85,

            "total_events": 3,

            "face_presence_ratio": 0.95

        },

        {

            "session_id": 4,

            "integrity_score": 75,

            "total_events": 5,

            "face_presence_ratio": 0.90

        },

        {

            "session_id": 5,

            "integrity_score": 70,

            "total_events": 6,

            "face_presence_ratio": 0.85

        },

        {

            "session_id": 6,

            "integrity_score": 60,

            "total_events": 8,

            "face_presence_ratio": 0.75

        },

        {

            "session_id": 7,

            "integrity_score": 45,

            "total_events": 10,

            "face_presence_ratio": 0.60

        },

        {

            "session_id": 8,

            "integrity_score": 35,

            "total_events": 12,

            "face_presence_ratio": 0.50

        },

        {

            "session_id": 9,

            "integrity_score": 20,

            "total_events": 15,

            "face_presence_ratio": 0.35

        }

    ]


    df = pd.DataFrame(
        synthetic_data
    )


    X = df[

        [

            "integrity_score",

            "total_events",

            "face_presence_ratio"

        ]

    ]


    scaler = StandardScaler()


    X_scaled = scaler.fit_transform(
        X
    )


    model = KMeans(

        n_clusters=3,

        random_state=42,

        n_init=10

    )


    df["cluster"] = (

        model.fit_predict(
            X_scaled
        )

    )


    df = classify_risk_clusters(
        df
    )


    return df

if __name__ == "__main__":
    df = analyze_session_risk()

    print("\n===== K-MEANS RISK CLUSTERING =====\n")
    print(df[[
        "session_id",
        "integrity_score",
        "total_events",
        "cluster",
        "risk_level"
    ]])

    plot_kmeans_clusters(df)
