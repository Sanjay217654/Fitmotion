import math


class LandmarkFilter:
    """
    Handles landmark reliability and automatically selects
    the more reliable side of the body.

    This prevents the system from always depending on
    only the left side.
    """

    VISIBILITY_THRESHOLD = 0.35

    def visibility(self, landmark):
        if landmark is None:
            return 0.0

        value = getattr(
            landmark,
            "visibility",
            1.0
        )

        if value is None:
            value = 1.0

        return max(
            0.0,
            min(1.0, float(value))
        )

    def is_reliable(
        self,
        landmark,
        threshold=None
    ):
        if landmark is None:
            return False

        if threshold is None:
            threshold = (
                self.VISIBILITY_THRESHOLD
            )

        return (
            self.visibility(landmark)
            >= threshold
        )

    def average_visibility(
        self,
        landmarks
    ):
        if not landmarks:
            return 0.0

        values = [
            self.visibility(point)
            for point in landmarks
            if point is not None
        ]

        if not values:
            return 0.0

        return sum(values) / len(values)

    def calculate_group_confidence(self, landmarks):
        """Compatibility name for a joint's aggregate landmark confidence."""
        return self.average_visibility(landmarks)

    def side_score(
        self,
        landmarks,
        indices
    ):
        if not landmarks:
            return 0.0

        points = []

        for index in indices:

            if index >= len(landmarks):
                return 0.0

            point = landmarks[index]

            if point is None:
                return 0.0

            points.append(point)

        return self.average_visibility(
            points
        )

    def choose_side(
        self,
        landmarks,
        left_indices,
        right_indices
    ):
        """
        Compare left and right body landmarks.

        Returns:
            side
            left confidence
            right confidence
        """

        left_score = self.side_score(
            landmarks,
            left_indices
        )

        right_score = self.side_score(
            landmarks,
            right_indices
        )

        # Neither side is reliable.
        if (
            left_score <
            self.VISIBILITY_THRESHOLD
            and
            right_score <
            self.VISIBILITY_THRESHOLD
        ):
            return (
                None,
                left_score,
                right_score
            )

        # Right side is more reliable.
        if right_score > left_score:
            return (
                "right",
                left_score,
                right_score
            )

        # Left side is more reliable.
        return (
            "left",
            left_score,
            right_score
        )

    def required_landmarks_visible(
        self,
        landmarks,
        indices,
        threshold=0.25
    ):
        """
        Checks whether the landmarks required by
        the selected exercise are usable.
        """

        if not landmarks:
            return False

        for index in indices:

            if index >= len(landmarks):
                return False

            landmark = landmarks[index]

            if not self.is_reliable(
                landmark,
                threshold
            ):
                return False

        return True

    def body_visibility(
        self,
        landmarks
    ):
        """
        Calculates overall landmark visibility.

        This is informational and should not be used
        as a hard requirement for the user.
        """

        if not landmarks:
            return 0.0

        values = []

        for point in landmarks:

            values.append(
                self.visibility(point)
            )

        if not values:
            return 0.0

        return sum(values) / len(values)

    def body_size(
        self,
        landmarks
    ):
        """
        Estimates the visible body size.

        Used for scale information rather than
        forcing the user to move closer/farther.
        """

        if not landmarks:
            return 0.0

        visible = [
            point
            for point in landmarks
            if self.is_reliable(point)
        ]

        if len(visible) < 2:
            return 0.0

        xs = [
            point.x
            for point in visible
        ]

        ys = [
            point.y
            for point in visible
        ]

        width = (
            max(xs) -
            min(xs)
        )

        height = (
            max(ys) -
            min(ys)
        )

        return math.sqrt(
            width ** 2 +
            height ** 2
        )


# Shared instance
landmark_filter = LandmarkFilter()
