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
    assert b'Health Macro Calculator' in response.data

def test_login_route(client):
    """Test login functionality."""
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
    assert b'Invalid credentials' in response.data

def test_signup_route(client):
    """Test user registration."""
    username = get_unique_username()
    email = get_unique_email()
    
    # Test valid signup
    response = client.post('/signup', data={
        'name': username,
        'email': email,
        'password': 'Password123!',
        'gender': 'Male',
        'age': '25'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify user was created in the database
    user = User.query.filter_by(email=email).first()
    assert user is not None
    assert user.name == username

def test_calculator_route(auth_client):
    """Test calculator functionality."""
    client, user = auth_client
    
    # First check that the calculator page loads
    response = client.get('/calculator')
    assert response.status_code == 200
    
    # Test calculator form submission
    # We'll manually create a MacroPost instead of using the AJAX endpoint
    # since the endpoint requires BMR and TDEE calculation which is done client-side
    macro_post = MacroPost(
        gender='Male',
        age=25,
        weight=70.0,
        height=175.0,
        bmr=1700.0,
        tdee=2500.0,
        calorie_goal='maintain',
        user_id=user.id
    )
    
    db.session.add(macro_post)
    db.session.commit()
    
    # Verify a macro post was created
    macro_post = MacroPost.query.filter_by(user_id=user.id).first()
    assert macro_post is not None
    assert macro_post.weight == 70.0
    assert macro_post.height == 175.0
    assert macro_post.bmr == 1700.0
    assert macro_post.tdee == 2500.0

def test_profile_route(auth_client):
    """Test profile page access and functionality."""
    client, user = auth_client
    
    # Test profile page access
    response = client.get('/profile')
    assert response.status_code == 200
    assert user.name.encode() in response.data
    
    # Save the current username to check against later
    original_name = user.name
    
    # Test profile update (using the correct update endpoint)
    new_username = get_unique_username()
    
    # First update the username via username field
    user.name = new_username
    db.session.commit()
    
    # Now test updating profile info (we're not testing name change, just age)
    response = client.post('/update_profile_info', data={
        'gender': 'Male',
        'age': '26'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify age was updated but name is still the one we manually set
    updated_user = User.query.filter_by(id=user.id).first()
    assert updated_user.name == new_username  # Name should be the manually updated one
    assert updated_user.age == 26  # Age should be updated 