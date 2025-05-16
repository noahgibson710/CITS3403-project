import pytest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app.models import User, MacroPost, FeedPost, SharedPost, FriendRequest
from conftest import get_unique_username, get_unique_email
from werkzeug.security import generate_password_hash

def test_user_registration(client):
    """Test user registration with valid data."""
    username = get_unique_username()
    email = get_unique_email()
    
    response = client.post('/signup', data={
        'name': username,
        'email': email,
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'gender': 'Male',
        'age': '25'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify user was created
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        assert user is not None
        assert user.name == username

def test_user_login(client):
    """Test user login with valid credentials."""
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
        
        # Test login
        response = client.post('/login', data={
            'email': email,
            'password': 'password'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Profile' in response.data or b'Dashboard' in response.data

def test_macro_calculation(auth_client):
    """Test macro calculation functionality."""
    client, user = auth_client
    
    response = client.post('/calculator', data={
        'weight': '70',
        'height': '175',
        'age': '25',
        'gender': 'Male',
        'activity_level': 'moderate',
        'goal': 'maintain'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check for calculation results
    assert b'Your BMR is' in response.data
    assert b'Your TDEE is' in response.data
    
    # Verify macro post was created
    with app.app_context():
        macro_post = MacroPost.query.filter_by(user_id=user.id).first()
        assert macro_post is not None
        assert macro_post.weight == 70.0
        assert macro_post.height == 175.0

def test_profile_update(auth_client):
    """Test profile update functionality."""
    client, user = auth_client
    
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

def test_friendship_flow(client):
    """Test the complete friendship flow."""
    with app.app_context():
        # Create two users
        user1 = User(
            name=get_unique_username(),
            email=get_unique_email(),
            password=generate_password_hash('password'),
            gender='Male',
            age=25
        )
        
        user2 = User(
            name=get_unique_username(),
            email=get_unique_email(),
            password=generate_password_hash('password'),
            gender='Female',
            age=30
        )
        
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Create a friend request
        friend_request = FriendRequest(
            requester_id=user1.id,
            receiver_id=user2.id,
            status='pending'
        )
        
        db.session.add(friend_request)
        db.session.commit()
        
        # Accept the request
        friend_request.status = 'accepted'
        user1.friends.append(user2)
        user2.friends.append(user1)
        db.session.commit()
        
        # Verify they are friends
        assert user2 in user1.friends.all()
        assert user1 in user2.friends.all()

def test_post_sharing(client):
    """Test post sharing functionality."""
    with app.app_context():
        # Create two users
        user1 = User(
            name=get_unique_username(),
            email=get_unique_email(),
            password=generate_password_hash('password'),
            gender='Male',
            age=25
        )
        
        user2 = User(
            name=get_unique_username(),
            email=get_unique_email(),
            password=generate_password_hash('password'),
            gender='Female',
            age=30
        )
        
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Make them friends
        user1.friends.append(user2)
        user2.friends.append(user1)
        db.session.commit()
        
        # Create a macro post
        macro_post = MacroPost(
            gender='Male',
            age=25,
            weight=70.0,
            height=175.0,
            bmr=1700.0,
            tdee=2500.0,
            calorie_goal='maintain',
            user_id=user1.id
        )
        
        db.session.add(macro_post)
        db.session.commit()
        
        # Share the post
        shared_post = SharedPost(
            sender_id=user1.id,
            receiver_id=user2.id,
            post_id=macro_post.id
        )
        
        db.session.add(shared_post)
        db.session.commit()
        
        # Verify shared post was created
        assert SharedPost.query.filter_by(
            sender_id=user1.id,
            receiver_id=user2.id
        ).first() is not None 