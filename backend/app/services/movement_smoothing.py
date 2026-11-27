from types import SimpleNamespace


class LandmarkSmoother:
    """
    Smooths MediaPipe landmark movement over time.

    MediaPipe landmarks can move slightly from frame to frame
    even when the person is relatively still.

    Smoothing reduces that jitter before angle calculation.
    """

    def __init__(
        self,
        alpha=0.55
    ):
        self.alpha = alpha
        self.previous = {}

    def reset(self):
        """
        Clear previous landmark data.
        """

        self.previous.clear()

    def smooth_point(
        self,
        index,
        landmark
    ):
        if landmark is None:
            return None

        # -----------------------------------------
        # Current landmark
        # -----------------------------------------

        x = float(
            landmark.x
        )

        y = float(
            landmark.y
        )

        z = float(
            getattr(
                landmark,
                "z",
                0.0
            )
        )

        visibility = float(
            getattr(
                landmark,
                "visibility",
                1.0
            )
            or 1.0
        )

        # -----------------------------------------
        # Previous landmark
        # -----------------------------------------

        previous = self.previous.get(
            index
        )

        # First frame.
        if previous is None:

            smoothed = (
                x,
                y,
                z,
                visibility
            )

        else:

            previous_x = previous[0]
            previous_y = previous[1]
            previous_z = previous[2]
            previous_visibility = previous[3]

            # -------------------------------------
            # Exponential moving average
            # -------------------------------------

            smoothed_x = (
                self.alpha * x
                +
                (1 - self.alpha)
                * previous_x
            )

            smoothed_y = (
                self.alpha * y
                +
                (1 - self.alpha)
                * previous_y
            )

            smoothed_z = (
                self.alpha * z
                +
                (1 - self.alpha)
                * previous_z
            )

            smoothed_visibility = (
                self.alpha * visibility
                +
                (1 - self.alpha)
                * previous_visibility
            )

            smoothed = (
                smoothed_x,
                smoothed_y,
                smoothed_z,
                smoothed_visibility
            )

        # -----------------------------------------
        # Store for next frame
        # -----------------------------------------

        self.previous[index] = smoothed

        # -----------------------------------------
        # Return MediaPipe-like landmark
        # -----------------------------------------

        return SimpleNamespace(
            x=smoothed[0],
            y=smoothed[1],
            z=smoothed[2],
            visibility=smoothed[3]
        )

    def smooth(
        self,
        landmarks
    ):
        """
        Smooth all landmarks in the current frame.
        """

        if not landmarks:
            return []

        result = []

        for index, landmark in enumerate(
            landmarks
        ):

            smoothed_landmark = (
                self.smooth_point(
                    index,
                    landmark
                )
            )

            result.append(
                smoothed_landmark
            )

        return result

    def update(self, landmarks):
        """Compatibility entry point used by the live and video analyzers."""
        return self.smooth(landmarks)


class MovementSmoother:
    """
    Smooths calculated joint angles.

    This prevents tiny angle fluctuations from
    immediately changing exercise state.
    """

    def __init__(
        self,
        alpha=0.50
    ):
        self.alpha = alpha
        self.previous_angle = None

    def reset(self):
        self.previous_angle = None

    def smooth_angle(
        self,
        angle
    ):
        if angle is None:

            return self.previous_angle

        # First valid angle.
        if self.previous_angle is None:

            self.previous_angle = angle

            return angle

        # -----------------------------------------
        # Exponential moving average
        # -----------------------------------------

        smoothed_angle = (
            self.alpha * angle
            +
            (1 - self.alpha)
            * self.previous_angle
        )

        self.previous_angle = (
            smoothed_angle
        )

        return smoothed_angle

    def update(self, angle):
        """Compatibility entry point used by ExerciseAnalyzer."""
        return self.smooth_angle(angle)


def create_smoother():
    """
    Create a landmark smoother.
    """

    return LandmarkSmoother(
        alpha=0.55
    )


def create_angle_smoother():
    """
    Create a joint-angle smoother.
    """

    return MovementSmoother(
        alpha=0.50
    )
