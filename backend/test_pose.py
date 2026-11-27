import cv2
import requests

from app.services.pose_estimation import PoseEstimator
from app.services.angle_calculation import calculate_angle
from app.services.rep_counter import SquatRepCounter
from app.services.form_analysis import SquatFormAnalyzer
from app.services.technique_score import calculate_technique_score
from app.services.workout_session import WorkoutSession


MODEL_PATH = "models/pose_landmarker_full.task"


# -----------------------------
# Initialize services
# -----------------------------
def save_workout(workout_result, token):
    url = "http://127.0.0.1:8000/workouts"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(
        url,
        json={
            "exercise": workout_result["exercise"],
            "total_reps": workout_result["total_reps"],
            "correct_reps": workout_result["correct_reps"],
            "incorrect_reps": workout_result["incorrect_reps"],
            "technique_score": workout_result["technique_score"],
            "duration_seconds": workout_result["duration_seconds"],
        },
        headers=headers
    )

    if response.status_code == 201:
        print("Workout saved successfully.")
        return response.json()

    print("Failed to save workout.")
    print(response.status_code)
    print(response.text)

    return None

pose_estimator = PoseEstimator(MODEL_PATH)

rep_counter = SquatRepCounter()

form_analyzer = SquatFormAnalyzer()

workout_session = WorkoutSession(
    exercise="Squat"
)
token = input("Enter your JWT access token: ").strip()

# -----------------------------
# Start camera
# -----------------------------

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera could not be opened.")
    exit()

print("Camera started.")
print("Exercise: Squat")
print("Press Q to finish workout.")

workout_session.start()

timestamp_ms = 0


# -----------------------------
# Main loop
# -----------------------------

while True:

    success, frame = camera.read()

    if not success:
        print("Could not read camera frame.")
        break


    # -------------------------
    # Pose detection
    # -------------------------

    result = pose_estimator.process_frame(
        frame,
        timestamp_ms
    )

    timestamp_ms += 33


    if result.pose_landmarks:

        # First detected person
        landmarks = result.pose_landmarks[0]


        # -------------------------
        # Get body landmarks
        # -------------------------

        hip = landmarks[23]

        knee = landmarks[25]

        ankle = landmarks[27]


        # -------------------------
        # Calculate knee angle
        # -------------------------

        knee_angle = calculate_angle(
            hip,
            knee,
            ankle
        )


        # -------------------------
        # Count repetitions
        # -------------------------

        reps = rep_counter.update(
            knee_angle
        )


        # -------------------------
        # Analyze form
        # -------------------------

        form_result = form_analyzer.analyze(
            knee_angle
        )

        status = form_result["status"]

        feedback = form_result["feedback"]


        # -------------------------
        # Calculate technique score
        # -------------------------

        technique_score = calculate_technique_score(
            knee_angle
        )


        # -------------------------
        # Update workout session
        # -------------------------

        workout_session.update(
            reps,
            status,
            technique_score
        )


        # -------------------------
        # Display information
        # -------------------------

        cv2.putText(
            frame,
            f"Knee Angle: {knee_angle:.1f}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Reps: {reps}",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Form: {status}",
            (30, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Score: {technique_score:.1f}",
            (30, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            feedback,
            (30, 210),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

    else:

        cv2.putText(
            frame,
            "No person detected",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )


    # -------------------------
    # Show camera
    # -------------------------

    cv2.imshow(
        "FitMotion - Workout",
        frame
    )


    # -------------------------
    # Quit
    # -------------------------

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# -----------------------------
# Finish workout
# -----------------------------

workout_session.finish()

camera.release()

cv2.destroyAllWindows()


# -----------------------------
# Display final result
# -----------------------------

result = workout_session.get_result()
saved_workout = save_workout(
    result,
    token
)

print("\n")
print("==============================")
print("      FITMOTION WORKOUT")
print("==============================")

print(
    f"Exercise: {result['exercise']}"
)

print(
    f"Total Reps: {result['total_reps']}"
)

print(
    f"Correct Reps: {result['correct_reps']}"
)

print(
    f"Incorrect Reps: {result['incorrect_reps']}"
)

print(
    f"Technique Score: {result['technique_score']}"
)

print(
    f"Duration: {result['duration_seconds']} seconds"
)

print("==============================")