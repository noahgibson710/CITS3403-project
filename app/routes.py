from flask import Flask, request, session, redirect, send_from_directory, jsonify, url_for, Blueprint, render_template
from flask_login import login_required, current_user
from app import app
from app.forms import SignupForm, LoginForm
# app = Blueprint("app", __name__)
from app.models import User, MacroPost, FeedPost
from app import db

@app.route('/')
def home():
    feed_posts = FeedPost.query.order_by(FeedPost.timestamp.desc()).all()
    return render_template('home.html', feed_posts=feed_posts)



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
    if "user" not in session:
        return redirect("/login")  # Block access if not logged in

    user = User.query.filter_by(name=session["user"]).first()
    if not user:
        return redirect("/login")
    
    macro_posts = MacroPost.query.filter_by(user_id=user.id).order_by(MacroPost.timestamp.desc()).all()
    print(len(macro_posts))
    return render_template("profile.html", user=user, macro_posts=macro_posts)

@app.route('/delete_macro_post/<int:post_id>', methods=['POST'])
def delete_macro_post(post_id):
    post = MacroPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('profile'))

@app.route("/feed", methods=["GET"])
def feed():
    if "user" not in session:
        return render_template("community.html", login_required=True)
    
    return render_template("community.html", login_required=False)

@app.route("/about")
def about():
    return render_template("about.html")


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

@app.route("/save_results", methods=["POST"])
def save_results():
    # Expecting JSON data from the frontend
    data = request.json

    # Assuming the user is logged in and has a session with their name
    user = User.query.filter_by(name=session["user"]).first()

    if user:
        # Save the macro results to the MacroPost table
        new_post = MacroPost(
            gender=data['gender'],
            age=data['age'],
            weight=data['weight'],
            height=data['height'],
            bmr=data['bmr'],
            tdee=data['tdee'],
            user_id=user.id  # User ID from the session
        )

        # Add to the session and commit to save to the database
        db.session.add(new_post)
        db.session.commit()

        return jsonify({"message": "Macro results saved successfully"}), 200
    else:
        return jsonify({"error": "User not logged in"}), 401
    
@app.route('/share-to-feed', methods=['POST'])
@login_required
def share_to_feed():
    content = request.form.get('content')
    if content:
        post = FeedPost(content=content, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('profile'))  # or url_for('home') to go straight to feed



# Run the server
if __name__ == "__app__":
    app.run(debug=True)