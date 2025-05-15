import pytest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from app.forms import SignupForm, LoginForm, ProfilePictureForm
from wtforms.validators import ValidationError

def test_registration_form_validation():
    """Test registration form validation."""
    with app.test_request_context():
        # Test valid form data
        form = SignupForm(
            name='validuser',
            email='valid@example.com',
            password='Password123!',
            confirm_password='Password123!',
            gender='Male',
            age='25'
        )
        
        assert form.validate()
        
        # Test password mismatch
        form = SignupForm(
            name='validuser',
            email='valid@example.com',
            password='Password123!',
            confirm_password='Password456!',
            gender='Male',
            age='25'
        )
        
        assert not form.validate()
        
        # Test invalid email format
        form = SignupForm(
            name='validuser',
            email='invalid-email',
            password='Password123!',
            confirm_password='Password123!',
            gender='Male',
            age='25'
        )
        
        assert not form.validate()
        assert any('Invalid email address' in error for error in form.email.errors)
        
        # Test invalid password format
        form = SignupForm(
            name='validuser',
            email='valid@example.com',
            password='password',  # Missing uppercase and special char
            confirm_password='password',
            gender='Male',
            age='25'
        )
        
        assert not form.validate()

def test_login_form_validation():
    """Test login form validation."""
    with app.test_request_context():
        # Test valid form data
        form = LoginForm(
            email='valid@example.com',
            password='password'
        )
        
        assert form.validate()
        
        # Test missing email
        form = LoginForm(
            email='',
            password='password'
        )
        
        assert not form.validate()
        assert 'This field is required' in form.email.errors
        
        # Test missing password
        form = LoginForm(
            email='valid@example.com',
            password=''
        )
        
        assert not form.validate()
        assert 'This field is required' in form.password.errors

def test_profile_picture_form_validation():
    """Test profile picture form validation."""
    with app.test_request_context():
        # Create a form instance
        form = ProfilePictureForm()
        
        # Initially, the form should be valid with no data
        assert form.validate()
        
        # Test with no file (should still be valid, as picture is not required)
        form = ProfilePictureForm(data={})
        assert form.validate()
        
        # Note: Testing file uploads requires more complex setup
        # and is typically done with integration tests rather than unit tests 