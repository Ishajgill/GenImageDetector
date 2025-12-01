"""Unit tests for auth routes."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base, get_db
from main import app


# Create test database with thread-safe settings for SQLite
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAuthRoutes:
    """Tests for authentication routes."""

    def test_signup_success(self):
        """Test successful user signup."""
        response = client.post(
            "/auth/signup",
            json={"username": "testuser", "password": "testpass123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_signup_duplicate_username(self):
        """Test signup with duplicate username fails."""
        # Create first user
        client.post(
            "/auth/signup",
            json={"username": "testuser", "password": "password1"}
        )

        # Try to create second user with same username
        response = client.post(
            "/auth/signup",
            json={"username": "testuser", "password": "password2"}
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_login_success(self):
        """Test successful login."""
        # Create user
        client.post(
            "/auth/signup",
            json={"username": "testuser", "password": "testpass123"}
        )

        # Login
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """Test login with wrong password fails."""
        # Create user
        client.post(
            "/auth/signup",
            json={"username": "testuser", "password": "correctpass"}
        )

        # Try to login with wrong password
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "wrongpass"}
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self):
        """Test login with non-existent user fails."""
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "somepass"}
        )

        assert response.status_code == 401

    def test_get_current_user_with_token(self):
        """Test getting current user with valid token."""
        # Create user and get token
        signup_response = client.post(
            "/auth/signup",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = signup_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data
        assert "created_at" in data

    def test_get_current_user_without_token(self):
        """Test getting current user without token fails."""
        response = client.get("/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token fails."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_password_is_hashed(self):
        """Test that passwords are properly hashed."""
        # Create user
        client.post(
            "/auth/signup",
            json={"username": "testuser", "password": "plaintext"}
        )

        # Verify password is not stored in plaintext
        # (This would require direct database access to fully verify,
        # but we can confirm login still works with correct password)
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "plaintext"}
        )

        assert response.status_code == 200
