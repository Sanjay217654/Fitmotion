import math
from collections import deque

from app.services.angle_calculation import calculate_robust_angle
from app.services.landmark_filter import LandmarkFilter
from app.services.movement_smoothing import (
    create_smoother,
    create_angle_smoother,
)


class ExerciseAnalyzer:

    SUPPORTED_EXERCISES = {
        "Squat",
        "Lunge",
        "Bicep Curl",
        "Push Up",
        "Running",
    }

    SIDE_LANDMARKS = {
        "Squat": {
            "left": (23, 25, 27),
            "right": (24, 26, 28),
        },
        "Lunge": {
            "left": (23, 25, 27),
            "right": (24, 26, 28),
        },
        "Running": {
            "left": (23, 25, 27),
            "right": (24, 26, 28),
        },
        "Bicep Curl": {
            "left": (11, 13, 15),
            "right": (12, 14, 16),
        },
        "Push Up": {
            "left": (11, 13, 15),
            "right": (12, 14, 16),
        },
    }

    EXERCISE_CONFIG = {
        "Squat": {
            "down_angle": 120.0,
            "up_angle": 160.0,
            "good_min": 115.0,
            "excellent_min": 95.0,
            "min_rom": 30.0,
            "target_rom": 55.0,
            "cooldown": 0.55,
        },

        "Lunge": {
            "down_angle": 125.0,
            "up_angle": 160.0,
            "good_min": 120.0,
            "excellent_min": 100.0,
            "min_rom": 25.0,
            "target_rom": 50.0,
            "cooldown": 0.55,
        },

        "Bicep Curl": {
            "down_angle": 75.0,
            "up_angle": 150.0,
            "good_min": 75.0,
            "excellent_min": 55.0,
            "min_rom": 35.0,
            "target_rom": 75.0,
            "cooldown": 0.55,
        },

        "Push Up": {
            # Push-up videos can have a smaller elbow-angle range than
            # the generic threshold used for other exercises.
            "down_angle": 115.0,
            "up_angle": 140.0,
            "good_min": 110.0,
            "excellent_min": 90.0,
            "min_rom": 25.0,
            "target_rom": 55.0,
            "cooldown": 0.40,
        },

        # Running counts one stride cycle on the selected leg. It uses knee
        # flexion/extension range, not a claim of gait-quality validation.
        "Running": {
            "down_angle": 105.0,
            "up_angle": 140.0,
            "good_min": 105.0,
            "excellent_min": 80.0,
            "min_rom": 25.0,
            "target_rom": 50.0,
            "cooldown": 0.25,
        },
    }

    RUNNING_DOWN_ANGLE = 105.0
    RUNNING_UP_ANGLE = 140.0

    STABLE_FRAMES = 2
    MIN_STABLE_SECONDS = 0.08
    SIDE_SWITCH_MARGIN = 0.12
    MIN_RELIABILITY_FOR_COUNTING = 45.0

    MIN_VALID_ANGLE = 5.0
    # A fully extended knee/elbow is physically valid at 180°. Rejecting
    # angles above 175° prevented normal standing/extended positions from
    # arming or completing a repetition.
    MAX_VALID_ANGLE = 180.0

    SCORE_HISTORY_SIZE = 8

    def __init__(self, exercise: str):

        if exercise not in self.SUPPORTED_EXERCISES:
            raise ValueError(
                f"Unsupported exercise: {exercise}"
            )

        self.exercise = exercise

        self.landmark_smoother = create_smoother()
        self.angle_smoother = create_angle_smoother()

        self.landmark_filter = LandmarkFilter()

        self.reset()

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        """
        Reset all analysis state.

        This method is required by video_analysis.py so the
        same ExerciseAnalyzer object can safely be reused.
        """

        # ----------------------------------------------------
        # Re-create smoothing objects so previous video data
        # does not affect the next video.
        # ----------------------------------------------------

        self.landmark_smoother = create_smoother()
        self.angle_smoother = create_angle_smoother()

        # ----------------------------------------------------
        # State
        # ----------------------------------------------------

        self.state = "UP"
        self.previous_state = "UP"

        self.stable_state = "UP"
        self.candidate_state = None
        self.candidate_count = 0
        self.candidate_started_at = None

        # ----------------------------------------------------
        # Repetitions
        # ----------------------------------------------------

        self.reps = 0
        self.correct_reps = 0
        self.incorrect_reps = 0

        # ----------------------------------------------------
        # Current repetition
        # ----------------------------------------------------

        self.rep_start_angle = None
        self.rep_min_angle = None
        self.rep_max_angle = None

        self.rep_start_timestamp = None
        self.rep_reliabilities = []
        self.cycle_armed = False
        self.last_rep_timestamp = None

        # ----------------------------------------------------
        # Scores
        # ----------------------------------------------------

        self.rep_scores = []

        self.score_history = deque(
            maxlen=self.SCORE_HISTORY_SIZE
        )

        self.technique_score = 0

        # ----------------------------------------------------
        # Angle statistics
        # ----------------------------------------------------

        self.angles = []

        self.minimum_angle = None
        self.maximum_angle = None
        self.average_angle = 0.0

        # ----------------------------------------------------
        # Side confidence
        # ----------------------------------------------------

        self.selected_side = None

        self.left_confidence = 0.0
        self.right_confidence = 0.0
        self.reliability = 0.0

        # ----------------------------------------------------
        # Timing
        # ----------------------------------------------------

        self.last_timestamp = None

        # ----------------------------------------------------
        # Running
        # ----------------------------------------------------

        self.running_state = "DOWN"

    # ========================================================
    # UTILITY
    # ========================================================

    @staticmethod
    def _safe_float(value, default=0.0):

        try:
            value = float(value)

            if not math.isfinite(value):
                return default

            return value

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clamp(value, minimum, maximum):

        return max(
            minimum,
            min(maximum, value)
        )

    # ========================================================
    # LANDMARK
    # ========================================================

    def _get_landmark(self, landmarks, index):

        if landmarks is None:
            return None

        try:

            if index < 0 or index >= len(landmarks):
                return None

            return landmarks[index]

        except Exception:

            return None

    # ========================================================
    # SIDE SELECTION
    # ========================================================

    def _select_side(self, landmarks):

        if landmarks is None:
            return None

        if self.exercise not in self.SIDE_LANDMARKS:
            return None

        left_indices = self.SIDE_LANDMARKS[
            self.exercise
        ]["left"]

        right_indices = self.SIDE_LANDMARKS[
            self.exercise
        ]["right"]

        left_points = [
            self._get_landmark(
                landmarks,
                index
            )
            for index in left_indices
        ]

        right_points = [
            self._get_landmark(
                landmarks,
                index
            )
            for index in right_indices
        ]

        try:

            left_confidence = (
                self.landmark_filter
                .calculate_group_confidence(
                    left_points
                )
            )

        except Exception:

            left_confidence = 0.0

        try:

            right_confidence = (
                self.landmark_filter
                .calculate_group_confidence(
                    right_points
                )
            )

        except Exception:

            right_confidence = 0.0

        self.left_confidence = round(
            self._safe_float(
                left_confidence
            ),
            4
        )

        self.right_confidence = round(
            self._safe_float(
                right_confidence
            ),
            4
        )

        if (
            left_confidence < self.landmark_filter.VISIBILITY_THRESHOLD
            and right_confidence < self.landmark_filter.VISIBILITY_THRESHOLD
        ):
            self.selected_side = None
            return None

        # Keep the currently selected side unless the other side is clearly
        # more visible. This avoids angle jumps caused by tiny confidence
        # fluctuations between adjacent video frames.
        if self.selected_side == "left" and left_confidence >= self.landmark_filter.VISIBILITY_THRESHOLD:
            if right_confidence < left_confidence + self.SIDE_SWITCH_MARGIN:
                return left_indices
        elif self.selected_side == "right" and right_confidence >= self.landmark_filter.VISIBILITY_THRESHOLD:
            if left_confidence < right_confidence + self.SIDE_SWITCH_MARGIN:
                return right_indices

        if left_confidence >= right_confidence:
            self.selected_side = "left"
            return left_indices

        self.selected_side = "right"
        return right_indices

    # ========================================================
    # ANGLE
    # ========================================================

    def _calculate_angle(self, landmarks):

        indices = self._select_side(
            landmarks
        )

        if indices is None:
            return None

        a_index, b_index, c_index = indices

        a = self._get_landmark(
            landmarks,
            a_index
        )

        b = self._get_landmark(
            landmarks,
            b_index
        )

        c = self._get_landmark(
            landmarks,
            c_index
        )

        if (
            a is None
            or b is None
            or c is None
        ):
            return None

        try:

            angle = calculate_robust_angle(
                a,
                b,
                c
            )

        except Exception:

            return None

        if angle is None:
            return None

        angle = self._safe_float(
            angle,
            default=-1
        )

        if (
            angle < self.MIN_VALID_ANGLE
            or
            angle > self.MAX_VALID_ANGLE
        ):
            return None

        return angle

    # ========================================================
    # RELIABILITY
    # ========================================================

    def _update_reliability(self):

        confidence = max(
            self.left_confidence,
            self.right_confidence
        )

        self.reliability = round(
            self._clamp(
                confidence * 100.0,
                0.0,
                100.0
            ),
            2
        )

    # ========================================================
    # STATE
    # ========================================================

    def _get_candidate_state(self, angle):

        config = self.EXERCISE_CONFIG[
            self.exercise
        ]

        if angle <= config["down_angle"]:
            return "DOWN"

        if angle >= config["up_angle"]:
            return "UP"

        return None

    def _update_stable_state(self, candidate_state, timestamp):

        if candidate_state is None:

            self.candidate_state = None
            self.candidate_count = 0
            self.candidate_started_at = None

            return self.stable_state

        if candidate_state == self.candidate_state:

            self.candidate_count += 1

        else:

            self.candidate_state = candidate_state
            self.candidate_count = 1
            self.candidate_started_at = timestamp

        required_frames = (
            2 if self.exercise == "Push Up" else self.STABLE_FRAMES
        )

        candidate_started_at = (
            self.candidate_started_at
            if self.candidate_started_at is not None
            else timestamp
        )
        stable_duration = max(0.0, timestamp - candidate_started_at)

        if (
            self.candidate_count >= required_frames
            and stable_duration >= self.MIN_STABLE_SECONDS
        ):

            if candidate_state != self.stable_state:

                self.previous_state = self.stable_state

                self.stable_state = candidate_state

        return self.stable_state

    # ========================================================
    # REP SCORE
    # ========================================================

    def _calculate_rep_score(
        self,
        minimum_angle,
        maximum_angle,
        reliability,
        duration
    ):

        config = self.EXERCISE_CONFIG[
            self.exercise
        ]

        good_min = config["good_min"]
        excellent_min = config["excellent_min"]

        min_rom = config["min_rom"]
        target_rom = config["target_rom"]

        if (
            minimum_angle is None
            or
            maximum_angle is None
        ):
            return 0

        rom = (
            maximum_angle -
            minimum_angle
        )

        if rom < min_rom:

            rom_score = (
                rom /
                max(min_rom, 1.0)
            ) * 50.0

        elif rom >= target_rom:

            rom_score = 100.0

        else:

            rom_score = (
                50.0
                +
                (
                    (rom - min_rom)
                    /
                    max(
                        target_rom - min_rom,
                        1.0
                    )
                ) * 50.0
            )

        rom_score = self._clamp(
            rom_score,
            0.0,
            100.0
        )

        if minimum_angle <= excellent_min:

            depth_score = 100.0

        elif minimum_angle <= good_min:

            depth_score = 85.0

        else:

            difference = (
                minimum_angle -
                good_min
            )

            depth_score = (
                85.0 -
                difference * 2.0
            )

        depth_score = self._clamp(
            depth_score,
            0.0,
            100.0
        )

        reliability_score = self._clamp(
            reliability,
            0.0,
            100.0
        )

        duration = self._safe_float(
            duration,
            0.0
        )

        if duration <= 0:

            duration_score = 50.0

        elif 0.25 <= duration <= 4.0:

            duration_score = 100.0

        elif duration < 0.25:

            duration_score = 60.0

        else:

            duration_score = max(
                50.0,
                100.0 -
                (
                    duration - 4.0
                ) * 8.0
            )

        score = (
            rom_score * 0.35
            +
            depth_score * 0.30
            +
            reliability_score * 0.25
            +
            duration_score * 0.10
        )

        return round(
            self._clamp(
                score,
                0.0,
                100.0
            )
        )

    # ========================================================
    # FINISH REP
    # ========================================================

    def _finish_rep(self, timestamp):

        if (
            self.rep_min_angle is None
            or
            self.rep_max_angle is None
        ):

            self.rep_start_angle = None
            self.rep_min_angle = None
            self.rep_max_angle = None
            self.rep_start_timestamp = None

            return

        if self.rep_start_timestamp is None:

            duration = 0.0

        else:

            duration = max(
                0.0,
                timestamp -
                self.rep_start_timestamp
            )

        score = self._calculate_rep_score(
            self.rep_min_angle,
            self.rep_max_angle,
            (
                sum(self.rep_reliabilities) / len(self.rep_reliabilities)
                if self.rep_reliabilities else self.reliability
            ),
            duration
        )

        self.rep_scores.append(score)

        self.score_history.append(score)

        self.reps += 1

        if score >= 70:

            self.correct_reps += 1

        else:

            self.incorrect_reps += 1

        self.technique_score = round(
            sum(self.score_history)
            /
            len(self.score_history)
        )

        self.last_rep_timestamp = timestamp

        self.rep_start_angle = None
        self.rep_min_angle = None
        self.rep_max_angle = None
        self.rep_start_timestamp = None
        self.rep_reliabilities = []

    # ========================================================
    # STANDARD EXERCISE
    # ========================================================

    def _handle_standard_exercise(
        self,
        angle,
        timestamp
    ):

        config = self.EXERCISE_CONFIG[
            self.exercise
        ]

        candidate_state = (
            self._get_candidate_state(
                angle
            )
        )

        stable_state = (
            self._update_stable_state(
                candidate_state,
                timestamp,
            )
        )

        required_frames = (
            2 if self.exercise == "Push Up" else self.STABLE_FRAMES
        )

        # A clip can begin halfway through a movement. Arm counting only after
        # a confirmed top/starting position, so a partial bottom -> top motion
        # at the beginning cannot be recorded as a full rep.
        if (
            stable_state == "UP"
            and candidate_state == "UP"
            and self.candidate_count >= required_frames
            and self.rep_start_angle is None
        ):
            self.cycle_armed = True
            self.rep_start_angle = angle
            self.rep_min_angle = angle
            self.rep_max_angle = angle
            self.rep_start_timestamp = timestamp

        elif self.cycle_armed and self.rep_start_angle is not None:

            self.rep_min_angle = min(
                self.rep_min_angle,
                angle
            )

            self.rep_max_angle = max(
                self.rep_max_angle,
                angle
            )

            self.rep_reliabilities.append(self.reliability)

        if stable_state == "DOWN":

            if self.rep_min_angle is None:
                self.rep_min_angle = angle

            self.rep_min_angle = min(
                self.rep_min_angle,
                angle
            )

        if (
            stable_state == "UP"
            and
            self.previous_state == "DOWN"
            and
            self.state != "UP"
            and
            self.cycle_armed
        ):

            can_count = True

            if self.last_rep_timestamp is not None:

                elapsed = (
                    timestamp -
                    self.last_rep_timestamp
                )

                if elapsed < config["cooldown"]:

                    can_count = False

            if can_count:

                self._finish_rep(
                    timestamp
                )

        self.state = stable_state

    # ========================================================
    # RUNNING
    # ========================================================

    def _handle_running(
        self,
        angle,
        timestamp
    ):

        if angle <= self.RUNNING_DOWN_ANGLE:

            candidate = "DOWN"

        elif angle >= self.RUNNING_UP_ANGLE:

            candidate = "UP"

        else:

            candidate = None

        stable_state = (
            self._update_stable_state(
                candidate,
                timestamp,
            )
        )

        if self.rep_start_angle is None:

            self.rep_start_angle = angle
            self.rep_min_angle = angle
            self.rep_max_angle = angle
            self.rep_start_timestamp = timestamp

        else:

            self.rep_min_angle = min(
                self.rep_min_angle,
                angle
            )

            self.rep_max_angle = max(
                self.rep_max_angle,
                angle
            )

        if (
            stable_state == "UP"
            and
            self.previous_state == "DOWN"
            and
            self.state != "UP"
        ):

            can_count = True

            if self.last_rep_timestamp is not None:

                elapsed = (
                    timestamp -
                    self.last_rep_timestamp
                )

                if elapsed < 0.25:

                    can_count = False

            if can_count:

                self._finish_rep(
                    timestamp
                )

        self.running_state = stable_state
        self.state = stable_state

    # ========================================================
    # FRAME ANALYSIS
    # ========================================================

    def analyze_frame(
        self,
        landmarks,
        timestamp=0.0
    ):

        timestamp = self._safe_float(
            timestamp,
            0.0
        )

        self.last_timestamp = timestamp

        if landmarks is None:

            return {
                "detected": False,
                "angle": None,
                "state": self.state,
                "reps": self.reps,
                "correct_reps": self.correct_reps,
                "incorrect_reps": self.incorrect_reps,
                "technique_score": self.technique_score,
                "selected_side": self.selected_side,
                "left_confidence": self.left_confidence,
                "right_confidence": self.right_confidence,
                "reliability": self.reliability,
            }

        try:

            smoothed_landmarks = (
                self.landmark_smoother.update(
                    landmarks
                )
            )

        except Exception:

            smoothed_landmarks = landmarks

        angle = self._calculate_angle(
            smoothed_landmarks
        )

        self._update_reliability()

        # Do not advance a rep state machine with an unreliable joint. This
        # prevents occlusion and poor framing from becoming false repetitions.
        if self.reliability < self.MIN_RELIABILITY_FOR_COUNTING:
            return {
                "detected": False,
                "angle": None,
                "state": self.state,
                "reps": self.reps,
                "correct_reps": self.correct_reps,
                "incorrect_reps": self.incorrect_reps,
                "technique_score": self.technique_score,
                "feedback": "Pose confidence is low. Keep the full joint visible.",
                "selected_side": self.selected_side,
                "left_confidence": self.left_confidence,
                "right_confidence": self.right_confidence,
                "reliability": self.reliability,
            }

        if angle is None:

            return {
                "detected": False,
                "angle": None,
                "state": self.state,
                "reps": self.reps,
                "correct_reps": self.correct_reps,
                "incorrect_reps": self.incorrect_reps,
                "technique_score": self.technique_score,
                "selected_side": self.selected_side,
                "left_confidence": self.left_confidence,
                "right_confidence": self.right_confidence,
                "reliability": self.reliability,
            }

        try:

            smoothed_angle = (
                self.angle_smoother.update(
                    angle
                )
            )

        except Exception:

            smoothed_angle = angle

        if smoothed_angle is None:
            smoothed_angle = angle

        smoothed_angle = self._safe_float(
            smoothed_angle,
            angle
        )

        self.angles.append(
            smoothed_angle
        )

        if self.minimum_angle is None:

            self.minimum_angle = smoothed_angle

        else:

            self.minimum_angle = min(
                self.minimum_angle,
                smoothed_angle
            )

        if self.maximum_angle is None:

            self.maximum_angle = smoothed_angle

        else:

            self.maximum_angle = max(
                self.maximum_angle,
                smoothed_angle
            )

        self.average_angle = (
            sum(self.angles)
            /
            len(self.angles)
        )

        if self.exercise == "Running":

            self._handle_running(
                smoothed_angle,
                timestamp
            )

        else:

            self._handle_standard_exercise(
                smoothed_angle,
                timestamp
            )

        feedback = self._generate_feedback(
            smoothed_angle
        )

        return {
            "detected": True,
            "angle": round(
                smoothed_angle,
                2
            ),
            "state": self.state,
            "reps": self.reps,
            "correct_reps": self.correct_reps,
            "incorrect_reps": self.incorrect_reps,
            "technique_score": self.technique_score,
            "feedback": feedback,
            "selected_side": self.selected_side,
            "left_confidence": self.left_confidence,
            "right_confidence": self.right_confidence,
            "reliability": self.reliability,
        }

    def get_result(self):
        """Return a safe live snapshot when no pose is visible in a frame."""
        return {
            "detected": False,
            "angle": None,
            "state": self.state,
            "reps": self.reps,
            "correct_reps": self.correct_reps,
            "incorrect_reps": self.incorrect_reps,
            "technique_score": self.technique_score,
            "feedback": "Move your full body into view.",
            "selected_side": self.selected_side,
            "left_confidence": self.left_confidence,
            "right_confidence": self.right_confidence,
            "reliability": self.reliability,
        }

    # ========================================================
    # FEEDBACK
    # ========================================================

    def _generate_feedback(self, angle):

        if self.exercise == "Squat":

            if angle <= 100:

                return (
                    "Good depth. "
                    "Drive upward through your feet."
                )

            if angle <= 120:

                return (
                    "Good. "
                    "Try to reach a little more depth."
                )

            if angle >= 160:

                return (
                    "Stand tall and prepare "
                    "for the next squat."
                )

            return (
                "Control the movement "
                "and keep your knees aligned."
            )

        if self.exercise == "Lunge":

            if angle <= 105:

                return (
                    "Good lunge depth. "
                    "Push back up with control."
                )

            if angle <= 125:

                return (
                    "Good. "
                    "Try slightly more depth."
                )

            if angle >= 160:

                return (
                    "Return to the starting position."
                )

            return (
                "Keep your movement controlled."
            )

        if self.exercise == "Bicep Curl":

            if angle <= 60:

                return (
                    "Good curl. "
                    "Lower the weight with control."
                )

            if angle <= 75:

                return (
                    "Good. "
                    "Try to curl a little higher."
                )

            if angle >= 150:

                return (
                    "Good extension. "
                    "Start the next curl."
                )

            return (
                "Keep your elbow stable while curling."
            )

        if self.exercise == "Push Up":

            if angle <= 90:

                return (
                    "Good depth. "
                    "Push upward while keeping "
                    "your body aligned."
                )

            if angle <= 105:

                return (
                    "Good. "
                    "Try to lower slightly further."
                )

            if angle >= 160:

                return (
                    "Good extension. "
                    "Lower for the next repetition."
                )

            return (
                "Keep your body straight "
                "and control the movement."
            )

        if self.exercise == "Running":

            if angle <= 95:

                return (
                    "Good knee lift. "
                    "Keep your stride controlled."
                )

            if angle >= 140:

                return (
                    "Good stride. "
                    "Keep moving consistently."
                )

            return (
                "Maintain a consistent running rhythm."
            )

        return "Keep your movement controlled."

    # ========================================================
    # FINAL RESULT
    # ========================================================

    def get_final_result(self):

        average_angle = round(
            self.average_angle,
            2
        )

        minimum_angle = (
            round(
                self.minimum_angle,
                2
            )
            if self.minimum_angle is not None
            else 0
        )

        maximum_angle = (
            round(
                self.maximum_angle,
                2
            )
            if self.maximum_angle is not None
            else 0
        )

        if self.rep_scores:

            average_rep_score = round(
                sum(self.rep_scores)
                /
                len(self.rep_scores)
            )

        else:

            average_rep_score = 0

        technique_score = (
            average_rep_score
            if self.rep_scores
            else 0
        )

        return {
            "exercise": self.exercise,
            "reps": self.reps,
            "correct_reps": self.correct_reps,
            "incorrect_reps": self.incorrect_reps,
            "technique_score": technique_score,
            "average_angle": average_angle,
            "minimum_angle": minimum_angle,
            "maximum_angle": maximum_angle,
            "rep_scores": self.rep_scores,
            "average_rep_score": average_rep_score,
            "selected_side": self.selected_side,
            "left_confidence": round(
                self.left_confidence,
                3
            ),
            "right_confidence": round(
                self.right_confidence,
                3
            ),
            "reliability": round(
                self.reliability,
                2
            ),
            "final_state": self.state,
        }
