from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_get_activities_returns_catalog():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"]
    assert "max_participants" in data["Chess Club"]


def test_signup_for_activity_adds_student():
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    activity = client.get("/activities").json()[activity_name]
    if email in activity["participants"]:
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in client.get("/activities").json()[activity_name]["participants"]

    client.delete(f"/activities/{activity_name}/signup?email={email}")


def test_signup_rejects_duplicate_registration():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unknown_activity_returns_404():
    response = client.post("/activities/Not Real/signup?email=test@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_removes_signup():
    activity_name = "Chess Club"
    email = "test-remove@mergington.edu"

    client.post(f"/activities/{activity_name}/signup?email={email}")
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]
