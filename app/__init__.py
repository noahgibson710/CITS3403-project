from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import secrets

db = SQLAlchemy()
migrate = Migrate()

app = Flask(__name__, instance_relative_config=True)
# Use environment variable for SECRET_KEY if available, otherwise generate a secure random key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.login_manager = login_manager

db.init_app(app)
migrate.init_app(app, db)

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


from app import routes

