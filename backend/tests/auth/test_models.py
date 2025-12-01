"""Unit tests for auth models."""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from auth.models import User


class TestUserModel:
    """Tests for the User model."""

    def test_create_user(self, db_session):
        """Test creating a basic user."""
        user = User(
            username="testuser",
            hashed_password="hashedpassword123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.hashed_password == "hashedpassword123"
        assert isinstance(user.created_at, datetime)

    def test_user_username_unique(self, db_session):
        """Test that username must be unique."""
        user1 = User(username="duplicate", hashed_password="pass1")
        user2 = User(username="duplicate", hashed_password="pass2")

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_username_required(self, db_session):
        """Test that username is required."""
        user = User(hashed_password="password123")
        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_password_required(self, db_session):
        """Test that hashed_password is required."""
        user = User(username="testuser")
        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_created_at_auto_set(self, db_session):
        """Test that created_at is automatically set."""
        user = User(
            username="timetest",
            hashed_password="password123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
        assert user.created_at <= datetime.utcnow()

    def test_user_analyses_relationship(self, db_session):
        """Test that user has analyses relationship."""
        user = User(
            username="relationtest",
            hashed_password="password123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Check that analyses attribute exists and is initially empty
        assert hasattr(user, 'analyses')
        assert user.analyses == []

    def test_multiple_users(self, db_session):
        """Test creating multiple users."""
        user1 = User(username="user1", hashed_password="pass1")
        user2 = User(username="user2", hashed_password="pass2")
        user3 = User(username="user3", hashed_password="pass3")

        db_session.add_all([user1, user2, user3])
        db_session.commit()

        users = db_session.query(User).all()
        assert len(users) == 3
        assert {u.username for u in users} == {"user1", "user2", "user3"}

    def test_user_query_by_username(self, db_session):
        """Test querying user by username."""
        user = User(username="findme", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        found_user = db_session.query(User).filter(User.username == "findme").first()
        assert found_user is not None
        assert found_user.username == "findme"
        assert found_user.hashed_password == "password123"
