import src.app as app_module


def test_get_activities(client):
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_signup_adds_participant(client):
    activity = "Chess Club"
    email = "new.student@mergington.edu"

    # Arrange
    initial_response = client.get("/activities")
    assert email not in initial_response.json()[activity]["participants"]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    activity_response = client.get("/activities")
    assert email in activity_response.json()[activity]["participants"]


def test_duplicate_signup_returns_400(client):
    activity = "Chess Club"
    email = "duplicate.student@mergington.edu"

    # Arrange
    first = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert first.status_code == 200

    # Act
    second = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert second.status_code == 400
    assert second.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant(client):
    activity = "Programming Class"
    email = "remove.student@mergington.edu"

    # Arrange
    initial_response = client.get("/activities")
    participants = initial_response.json()[activity]["participants"]
    if email not in participants:
        signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert signup_response.status_code == 200

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    final_response = client.get("/activities")
    assert email not in final_response.json()[activity]["participants"]


def test_remove_nonexistent_returns_404(client):
    activity = "Tennis Club"
    email = "not.registered@mergington.edu"

    # Arrange
    initial_response = client.get("/activities")
    assert email not in initial_response.json()[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_availability_changes(client):
    activity = "Basketball Team"
    email = "availability.student@mergington.edu"

    # Arrange
    initial_response = client.get("/activities")
    initial_activity = initial_response.json()[activity]
    initial_spots = initial_activity["max_participants"] - len(initial_activity["participants"])

    # Act
    signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert signup_response.status_code == 200
    after_signup = client.get("/activities").json()[activity]
    assert after_signup["max_participants"] - len(after_signup["participants"]) == initial_spots - 1

    # Act
    remove_response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert remove_response.status_code == 200
    after_remove = client.get("/activities").json()[activity]
    assert after_remove["max_participants"] - len(after_remove["participants"]) == initial_spots
