from fastapi.testclient import TestClient

from test_auth import REGISTER


def test_summary_is_scoped_to_the_authenticated_athlete(client: TestClient) -> None:
    registration = client.post("/auth/register", json=REGISTER).json()
    headers = {"Authorization": f"Bearer {registration['access_token']}"}
    workout = {
        "exercise": "Squat",
        "total_reps": 12,
        "correct_reps": 10,
        "incorrect_reps": 2,
        "technique_score": 82,
        "duration_seconds": 300,
    }
    assert client.post("/workouts", headers=headers, json=workout).status_code == 201
    second_workout = {**workout, "total_reps": 8, "technique_score": 78}
    assert client.post("/workouts", headers=headers, json=second_workout).status_code == 201
    summary = client.get("/analytics/summary", headers=headers)

    assert summary.status_code == 200
    body = summary.json()
    assert body["total_workouts"] == 2
    assert body["total_reps"] == 20
    assert body["average_technique_score"] == 80
    assert body["exercise_counts"] == {"Squat": 2}
    assert len(body["recent_workouts"]) == 2

    workout_id = body["recent_workouts"][0]["id"]
    assert client.delete(f"/workouts/{workout_id}", headers=headers).status_code == 204
    assert client.get("/analytics/summary", headers=headers).json()["total_workouts"] == 1
