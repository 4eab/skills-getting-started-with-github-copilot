import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesAPI:
    """Test suite for Activities API endpoints using AAA pattern"""

    def test_get_activities_success(self):
        """Test GET /activities returns all activities"""
        # Arrange - no setup needed, using default data

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        # Check structure of first activity
        first_activity = next(iter(data.values()))
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)

    def test_signup_success(self):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity_name}" in data["message"]

    def test_signup_duplicate_email(self):
        """Test signup fails when email is already registered"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in initial data

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_invalid_activity(self):
        """Test signup fails for non-existent activity"""
        # Arrange
        activity_name = "NonExistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_max_capacity(self):
        """Test signup fails when activity reaches max capacity"""
        # Arrange - use an activity with low max_participants
        activity_name = "Chess Club"  # max_participants: 12
        # Fill to capacity (initially has 2, add 10 more)
        for i in range(10):
            email = f"student{i}@mergington.edu"
            client.post(f"/activities/{activity_name}/signup?email={email}")

        # Now try to add one more
        email = "overflow@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "maximum capacity" in data["detail"]

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already in initial data

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Unregistered {email} from {activity_name}" in data["message"]

    def test_unregister_not_registered(self):
        """Test unregistration fails when email is not registered"""
        # Arrange
        activity_name = "Programming Class"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"]

    def test_unregister_invalid_activity(self):
        """Test unregistration fails for non-existent activity"""
        # Arrange
        activity_name = "Invalid Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_empty_participants(self):
        """Test unregistration when participants list becomes empty"""
        # Arrange - create a test activity with one participant
        # Since we can't modify global data easily, use an existing one and remove all
        activity_name = "Art Club"  # Initially has 2 participants
        emails = ["ava@mergington.edu", "sophia@mergington.edu"]

        # Remove both
        for email in emails:
            client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Verify empty
        response = client.get("/activities")
        data = response.json()
        assert len(data[activity_name]["participants"]) == 0

        # Now try to remove from empty list
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404  # Not registered