from flask import Blueprint, render_template
from flask import Flask, request, session, redirect, send_from_directory, jsonify
from app import app
from app.forms import SignupForm, LoginForm
# app = Blueprint("app", __name__)
from app.models import User  # Assuming you have a User model defined in models.py
from app import db

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            session["user"] = user.name
            print("User logged in:", user.name)
        else:
            print("Invalid credentials")
            return render_template("login.html", form=form, error="Invalid credentials")

        return redirect("/profile")  # or wherever you want after login
    return render_template("login.html", form=form)


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    return render_template("calc.html")

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return f"<h2>Welcome {session['user']}!</h2><br><a href='/logout'>Logout</a>"
    return redirect("/login")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/results")
def results():
    return render_template("results.html")

@app.route("/profile")
def profile():
    # Example: fetch the current user if logged in, otherwise show placeholders
    user = None
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
    return render_template("profile.html", user=user)


@app.route("/about")
def about():
    return render_template("about.html")



# Handle the POST request
# @app.route("/api/signup", methods=["GET", 'POST'])
# def signup():
#     username = request.form.get('name')
#     email = request.form.get('email')
#     password = request.form.get('password')

#     print(f"Received: {username}, {email}, {password}")   #debugging, showing on console

#     if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$', password): #Return an error if the signup password does not meet the requirement
#         return jsonify({"signup-message": "Password must be at least 8 characters and include uppercase, lowercase, and special character."}), 4002
#     existing = User.query.filter(User.username == username).first()  #Return an error signup-message if user name exists 
#     if existing:
#         return jsonify({"signup-message": "User already exists. Please log in instead"}), 400

#     if User.query.filter_by(email=email).first():  #Return an error signup-message if email is already used
#         return jsonify({"signup-message": "Email is already registered. Please use a different email."}), 400
    
#     try:
#         user = User(username=username, email=email, password=password)   #Save to database
#         db.session.add(user)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"signup-message": "User already exists. Please log in instead"}), 400

#     return jsonify({'message': 'Signup successful!'}), 200

@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        print("Received: ", form.name.data, form.email.data, form.password.data)
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template('signup.html', form=form)

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
if __name__ == "__app__":
    app.run(debug=True)