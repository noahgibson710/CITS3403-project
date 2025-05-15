import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash
import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            user = User(
                name="testuser",
                email="test@example.com",
                password=generate_password_hash("Password@!!")
            )
            db.session.add(user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_login_success(client):
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "Password@!!"
    }, follow_redirects=True)
    assert b"Logout" in response.data or b"testuser" in response.data

def test_login_failure(client):
    response = client.post("/login", data={
        "email": "wrong@example.com",
        "password": "Password@!!"
    }, follow_redirects=True)
    assert b"Invalid credentials" in response.data
