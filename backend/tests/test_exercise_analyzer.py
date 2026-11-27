from app.services.exercise_analyzers import ExerciseAnalyzer
from app.services.movement_smoothing import create_angle_smoother


class Landmark:
    def __init__(self, x=0.5, y=0.5, z=0.0, visibility=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility


def squat_landmarks(position: str) -> list[Landmark]:
    landmarks = [Landmark(visibility=0.1) for _ in range(33)]
    if position == "up":
        hip, knee, ankle = Landmark(0.48, 0.25), Landmark(0.5, 0.5), Landmark(0.52, 0.75)
    else:
        hip, knee, ankle = Landmark(0.25, 0.5), Landmark(0.5, 0.5), Landmark(0.5, 0.75)
    landmarks[23], landmarks[25], landmarks[27] = hip, knee, ankle
    return landmarks


def test_squat_counts_one_complete_cycle_not_every_up_frame() -> None:
    analyzer = ExerciseAnalyzer("Squat")
    analyzer.reliability = 100.0

    # Three stable frames are required for normal exercises. This simulates
    # standing -> bottom -> standing and then extra standing frames.
    for timestamp in (0.0, 0.1, 0.2):
        analyzer._handle_standard_exercise(170.0, timestamp)
    for timestamp in (0.3, 0.4, 0.5):
        analyzer._handle_standard_exercise(105.0, timestamp)
    for timestamp in (0.6, 0.7, 0.8, 0.9, 1.0):
        analyzer._handle_standard_exercise(170.0, timestamp)

    assert analyzer.reps == 1


def test_live_snapshot_has_api_contract_fields() -> None:
    result = ExerciseAnalyzer("Squat").get_result()
    assert result["reps"] == 0
    assert result["left_confidence"] == 0.0
    assert result["right_confidence"] == 0.0


def test_short_angle_jitter_does_not_change_state() -> None:
    analyzer = ExerciseAnalyzer("Squat")
    analyzer._handle_standard_exercise(170.0, 0.0)
    analyzer._handle_standard_exercise(170.0, 0.05)
    analyzer._handle_standard_exercise(110.0, 0.10)
    analyzer._handle_standard_exercise(170.0, 0.15)

    assert analyzer.state == "UP"
    assert analyzer.reps == 0


def test_angle_smoother_exposes_update_interface() -> None:
    smoother = create_angle_smoother()
    assert smoother.update(100.0) == 100.0
    assert smoother.update(120.0) == 110.0


def test_pose_landmark_path_counts_one_squat_cycle() -> None:
    analyzer = ExerciseAnalyzer("Squat")
    timestamp = 0.0
    for position, frames in (("up", 6), ("down", 8), ("up", 8)):
        for _ in range(frames):
            analyzer.analyze_frame(squat_landmarks(position), timestamp)
            timestamp += 0.1

    assert analyzer.reps == 1


def test_running_counts_a_stride_without_missing_score_config() -> None:
    analyzer = ExerciseAnalyzer("Running")
    analyzer.reliability = 100.0

    # Extended knee -> flexed knee -> extended knee is one selected-leg stride.
    for timestamp, angle in (
        (0.0, 150.0), (0.1, 150.0),
        (0.2, 95.0), (0.3, 95.0),
        (0.4, 150.0), (0.5, 150.0),
    ):
        analyzer._handle_running(angle, timestamp)

    assert analyzer.reps == 1
    assert analyzer.technique_score >= 0
