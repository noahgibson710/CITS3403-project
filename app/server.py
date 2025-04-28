from flask import Flask, request, session, redirect, send_from_directory, jsonify
from flask_cors import CORS
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

# Handle the POST request
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    print(f"Received: {username}, {email}, {password}")   #debugging, showing on console

    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$', password): #Return an error if the signup password does not meet the requirement
        return jsonify({"signup-message": "Password must be at least 8 characters and include uppercase, lowercase, and special character."}), 400

    existing = User.query.filter(User.username == username).first()  #Return an error signup-message if user name exists 
    if existing:
        return jsonify({"signup-message": "User already exists. Please log in instead"}), 400

    if User.query.filter_by(email=email).first():  #Return an error signup-message if email is already used
        return jsonify({"signup-message": "Email is already registered. Please use a different email."}), 400
    
    try:
        user = User(username=username, email=email, password=password)   #Save to database
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"signup-message": "User already exists. Please log in instead"}), 400

    return jsonify({'message': 'Signup successful!'}), 200

# Static file serving (CSS, JS, etc.)
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

# Optional: Suppress favicon error
@app.route("/favicon.ico")
def favicon():
    return "", 204

# favicon
@app.route('/favicon.ico')
def web_favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'images'),
        'web_favicon',
        mimetype='image/png'
    )

# Run the server
if __name__ == "__main__":
    app.run(debug=True)
