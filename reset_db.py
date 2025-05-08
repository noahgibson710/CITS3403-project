from app import app, db

# This will drop all tables and recreate them
with app.app_context():
    db.drop_all()  # Drops all tables, including FeedPost
    db.create_all()  # Creates all tables according to your models
