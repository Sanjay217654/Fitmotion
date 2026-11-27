from fastapi.testclient import TestClient


REGISTER = {
    "full_name": "Alex Morgan",
    "email": "alex@example.com",
    "password": "SecurePass2026",
    "confirm_password": "SecurePass2026",
    "age": 26,
    "gender": "Prefer not to say",
    "height_cm": 170,
    "weight_kg": 64,
    "sport": "Running",
    "fitness_level": "intermediate",
    "fitness_goal": "improve_fitness",
}


def test_register_login_and_protected_profile(client: TestClient) -> None:
    registration = client.post("/auth/register", json=REGISTER)
    assert registration.status_code == 201
    body = registration.json()
    assert body["user"]["email"] == "alex@example.com"
    assert "password_hash" not in body["user"]
    assert body["access_token"]

    duplicate = client.post("/auth/register", json=REGISTER)
    assert duplicate.status_code == 409

    login = client.post("/auth/login", json={"email": REGISTER["email"], "password": REGISTER["password"]})
    assert login.status_code == 200
    token = login.json()["access_token"]
    profile = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["sport"] == "Running"
    updated = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"fitness_goal": "build_strength", "weight_kg": 63.5},
    )
    assert updated.status_code == 200
    assert updated.json()["fitness_goal"] == "build_strength"


def test_invalid_login_and_invalid_password(client: TestClient) -> None:
    assert client.post("/auth/login", json={"email": "missing@example.com", "password": "wrong"}).status_code == 401
    invalid = {**REGISTER, "email": "invalid@example.com", "password": "onlyletters", "confirm_password": "onlyletters"}
    assert client.post("/auth/register", json=invalid).status_code == 422


def test_refresh_and_logout_revoke_access_token(client: TestClient) -> None:
    registration = client.post("/auth/register", json=REGISTER).json()
    access_token = registration["access_token"]
    refresh_token = registration["refresh_token"]
    refreshed = client.post("/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert refreshed.status_code == 200
    logout = client.post("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
    assert logout.status_code == 204
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"}).status_code == 401


def test_profile_image_validation(client: TestClient) -> None:
    token = client.post("/auth/register", json=REGISTER).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    rejected = client.post("/users/me/profile-image", headers=headers, files={"image": ("avatar.txt", b"text", "text/plain")})
    assert rejected.status_code == 415
