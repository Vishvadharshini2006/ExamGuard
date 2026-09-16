import cv2
import os
from datetime import datetime


SAVE_FOLDER = "static/photos"


def capture_candidate_photo():

    os.makedirs(SAVE_FOLDER, exist_ok=True)

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Unable to access webcam.")
        return None

    print("Press SPACE to capture photo.")
    print("Press ESC to cancel.")

    while True:

        success, frame = camera.read()

        if not success:
            break

        cv2.imshow("Capture Candidate Photo", frame)

        key = cv2.waitKey(1)

        if key == 27:

            camera.release()
            cv2.destroyAllWindows()

            return None

        elif key == 32:

            filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"

            filepath = os.path.join(SAVE_FOLDER, filename)

            cv2.imwrite(filepath, frame)

            camera.release()
            cv2.destroyAllWindows()

            print("Photo Saved:", filepath)

            return filepath


if __name__ == "__main__":

    capture_candidate_photo()