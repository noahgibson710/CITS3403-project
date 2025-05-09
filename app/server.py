from flask import Flask, render_template, request, session, redirect, send_from_directory, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from models import db, User
import re
import os

app = Flask(__name__)
CORS(app)  # Allow frontend JS to access API

app.secret_key = "supersecretkey"

# DB setup
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'users.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize DB
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', email ='admin@example.com', password='12345678'))
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Assuming you have a User model with an `id` field

# Optionally, set the login view (URL to redirect unauthenticated users)
login_manager.login_view = 'login'  # Change to your login route


# Run the server
if __name__ == "__main__":
    app.run(debug=True)
