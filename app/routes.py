from flask import Flask, request, redirect, send_from_directory, jsonify, url_for, Blueprint, render_template, flash
from flask_login import login_required, current_user, login_user, logout_user
from app import app
from app.forms import SignupForm, LoginForm
# app = Blueprint("app", __name__)
from app.models import User, MacroPost, FeedPost
from app import db
from datetime import datetime


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
def delete_macro_post(post_id):
    post = MacroPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('profile'))

@app.route("/feed", methods=["GET"])
@login_required
def feed():
    if "user" not in session:
        return render_template("community.html", login_required=True)
    
    # Get all feed posts
    posts = FeedPost.query.order_by(FeedPost.timestamp.desc()).all()
    
    # Get user's macro posts for the dropdown
    user = User.query.filter_by(name=session["user"]).first()
    user_macros = MacroPost.query.filter_by(user_id=user.id).order_by(MacroPost.timestamp.desc()).all()
    
    return render_template("community.html", login_required=False, posts=posts, user_macros=user_macros)

@app.route("/create_feed_post", methods=["POST"])
def create_feed_post():
    if "user" not in session:
        return redirect(url_for("login"))
    
    content = request.form.get("content")
    macro_post_id = request.form.get("macro_post_id")
    
    if not content:
        return redirect(url_for("feed"))
    
    user = User.query.filter_by(name=session["user"]).first()
    
    # Create new feed post
    new_post = FeedPost(
        content=content,
        user_id=user.id
    )
    
    # If macro results were selected, add them to the post
    if macro_post_id:
        macro_post = MacroPost.query.get(macro_post_id)
        if macro_post and macro_post.user_id == user.id:
            new_post.gender = macro_post.gender
            new_post.age = macro_post.age
            new_post.weight = macro_post.weight
            new_post.height = macro_post.height
            new_post.bmr = macro_post.bmr
            new_post.tdee = macro_post.tdee
    
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

@app.route('/share_to_feed', methods=['POST'])
@login_required
def share_to_feed():
    if request.method == 'POST':
        content = request.form['content']
        timestamp = datetime.utcnow()
        user_id = current_user.id

        new_post = FeedPost(content=content, timestamp=timestamp, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        flash("Post shared successfully", 'success')
        return redirect(url_for('feed'))




# Run the server
if __name__ == "__app__":
    app.run(debug=True)