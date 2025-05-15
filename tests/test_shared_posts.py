import pytest
import sys
import os
import json

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app.models import User, MacroPost, SharedPost
from conftest import get_unique_username, get_unique_email
from werkzeug.security import generate_password_hash

def test_shared_post_creation(client):
    """Test creating a shared post."""
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
    
    # Create a macro post for user1
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
    
    # Share the macro post from user1 to user2
    shared_post = SharedPost(
        sender_id=user1.id,
        receiver_id=user2.id,
        post_id=macro_post.id
    )
    
    db.session.add(shared_post)
    db.session.commit()
    
    # Verify shared post was created
    queried_shared_post = SharedPost.query.filter_by(
        sender_id=user1.id,
        receiver_id=user2.id
    ).first()
    
    assert queried_shared_post is not None
    assert queried_shared_post.sender == user1
    assert queried_shared_post.receiver == user2
    assert queried_shared_post.post == macro_post

def test_shared_post_api(auth_client):
    """Test shared post API endpoints."""
    client, user1 = auth_client
    
    # Create another user
    user2 = User(
        name=get_unique_username(),
        email=get_unique_email(),
        password=generate_password_hash('password'),
        gender='Female',
        age=30
    )
    
    db.session.add(user2)
    db.session.commit()
    
    # Create a macro post for user1
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
    
    # Test sharing a post using the JSON API
    response = client.post('/share_post', 
                          json={
                              'receiver': user2.name,
                              'post_id': macro_post.id
                          })
    assert response.status_code == 200
    
    # Verify shared post was created
    shared_post = SharedPost.query.filter_by(
        sender_id=user1.id,
        receiver_id=user2.id,
        post_id=macro_post.id
    ).first()
    
    assert shared_post is not None

def test_view_shared_posts(auth_client):
    """Test viewing shared posts."""
    client, receiver = auth_client
    
    # Create another user (sender)
    sender = User(
        name=get_unique_username(),
        email=get_unique_email(),
        password=generate_password_hash('password'),
        gender='Male',
        age=25
    )
    
    db.session.add(sender)
    db.session.commit()
    
    # Create a macro post for the sender
    macro_post = MacroPost(
        gender='Male',
        age=25,
        weight=70.0,
        height=175.0,
        bmr=1700.0,
        tdee=2500.0,
        calorie_goal='maintain',
        user_id=sender.id
    )
    
    db.session.add(macro_post)
    db.session.commit()
    
    # Share the post with the receiver
    shared_post = SharedPost(
        sender_id=sender.id,
        receiver_id=receiver.id,
        post_id=macro_post.id
    )
    
    db.session.add(shared_post)
    db.session.commit()
    
    # Test viewing shared posts
    response = client.get('/shared_posts')
    assert response.status_code == 200
    
    # Parse the JSON response
    data = json.loads(response.data)
    
    # Check that the shared post is in the received data
    assert any(post.get('id') == macro_post.id for post in data.get('received', [])) 