def calculate_technique_score(knee_angle):
    """
    Simple squat technique score.
    Returns a value from 0 to 100.
    """

    if 70 <= knee_angle <= 100:
        return 100.0

    if 100 < knee_angle <= 120:
        return 90.0

    if 120 < knee_angle <= 150:
        return 75.0

    if 150 < knee_angle <= 180:
        return 85.0

    return 60.0