from flask import Blueprint, render_template
from flask import Flask, request, session, redirect, send_from_directory, jsonify

main = Blueprint("main", __name__)
# from main.models import User  # Assuming you have a User model defined in models.py

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/login")
def login_page():
    return render_template("login.html")

@main.route("/api/login", methods=["POST"])
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

@main.route("/dashboard")
def dashboard():
    if "user" in session:
        return f"<h2>Welcome {session['user']}!</h2><br><a href='/logout'>Logout</a>"
    return redirect("/login")

@main.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# Static file serving (CSS, JS, etc.)
@main.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

# Optional: Suppress favicon error
@main.route("/favicon.ico")
def favicon():
    return "", 204


#for results rendering test
@main.route("/api/results", methods=["GET"])
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