from flask import Flask, request, redirect, send_from_directory, jsonify, url_for, Blueprint, render_template, flash, current_app
from flask_login import login_required, current_user, login_user, logout_user
from app import app
from app.forms import SignupForm, LoginForm, ProfilePictureForm
# app = Blueprint("app", __name__)
from app.models import User, MacroPost, FeedPost, SharedPost
from app import db
from datetime import datetime
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash, check_password_hash
import os
from PIL import Image
import secrets

@app.route('/')
def home():
    feed_posts = FeedPost.query.order_by(FeedPost.timestamp.desc()).all()
    return render_template('home.html', feed_posts=feed_posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
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
    form = ProfilePictureForm()
    return render_template("profile.html", user=current_user, macro_posts=macro_posts, form=form)

@app.route('/delete_macro_post/<int:post_id>', methods=['POST'])
@login_required
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
    if request.method == "POST":
        if form.validate_on_submit():
            try:
                existing_user = User.query.filter_by(email=form.email.data).first()
                if existing_user:
                    return jsonify({"error": "This email is already registered"}), 400
                
                existing_name = User.query.filter(db.func.lower(User.name) == form.name.data.lower()).first()
                if existing_name:
                    return jsonify({"error": "This name is already taken"}), 400

                hashed_password = generate_password_hash(form.password.data)
                user = User(name=form.name.data, email=form.email.data, password=hashed_password)
                db.session.add(user)
                db.session.commit()
                return jsonify({"message": "Signup successful"}), 200
            except Exception as e:
                db.session.rollback()
                print("DB error:", str(e))
                return jsonify({"error": "Server error"}), 500

    return render_template("signup.html", form=form)


# Static file serving (CSS, JS, etc.)
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

@app.route('/favicon.ico')
def web_favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'images'),
        'web_favicon.png',
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

@app.route('/update_profile_info', methods=['POST'])
@login_required
def update_profile_info():
    gender = request.form.get('gender')
    age = request.form.get('age')
    if gender:
        current_user.gender = gender
    if age:
        try:
            age_int = int(age)
            if age_int < 21 or age_int > 70:
                flash('Age must be between 21 and 70.', 'danger')
                return redirect(url_for('profile'))
            current_user.age = age_int
        except ValueError:
            flash('Invalid age value.', 'danger')
            return redirect(url_for('profile'))
    db.session.commit()
    return redirect(url_for('profile', updated='1'))

@app.route('/update_profile_picture', methods=['POST'])
@login_required
def update_profile_picture():
    form = ProfilePictureForm()
    if form.validate_on_submit():
        if form.picture.data:
            # Save the picture
            picture_file = form.picture.data
            picture_filename = secrets.token_hex(8) + os.path.splitext(picture_file.filename)[1]
            picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(picture_path), exist_ok=True)
            
            # Save the file
            picture_file.save(picture_path)
            
            # Update user's profile picture
            current_user.profile_picture = picture_filename
            db.session.commit()
            flash('Profile picture updated successfully!', 'success')
        else:
            flash('No picture selected.', 'warning')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    return redirect(url_for('profile'))

@app.route('/delete_profile_picture', methods=['POST'])
@login_required
def delete_profile_picture():
    if current_user.profile_picture != 'placeholder-profile.jpg':
        # Delete the old picture file
        old_picture_path = os.path.join(app.root_path, 'static/profile_pics', current_user.profile_picture)
        if os.path.exists(old_picture_path):
            os.remove(old_picture_path)
        
        # Reset to default picture
        current_user.profile_picture = 'placeholder-profile.jpg'
        db.session.commit()
        flash('Profile picture deleted successfully!', 'success')
    return redirect(url_for('profile'))

@app.route("/news")
@login_required  # optional: restrict access to logged-in users
def news():
    return render_template("news.html")

@app.route('/search_users', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('q', '')
    results = []
    if query:
        users = User.query.filter(User.name.ilike(f"%{query}%")).all()
        results = [{'id': user.id, 'name': user.name} for user in users if user.id != current_user.id]
    return jsonify(results)

@app.route('/my_macroposts')
@login_required
def get_my_macroposts():
    posts = MacroPost.query.filter_by(user_id=current_user.id).order_by(MacroPost.timestamp.desc()).all()
    return jsonify([
        {
            'id': post.id,
            'age': post.age,
            'weight': post.weight,
            'height': post.height,
            'bmr': post.bmr,
            'tdee': post.tdee,
            'timestamp': post.timestamp.strftime('%Y-%m-%d %H:%M')
        }
        for post in posts
    ])

@app.route('/share_post', methods=['POST'])
@login_required
def share_post():
    data = request.get_json()
    receiver_name = data.get('receiver')
    post_id = data.get('post_id')

    receiver = User.query.filter_by(name=receiver_name).first()
    post = MacroPost.query.get(post_id)

    if not receiver or not post or post.user_id != current_user.id:
        return jsonify({'error': 'Invalid data'}), 400

    shared = SharedPost(sender_id=current_user.id, receiver_id=receiver.id, post_id=post.id)
    db.session.add(shared)
    db.session.commit()

    return jsonify({'message': 'Post shared successfully'})

@app.route('/shared_posts')
@login_required
def shared_posts():
    sent = SharedPost.query.filter_by(sender_id=current_user.id).all()
    received = SharedPost.query.filter_by(receiver_id=current_user.id).all()

    def format_post(sp):
        return {
            'id': sp.post.id,
            'age': sp.post.age,
            'weight': sp.post.weight,
            'height': sp.post.height,
            'tdee': sp.post.tdee,
            'timestamp': sp.timestamp.strftime('%Y-%m-%d'),
            'shared_with': sp.receiver.name if sp.sender_id == current_user.id else sp.sender.name
        }

    return jsonify({
        'sent': [format_post(p) for p in sent],
        'received': [format_post(p) for p in received]
    })

# Run the server
if __name__ == "__app__":
    app.run(debug=True)