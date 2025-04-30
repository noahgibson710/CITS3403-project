from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = "alskdjflkasjfdlaskjdf2392039"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db.init_app(app)

from app import routes

with app.app_context():
    db.create_all()