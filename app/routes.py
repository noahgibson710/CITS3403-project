from flask import Flask, request, redirect, send_from_directory, jsonify, url_for, Blueprint, render_template, flash, abort
from flask_login import login_required, current_user, login_user, logout_user
from app import app
from app.forms import SignupForm, LoginForm
# app = Blueprint("app", __name__)
from app.models import User, MacroPost, FeedPost
from app import db
from datetime import datetime
from sqlalchemy.orm import joinedload

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
            login_user(user)
            return redirect("/profile")
        else:
            return render_template("login.html", form=form, error="Invalid credentials")
    return render_template("login.html", form=form)


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    return render_template("calc.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return f"<h2>Welcome {current_user.name}!</h2><br><a href='/logout'>Logout</a>"

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@app.route("/results")
def results():
    return render_template("results.html")

@app.route("/profile")
@login_required
def profile():
    macro_posts = MacroPost.query.filter_by(user_id=current_user.id).order_by(MacroPost.timestamp.desc()).all()
    return render_template("profile.html", user=current_user, macro_posts=macro_posts)

@app.route('/delete_macro_post/<int:post_id>', methods=['POST'])
@login_required
def delete_macro_post(post_id):
    # 1) Fetch the macro post (404 if not found)
    post = MacroPost.query.get_or_404(post_id)

    # 2) Security: only its owner may delete it
    if post.user_id != current_user.id:
        abort(403)

    # 3) Delete any feed entries that point to this macro post
    FeedPost.query.filter_by(macro_post_id=post.id).delete()

    # 4) Now delete the macro post itself
    db.session.delete(post)
    db.session.commit()

    flash('Your macro entry was successfully deleted.', 'success')
    return redirect(url_for('profile'))

@app.route("/feed", methods=["GET"])
@login_required
def feed():    
    # Get all feed posts

    posts = (FeedPost.query
                .options(
                  joinedload(FeedPost.user),
                  joinedload(FeedPost.macro_post)
                )
                .order_by(FeedPost.timestamp.desc())
                .all())    
    return render_template("community.html",  posts=posts)

@login_required
@app.route("/create_feed_post/<int:post_id>", methods=["POST"])
def create_feed_post(post_id):
    post = MacroPost.query.get_or_404(post_id)
    print(current_user)
    user_who_shared_id = current_user.id
    
    # Create new feed post
    new_post = FeedPost(
        user_id=user_who_shared_id,
        macro_post_id= post.id
    )
    
    db.session.add(new_post)
    db.session.commit()
    
    return redirect(url_for("feed"))

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            # Add an error to the form if the email is already taken
            form.email.errors.append('Email is already registered, please use a different one.')
            return render_template('signup.html', form=form)

        # If the email doesn't exist, create the new user and add to the database
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template('signup.html', form=form)


# Static file serving (CSS, JS, etc.)
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

# favicon
@app.route('/favicon.ico')
def web_favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'images'),
        'web_favicon',
        mimetype='image/png'
    )

@app.route("/save_results", methods=["POST"])
@login_required
def save_results():
    data = request.json
    new_post = MacroPost(
        gender=data['gender'],
        age=data['age'],
        weight=data['weight'],
        height=data['height'],
        bmr=data['bmr'],
        tdee=data['tdee'],
        user_id=current_user.id
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"message": "Macro results saved successfully"}), 200



# Run the server
if __name__ == "__app__":
    app.run(debug=True)