import math
from collections import deque


class ExerciseDetector:

    def __init__(self):
        # A fixed time window keeps classification responsive and prevents a
        # long session from letting old movements dominate current detection.
        self.frames = deque(maxlen=90)

    # =========================================================
    # BASIC FUNCTIONS
    # =========================================================

    def calculate_angle(self, a, b, c):
        try:
            angle = math.degrees(
                math.atan2(
                    c.y - b.y,
                    c.x - b.x
                )
                -
                math.atan2(
                    a.y - b.y,
                    a.x - b.x
                )
            )

            angle = abs(angle)

            if angle > 180:
                angle = 360 - angle

            return angle

        except Exception:
            return None

    def get_landmark(self, landmarks, index):
        if landmarks is None:
            return None

        if index < 0 or index >= len(landmarks):
            return None

        return landmarks[index]

    def average(self, values):
        values = [
            v for v in values
            if v is not None
        ]

        if not values:
            return None

        return sum(values) / len(values)

    def value_range(self, values):
        values = [
            v for v in values
            if v is not None
        ]

        if len(values) < 2:
            return 0

        return max(values) - min(values)

    # =========================================================
    # FRAME ANALYSIS
    # =========================================================

    def analyze_frame(self, landmarks):

        if not landmarks:
            return None

        # MediaPipe Pose landmarks
        LEFT_SHOULDER = 11
        RIGHT_SHOULDER = 12

        LEFT_ELBOW = 13
        RIGHT_ELBOW = 14

        LEFT_WRIST = 15
        RIGHT_WRIST = 16

        LEFT_HIP = 23
        RIGHT_HIP = 24

        LEFT_KNEE = 25
        RIGHT_KNEE = 26

        LEFT_ANKLE = 27
        RIGHT_ANKLE = 28

        left_shoulder = self.get_landmark(
            landmarks, LEFT_SHOULDER
        )

        right_shoulder = self.get_landmark(
            landmarks, RIGHT_SHOULDER
        )

        left_elbow = self.get_landmark(
            landmarks, LEFT_ELBOW
        )

        right_elbow = self.get_landmark(
            landmarks, RIGHT_ELBOW
        )

        left_wrist = self.get_landmark(
            landmarks, LEFT_WRIST
        )

        right_wrist = self.get_landmark(
            landmarks, RIGHT_WRIST
        )

        left_hip = self.get_landmark(
            landmarks, LEFT_HIP
        )

        right_hip = self.get_landmark(
            landmarks, RIGHT_HIP
        )

        left_knee = self.get_landmark(
            landmarks, LEFT_KNEE
        )

        right_knee = self.get_landmark(
            landmarks, RIGHT_KNEE
        )

        left_ankle = self.get_landmark(
            landmarks, LEFT_ANKLE
        )

        right_ankle = self.get_landmark(
            landmarks, RIGHT_ANKLE
        )

        # =====================================================
        # KNEE ANGLES
        # =====================================================

        left_knee_angle = None
        right_knee_angle = None

        if left_hip and left_knee and left_ankle:
            left_knee_angle = self.calculate_angle(
                left_hip,
                left_knee,
                left_ankle
            )

        if right_hip and right_knee and right_ankle:
            right_knee_angle = self.calculate_angle(
                right_hip,
                right_knee,
                right_ankle
            )

        # =====================================================
        # ELBOW ANGLES
        # =====================================================

        left_elbow_angle = None
        right_elbow_angle = None

        if left_shoulder and left_elbow and left_wrist:
            left_elbow_angle = self.calculate_angle(
                left_shoulder,
                left_elbow,
                left_wrist
            )

        if right_shoulder and right_elbow and right_wrist:
            right_elbow_angle = self.calculate_angle(
                right_shoulder,
                right_elbow,
                right_wrist
            )

        # =====================================================
        # WRIST -> SHOULDER DISTANCE
        #
        # Very important for distinguishing curls from running.
        # =====================================================

        left_wrist_shoulder_distance = None
        right_wrist_shoulder_distance = None

        if left_wrist and left_shoulder:
            left_wrist_shoulder_distance = math.sqrt(
                (
                    left_wrist.x -
                    left_shoulder.x
                ) ** 2
                +
                (
                    left_wrist.y -
                    left_shoulder.y
                ) ** 2
            )

        if right_wrist and right_shoulder:
            right_wrist_shoulder_distance = math.sqrt(
                (
                    right_wrist.x -
                    right_shoulder.x
                ) ** 2
                +
                (
                    right_wrist.y -
                    right_shoulder.y
                ) ** 2
            )

        # =====================================================
        # KNEE DIFFERENCE
        # =====================================================

        knee_difference = None

        if (
            left_knee_angle is not None
            and right_knee_angle is not None
        ):
            knee_difference = abs(
                left_knee_angle -
                right_knee_angle
            )

        # =====================================================
        # ELBOW DIFFERENCE
        # =====================================================

        elbow_difference = None

        if (
            left_elbow_angle is not None
            and right_elbow_angle is not None
        ):
            elbow_difference = abs(
                left_elbow_angle -
                right_elbow_angle
            )

        # =====================================================
        # FOOT SEPARATION
        # =====================================================

        foot_separation = None

        if left_ankle and right_ankle:

            foot_separation = math.sqrt(
                (
                    left_ankle.x -
                    right_ankle.x
                ) ** 2
                +
                (
                    left_ankle.y -
                    right_ankle.y
                ) ** 2
            )

        # =====================================================
        # SHOULDER WIDTH
        # =====================================================

        shoulder_width = None

        if left_shoulder and right_shoulder:

            shoulder_width = math.sqrt(
                (
                    left_shoulder.x -
                    right_shoulder.x
                ) ** 2
                +
                (
                    left_shoulder.y -
                    right_shoulder.y
                ) ** 2
            )

        # =====================================================
        # TORSO RATIO
        # =====================================================

        torso_ratio = None

        if (
            left_shoulder
            and left_hip
            and shoulder_width
            and shoulder_width > 0.001
        ):

            torso_height = math.sqrt(
                (
                    left_shoulder.x -
                    left_hip.x
                ) ** 2
                +
                (
                    left_shoulder.y -
                    left_hip.y
                ) ** 2
            )

            torso_ratio = (
                torso_height /
                shoulder_width
            )

        # =====================================================
        # SAVE FRAME
        # =====================================================

        frame = {

            "left_knee_angle":
                left_knee_angle,

            "right_knee_angle":
                right_knee_angle,

            "left_elbow_angle":
                left_elbow_angle,

            "right_elbow_angle":
                right_elbow_angle,

            "knee_difference":
                knee_difference,

            "elbow_difference":
                elbow_difference,

            "foot_separation":
                foot_separation,

            "shoulder_width":
                shoulder_width,

            "torso_ratio":
                torso_ratio,

            "left_knee_y":
                left_knee.y
                if left_knee else None,

            "right_knee_y":
                right_knee.y
                if right_knee else None,

            "left_ankle_y":
                left_ankle.y
                if left_ankle else None,

            "right_ankle_y":
                right_ankle.y
                if right_ankle else None,

            "left_ankle_x":
                left_ankle.x
                if left_ankle else None,

            "right_ankle_x":
                right_ankle.x
                if right_ankle else None,

            "left_wrist_y":
                left_wrist.y
                if left_wrist else None,

            "right_wrist_y":
                right_wrist.y
                if right_wrist else None,

            "left_wrist_x":
                left_wrist.x
                if left_wrist else None,

            "right_wrist_x":
                right_wrist.x
                if right_wrist else None,

            "left_wrist_shoulder_distance":
                left_wrist_shoulder_distance,

            "right_wrist_shoulder_distance":
                right_wrist_shoulder_distance,

            "left_shoulder_y":
                left_shoulder.y
                if left_shoulder else None,

            "right_shoulder_y":
                right_shoulder.y
                if right_shoulder else None,

            "left_hip_y":
                left_hip.y
                if left_hip else None,

            "right_hip_y":
                right_hip.y
                if right_hip else None,
        }

        self.frames.append(frame)

        return frame

    # =========================================================
    # SQUAT
    # =========================================================

    def squat_score(self):

        if len(self.frames) < 20:
            return 0

        left = [
            f["left_knee_angle"]
            for f in self.frames
            if f["left_knee_angle"] is not None
        ]

        right = [
            f["right_knee_angle"]
            for f in self.frames
            if f["right_knee_angle"] is not None
        ]

        if not left or not right:
            return 0

        left_range = self.value_range(left)
        right_range = self.value_range(right)

        knee_diff = self.average([
            f["knee_difference"]
            for f in self.frames
            if f["knee_difference"] is not None
        ])

        minimum_angle = min(
            min(left),
            min(right)
        )

        score = 0

        # Both knees must move
        if left_range > 30:
            score += 20

        if right_range > 30:
            score += 20

        # Squat is usually symmetrical
        if (
            knee_diff is not None
            and knee_diff < 25
        ):
            score += 25

        # Actual squat depth
        if 70 <= minimum_angle <= 115:
            score += 25

        elif 115 < minimum_angle <= 135:
            score += 10

        # Similar movement both legs
        if abs(
            left_range -
            right_range
        ) < 35:
            score += 10

        return min(score, 100)

    # =========================================================
    # LUNGE
    # =========================================================

    def lunge_score(self):

        if len(self.frames) < 20:
            return 0

        left = [
            f["left_knee_angle"]
            for f in self.frames
            if f["left_knee_angle"] is not None
        ]

        right = [
            f["right_knee_angle"]
            for f in self.frames
            if f["right_knee_angle"] is not None
        ]

        feet = [
            f["foot_separation"]
            for f in self.frames
            if f["foot_separation"] is not None
        ]

        if not left or not right:
            return 0

        left_range = self.value_range(left)
        right_range = self.value_range(right)

        knee_diff = self.average([
            f["knee_difference"]
            for f in self.frames
            if f["knee_difference"] is not None
        ])

        average_feet = self.average(feet)

        score = 0

        # Asymmetric legs
        if knee_diff is not None:

            if knee_diff > 25:
                score += 30

            if knee_diff > 40:
                score += 15

        # Knee movement
        if left_range > 30:
            score += 15

        if right_range > 30:
            score += 15

        # Feet separated
        if (
            average_feet is not None
            and average_feet > 0.15
        ):
            score += 20

        # Strongly symmetrical movement is more squat-like
        if (
            knee_diff is not None
            and knee_diff < 15
        ):
            score -= 25

        return max(
            0,
            min(score, 100)
        )

    # =========================================================
    # BICEP CURL
    # =========================================================

    def bicep_score(self):

        if len(self.frames) < 20:
            return 0

        left_elbows = [
            f["left_elbow_angle"]
            for f in self.frames
            if f["left_elbow_angle"] is not None
        ]

        right_elbows = [
            f["right_elbow_angle"]
            for f in self.frames
            if f["right_elbow_angle"] is not None
        ]

        left_distances = [
            f["left_wrist_shoulder_distance"]
            for f in self.frames
            if f["left_wrist_shoulder_distance"]
            is not None
        ]

        right_distances = [
            f["right_wrist_shoulder_distance"]
            for f in self.frames
            if f["right_wrist_shoulder_distance"]
            is not None
        ]

        if (
            not left_elbows
            and not right_elbows
        ):
            return 0

        score = 0

        # -----------------------------------------------------
        # Elbow flexion
        # -----------------------------------------------------

        left_range = self.value_range(
            left_elbows
        )

        right_range = self.value_range(
            right_elbows
        )

        maximum_elbow_range = max(
            left_range,
            right_range
        )

        if maximum_elbow_range > 40:
            score += 20

        if maximum_elbow_range > 70:
            score += 15

        # -----------------------------------------------------
        # Wrist should move toward shoulder
        # -----------------------------------------------------

        wrist_distance_range = max(
            self.value_range(left_distances),
            self.value_range(right_distances)
        )

        if wrist_distance_range > 0.08:
            score += 20

        if wrist_distance_range > 0.15:
            score += 15

        # -----------------------------------------------------
        # Bent elbow should actually get fairly small
        # -----------------------------------------------------

        minimum_elbow = min(
            left_elbows + right_elbows
        )

        if minimum_elbow < 90:
            score += 10

        if minimum_elbow < 70:
            score += 10

        # -----------------------------------------------------
        # Bicep curls normally keep legs relatively stable
        # -----------------------------------------------------

        knee_ranges = []

        for key in [
            "left_knee_angle",
            "right_knee_angle"
        ]:

            values = [
                f[key]
                for f in self.frames
                if f[key] is not None
            ]

            if values:
                knee_ranges.append(
                    self.value_range(values)
                )

        if knee_ranges:

            average_knee_range = sum(
                knee_ranges
            ) / len(knee_ranges)

            if average_knee_range < 30:
                score += 10

            elif average_knee_range > 70:
                score -= 20

        return max(
            0,
            min(score, 100)
        )

    # =========================================================
    # PUSH UP
    # =========================================================

    def pushup_score(self):

        if len(self.frames) < 20:
            return 0

        elbows = []

        for f in self.frames:

            if f["left_elbow_angle"] is not None:
                elbows.append(
                    f["left_elbow_angle"]
                )

            if f["right_elbow_angle"] is not None:
                elbows.append(
                    f["right_elbow_angle"]
                )

        if not elbows:
            return 0

        elbow_range = self.value_range(
            elbows
        )

        minimum_elbow = min(elbows)

        score = 0

        if elbow_range > 40:
            score += 30

        if elbow_range > 70:
            score += 20

        if minimum_elbow < 110:
            score += 15

        if minimum_elbow < 90:
            score += 10

        # Push-up requires substantial body horizontal posture
        torso_values = [
            f["torso_ratio"]
            for f in self.frames
            if f["torso_ratio"] is not None
        ]

        if torso_values:

            torso_average = self.average(
                torso_values
            )

            if torso_average < 2.5:
                score += 25

        return min(score, 100)

    # =========================================================
    # RUNNING
    # =========================================================

    def running_score(self):

        if len(self.frames) < 30:
            return 0

        score = 0

        # -----------------------------------------------------
        # 1. KNEE VERTICAL MOVEMENT
        # -----------------------------------------------------

        left_knee_y = [
            f["left_knee_y"]
            for f in self.frames
            if f["left_knee_y"] is not None
        ]

        right_knee_y = [
            f["right_knee_y"]
            for f in self.frames
            if f["right_knee_y"] is not None
        ]

        left_ankle_y = [
            f["left_ankle_y"]
            for f in self.frames
            if f["left_ankle_y"] is not None
        ]

        right_ankle_y = [
            f["right_ankle_y"]
            for f in self.frames
            if f["right_ankle_y"] is not None
        ]

        if (
            not left_knee_y
            or not right_knee_y
        ):
            return 0

        left_knee_range = self.value_range(
            left_knee_y
        )

        right_knee_range = self.value_range(
            right_knee_y
        )

        if left_knee_range > 0.04:
            score += 15

        if right_knee_range > 0.04:
            score += 15

        # -----------------------------------------------------
        # 2. ANKLE MOVEMENT
        # -----------------------------------------------------

        left_ankle_range = self.value_range(
            left_ankle_y
        )

        right_ankle_range = self.value_range(
            right_ankle_y
        )

        if left_ankle_range > 0.04:
            score += 10

        if right_ankle_range > 0.04:
            score += 10

        # -----------------------------------------------------
        # 3. ALTERNATING KNEE MOVEMENT
        #
        # Running should have opposite movement of legs.
        # -----------------------------------------------------

        opposite_count = 0
        movement_count = 0

        for i in range(1, len(self.frames)):

            previous = self.frames[i - 1]
            current = self.frames[i]

            if (
                previous["left_knee_y"] is None
                or current["left_knee_y"] is None
                or previous["right_knee_y"] is None
                or current["right_knee_y"] is None
            ):
                continue

            left_delta = (
                current["left_knee_y"]
                -
                previous["left_knee_y"]
            )

            right_delta = (
                current["right_knee_y"]
                -
                previous["right_knee_y"]
            )

            # Ignore tiny tracking noise
            if (
                abs(left_delta) < 0.003
                and abs(right_delta) < 0.003
            ):
                continue

            movement_count += 1

            if (
                left_delta *
                right_delta
                < 0
            ):
                opposite_count += 1

        alternating_ratio = 0

        if movement_count > 0:
            alternating_ratio = (
                opposite_count /
                movement_count
            )

        if alternating_ratio > 0.20:
            score += 15

        if alternating_ratio > 0.35:
            score += 15

        if alternating_ratio > 0.50:
            score += 10

        # -----------------------------------------------------
        # 4. FOOT SEPARATION CHANGES
        # -----------------------------------------------------

        foot_values = [
            f["foot_separation"]
            for f in self.frames
            if f["foot_separation"] is not None
        ]

        foot_range = self.value_range(
            foot_values
        )

        if foot_range > 0.05:
            score += 10

        # -----------------------------------------------------
        # 5. KNEE ANGLE MOVEMENT
        # -----------------------------------------------------

        left_angles = [
            f["left_knee_angle"]
            for f in self.frames
            if f["left_knee_angle"] is not None
        ]

        right_angles = [
            f["right_knee_angle"]
            for f in self.frames
            if f["right_knee_angle"] is not None
        ]

        left_angle_range = self.value_range(
            left_angles
        )

        right_angle_range = self.value_range(
            right_angles
        )

        if left_angle_range > 30:
            score += 5

        if right_angle_range > 30:
            score += 5

        return min(score, 100)

    # =========================================================
    # RUNNING OVERRIDE
    #
    # This is important:
    # if strong alternating leg motion exists,
    # don't allow arm movement to turn running into
    # Bicep Curl.
    # =========================================================

    def is_running(self):

        if len(self.frames) < 30:
            return False

        left_knee = [
            f["left_knee_y"]
            for f in self.frames
            if f["left_knee_y"] is not None
        ]

        right_knee = [
            f["right_knee_y"]
            for f in self.frames
            if f["right_knee_y"] is not None
        ]

        if (
            len(left_knee) < 20
            or len(right_knee) < 20
        ):
            return False

        left_range = self.value_range(
            left_knee
        )

        right_range = self.value_range(
            right_knee
        )

        opposite = 0
        total = 0

        for i in range(1, len(self.frames)):

            p = self.frames[i - 1]
            c = self.frames[i]

            if (
                p["left_knee_y"] is None
                or c["left_knee_y"] is None
                or p["right_knee_y"] is None
                or c["right_knee_y"] is None
            ):
                continue

            ld = (
                c["left_knee_y"] -
                p["left_knee_y"]
            )

            rd = (
                c["right_knee_y"] -
                p["right_knee_y"]
            )

            if (
                abs(ld) < 0.003
                and abs(rd) < 0.003
            ):
                continue

            total += 1

            if ld * rd < 0:
                opposite += 1

        if total == 0:
            return False

        alternating_ratio = (
            opposite / total
        )

        return (
            left_range > 0.04
            and right_range > 0.04
            and alternating_ratio > 0.20
        )

    # =========================================================
    # FINAL CLASSIFICATION
    # =========================================================

    def get_result(self):

        if len(self.frames) < 20:

            return {
                "exercise": "Unknown",
                "confidence": 0,
                "scores": {}
            }

        scores = {
            "Squat":
                self.squat_score(),

            "Lunge":
                self.lunge_score(),

            "Bicep Curl":
                self.bicep_score(),

            "Push Up":
                self.pushup_score(),

            "Running":
                self.running_score()
        }

        # -----------------------------------------------------
        # RUNNING HAS TEMPORAL PRIORITY
        # -----------------------------------------------------

        if self.is_running():

            running_confidence = scores["Running"]

            if running_confidence >= 40:

                return {
                    "exercise": "Running",
                    "confidence": running_confidence,
                    "scores": scores
                }

        # -----------------------------------------------------
        # OTHERWISE SELECT BEST EXERCISE
        # -----------------------------------------------------

        detected_exercise = max(
            scores,
            key=scores.get
        )

        confidence = scores[
            detected_exercise
        ]

        # -----------------------------------------------------
        # Don't make weak guesses
        # -----------------------------------------------------

        if confidence < 35:

            return {
                "exercise": "Unknown",
                "confidence": confidence,
                "scores": scores
            }

        return {
            "exercise": detected_exercise,
            "confidence": confidence,
            "scores": scores
        }
