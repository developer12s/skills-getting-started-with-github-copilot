import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a clean state before each test"""
    activities.clear()
    activities.update({
        "Basketball": {
            "description": "Team sport focusing on basketball skills and competitive play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and participate in matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu"]
        },
        "Music Band": {
            "description": "Play instruments and perform in school concerts",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
    })
    yield
    # Cleanup after test
    activities.clear()


class TestGetActivities:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that getting activities returns status code 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that getting activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        data = response.json()
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert "Music Band" in data

    def test_get_activities_contains_correct_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_participants_list(self, client):
        """Test that participants are returned as a list"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data["Basketball"]["participants"], list)
        assert "alex@mergington.edu" in data["Basketball"]["participants"]

    def test_get_activities_music_band_has_two_participants(self, client):
        """Test that Music Band has the correct participants"""
        response = client.get("/activities")
        data = response.json()
        assert len(data["Music Band"]["participants"]) == 2
        assert "lucas@mergington.edu" in data["Music Band"]["participants"]
        assert "mia@mergington.edu" in data["Music Band"]["participants"]


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_returns_200(self, client):
        """Test that signup returns status code 200"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Basketball"]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up twice returns 400 error"""
        # Alex is already signed up for Basketball
        response = client.post(
            "/activities/Basketball/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_activity_name_with_spaces(self, client):
        """Test that activity names with spaces are handled correctly"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        # Verify the participant was added to the correct activity
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert "newstudent@mergington.edu" in data["Tennis Club"]["participants"]

    def test_signup_multiple_different_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multistudent@mergington.edu"
        client.post(f"/activities/Basketball/signup?email={email}")
        client.post(f"/activities/Tennis%20Club/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]
        assert email in data["Tennis Club"]["participants"]


class TestRemoveParticipant:
    """Test the POST /activities/{activity_name}/remove endpoint"""

    def test_remove_returns_200(self, client):
        """Test that remove returns status code 200"""
        response = client.post(
            "/activities/Basketball/remove?email=alex@mergington.edu"
        )
        assert response.status_code == 200

    def test_remove_returns_success_message(self, client):
        """Test that remove returns a success message"""
        response = client.post(
            "/activities/Basketball/remove?email=alex@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "alex@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]

    def test_remove_participant_actually_removes(self, client):
        """Test that remove actually removes the participant"""
        client.post("/activities/Basketball/remove?email=alex@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" not in data["Basketball"]["participants"]

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Test that removing from nonexistent activity returns 404"""
        response = client.post(
            "/activities/NonexistentActivity/remove?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removing nonexistent participant returns 404"""
        response = client.post(
            "/activities/Basketball/remove?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_activity_name_with_spaces(self, client):
        """Test that activity names with spaces are handled correctly"""
        response = client.post(
            "/activities/Music%20Band/remove?email=lucas@mergington.edu"
        )
        assert response.status_code == 200
        # Verify the participant was removed
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert "lucas@mergington.edu" not in data["Music Band"]["participants"]
        assert "mia@mergington.edu" in data["Music Band"]["participants"]

    def test_remove_one_participant_keeps_others(self, client):
        """Test that removing one participant keeps others"""
        # Music Band has lucas and mia
        client.post(
            "/activities/Music%20Band/remove?email=lucas@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "lucas@mergington.edu" not in data["Music Band"]["participants"]
        assert "mia@mergington.edu" in data["Music Band"]["participants"]
        assert len(data["Music Band"]["participants"]) == 1

    def test_remove_all_participants_from_activity(self, client):
        """Test that all participants can be removed from an activity"""
        client.post(
            "/activities/Music%20Band/remove?email=lucas@mergington.edu"
        )
        client.post(
            "/activities/Music%20Band/remove?email=mia@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert len(data["Music Band"]["participants"]) == 0


class TestRootRedirect:
    """Test the GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root URL redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]


class TestIntegration:
    """Integration tests for signup and remove workflows"""

    def test_signup_and_remove_workflow(self, client):
        """Test a complete workflow of signup and remove"""
        email = "workflow@mergington.edu"
        activity = "Basketball"

        # Signup
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200

        # Verify signup
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]

        # Remove
        remove_response = client.post(
            f"/activities/{activity}/remove?email={email}"
        )
        assert remove_response.status_code == 200

        # Verify removal
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]

    def test_participant_count_updates(self, client):
        """Test that participant count updates correctly"""
        email = "count@mergington.edu"
        activity = "Basketball"

        # Initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])

        # After signup
        client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")
        after_signup_count = len(response.json()[activity]["participants"])
        assert after_signup_count == initial_count + 1

        # After remove
        client.post(f"/activities/{activity}/remove?email={email}")
        response = client.get("/activities")
        after_remove_count = len(response.json()[activity]["participants"])
        assert after_remove_count == initial_count
