import sys
import os
import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app.models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_signup_success(client):
    response = client.post("/signup", data={
        "name": "newuser",
        "email": "newuser@example.com",
        "password": "NewPassword@123"
    }, follow_redirects=True)

    assert response.status_code in (200, 302)
    assert b"Login" in response.data or b"Sign in" in response.data or b"Email" in response.data

def test_signup_duplicate_email(client):
    client.post("/signup", data={
        "name": "user1",
        "email": "duplicate@example.com",
        "password": "GoodPass1@"
    })

    response = client.post("/signup", data={
        "name": "user2",
        "email": "duplicate@example.com",
        "password": "AnotherPass1@"
    })

    assert b"This email is already registered" in response.data

def test_signup_duplicate_name(client):
    client.post("/signup", data={
        "name": "SameName",
        "email": "first@example.com",
        "password": "GoodPass1@"
    })

    response = client.post("/signup", data={
        "name": "SameName",
        "email": "second@example.com",
        "password": "GoodPass2@"
    })

    assert b"This name is already taken" in response.data
