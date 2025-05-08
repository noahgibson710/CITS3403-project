from flask import Flask, request, redirect, send_from_directory, jsonify, url_for, Blueprint, render_template, flash
from flask_login import login_required, current_user, login_user, logout_user
from app import app
from app.forms import SignupForm, LoginForm
# app = Blueprint("app", __name__)
from app.models import User, MacroPost, FeedPost
from app import db
from datetime import datetime
from sqlalchemy.orm import joinedload


global logged_in

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
            logged_in = True
            return redirect("/profile")
        else:
            return render_template("login.html", form=form, error="Invalid credentials")
    return render_template("login.html", form=form)


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    gender = None
    age = None
    if current_user.is_authenticated:
        gender = current_user.gender
        age = current_user.age
    return render_template("calc.html", gender=gender, age=age)

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
    macro_posts = []
    if current_user.is_authenticated:
        macro_posts = MacroPost.query.filter_by(user_id=current_user.id).order_by(MacroPost.timestamp.desc()).all()
    return render_template("results.html", macro_posts=macro_posts)

@app.route("/profile")
@login_required
def profile():
    macro_posts = MacroPost.query.filter_by(user_id=current_user.id).order_by(MacroPost.timestamp.desc()).all()
    return render_template("profile.html", user=current_user, macro_posts=macro_posts)

@app.route('/delete_macro_post/<int:post_id>', methods=['POST'])
def delete_macro_post(post_id):
    post = MacroPost.query.get_or_404(post_id)
    # Delete all feed posts that reference this macro post
    FeedPost.query.filter_by(macro_post_id=post.id).delete()
    db.session.delete(post)
    db.session.commit()
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
    # feed_posts = FeedPost.query.order_by(FeedPost.timestamp.desc()).all()
    # posts = MacroPost.query.order_by(MacroPost.timestamp.desc()).all()
    
    # Get user's macro posts for the dropdown
    # user_macros = MacroPost.query.filter_by(user_id=current_user.id).order_by(MacroPost.timestamp.desc()).all()
    
    return render_template("community.html",  posts=posts)

@login_required
@app.route("/create_feed_post/<int:post_id>", methods=["POST"])
def create_feed_post(post_id):
    post = MacroPost.query.get_or_404(post_id)
    user_who_shared_id = current_user.id

    # Prevent duplicate posts: check if this macro_post has already been shared by this user
    existing_post = FeedPost.query.filter_by(user_id=user_who_shared_id, macro_post_id=post.id).first()
    if existing_post:
        flash("You have already shared this result to the community feed.", "warning")
        return redirect(url_for("feed"))

    new_post = FeedPost(
        user_id=user_who_shared_id,
        macro_post_id=post.id
    )
    db.session.add(new_post)
    db.session.commit()
    flash("Result shared to community feed!", "success")
    return redirect(url_for("feed"))

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

# @app.route('/share_to_feed', methods=['POST'])
# @login_required
# def share_to_feed():
#     if request.method == 'POST':
#         content = request.form['content']
#         timestamp = datetime.utcnow()
#         user_id = current_user.id

#         new_post = FeedPost(content=content, timestamp=timestamp, user_id=user_id)
#         db.session.add(new_post)
#         db.session.commit()

#         flash("Post shared successfully", 'success')
#         return redirect(url_for('feed'))

@app.route('/update_profile_info', methods=['POST'])
@login_required
def update_profile_info():
    gender = request.form.get('gender')
    age = request.form.get('age')
    if gender:
        current_user.gender = gender
    if age:
        try:
            current_user.age = int(age)
        except ValueError:
            flash('Invalid age value.', 'danger')
            return redirect(url_for('profile'))
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

# Run the server
if __name__ == "__app__":
    app.run(debug=True)