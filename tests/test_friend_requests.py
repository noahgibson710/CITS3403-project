import pytest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app.models import User, FriendRequest
from conftest import get_unique_username, get_unique_email
from werkzeug.security import generate_password_hash

def test_friend_request_creation(client):
    """Test creating a friend request."""
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
        
        # Verify friend request was created
        request = FriendRequest.query.filter_by(
            requester_id=user1.id,
            receiver_id=user2.id
        ).first()
        
        assert request is not None
        assert request.status == 'pending'
        assert request.requester == user1
        assert request.receiver == user2
        
        # Check relationships
        assert request in user1.requests_sent.all()
        assert request in user2.requests_received.all()

def test_accept_friend_request(client):
    """Test accepting a friend request."""
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
        
        # Accept the friend request
        friend_request.status = 'accepted'
        user1.friends.append(user2)
        user2.friends.append(user1)
        db.session.commit()
        
        # Verify friend request was accepted
        request = FriendRequest.query.filter_by(
            requester_id=user1.id,
            receiver_id=user2.id
        ).first()
        
        assert request.status == 'accepted'
        
        # Verify users are now friends
        assert user2 in user1.friends.all()
        assert user1 in user2.friends.all()

def test_reject_friend_request(client):
    """Test rejecting a friend request."""
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
        
        # Reject the friend request
        friend_request.status = 'rejected'
        db.session.commit()
        
        # Verify friend request was rejected
        request = FriendRequest.query.filter_by(
            requester_id=user1.id,
            receiver_id=user2.id
        ).first()
        
        assert request.status == 'rejected'
        
        # Verify users are not friends
        assert user2 not in user1.friends.all()
        assert user1 not in user2.friends.all()

def test_friend_request_api(auth_client):
    """Test friend request API endpoints."""
    client, user1 = auth_client
    
    with app.app_context():
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
        
        # Test sending a friend request
        response = client.post(f'/send_friend_request/{user2.id}', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify friend request was created
        request = FriendRequest.query.filter_by(
            requester_id=user1.id,
            receiver_id=user2.id
        ).first()
        
        assert request is not None
        assert request.status == 'pending' 