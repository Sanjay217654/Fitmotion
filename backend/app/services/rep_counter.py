class SquatRepCounter:

    def __init__(self):
        self.reps = 0
        self.correct_reps = 0
        self.incorrect_reps = 0

        self.state = "UP"

        self.min_angle = 120
        self.max_angle = 160

        self.lowest_angle = 180

    def update(self, knee_angle):

        # Track the deepest point of the current squat
        if self.state == "DOWN":
            self.lowest_angle = min(
                self.lowest_angle,
                knee_angle
            )

        # Person goes from standing to squat
        if (
            knee_angle < self.min_angle
            and self.state == "UP"
        ):
            self.state = "DOWN"
            self.lowest_angle = knee_angle

        # Person returns to standing
        elif (
            knee_angle > self.max_angle
            and self.state == "DOWN"
        ):
            self.reps += 1

            # Check squat depth
            if self.lowest_angle <= self.min_angle:
                self.correct_reps += 1
            else:
                self.incorrect_reps += 1

            self.state = "UP"
            self.lowest_angle = 180

        return {
            "reps": self.reps,
            "correct_reps": self.correct_reps,
            "incorrect_reps": self.incorrect_reps,
            "state": self.state
        }