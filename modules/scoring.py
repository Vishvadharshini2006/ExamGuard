import pandas as pd


EVENT_WEIGHTS = {

    "Tab Switched": 10,

    "Window Lost Focus": 5,

    "Right Click": 5,

    "Copy Attempt": 15,

    "Paste Attempt": 15,

    "F12 Pressed": 25,

    "Developer Tools Attempt": 25,

    "View Source Attempt": 25,

    "Face Missing": 20,

    "Multiple Faces Detected": 30,

    "Camera Covered": 25
}




def events_to_dataframe(events):

    """
    Convert database event records into
    a Pandas DataFrame.
    """

    if not events:

        return pd.DataFrame(
            columns=[
                "event",
                "timestamp",
                "details"
            ]
        )

    rows = []

    for event in events:

        # event_log contains:
        # event_type, timestamp, details

        if len(event) >= 3:

            rows.append({

                "event": event[0],

                "timestamp": event[1],

                "details": event[2]

            })

        else:

            rows.append({

                "event": event[0],

                "timestamp": event[1],

                "details": ""

            })

    return pd.DataFrame(rows)




def calculate_event_counts(events):

    """
    Count the frequency of every violation.
    """

    df = events_to_dataframe(events)

    if df.empty:

        return {}

    return df["event"].value_counts().to_dict()



def calculate_weighted_risk_score(events):

    """
    Calculate analytical risk based on
    event frequency and event severity.
    """

    counts = calculate_event_counts(events)

    risk_score = 0

    for event, count in counts.items():

        weight = EVENT_WEIGHTS.get(
            event,
            0
        )

        risk_score += count * weight

    return risk_score


def calculate_face_presence_ratio(
    exam_duration_seconds,
    face_absent_seconds
):

    """
    Calculate the percentage of exam time
    during which the candidate was visible.
    """

    if exam_duration_seconds <= 0:

        return 0.0

    face_present_seconds = (
        exam_duration_seconds -
        face_absent_seconds
    )

    face_present_seconds = max(
        0,
        face_present_seconds
    )

    ratio = (
        face_present_seconds /
        exam_duration_seconds
    )

    return round(
        ratio,
        4
    )



def normalize_risk_score(
    weighted_score,
    maximum_expected_score=100
):

    """
    Convert raw risk score into
    a 0-100 scale.
    """

    if maximum_expected_score <= 0:

        return 0

    normalized = (
        weighted_score /
        maximum_expected_score
    ) * 100

    normalized = min(
        100,
        normalized
    )

    return round(
        normalized,
        2
    )



def classify_risk(normalized_risk):

    """
    Convert numerical risk into
    Low / Medium / High risk.
    """

    if normalized_risk < 30:

        return "Low Risk"

    elif normalized_risk < 60:

        return "Medium Risk"

    else:

        return "High Risk"




def analyze_session(
    events,
    exam_duration_seconds,
    face_absent_seconds
):

    """
    Perform complete analytical risk
    assessment for one exam session.
    """

    dataframe = events_to_dataframe(
        events
    )

    event_counts = calculate_event_counts(
        events
    )

    weighted_score = calculate_weighted_risk_score(
        events
    )

    face_presence_ratio = calculate_face_presence_ratio(
        exam_duration_seconds,
        face_absent_seconds
    )

    normalized_risk = normalize_risk_score(
        weighted_score
    )

    risk_level = classify_risk(
        normalized_risk
    )

    return {

        "dataframe": dataframe,

        "event_counts": event_counts,

        "weighted_risk_score":
            weighted_score,

        "face_presence_ratio":
            face_presence_ratio,

        "normalized_risk":
            normalized_risk,

        "risk_level":
            risk_level
    }