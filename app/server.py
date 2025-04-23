from flask import Flask, request, session, redirect, send_from_directory, jsonify
from flask_cors import CORS
from models import db, User
import os

app = Flask(__name__)
CORS(app)  # Allow frontend JS to access API

app.secret_key = "supersecretkey"

# DB setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize DB
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password='1234'))
        db.session.commit()

# === ROUTES ===

@app.route("/")
def home():
    return redirect("/static/home.html")

@app.route("/login")
def login_page():
    return send_from_directory("static", "login.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    print("[DEBUG] Received login data:", data)

    username = data.get("username")
    password = data.get("password")
    print(username, password)
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        session["user"] = username
        return jsonify({"success": True, "username": username})
    return jsonify({"success": False}), 401

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return f"<h2>Welcome {session['user']}!</h2><br><a href='/logout'>Logout</a>"
    return redirect("/login")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# Static file serving (CSS, JS, etc.)
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

# Optional: Suppress favicon error
@app.route("/favicon.ico")
def favicon():
    return "", 204


#for results rendering test
@app.route("/api/results", methods=["GET"])
def api_results():
    # Simulate some data
    results = {
        "data": [
            {"id": 1, "name": "Result 1"},
            {"id": 2, "name": "Result 2"},
            {"id": 3, "name": "Result 3"},
        ]
    }
    return jsonify(results)
# Run the server
if __name__ == "__main__":
    app.run(debug=True)
