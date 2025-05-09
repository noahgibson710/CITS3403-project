from app import app, db
from app.models import User, MacroPost, FeedPost

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database has been reset successfully!")

if __name__ == "__main__":
    reset_database() 