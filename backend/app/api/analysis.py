import time
from dataclasses import dataclass, field
from threading import Lock
from uuid import UUID

import cv2
import numpy as np

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    Form
)

from app.services.pose_estimation import (
    PoseEstimator
)

from app.services.exercise_analyzers import (
    ExerciseAnalyzer
)
from app.services.exercise_detection import ExerciseDetector

from app.services.frame_preprocessing import (
    frame_preprocessor
)


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


MODEL_PATH = (
    "models/pose_landmarker_full.task"
)


ALLOWED_EXERCISES = {
    "Squat",
    "Lunge",
    "Bicep Curl",
    "Push Up",
    "Running",
}


pose_estimator = PoseEstimator(
    MODEL_PATH
)


SESSION_TTL_SECONDS = 30 * 60
MAX_ACTIVE_SESSIONS = 100


@dataclass
class AnalysisSession:
    """State that belongs to one browser workout, never the entire server."""

    exercise: str
    analyzer: ExerciseAnalyzer
    detector: ExerciseDetector = field(default_factory=ExerciseDetector)
    last_seen: float = field(default_factory=time.monotonic)
    lock: Lock = field(default_factory=Lock)


sessions: dict[str, AnalysisSession] = {}
sessions_lock = Lock()
pose_lock = Lock()


def _validate_session_id(session_id: str) -> str:
    try:
        return str(UUID(session_id))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid analysis session id.") from exc


def _remove_expired_sessions(now: float) -> None:
    expired = [key for key, value in sessions.items() if now - value.last_seen > SESSION_TTL_SECONDS]
    for key in expired:
        sessions.pop(key, None)


def get_session(exercise: str, session_id: str) -> AnalysisSession:
    now = time.monotonic()
    with sessions_lock:
        _remove_expired_sessions(now)
        session = sessions.get(session_id)
        if session is None or session.exercise != exercise:
            if len(sessions) >= MAX_ACTIVE_SESSIONS:
                oldest_session_id = min(sessions, key=lambda key: sessions[key].last_seen)
                sessions.pop(oldest_session_id, None)
            session = AnalysisSession(exercise=exercise, analyzer=ExerciseAnalyzer(exercise))
            sessions[session_id] = session
        session.last_seen = now
        return session


@router.post("/reset")
async def reset_analysis(
    exercise: str = Form(...),
    session_id: str = Form(...),
):

    if exercise not in ALLOWED_EXERCISES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported exercise: "
                f"{exercise}"
            )
        )

    session = get_session(exercise, _validate_session_id(session_id))
    with session.lock:
        session.analyzer.reset()
        session.detector = ExerciseDetector()

    return {
        "success": True,
        "exercise": exercise,
        "message": "Analysis reset."
    }


@router.post("/pose")
async def analyze_pose(
    file: UploadFile = File(...),
    exercise: str = Form(...),
    session_id: str = Form(...),
):

    try:

        if exercise not in ALLOWED_EXERCISES:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported exercise: "
                    f"{exercise}. "
                    f"Allowed: "
                    f"{sorted(ALLOWED_EXERCISES)}"
                )
            )

        session = get_session(exercise, _validate_session_id(session_id))

        image_bytes = await file.read()

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image frame."
            )

        # -----------------------------------------
        # AUTOMATIC IMAGE IMPROVEMENT
        # -----------------------------------------

        processed_frame = (
            frame_preprocessor.process(
                frame
            )
        )

        # -----------------------------------------
        # POSE ESTIMATION
        # -----------------------------------------

        timestamp_ms = int(
            time.monotonic() * 1000
        )

        # MediaPipe's VIDEO landmarker and the session state machines are
        # mutable. Serialize access to preserve timestamp ordering and avoid
        # mixing simultaneous browser streams.
        with pose_lock:
            result = pose_estimator.process_frame(processed_frame, timestamp_ms)

        # -----------------------------------------
        # NO PERSON DETECTED
        # -----------------------------------------

        if not result.pose_landmarks:

            current = (
                session.analyzer.get_result()
            )

            return {
                "detected": False,
                "exercise": exercise,
                "angle": None,
                "knee_angle": None,
                "reps":
                    current["reps"],
                "correct_reps":
                    current["correct_reps"],
                "incorrect_reps":
                    current["incorrect_reps"],
                "technique_score":
                    current[
                        "technique_score"
                    ],
                "feedback":
                    "Searching for movement...",
                "state":
                    current["state"],
                "selected_side":
                    current[
                        "selected_side"
                    ],
                "reliability":
                    current[
                        "reliability"
                    ],
            }

        # -----------------------------------------
        # GET PERSON LANDMARKS
        # -----------------------------------------

        landmarks = (
            result.pose_landmarks[0]
        )

        # -----------------------------------------
        # COMMON ANALYSIS ENGINE
        # -----------------------------------------

        # ExerciseAnalyzer operates in seconds; passing the monotonic server
        # timestamp fixes the previous "all frames are at t=0" cooldown bug.
        with session.lock:
            session.detector.analyze_frame(landmarks)
            detection = session.detector.get_result()
            current = session.analyzer.analyze_frame(landmarks, timestamp=timestamp_ms / 1000.0)

        return {
            "detected": True,

            "exercise":
                exercise,

            "angle":
                current["angle"],

            "knee_angle":
                current["angle"],

            "reps":
                current["reps"],

            "correct_reps":
                current["correct_reps"],

            "incorrect_reps":
                current["incorrect_reps"],

            "technique_score":
                current[
                    "technique_score"
                ],

            "feedback":
                current["feedback"],

            "state":
                current["state"],

            "selected_side":
                current[
                    "selected_side"
                ],

            "left_confidence":
                current[
                    "left_confidence"
                ],

            "right_confidence":
                current[
                    "right_confidence"
                ],

            "reliability":
                current[
                    "reliability"
                ],

            # classifficating of do not  dojghti jutieoj not silently switch exercises
            # while a user is in the middle of a rep.
            "detected_exercise": detection["exercise"],
            "exercise_confidence": detection["confidence"],
            "exercise_matches_selection": detection["exercise"] in {"Unknown", exercise},
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            "Live analysis error:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
