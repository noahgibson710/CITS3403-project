from flask import Flask, request, session, redirect, send_from_directory
from models import db, User
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# SQLite DB setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize DB
with app.app_context():
    db.create_all()
    # Add default user if not present
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password='1234'))
        db.session.commit()

@app.route("/")
def home():
    return send_from_directory("../client", "home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user'] = user.username
            return redirect("/dashboard")
        else:
            return "Invalid login. <a href='/login'>Try again</a>"

    return send_from_directory("../client", "login.html")

@app.route("/dashboard")
def dashboard():
    if 'user' in session:
        return f"<h2>Welcome {session['user']}!</h2><br><a href='/logout'>Logout</a>"
    return redirect("/login")

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect("/")

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory("../client", filename)

if __name__ == "__main__":
    app.run(debug=True)
