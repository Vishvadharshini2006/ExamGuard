import cv2
import os
import requests
from datetime import datetime


# ==========================================================
# CASCADE PATH
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

cascade_path = os.path.join(
    BASE_DIR,
    "haarcascade",
    "haarcascade_frontalface_default copy.xml"
)

face_cascade = cv2.CascadeClassifier(
    cascade_path
)

if face_cascade.empty():
    print("ERROR: Haar Cascade could not be loaded.")
    print("Expected path:", cascade_path)
else:
    print("Haar Cascade loaded successfully.")


# ==========================================================
# CAMERA
# ==========================================================

camera = None


# ==========================================================
# MONITORING STATES
# ==========================================================

face_missing = False
multiple_faces = False
camera_covered = False

missing_start = None


# ==========================================================
# SESSION
# ==========================================================

SERVER_URL = "http://127.0.0.1:5000"

CURRENT_SESSION_ID = None


def set_session(session_id):

    global CURRENT_SESSION_ID

    CURRENT_SESSION_ID = session_id

    print(
        "Face monitoring session set:",
        CURRENT_SESSION_ID
    )


# ==========================================================
# SAVE EVIDENCE FRAME
# ==========================================================

def save_evidence_frame(frame, event):

    if CURRENT_SESSION_ID is None:
        print("No session ID. Evidence not saved.")
        return None

    if frame is None:
        print("No frame available. Evidence not saved.")
        return None

    try:

        evidence_dir = os.path.join(
            BASE_DIR,
            "static",
            "evidence",
            str(CURRENT_SESSION_ID)
        )

        os.makedirs(
            evidence_dir,
            exist_ok=True
        )

        safe_event = (
            event
            .replace(" ", "_")
            .replace("/", "_")
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        filename = (
            safe_event
            + "_"
            + timestamp
            + ".jpg"
        )

        file_path = os.path.join(
            evidence_dir,
            filename
        )

        success = cv2.imwrite(
            file_path,
            frame
        )

        if not success:

            print(
                "Failed to save evidence:",
                file_path
            )

            return None

        print(
            "Evidence saved:",
            file_path
        )

        relative_path = os.path.join(
            "evidence",
            str(CURRENT_SESSION_ID),
            filename
        )

        relative_path = relative_path.replace(
            "\\",
            "/"
        )

        return relative_path

    except Exception as e:

        print(
            "Evidence save error:",
            e
        )

        return None


# ==========================================================
# SEND MONITORING EVENT
# ==========================================================

def send_monitoring_event(
    event,
    frame=None
):

    if CURRENT_SESSION_ID is None:

        print(
            "No active session. Event ignored:",
            event
        )

        return

    print(
        "MONITORING EVENT:",
        event,
        "| Session:",
        CURRENT_SESSION_ID
    )

    evidence_path = None

    # ------------------------------------------------------
    # SAVE EVIDENCE
    # ------------------------------------------------------

    if event in [
        "Face Missing",
        "Multiple Faces",
        "Camera Covered"
    ]:

        evidence_path = save_evidence_frame(
            frame,
            event
        )

    try:

        response = requests.post(

            SERVER_URL + "/update_integrity",

            json={
                "session_id": CURRENT_SESSION_ID,
                "event": event,

                # Face/camera events do NOT
                # reduce integrity score.
                "deduction": 0,

                "evidence_path": evidence_path
            },

            timeout=1
        )

        print(
            "Integrity update response:",
            response.status_code
        )

        # --------------------------------------------------
        # WARNING
        # --------------------------------------------------

        if event in [
            "Face Missing",
            "Multiple Faces",
            "Camera Covered"
        ]:

            requests.post(

                SERVER_URL + "/update_warning",

                json={
                    "warning": "⚠ " + event
                },

                timeout=1
            )

    except Exception as e:

        print(
            "Monitoring event error:",
            e
        )


# ==========================================================
# CLEAR WARNING
# ==========================================================

def clear_warning():

    try:

        requests.post(

            SERVER_URL + "/update_warning",

            json={
                "warning": "✅ No Violations"
            },

            timeout=1
        )

    except Exception:

        pass


# ==========================================================
# STOP CAMERA
# ==========================================================

def stop_camera():

    global camera

    if camera is not None:

        if camera.isOpened():

            camera.release()

        camera = None

    cv2.destroyAllWindows()

    print(
        "Camera Released"
    )


# ==========================================================
# VIDEO STREAM
# ==========================================================

def generate_frames():

    global camera

    global face_missing
    global multiple_faces
    global camera_covered
    global missing_start


    print(
        ">>> generate_frames() STARTED"
    )

    print(
        ">>> CURRENT_SESSION_ID:",
        CURRENT_SESSION_ID
    )


    # ======================================================
    # RESET STATES
    # ======================================================

    face_missing = False
    multiple_faces = False
    camera_covered = False
    missing_start = None


    # ======================================================
    # OPEN CAMERA
    # ======================================================

    if camera is None:

        print(
            ">>> Attempting to open camera..."
        )

        camera = cv2.VideoCapture(0)

        camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            640
        )

        camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            480
        )

        if not camera.isOpened():

            print(
                "!!! Unable to open camera."
            )

            camera = None

            return

        print(
            ">>> Camera Started Successfully"
        )

    else:

        print(
            ">>> Existing camera object is being used."
        )


    # ======================================================
    # FRAME LOOP
    # ======================================================

    while True:

        success, frame = camera.read()

        if not success:

            print(
                "!!! Unable to read frame from camera."
            )

            break


        # ==================================================
        # GRAYSCALE
        # ==================================================

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        brightness = gray.mean()


        # ==================================================
        # FACE DETECTION
        # ==================================================

        faces = face_cascade.detectMultiScale(

            gray,

            scaleFactor=1.2,

            minNeighbors=5
        )


        # ==================================================
        # CAMERA COVERED
        # ==================================================

        if brightness < 20:

            cv2.putText(

                frame,

                "Camera Covered",

                (20, 80),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0, 0, 255),

                2
            )

            if not camera_covered:

                camera_covered = True

                print(
                    ">>> Camera Covered detected"
                )

                send_monitoring_event(
                    "Camera Covered",
                    frame
                )

        else:

            if camera_covered:

                print(
                    ">>> Camera visibility restored"
                )

                clear_warning()

            camera_covered = False


        # ==================================================
        # ONE FACE
        # ==================================================

        if len(faces) == 1:

            x, y, w, h = faces[0]


            cv2.rectangle(

                frame,

                (x, y),

                (x + w, y + h),

                (0, 255, 0),

                2
            )


            cv2.putText(

                frame,

                "Face Detected",

                (20, 40),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0, 255, 0),

                2
            )


            # ------------------------------------------------
            # FACE RETURNED
            # ------------------------------------------------

            if face_missing:

                print(
                    ">>> Face Returned"
                )

                face_missing = False
                missing_start = None

                send_monitoring_event(
                    "Face Detected"
                )

            elif multiple_faces:

                print(
                    ">>> Multiple face condition cleared"
                )

                multiple_faces = False

                send_monitoring_event(
                    "Face Detected"
                )


            clear_warning()


        # ==================================================
        # NO FACE
        # ==================================================

        elif len(faces) == 0:

            cv2.putText(

                frame,

                "Face Missing",

                (20, 40),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0, 0, 255),

                2
            )


            # ------------------------------------------------
            # FACE JUST BECAME MISSING
            # ------------------------------------------------

            if not face_missing:

                face_missing = True

                missing_start = datetime.now()

                print(
                    ">>> Face Missing detected"
                )

                send_monitoring_event(
                    "Face Missing",
                    frame
                )


            # ------------------------------------------------
            # FACE CONTINUES TO BE MISSING
            # ------------------------------------------------

            else:

                if missing_start is not None:

                    duration = (
                        datetime.now()
                        -
                        missing_start
                    ).total_seconds()


                    # ----------------------------------------
                    # DEBUG MESSAGE AFTER 5 SECONDS
                    # ----------------------------------------

                    if duration >= 5:

                        cv2.putText(

                            frame,

                            "Face absent > 5 seconds",

                            (20, 80),

                            cv2.FONT_HERSHEY_SIMPLEX,

                            0.7,

                            (0, 0, 255),

                            2
                        )


        # ==================================================
        # MULTIPLE FACES
        # ==================================================

        else:

            cv2.putText(

                frame,

                "Multiple Faces",

                (20, 40),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (255, 0, 0),

                2
            )


            for (x, y, w, h) in faces:

                cv2.rectangle(

                    frame,

                    (x, y),

                    (x + w, y + h),

                    (255, 0, 0),

                    2
                )


            # ------------------------------------------------
            # MULTIPLE FACES JUST DETECTED
            # ------------------------------------------------

            if not multiple_faces:

                multiple_faces = True

                face_missing = False

                missing_start = None

                print(
                    ">>> Multiple Faces detected"
                )

                send_monitoring_event(
                    "Multiple Faces",
                    frame
                )


        # ==================================================
        # STREAM FRAME
        # ==================================================

        ret, buffer = cv2.imencode(
            ".jpg",
            frame
        )

        if not ret:

            print(
                "!!! Failed to encode frame"
            )

            continue


        frame_bytes = buffer.tobytes()


        yield (

            b"--frame\r\n"

            b"Content-Type: image/jpeg\r\n\r\n"

            + frame_bytes

            + b"\r\n"

        )


    # ======================================================
    # RELEASE CAMERA
    # ======================================================

    print(
        ">>> Frame loop ended."
    )

    stop_camera()
