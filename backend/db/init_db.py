"""Initialize the database and create tables."""
from db.database import Base, engine
from analysis.models import Analysis, ModelResult
from auth.models import User

def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
