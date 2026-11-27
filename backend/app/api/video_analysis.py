import os
import uuid
import shutil
import subprocess

import cv2

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Form,
    HTTPException,
)

from fastapi.responses import FileResponse

from app.services.pose_estimation import (
    PoseEstimator
)

from app.services.exercise_analyzers import (
    ExerciseAnalyzer
)

from app.services.frame_preprocessing import (
    frame_preprocessor
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/analysis",
    tags=["Video Analysis"]
)


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = (
    "models/pose_landmarker_full.task"
)

OUTPUT_DIR = "generated_videos"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# SUPPORTED EXERCISES
# ============================================================

ALLOWED_EXERCISES = {
    "Squat",
    "Lunge",
    "Bicep Curl",
    "Push Up",
    "Running",
}


# ============================================================
# POSE CONNECTIONS
# ============================================================

POSE_CONNECTIONS = [

    # Left arm
    (11, 13),
    (13, 15),

    # Right arm
    (12, 14),
    (14, 16),

    # Shoulders
    (11, 12),

    # Torso
    (11, 23),
    (12, 24),

    # Hips
    (23, 24),

    # Left leg
    (23, 25),
    (25, 27),

    # Right leg
    (24, 26),
    (26, 28),
]


# ============================================================
# DRAW POSE
# ============================================================

def draw_pose(
    frame,
    landmarks
):

    if not landmarks:
        return frame

    height, width = frame.shape[:2]

    points = []

    # -----------------------------------------
    # Draw landmarks
    # -----------------------------------------

    for landmark in landmarks:

        x = int(
            landmark.x * width
        )

        y = int(
            landmark.y * height
        )

        points.append(
            (x, y)
        )

        # Only draw points that are
        # inside the frame.

        if (
            0 <= x < width
            and
            0 <= y < height
        ):

            cv2.circle(
                frame,
                (x, y),
                4,
                (0, 255, 0),
                -1
            )

    # -----------------------------------------
    # Draw skeleton
    # -----------------------------------------

    for start, end in POSE_CONNECTIONS:

        if (
            start < len(points)
            and
            end < len(points)
        ):

            x1, y1 = points[start]
            x2, y2 = points[end]

            if (
                0 <= x1 < width
                and
                0 <= y1 < height
                and
                0 <= x2 < width
                and
                0 <= y2 < height
            ):

                cv2.line(
                    frame,
                    points[start],
                    points[end],
                    (0, 255, 0),
                    2
                )

    return frame


# ============================================================
# DRAW ANALYSIS TEXT
# ============================================================

def draw_analysis_text(
    frame,
    exercise,
    analyzer
):

    # ExerciseAnalyzer uses get_final_result()
    # as the common result interface.

    result = analyzer.get_final_result()

    reps = result.get(
        "reps",
        0
    )

    correct_reps = result.get(
        "correct_reps",
        0
    )

    incorrect_reps = result.get(
        "incorrect_reps",
        0
    )

    technique_score = result.get(
        "technique_score",
        0
    )

    state = result.get(
        "state",
        "READY"
    )

    feedback = result.get(
        "feedback",
        ""
    )

    selected_side = result.get(
        "selected_side"
    )

    angle = result.get(
        "angle"
    )

    reliability = result.get(
        "reliability",
        0
    )

    # -----------------------------------------
    # Background panel
    # -----------------------------------------

    cv2.rectangle(
        frame,
        (15, 15),
        (430, 270),
        (0, 0, 0),
        -1
    )

    # -----------------------------------------
    # Exercise
    # -----------------------------------------

    cv2.putText(
        frame,
        f"Exercise: {exercise}",
        (30, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.70,
        (255, 255, 255),
        2
    )

    # -----------------------------------------
    # Reps
    # -----------------------------------------

    cv2.putText(
        frame,
        f"Reps: {reps}",
        (30, 78),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    # -----------------------------------------
    # Correct
    # -----------------------------------------

    cv2.putText(
        frame,
        f"Correct: {correct_reps}",
        (30, 108),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (0, 255, 0),
        2
    )

    # -----------------------------------------
    # Incorrect
    # -----------------------------------------

    cv2.putText(
        frame,
        f"Incorrect: {incorrect_reps}",
        (30, 138),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (0, 0, 255),
        2
    )

    # -----------------------------------------
    # Technique score
    # -----------------------------------------

    cv2.putText(
        frame,
        f"Score: {technique_score}/100",
        (30, 168),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 0),
        2
    )

    # -----------------------------------------
    # Current angle
    # -----------------------------------------

    angle_text = (
        f"Angle: {angle:.1f}"
        if angle is not None
        else "Angle: --"
    )

    cv2.putText(
        frame,
        angle_text,
        (30, 198),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 0),
        2
    )

    # -----------------------------------------
    # State
    # -----------------------------------------

    cv2.putText(
        frame,
        f"State: {state}",
        (180, 198),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

    # -----------------------------------------
    # Selected side
    # -----------------------------------------

    side_text = (
        selected_side
        if selected_side
        else "detecting"
    )

    cv2.putText(
        frame,
        f"Side: {side_text}",
        (30, 228),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

    # -----------------------------------------
    # Reliability
    # -----------------------------------------

    cv2.putText(
        frame,
        f"Reliability: {reliability:.1f}%",
        (210, 228),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (255, 255, 255),
        2
    )

    # -----------------------------------------
    # Feedback
    # -----------------------------------------

    if feedback:

        cv2.putText(
            frame,
            feedback[:52],
            (30, 255),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (200, 255, 200),
            1
        )

    return frame


# ============================================================
# CREATE POSE ESTIMATOR
# ============================================================

def create_pose_estimator():

    return PoseEstimator(
        MODEL_PATH
    )


# ============================================================
# VIDEO ANALYSIS
# ============================================================

@router.post("/video")
async def analyze_video(
    file: UploadFile = File(...),
    exercise: str = Form(...)
):

    # These variables are needed by
    # the finally block.

    input_path = None
    raw_output_path = None
    output_path = None

    cap = None
    writer = None
    pose_estimator = None

    # ========================================================
    # VALIDATE EXERCISE
    # ========================================================

    if exercise not in ALLOWED_EXERCISES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid exercise. "
                "Choose Squat, Lunge, Bicep Curl, "
                "Push Up or Running."
            )
        )

    # ========================================================
    # VALIDATE FILE
    # ========================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No video file selected."
        )

    # ========================================================
    # CREATE FILE NAMES
    # ========================================================

    video_id = str(
        uuid.uuid4()
    )

    extension = os.path.splitext(
        file.filename
    )[1]

    if not extension:
        extension = ".mp4"

    input_path = os.path.join(
        OUTPUT_DIR,
        f"input_{video_id}{extension}"
    )

    raw_output_path = os.path.join(
        OUTPUT_DIR,
        f"raw_{video_id}.avi"
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        f"analyzed_{video_id}.mp4"
    )

    try:

        # ====================================================
        # SAVE UPLOADED VIDEO
        # ====================================================

        with open(
            input_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # ====================================================
        # OPEN VIDEO
        # ====================================================

        cap = cv2.VideoCapture(
            input_path
        )

        if not cap.isOpened():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Unable to open uploaded video."
                )
            )

        # ====================================================
        # VIDEO INFORMATION
        # ====================================================

        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        if not fps or fps <= 0:
            fps = 30.0

        total_frames = int(
            cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        width = int(
            cap.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )

        height = int(
            cap.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )

        duration_seconds = (
            total_frames / fps
            if fps > 0
            else 0
        )

        # ====================================================
        # CREATE COMMON ANALYZER
        # ====================================================

        analyzer = ExerciseAnalyzer(
            exercise
        )

        analyzer.reset()

        # ====================================================
        # CREATE POSE ESTIMATOR
        # ====================================================

        pose_estimator = (
            create_pose_estimator()
        )

        # ====================================================
        # VIDEO WRITER
        # ====================================================

        fourcc = cv2.VideoWriter_fourcc(
            *"MJPG"
        )

        writer = cv2.VideoWriter(
            raw_output_path,
            fourcc,
            fps,
            (width, height)
        )

        if not writer.isOpened():

            raise HTTPException(
                status_code=500,
                detail=(
                    "Unable to create output video."
                )
            )

        # ====================================================
        # ANALYSIS VARIABLES
        # ====================================================

        frame_index = 0

        analyzed_frames = 0

        detected_frames = 0

        all_angles = []

        # ====================================================
        # PROCESS VIDEO
        # ====================================================

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            frame_index += 1

            analyzed_frames += 1

            # ------------------------------------------------
            # VIDEO TIMESTAMP
            # ------------------------------------------------

            video_timestamp = (
                frame_index / fps
                if fps > 0
                else 0.0
            )

            timestamp_ms = int(
                video_timestamp * 1000
            )

            # ------------------------------------------------
            # AUTOMATIC FRAME PREPROCESSING
            # ------------------------------------------------

            processed_frame = (
                frame_preprocessor.process(
                    frame
                )
            )

            # ------------------------------------------------
            # POSE ESTIMATION
            # ------------------------------------------------

            result = (
                pose_estimator.process_frame(
                    processed_frame,
                    timestamp_ms
                )
            )

            # =================================================
            # PERSON DETECTED
            # =================================================

            if result.pose_landmarks:

                detected_frames += 1

                landmarks = (
                    result.pose_landmarks[0]
                )

                # ---------------------------------------------
                # COMMON EXERCISE ANALYZER
                # ---------------------------------------------

                analysis_result = (
                    analyzer.analyze_frame(
                        landmarks,
                        timestamp=video_timestamp,
                    )
                )

                # ---------------------------------------------
                # USE COMMON ENGINE ANGLE
                # ---------------------------------------------

                current_angle = (
                    analysis_result.get(
                        "angle"
                    )
                )

                if current_angle is not None:

                    all_angles.append(
                        current_angle
                    )

                # ---------------------------------------------
                # Draw pose on ORIGINAL frame
                # ---------------------------------------------

                frame = draw_pose(
                    frame,
                    landmarks
                )

            else:

                # No pose in this frame.
                analysis_result = (
                    analyzer.get_final_result()
                )

            # =================================================
            # DRAW ANALYSIS
            # =================================================

            frame = draw_analysis_text(
                frame,
                exercise,
                analyzer
            )

            # =================================================
            # WRITE FRAME
            # =================================================

            writer.write(
                frame
            )

        # ====================================================
        # RELEASE VIDEO
        # ====================================================

        cap.release()
        cap = None

        writer.release()
        writer = None

        # ====================================================
        # FINAL ANALYSIS RESULT
        # ====================================================

        analysis_result = (
            analyzer.get_final_result()
        )

        completed_reps = analysis_result.get("reps", 0)
        # A technique percentage without a complete cycle is misleading. Use
        # null so the client can clearly show that no assessment was made.
        technique_score = (
            analysis_result.get("technique_score", 0)
            if completed_reps > 0
            else None
        )
        final_feedback = (
            analysis_result.get("feedback", "Analysis completed.")
            if completed_reps > 0
            else "No complete repetition was detected. Start and finish in the full camera frame."
        )

        # ====================================================
        # ANGLE STATISTICS
        # ====================================================

        average_angle = None
        minimum_angle = None
        maximum_angle = None

        if all_angles:

            average_angle = round(
                sum(all_angles)
                /
                len(all_angles),
                2
            )

            minimum_angle = round(
                min(all_angles),
                2
            )

            maximum_angle = round(
                max(all_angles),
                2
            )

        # ====================================================
        # FFMPEG
        # ====================================================

        ffmpeg_path = shutil.which(
            "ffmpeg"
        )

        if not ffmpeg_path:

            raise HTTPException(
                status_code=500,
                detail=(
                    "FFmpeg was not found. "
                    "Please install FFmpeg and "
                    "restart the terminal/PyCharm."
                )
            )

        # ====================================================
        # CONVERT AVI → H264 MP4
        # ====================================================

        ffmpeg_command = [

            ffmpeg_path,

            "-y",

            "-i",
            raw_output_path,

            "-c:v",
            "libx264",

            "-preset",
            "fast",

            "-pix_fmt",
            "yuv420p",

            "-movflags",
            "+faststart",

            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",

            output_path
        ]

        ffmpeg_result = subprocess.run(
            ffmpeg_command,
            capture_output=True,
            text=True
        )

        if ffmpeg_result.returncode != 0:

            print(
                "FFmpeg ERROR:"
            )

            print(
                ffmpeg_result.stderr
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to convert "
                    "analyzed video."
                )
            )

        # ====================================================
        # REMOVE RAW AVI
        # ====================================================

        if os.path.exists(
            raw_output_path
        ):

            try:

                os.remove(
                    raw_output_path
                )

            except Exception:
                pass

        # ====================================================
        # RESULT
        # ====================================================

        return {

            "success": True,

            # -----------------------------------------------
            # Selected exercise
            # -----------------------------------------------

            "exercise":
                exercise,

            "filename":
                file.filename,

            # -----------------------------------------------
            # Video information
            # -----------------------------------------------

            "duration_seconds":
                round(
                    duration_seconds,
                    2
                ),

            "total_frames":
                total_frames,

            "analyzed_frames":
                analyzed_frames,

            "detected_frames":
                detected_frames,

            # -----------------------------------------------
            # Exercise results
            # -----------------------------------------------

            "reps":
                completed_reps,

            "correct_reps":
                analysis_result.get(
                    "correct_reps",
                    0
                ),

            "incorrect_reps":
                analysis_result.get(
                    "incorrect_reps",
                    0
                ),

            "technique_score":
                technique_score,

            "feedback":
                final_feedback,

            "final_state":
                analysis_result.get(
                    "final_state",
                    "UP"
                ),

            # -----------------------------------------------
            # Generic angle information
            # -----------------------------------------------

            "average_angle":
                average_angle,

            "minimum_angle":
                minimum_angle,

            "maximum_angle":
                maximum_angle,

            # -----------------------------------------------
            # Per-repetition scores
            # -----------------------------------------------

            "rep_scores":
                analysis_result.get(
                    "rep_scores",
                    []
                ),

            "average_rep_score":
                analysis_result.get(
                    "average_rep_score",
                    0
                ),

            # -----------------------------------------------
            # Detection information
            # -----------------------------------------------

            "selected_side":
                analysis_result.get(
                    "selected_side"
                ),

            "left_confidence":
                analysis_result.get(
                    "left_confidence",
                    0
                ),

            "right_confidence":
                analysis_result.get(
                    "right_confidence",
                    0
                ),

            "reliability":
                analysis_result.get(
                    "reliability",
                    0
                ),

            # -----------------------------------------------
            # Output video
            # -----------------------------------------------

            "analyzed_video":
                f"/analysis/video-result/{video_id}"
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            "VIDEO ANALYSIS ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        # ====================================================
        # RELEASE RESOURCES
        # ====================================================

        if cap is not None:

            try:
                cap.release()
            except Exception:
                pass

        if writer is not None:

            try:
                writer.release()
            except Exception:
                pass

        # ====================================================
        # REMOVE INPUT VIDEO
        # ====================================================

        if (
            input_path
            and
            os.path.exists(
                input_path
            )
        ):

            try:

                os.remove(
                    input_path
                )

            except Exception:
                pass


# ============================================================
# SERVE ANALYZED VIDEO
# ============================================================

@router.get(
    "/video-result/{video_id}"
)
async def get_analyzed_video(
    video_id: str
):

    video_path = os.path.join(
        OUTPUT_DIR,
        f"analyzed_{video_id}.mp4"
    )

    if not os.path.exists(
        video_path
    ):

        raise HTTPException(
            status_code=404,
            detail=(
                "Analyzed video not found."
            )
        )

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=(
            f"analyzed_{video_id}.mp4"
        ),
        headers={
            "Content-Disposition":
                "inline"
        }
    )
