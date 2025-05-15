import pytest
import os
import sys
import tempfile
import uuid

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db

# Import all models explicitly to ensure they're registered with SQLAlchemy
from app.models import User, MacroPost, FeedPost, SharedPost, FriendRequest, friend_assoc

from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    """Create a test client for the app."""
    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Create app context explicitly and push it
    app_context = app.app_context()
    app_context.push()
    
    # Create all tables
    db.create_all()
    
    # Create and yield the test client
    with app.test_client() as client:
        yield client
    
    # Clean up
    db.session.remove()
    db.drop_all()
    app_context.pop()

def get_unique_username():
    """Generate a unique username for testing."""
    return f"user_{uuid.uuid4().hex[:8]}"

def get_unique_email():
    """Generate a unique email for testing."""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

@pytest.fixture
def auth_client(client):
    """Create an authenticated test client."""
    # Create a test user with unique username and email
    username = get_unique_username()
    email = get_unique_email()
    
    user = User(
        name=username,
        email=email,
        password=generate_password_hash('password'),
        gender='Male',
        age=25
    )
    db.session.add(user)
    db.session.commit()
    
    # Log in the user
    client.post('/login', data={
        'email': email,
        'password': 'password'
    }, follow_redirects=True)
    
    yield client, user  # Return both client and user object 