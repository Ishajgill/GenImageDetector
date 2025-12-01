"""Load database fixtures."""
import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import sessionmaker
from db.database import engine
from auth.models import User
from analysis.models import Analysis  # Import to resolve relationship
from auth.auth import get_password_hash


def load_users():
    """Load users from fixtures."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        fixtures_path = Path(__file__).parent / "fixtures" / "users.json"
        with open(fixtures_path, "r") as f:
            users_data = json.load(f)

        for user_data in users_data:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if existing_user:
                print(f"User '{user_data['username']}' already exists, skipping...")
                continue

            # Create new user
            user = User(
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"])
            )
            db.add(user)
            print(f"Created user: {user_data['username']}")

        db.commit()
        print("Users loaded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error loading users: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    load_users()
