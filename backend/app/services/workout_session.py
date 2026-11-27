import time


class WorkoutSession:

    def __init__(self, exercise="Squat"):
        self.exercise = exercise
        self.start_time = None
        self.end_time = None

        self.total_reps = 0
        self.correct_reps = 0
        self.incorrect_reps = 0

        self.technique_scores = []

    def start(self):
        self.start_time = time.time()

    def update(
        self,
        reps,
        form_status,
        technique_score
    ):
        # Detect when a new rep is completed
        if reps > self.total_reps:

            new_reps = reps - self.total_reps

            self.total_reps = reps

            # Count correct/incorrect completed reps
            if form_status == "correct":
                self.correct_reps += new_reps
            else:
                self.incorrect_reps += new_reps

            self.technique_scores.append(
                technique_score
            )

    def finish(self):
        self.end_time = time.time()

    def get_duration(self):
        if self.start_time is None:
            return 0

        end = self.end_time or time.time()

        return int(end - self.start_time)

    def get_average_score(self):
        if not self.technique_scores:
            return 0.0

        return round(
            sum(self.technique_scores)
            / len(self.technique_scores),
            2
        )

    def get_result(self):

        return {
            "exercise": self.exercise,
            "total_reps": self.total_reps,
            "correct_reps": self.correct_reps,
            "incorrect_reps": self.incorrect_reps,
            "technique_score": self.get_average_score(),
            "duration_seconds": self.get_duration()
        }