import pytest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from app.forms import SignupForm, LoginForm, ProfilePictureForm
from wtforms.validators import ValidationError

def test_form_field_existence():
    """Test that all required form fields exist with correct validators."""
    with app.test_request_context():
        # SignupForm should have name, email, and password fields
        form = SignupForm()
        assert hasattr(form, 'name')
        assert hasattr(form, 'email') 
        assert hasattr(form, 'password')
        assert hasattr(form, 'submit')
        
        # LoginForm should have email and password fields
        form = LoginForm()
        assert hasattr(form, 'email')
        assert hasattr(form, 'password')
        assert hasattr(form, 'submit')
        
        # ProfilePictureForm should have picture field
        form = ProfilePictureForm()
        assert hasattr(form, 'picture')
        assert hasattr(form, 'submit')

def test_login_form_required_fields():
    """Test that login form fields are required."""
    with app.test_request_context():
        # Test with empty data
        form = LoginForm(formdata=None)
        assert not form.validate()
        
        # Manually set data
        form = LoginForm(formdata=None)
        form.email.data = ''
        form.password.data = ''
        form.validate()
        
        assert 'email' in form.errors
        assert 'password' in form.errors

def test_signup_form_validators():
    """Test the validators on the signup form."""
    with app.test_request_context():
        # Test with invalid email format
        form = SignupForm(formdata=None)
        form.name.data = 'testuser'
        form.email.data = 'not-an-email'
        form.password.data = 'Password123!'
        form.validate()
        
        assert 'email' in form.errors
        
        # Test with invalid password format (missing requirements)
        form = SignupForm(formdata=None)
        form.name.data = 'testuser'
        form.email.data = 'valid@example.com'
        form.password.data = 'password' # Missing uppercase and special char
        form.validate()
        
        assert 'password' in form.errors 