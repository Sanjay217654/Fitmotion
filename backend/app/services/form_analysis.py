class SquatFormAnalyzer:

    def analyze(self, knee_angle):
        """
        Analyze squat form using knee angle.
        """

        if knee_angle < 70:
            return {
                "status": "incorrect",
                "feedback": "Do not bend your knee too much."
            }

        elif 70 <= knee_angle < 100:
            return {
                "status": "correct",
                "feedback": "Good squat depth."
            }

        elif 100 <= knee_angle < 160:
            return {
                "status": "moving",
                "feedback": "Keep going."
            }

        else:
            return {
                "status": "standing",
                "feedback": "Good starting position."
            }