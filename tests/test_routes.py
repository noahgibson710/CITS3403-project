import pytest
import sys
import os
from io import BytesIO

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app.models import User, MacroPost, FeedPost
from conftest import get_unique_username, get_unique_email
from werkzeug.security import generate_password_hash

def test_home_page(client):
    """Test home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    # Check for some expected content on the home page
    assert b'MacroCalc' in response.data

def test_login_route(client):
    """Test login functionality."""
    with app.app_context():
        # Create a user
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
        
        # Test login with valid credentials
        response = client.post('/login', data={
            'email': email,
            'password': 'password'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for successful login indicators
        assert b'Profile' in response.data or b'Dashboard' in response.data
        
        # Test login with invalid password
        response = client.post('/login', data={
            'email': email,
            'password': 'wrong_password'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for login error message
        assert b'Invalid email or password' in response.data

def test_signup_route(client):
    """Test user registration."""
    username = get_unique_username()
    email = get_unique_email()
    
    # Test valid signup
    response = client.post('/signup', data={
        'name': username,
        'email': email,
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'gender': 'Male',
        'age': '25'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check for successful registration indicators
    assert b'Profile' in response.data or b'Dashboard' in response.data
    
    # Verify user was created in the database
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        assert user is not None
        assert user.name == username

def test_calculator_route(auth_client):
    """Test calculator functionality."""
    client, user = auth_client
    
    # Test calculator form submission
    response = client.post('/calculator', data={
        'weight': '70',
        'height': '175',
        'age': '25',
        'gender': 'Male',
        'activity_level': 'moderate',
        'goal': 'maintain'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check for expected calculation results
    assert b'Your BMR is' in response.data
    assert b'Your TDEE is' in response.data
    
    # Verify a macro post was created
    with app.app_context():
        macro_post = MacroPost.query.filter_by(user_id=user.id).first()
        assert macro_post is not None
        assert macro_post.weight == 70.0
        assert macro_post.height == 175.0

def test_profile_route(auth_client):
    """Test profile page access and functionality."""
    client, user = auth_client
    
    # Test profile page access
    response = client.get('/profile')
    assert response.status_code == 200
    assert user.name.encode() in response.data
    
    # Test profile update
    new_username = get_unique_username()
    response = client.post('/profile', data={
        'name': new_username,
        'gender': 'Male',
        'age': '26'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify profile was updated
    with app.app_context():
        updated_user = User.query.filter_by(id=user.id).first()
        assert updated_user.name == new_username
        assert updated_user.age == 26 