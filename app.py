import cv2

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    Response
)

import os

from datetime import datetime, timedelta

from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from config import SECRET_KEY


# ===================================================
# ANALYTICS
# ===================================================

from modules.analytics import (
    get_session_analytics,
    get_event_frequency,
    analyze_session_risk,
    get_risk_profile
)


# ===================================================
# FACE MONITOR
# ===================================================

from modules.face_monitor import (
    generate_frames,
    stop_camera,
    set_session
)



from modules.ai_report import generate_session_ai_report



# ===================================================
# DATABASE
# ===================================================

from database import (
    add_candidate,
    create_connection,
    get_candidate_by_email,
    start_exam_session,
    pause_exam_session,
    resume_exam_session,
    end_exam_session,
    update_candidate_photo,
    update_govt_id,
    get_integrity_score,
    update_integrity_score,
    get_question,
    get_saved_response,
    log_event,
    get_all_events,
    get_all_questions,
    save_response,
    get_attempted_count,
    get_total_questions,
    get_session_report,

    # Incident management
    create_incident,
    get_incidents,
    get_incident,
    update_incident_status,
    update_incident_evidence
)


# ===================================================
# SESSION
# ===================================================

from modules.session import get_latest_session


# ===================================================
# INCIDENT MANAGEMENT
# ===================================================

from modules.incident_manager import (
    register_incident,
    get_incident_summary
)


# ===================================================
# FLASK APP
# ===================================================

app = Flask(__name__)

app.secret_key = SECRET_KEY


# ===================================================
# GLOBAL WARNING
# ===================================================

current_warning = "✓ No Violations"


# ===================================================
# HOME
# ===================================================

@app.route("/")
def home():

    return redirect(
        url_for("login")
    )


# ===================================================
# REGISTER
# ===================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]

        email = request.form["email"]

        password = request.form["password"]

        # -------------------------------------------
        # CHECK EXISTING USER
        # -------------------------------------------

        if get_candidate_by_email(email):

            flash(
                "Email already exists",
                "error"
            )

            return redirect(
                url_for("register")
            )

        # -------------------------------------------
        # ADD CANDIDATE
        # -------------------------------------------

        add_candidate(
            full_name,
            email,
            password
        )

        flash(
            "Registration Successful",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )



@app.route("/evidence/<int:incident_id>")
def view_evidence(incident_id):

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "candidate_id" not in session:

        return jsonify({
            "error": "Unauthorized"
        }), 401

    # -----------------------------------------------------
    # GET INCIDENT
    # -----------------------------------------------------

    incident = get_incident(
        incident_id
    )

    if incident is None:

        return "Evidence not found", 404

    # -----------------------------------------------------
    # SECURITY CHECK
    # -----------------------------------------------------

    # Make sure this incident belongs to
    # the logged-in candidate

    if incident["candidate_id"] != session["candidate_id"]:

        return "Access denied", 403

    # -----------------------------------------------------
    # CHECK EVIDENCE
    # -----------------------------------------------------

    evidence_path = incident.get(
        "evidence_path"
    )

    if not evidence_path:

        return "No evidence available", 404

    # -----------------------------------------------------
    # SECURE PATH VALIDATION
    # -----------------------------------------------------

    evidence_root = os.path.abspath(
        os.path.join(
            app.root_path,
            "static",
            "evidence"
        )
    )

    requested_file = os.path.abspath(
        os.path.join(
            evidence_root,
            evidence_path.replace(
                "evidence/",
                "",
                1
            )
        )
    )

    # Prevent path traversal
    if not requested_file.startswith(
        evidence_root + os.sep
    ):

        return "Invalid evidence path", 403

    # -----------------------------------------------------
    # FILE EXISTS?
    # -----------------------------------------------------

    if not os.path.isfile(requested_file):

        return "Evidence file not found", 404

    # -----------------------------------------------------
    # SEND FILE
    # -----------------------------------------------------

    from flask import send_file

    return send_file(
        requested_file,
        mimetype="image/jpeg"
    )





# ===================================================
# LOGIN
# ===================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = get_candidate_by_email(email)

        # -------------------------------------------
        # INVALID EMAIL
        # -------------------------------------------

        if user is None:

            flash(
                "Invalid Email",
                "error"
            )

            return redirect(
                url_for("login")
            )

        # -------------------------------------------
        # INVALID PASSWORD
        # -------------------------------------------

        if not check_password_hash(
            user[3],
            password
        ):

            flash(
                "Invalid Password",
                "error"
            )

            return redirect(
                url_for("login")
            )

        # -------------------------------------------
        # SAVE USER SESSION
        # -------------------------------------------

        session["candidate_id"] = user[0]

        session["candidate_name"] = user[1]

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html"
    )


# ===================================================
# DASHBOARD
# ===================================================

@app.route("/dashboard")
def dashboard():

    if "candidate_id" not in session:

        return redirect(
            url_for("login")
        )

    candidate_id = session.get(
        "candidate_id"
    )

    latest_session_id = get_latest_session(
        candidate_id
    )

    return render_template(

        "dashboard.html",

        candidate=session.get(
            "candidate_name"
        ),

        latest_session_id=latest_session_id

    )


# ===================================================
# ANALYTICS
# ===================================================

@app.route("/analytics/<int:session_id>")
def analytics(session_id):

    if "candidate_id" not in session:

        return redirect(
            url_for("login")
        )

    from modules.analytics import (
        get_session_analytics,
        get_event_frequency,
        get_category_frequency,
        get_integrity_timeline,
        get_violation_categories,
        analyze_session_risk,
        get_risk_profile,
        plot_event_heatmap
    )

    # ---------------------------------------------------------
    # CURRENT SESSION ANALYTICS
    # ---------------------------------------------------------

    session_data = get_session_analytics(
        session_id
    )

    if session_data is None:

        flash(
            "Session not found.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # ---------------------------------------------------------
    # EVENT DATA
    # ---------------------------------------------------------

    event_frequency = get_event_frequency(
        session_id
    )

    category_frequency = get_category_frequency(
        session_id
    )

    violation_categories = get_violation_categories(
        session_id
    )

    integrity_timeline = get_integrity_timeline(
        session_id
    )

    # ---------------------------------------------------------
    # K-MEANS RISK ANALYSIS
    # ---------------------------------------------------------

    all_sessions = analyze_session_risk()

    risk_profile = []

    current_risk = None

    sessions_data = []

    if (
        all_sessions is not None
        and not all_sessions.empty
    ):

        profile = get_risk_profile(
            all_sessions
        )

        if (
            profile is not None
            and not profile.empty
        ):

            risk_profile = profile.to_dict(
                orient="records"
            )

        # -----------------------------------------------------
        # CURRENT SESSION RISK
        # -----------------------------------------------------

        current_session = all_sessions[
            all_sessions["session_id"] ==
            session_id
        ]

        if not current_session.empty:

            current_risk = (
                current_session
                .iloc[0]
                .to_dict()
            )

        # -----------------------------------------------------
        # ALL SESSION DATA
        # -----------------------------------------------------

        sessions_data = (
            all_sessions
            .to_dict(
                orient="records"
            )
        )

    # ---------------------------------------------------------
    # GENERATE EVENT HEATMAP
    # ---------------------------------------------------------

    heatmap_path = plot_event_heatmap()

    heatmap_available = (
        heatmap_path is not None
    )

    # ---------------------------------------------------------
    # RENDER ANALYTICS
    # ---------------------------------------------------------

    return render_template(

        "analytics.html",
            session_id=session_id,

        session_data=session_data,

        event_frequency=event_frequency,

        category_frequency=category_frequency,

        violation_categories=violation_categories,

        integrity_timeline=integrity_timeline,

        current_risk=current_risk,

        risk_profile=risk_profile,

        sessions=sessions_data,

        heatmap_available=heatmap_available

    )


# ===================================================
# INCIDENT MANAGEMENT
# ===================================================

@app.route("/incidents/<int:session_id>")
def incidents(session_id):

    # --------------------------------------------------
    # LOGIN CHECK
    # --------------------------------------------------

    if "candidate_id" not in session:

        return redirect(
            url_for("login")
        )

    # --------------------------------------------------
    # GET INCIDENTS
    # --------------------------------------------------

    incidents_data = get_incidents(
        session_id
    )


    print("===================================") 
    print("INCIDENT PAGE SESSION:", session_id) 
    print("INCIDENTS FETCHED:", incidents_data) 
    print("NUMBER OF INCIDENTS:", len(incidents_data)) 
    print("===================================")
    # --------------------------------------------------
    # CREATE SUMMARY
    # --------------------------------------------------

    summary = get_incident_summary(
        incidents_data
    )

    # --------------------------------------------------
    # RENDER
    # --------------------------------------------------

    return render_template(

        "incidents.html",

        incidents=incidents_data,

        summary=summary,

        session_id=session_id

    )


# ===================================================
# UPDATE INCIDENT STATUS
# ===================================================

@app.route(
    "/incident/<int:incident_id>/status",
    methods=["POST"]
)
def update_incident(incident_id):

    # --------------------------------------------------
    # LOGIN CHECK
    # --------------------------------------------------

    if "candidate_id" not in session:

        return redirect(
            url_for("login")
        )

    # --------------------------------------------------
    # GET STATUS
    # --------------------------------------------------

    status = request.form.get(
        "status"
    )

    allowed_statuses = {

        "Pending",

        "Reviewed",

        "Dismissed"

    }

    # --------------------------------------------------
    # VALIDATE STATUS
    # --------------------------------------------------

    if status not in allowed_statuses:

        flash(
            "Invalid incident status.",
            "error"
        )

        return redirect(
            request.referrer
            or url_for("dashboard")
        )

    # --------------------------------------------------
    # GET INCIDENT
    # --------------------------------------------------

    incident = get_incident(
        incident_id
    )

    if incident is None:

        flash(
            "Incident not found.",
            "error"
        )

        return redirect(
            request.referrer
            or url_for("dashboard")
        )

    # --------------------------------------------------
    # UPDATE STATUS
    # --------------------------------------------------

    update_incident_status(

        incident_id,

        status

    )

    flash(
        "Incident status updated.",
        "success"
    )

    # --------------------------------------------------
    # RETURN TO INCIDENT PAGE
    # --------------------------------------------------

    return redirect(

        url_for(
            "incidents",
            session_id=incident["session_id"]
        )

    )



@app.route("/ai_report/<int:session_id>")
def ai_report(session_id):

    if "candidate_id" not in session:
        return redirect(url_for("login"))

    try:

        print("\n" + "=" * 70)
        print("AI REPORT REQUEST")
        print("Requested Session ID:", session_id)
        print("Logged-in Candidate ID:", session.get("candidate_id"))
        print("=" * 70)

        # -------------------------------------------------
        # GENERATE REPORT
        # -------------------------------------------------

        report, session_data = generate_session_ai_report(
            session_id
        )

        print("SESSION DATA:")
        print(session_data)

        print("\nREPORT RECEIVED:")
        print(report)

        # -------------------------------------------------
        # SESSION CHECK
        # -------------------------------------------------

        if session_data is None:

            print("ERROR: SESSION DATA IS NONE")

            return "Examination session not found", 404

        # -------------------------------------------------
        # GET CANDIDATE ID
        # -------------------------------------------------

        logged_in_candidate = int(
            session["candidate_id"]
        )

        session_information = session_data.get(
            "session_information",
            {}
        )

        session_candidate = session_information.get(
            "candidate_id"
        )

        print("\nCANDIDATE CHECK")
        print(
            "Logged-in candidate:",
            logged_in_candidate
        )
        print(
            "Session candidate:",
            session_candidate
        )

        # -------------------------------------------------
        # SECURITY CHECK
        # -------------------------------------------------

        if session_candidate is None:

            print(
                "ERROR: SESSION CANDIDATE ID IS NONE"
            )

            return "Unable to verify session ownership", 403

        session_candidate = int(
            session_candidate
        )

        if logged_in_candidate != session_candidate:

            print("ERROR: CANDIDATE IDs DO NOT MATCH")

            return "Access denied", 403

        # -------------------------------------------------
        # REPORT CHECK
        # -------------------------------------------------

        if report is None:

            print(
                "ERROR: generate_session_ai_report "
                "returned report=None"
            )

            return render_template(
                "ai_report.html",
                session_data=session_data,
                report=None,
                error="AI report generation failed."
            )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        print("\nAI REPORT SUCCESS")
        print("=" * 70)

        return render_template(
            "ai_report.html",
            session_data=session_data,
            report=report,
            error=None
        )

    except Exception as e:

        import traceback

        print("\n" + "=" * 70)
        print("AI REPORT ROUTE ERROR")
        print("=" * 70)

        print("ERROR:", str(e))

        print("\nFULL TRACEBACK:")
        traceback.print_exc()

        print("=" * 70)

        return render_template(
            "ai_report.html",
            session_data=None,
            report=None,
            error="Unable to generate the AI integrity report."
        ), 500



# ===================================================
# START EXAM
# ===================================================

@app.route("/start_exam")
def start_exam():

    if "candidate_id" not in session:

        return redirect(
            url_for("login")
        )

    # --------------------------------------------------
    # CREATE EXAM SESSION
    # --------------------------------------------------

    session_id = start_exam_session(

        session["candidate_id"],

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    )

    # --------------------------------------------------
    # SAVE ACTIVE SESSION
    # --------------------------------------------------

    session["session_id"] = session_id

    # --------------------------------------------------
    # CONNECT FACE MONITOR
    # --------------------------------------------------

    set_session(
        session_id
    )

    # --------------------------------------------------
    # EXAM END TIME
    # --------------------------------------------------

    session["exam_end"] = (

        datetime.now()
        + timedelta(minutes=5)

    ).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return redirect(
        url_for("camera_verify")
    )


# ===================================================
# CAMERA VERIFY
# ===================================================

@app.route("/camera_verify")
def camera_verify():

    if "candidate_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "camera_verify.html"
    )


# ===================================================
# CAPTURE PHOTO
# ===================================================

@app.route("/capture_photo")
def capture_photo():

    if "candidate_id" not in session:

        return redirect(
            url_for("login")
        )

    camera = cv2.VideoCapture(0)

    success, frame = camera.read()

    if success:

        folder = os.path.join(
            "static",
            "photos"
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        filename = (
            f"{session['candidate_id']}.jpg"
        )

        save_path = os.path.join(
            folder,
            filename
        )

        cv2.imwrite(
            save_path,
            frame
        )

        update_candidate_photo(

            session["candidate_id"],

            save_path

        )

        print(
            "IMAGE SAVED:",
            save_path
        )

    else:

        print(
            "CAMERA ERROR"
        )

    camera.release()

    return jsonify({
        "status": "success"
    })


# ===================================================
# GOVERNMENT ID
# ===================================================

@app.route(
    "/govt_id",
    methods=["GET", "POST"]
)
def govt_id():

    if "candidate_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        file = request.files["govt_id"]

        if (
            file
            and file.filename != ""
        ):

            filename = secure_filename(
                file.filename
            )

            folder = os.path.join(
                "static",
                "govt_id"
            )

            os.makedirs(
                folder,
                exist_ok=True
            )

            save_path = os.path.join(
                folder,
                filename
            )

            file.save(
                save_path
            )

            update_govt_id(

                session["candidate_id"],

                save_path

            )

            session["govt_id"] = save_path

            return redirect(
                url_for("microphone")
            )

    return render_template(
        "govt_id.html"
    )


# ===================================================
# MICROPHONE
# ===================================================

@app.route("/microphone")
def microphone():

    if "candidate_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "microphone.html"
    )


# ===================================================
# EXAM
# ===================================================

@app.route("/exam")
def exam():

    if "candidate_id" not in session:

        return redirect(
            url_for("login")
        )

    # --------------------------------------------------
    # QUESTION NUMBER
    # --------------------------------------------------

    question_no = request.args.get(
        "q",
        1,
        type=int
    )

    total = get_total_questions()

    if question_no < 1:

        question_no = 1

    if question_no > total:

        question_no = total

    # --------------------------------------------------
    # GET QUESTION
    # --------------------------------------------------

    question = get_question(
        question_no
    )

    # --------------------------------------------------
    # GET ACTIVE SESSION
    # --------------------------------------------------

    session_id = session.get(
        "session_id"
    )

    if session_id is None:

        flash(
            "Exam session expired.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # --------------------------------------------------
    # GET SAVED ANSWER
    # --------------------------------------------------

    selected = get_saved_response(

        session_id,

        question[0]

    )

    # --------------------------------------------------
    # GET ATTEMPTED QUESTIONS
    # --------------------------------------------------

    attempted = get_attempted_count(
        session_id
    )

    # --------------------------------------------------
    # RENDER EXAM
    # --------------------------------------------------

    return render_template(

        "exam.html",

        question=question,

        question_no=question_no,

        total_questions=total,

        selected=selected,

        attempted=attempted,

        exam_end=session["exam_end"]

    )


# ===================================================
# SAVE ANSWER
# ===================================================

@app.route(
    "/save_answer",
    methods=["POST"]
)
def save_answer():

    session_id = session.get(
        "session_id"
    )

    if session_id is None:

        return redirect(
            url_for("dashboard")
        )

    question_id = request.form[
        "question_id"
    ]

    answer = request.form.get(
        "answer"
    )

    action = request.form[
        "action"
    ]

    # --------------------------------------------------
    # SAVE RESPONSE
    # --------------------------------------------------

    save_response(

        session_id,

        question_id,

        answer

    )

    current = int(
        request.form["question_no"]
    )

    # --------------------------------------------------
    # NEXT
    # --------------------------------------------------

    if action == "next":

        return redirect(

            url_for(
                "exam",
                q=current + 1
            )

        )

    # --------------------------------------------------
    # PREVIOUS
    # --------------------------------------------------

    elif action == "previous":

        return redirect(

            url_for(
                "exam",
                q=current - 1
            )

        )

    # --------------------------------------------------
    # SUBMIT
    # --------------------------------------------------

    else:

        return redirect(
            url_for("submit_exam")
        )


# ===================================================
# LOG BROWSER EVENT
# ===================================================

@app.route(
    "/log_browser_event",
    methods=["POST"]
)
def log_browser_event():

    print(
        "==================================="
    )

    print(
        "BROWSER EVENT ROUTE CALLED"
    )

    print(
        "==================================="
    )

    # ===================================================
    # CHECK LOGIN
    # ===================================================

    if "candidate_id" not in session:

        return jsonify(

            success=False,

            message="Candidate not logged in"

        ), 401

    # ===================================================
    # GET EVENT DATA
    # ===================================================

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify(

            success=False,

            message="Invalid request"

        ), 400

    event = data.get(
        "event"
    )

    if not event:

        return jsonify(

            success=False,

            message="Event missing"

        ), 400

    # ===================================================
    # GET SESSION ID
    # ===================================================

    session_id = session.get(
        "session_id"
    )

    if not session_id:

        return jsonify(

            success=False,

            message="No active exam session"

        ), 400

    # ===================================================
    # BROWSER VIOLATION DEDUCTIONS
    # ===================================================

    deductions = {

        "Tab Switched": 5,

        "Right Click": 2,

        "Copy Attempt": 3,

        "Paste Attempt": 3,

        "F12 Pressed": 5,

        "Developer Tools Attempt": 10,

        "Developer Tools": 10,

        "View Source Attempt": 5

    }

    deduction = deductions.get(
        event,
        0
    )

    # ===================================================
    # GET CURRENT SCORE
    # ===================================================

    current_score = get_integrity_score(
        session_id
    )

    if current_score is None:

        current_score = 100

    print(
        "Current score:",
        current_score
    )

    # ===================================================
    # CALCULATE NEW SCORE
    # ===================================================

    if deduction > 0:

        new_score = max(

            0,

            current_score - deduction

        )

        print(
            "Browser violation:",
            event
        )

        print(
            "Score:",
            current_score,
            "->",
            new_score
        )

        update_integrity_score(

            session_id,

            new_score

        )

    else:

        new_score = current_score

    # ===================================================
    # TIMESTAMP
    # ===================================================

    event_timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # ===================================================
    # LOG EVENT
    # ===================================================

    log_event(

        session_id,

        event,

        event_timestamp,

        "Browser monitoring event"

    )

    # ===================================================
    # CREATE INCIDENT
    # ===================================================

    incident_id = register_incident(

        session_id=session_id,

        candidate_id=session["candidate_id"],

        event_type=event,

        details="Browser monitoring event",

        timestamp=event_timestamp

    )

    print(
        "Incident created:",
        incident_id
    )

    # ===================================================
    # WARNING
    # ===================================================

    global current_warning

    current_warning = (
        "⚠ " + event
    )

    # ===================================================
    # RESPONSE
    # ===================================================

    return jsonify(

        success=True,

        event=event,

        warning=current_warning,

        integrity_score=new_score,

        incident_id=incident_id,

        terminated=False

    )


# ===================================================
# GET SCORE
# ===================================================

@app.route("/get_score")
def get_score():

    if "session_id" not in session:

        return jsonify({
            "score": 100
        })

    score = get_integrity_score(

        session.get(
            "session_id"
        )

    )

    return jsonify({
        "score": score
    })


# ===================================================
# VIDEO FEED
# ===================================================

@app.route("/video_feed")
def video_feed():

    if "candidate_id" not in session:
        return "Unauthorized", 401

    if "session_id" not in session:
        return "No active exam session", 400

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )



# ===================================================
# PAUSE EXAM
# ===================================================

@app.route("/pause_exam")
def pause_exam():

    if "session_id" not in session:

        return redirect(
            url_for("dashboard")
        )

    pause_exam_session(

        session.get(
            "session_id"
        )

    )

    return redirect(
        url_for("dashboard")
    )


# ===================================================
# RESUME EXAM
# ===================================================

@app.route("/resume_exam")
def resume_exam():

    if "session_id" not in session:

        return redirect(
            url_for("dashboard")
        )

    resume_exam_session(

        session.get(
            "session_id"
        )

    )

    return redirect(
        url_for("dashboard")
    )


# ===================================================
# SUBMIT EXAM
# ===================================================

@app.route("/submit_exam")
def submit_exam():

    session_id = session.get(
        "session_id"
    )

    if session_id is None:

        flash(
            "Exam session expired.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # --------------------------------------------------
    # STOP CAMERA
    # --------------------------------------------------

    stop_camera()

    set_session(None)

    # --------------------------------------------------
    # END EXAM SESSION
    # --------------------------------------------------

    end_exam_session(

        session_id,

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    )

    # --------------------------------------------------
    # GET REPORT
    # --------------------------------------------------

    report = get_session_report(
        session_id
    )

    events = get_all_events(
        session_id
    )

    score = get_integrity_score(
        session_id
    )

    attempted = get_attempted_count(
        session_id
    )

    total = get_total_questions()

    candidate = session.get(
        "candidate_name"
    )

    # --------------------------------------------------
    # DEBUG
    # --------------------------------------------------

    print(
        "Report:",
        report
    )

    print(
        "Events:",
        events
    )

    print(
        "Integrity Score:",
        score
    )

    # --------------------------------------------------
    # RENDER REPORT
    # --------------------------------------------------

    return render_template(

        "exam_report.html",

        candidate=candidate,

        report=report,

        score=score,

        exam_status="Completed",

        attempted=attempted,

        total=total,

        events=events

    )


# ===================================================
# FACE EVENT LOGGING
# ===================================================

@app.route(
    "/log_face_event",
    methods=["POST"]
)
def log_face_event():

    if "candidate_id" not in session:

        return jsonify({
            "status": "not logged in"
        }), 401

    data = request.get_json(
        silent=True
    )

    if not data or "event" not in data:

        return jsonify({
            "status": "invalid event"
        }), 400

    event = data["event"]

    session_id = session.get(
        "session_id"
    )

    if session_id is None:

        return jsonify({
            "status": "no session"
        }), 400

    # ==================================================
    # CAMERA EVENTS DO NOT REDUCE SCORE
    # ==================================================

    global current_warning

    current_warning = (
        "⚠ " + event
    )

    # --------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------

    event_timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # --------------------------------------------------
    # LOG EVENT
    # --------------------------------------------------

    log_event(

        session_id,

        event,

        event_timestamp,

        "Camera monitoring event"

    )

    # --------------------------------------------------
    # INCIDENT
    # --------------------------------------------------

    incident_event = event

    if event == "Multiple Faces Detected":

        incident_event = "Multiple Faces"

    incident_id = register_incident(

        session_id=session_id,

        candidate_id=session["candidate_id"],

        event_type=incident_event,

        details="Camera monitoring event",

        timestamp=event_timestamp

    )

    # --------------------------------------------------
    # GET SCORE WITHOUT CHANGING IT
    # --------------------------------------------------

    score = get_integrity_score(
        session_id
    )

    if score is None:

        score = 100

    return jsonify({

        "status": "success",

        "score": score,

        "warning": current_warning,

        "incident_id": incident_id

    })


# ===================================================
# FACE EVENT
# ===================================================

@app.route(
    "/face_event",
    methods=["POST"]
)
def face_event():

    if "session_id" not in session:

        return jsonify({
            "status": "no session"
        }), 400

    data = request.get_json(
        silent=True
    )

    if not data or "event" not in data:

        return jsonify({
            "status": "invalid event"
        }), 400

    event = data["event"]

    session_id = session.get(
        "session_id"
    )

    # ==================================================
    # CAMERA EVENTS DO NOT REDUCE SCORE
    # ==================================================

    global current_warning

    current_warning = (
        "⚠ " + event
    )

    # --------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------

    event_timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # --------------------------------------------------
    # LOG CAMERA EVENT
    # --------------------------------------------------

    log_event(

        session_id,

        event,

        event_timestamp,

        "Camera monitoring event"

    )

    # --------------------------------------------------
    # INCIDENT
    # --------------------------------------------------

    incident_event = event

    if event == "Multiple Faces Detected":

        incident_event = "Multiple Faces"

    incident_id = register_incident(

        session_id=session_id,

        candidate_id=session["candidate_id"],

        event_type=incident_event,

        details="Camera monitoring event",

        timestamp=event_timestamp

    )

    # --------------------------------------------------
    # GET SCORE WITHOUT MODIFYING IT
    # --------------------------------------------------

    score = get_integrity_score(
        session_id
    )

    if score is None:

        score = 100

    return jsonify({

        "status": "success",

        "score": score,

        "warning": current_warning,

        "incident_id": incident_id

    })


# ===================================================
# UPDATE INTEGRITY
# ===================================================

@app.route(
    "/update_integrity",
    methods=["POST"]
)
def update_integrity():

    global current_warning

    data = request.get_json(
        silent=True
    )

    # -------------------------------------------------
    # VALIDATE REQUEST
    # -------------------------------------------------

    if not data:
        return jsonify(
            success=False,
            message="Invalid request"
        ), 400

    event = data.get("event")

    if not event:
        return jsonify(
            success=False,
            message="Event missing"
        ), 400

    # -------------------------------------------------
    # GET SESSION ID FROM REQUEST
    # -------------------------------------------------
    # face_monitor.py sends the active session_id
    # directly in the JSON request.
    #
    # We should NOT depend on:
    #
    #     session.get("session_id")
    #
    # because face_monitor.py uses requests.post()
    # and does not have the browser's Flask session cookie.
    # -------------------------------------------------

    session_id = data.get("session_id")

    if not session_id:
        return jsonify(
            success=False,
            message="Session ID missing"
        ), 400

    # -------------------------------------------------
    # GET CANDIDATE ID FROM DATABASE
    # -------------------------------------------------

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT candidate_id
        FROM exam_session
        WHERE session_id = ?
    """, (session_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return jsonify(
            success=False,
            message="Invalid exam session"
        ), 400

    candidate_id = row[0]

    # -------------------------------------------------
    # CURRENT TIMESTAMP
    # -------------------------------------------------

    event_timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # -------------------------------------------------
    # CAMERA / FACE EVENTS
    # -------------------------------------------------

    camera_events = {
        "Face Missing",
        "Camera Covered",
        "Multiple Faces Detected",
        "Multiple Faces",
        "Face Detected"
    }

    if event in camera_events:

        print(
            "CAMERA EVENT - NO SCORE DEDUCTION:",
            event
        )

        # -------------------------------------------------
        # LOG EVENT
        # -------------------------------------------------

        log_event(
            session_id,
            event,
            event_timestamp,
            "Camera monitoring event"
        )

        # -------------------------------------------------
        # NORMALIZE EVENT NAME
        # -------------------------------------------------

        incident_event = event

        if event == "Multiple Faces Detected":
            incident_event = "Multiple Faces"

        # -------------------------------------------------
        # CREATE INCIDENT
        # -------------------------------------------------

        incident_id = register_incident(
            session_id=session_id,
            candidate_id=candidate_id,
            event_type=incident_event,
            details="Camera monitoring event",
            evidence_path=data.get("evidence_path"),
            timestamp=event_timestamp
        )

        print(
            "Camera incident created:",
            incident_id
        )

        # -------------------------------------------------
        # WARNING
        # -------------------------------------------------

        if event != "Face Detected":

            current_warning = "⚠ " + event

        else:

            current_warning = ""

        # -------------------------------------------------
        # IMPORTANT:
        # CAMERA EVENTS DO NOT REDUCE INTEGRITY SCORE
        # -------------------------------------------------

        integrity_score = get_integrity_score(
            session_id
        )

        if integrity_score is None:
            integrity_score = 100

        return jsonify(
            success=True,
            warning=current_warning,
            event=event,
            integrity_score=integrity_score,
            incident_id=incident_id,
            terminated=False
        )

    # -------------------------------------------------
    # BROWSER EVENTS
    # -------------------------------------------------

    log_event(
        session_id,
        event,
        event_timestamp,
        "Monitoring event"
    )

    current_warning = "⚠ " + event

    # -------------------------------------------------
    # GET CURRENT SCORE
    # -------------------------------------------------

    integrity_score = get_integrity_score(
        session_id
    )

    if integrity_score is None:
        integrity_score = 100

    return jsonify(
        success=True,
        warning=current_warning,
        event=event,
        integrity_score=integrity_score,
        terminated=False
    )


# ===================================================
# UPDATE WARNING
# ===================================================

@app.route(
    "/update_warning",
    methods=["POST"]
)
def update_warning():

    global current_warning

    data = request.get_json(
        silent=True
    )

    if not data or "warning" not in data:

        return jsonify({
            "status": "invalid warning"
        }), 400

    current_warning = data["warning"]

    return jsonify({
        "status": "success"
    })


# ===================================================
# GET WARNING
# ===================================================

@app.route("/get_warning")
def get_warning():

    global current_warning

    return jsonify(
        warning=current_warning
    )


# ===================================================
# LOGOUT
# ===================================================

@app.route("/logout")
def logout():

    # --------------------------------------------------
    # STOP CAMERA
    # --------------------------------------------------

    try:

        stop_camera()

        set_session(None)

    except Exception as e:

        print(
            "Camera cleanup error:",
            e
        )

    # --------------------------------------------------
    # CLEAR SESSION
    # --------------------------------------------------

    session.clear()

    return redirect(
        url_for("login")
    )


# ===================================================
# RUN APPLICATION
# ===================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
