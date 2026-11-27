def calculate_squat_score(
    minimum_angle,
    average_angle
):
    """
    Calculate a simple squat technique score.

    This is an initial project-level
    scoring rule.
    """

    if minimum_angle is None:
        return 0

    # Very shallow squat
    if minimum_angle > 120:
        return 50

    # Good squat depth
    elif 70 <= minimum_angle <= 110:
        return 100

    # Very deep squat
    elif minimum_angle < 60:
        return 80

    # Acceptable range
    else:
        return 85


def generate_feedback(minimum_angle):

    if minimum_angle is None:
        return "No squat movement detected."

    if minimum_angle > 120:
        return "Go lower during the squat."

    if minimum_angle < 60:
        return (
            "You are going very deep. "
            "Maintain controlled movement."
        )

    if 70 <= minimum_angle <= 110:
        return (
            "Good squat depth. "
            "Keep your movement controlled."
        )

    return (
        "Squat depth is acceptable. "
        "Keep your knees aligned and maintain control."
    )