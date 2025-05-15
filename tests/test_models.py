import pytest
import sys
import os
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app.models import User, MacroPost, FeedPost, SharedPost, FriendRequest
from conftest import get_unique_username, get_unique_email
from werkzeug.security import generate_password_hash

def test_user_model(client):
    """Test User model creation and relationships."""
    with app.app_context():
        # Create a user with unique username and email
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
        
        # Test user was created
        queried_user = User.query.filter_by(email=email).first()
        assert queried_user is not None
        assert queried_user.name == username
        assert queried_user.gender == 'Male'
        assert queried_user.age == 25
        
        # Test default values
        assert queried_user.profile_picture == 'placeholder-profile.jpg'
        
        # Test relationships
        assert hasattr(user, 'macroposts')
        assert hasattr(user, 'feed_posts')
        assert hasattr(user, 'friends')
        assert hasattr(user, 'requests_sent')
        assert hasattr(user, 'requests_received')

def test_macro_post_model(client):
    """Test MacroPost model creation and relationships."""
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
        
        # Create a macro post
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
        
        # Test macro post was created
        queried_post = MacroPost.query.filter_by(user_id=user.id).first()
        assert queried_post is not None
        assert queried_post.gender == 'Male'
        assert queried_post.weight == 70.0
        assert queried_post.height == 175.0
        assert queried_post.bmr == 1700.0
        assert queried_post.tdee == 2500.0
        assert queried_post.calorie_goal == 'maintain'
        
        # Test relationships
        assert queried_post.user == user
        assert macro_post in user.macroposts

def test_feed_post_model(client):
    """Test FeedPost model creation and relationships."""
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
        
        # Create a macro post
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
        
        # Create a feed post
        feed_post = FeedPost(
            user_id=user.id,
            macro_post_id=macro_post.id,
            visibility='public'
        )
        
        db.session.add(feed_post)
        db.session.commit()
        
        # Test feed post was created
        queried_feed_post = FeedPost.query.filter_by(user_id=user.id).first()
        assert queried_feed_post is not None
        assert queried_feed_post.visibility == 'public'
        
        # Test relationships
        assert queried_feed_post.user == user
        assert queried_feed_post.macro_post == macro_post
        assert feed_post in user.feed_posts

def test_friend_relationship(client):
    """Test friend relationship between users."""
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
        
        # Add user2 as a friend of user1
        user1.friends.append(user2)
        db.session.commit()
        
        # Test friendship
        assert user2 in user1.friends.all()
        
        # Test if user1 is also a friend of user2 (bidirectional)
        # This depends on how your app manages friendships
        # If bidirectional, uncomment the following:
        # assert user1 in user2.friends.all() 