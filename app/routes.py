from flask import Flask, request, redirect, send_from_directory, jsonify, url_for, Blueprint, render_template, flash, current_app, session
from flask_login import login_required, current_user, login_user, logout_user
from app import app, db
from app.forms import SignupForm, LoginForm, ProfilePictureForm
# app = Blueprint("app", __name__)
from app.models import User, MacroPost, FeedPost, SharedPost, FriendRequest
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash, check_password_hash
import os
from PIL import Image
import secrets
from sqlalchemy import and_, or_
from flask import flash


# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    # Protect against XSS attacks
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Enable XSS protection in browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@app.route('/')
def home():  #If logged in then it should stay on the profile page when clicking on 'home'
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
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
    # pending_count = AddFriend.query.filter_by(receiver_id=current_user.id, status='pending').count()
    # last_count = session.get("last_pending_count", 0)
    # if pending_count != last_count:
    #     session["last_pending_count"] = pending_count
    #     if pending_count > 0:
    #         flash(f"You have {pending_count} pending friend request(s).", "warning")

    macro_posts = MacroPost.query.filter_by(user_id=current_user.id).order_by(MacroPost.timestamp.desc()).all()
    form = ProfilePictureForm()

    # raw_requests = AddFriend.query\
    #     .filter_by(receiver_id=current_user.id, status='pending')\
    #     .join(User, AddFriend.sender_id == User.id)\
    #     .add_columns(User.name, AddFriend.id)\
    #     .all()

    # incoming_requests = [(row[1], row[2]) for row in raw_requests]

    pending_requests = FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()

    return render_template(
        "profile.html",
        user=current_user,
        macro_posts=macro_posts,
        form=form,
        pending_requests=pending_requests,
    )


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
    # Build a query to get posts based on visibility settings:
    # 1. Public posts from anyone
    # 2. Friends-only posts from friends
    # 3. All posts from the current user
    
    # Get IDs of current user's friends
    friend_ids = [friend.id for friend in current_user.friends]
    
    posts_query = FeedPost.query.filter(
        or_(
            FeedPost.visibility == 'public',  # All public posts
            (FeedPost.visibility == 'friends') & (FeedPost.user_id.in_(friend_ids)),  # Friends' posts with 'friends' visibility
            FeedPost.user_id == current_user.id  # All posts by current user
        )
    ).options(
        joinedload(FeedPost.user),
        joinedload(FeedPost.macro_post)
    ).order_by(FeedPost.timestamp.desc())
    
    #get all shared community posts
    posts = posts_query.all()
    
    # Get the shared post ID from the request, (only if redirected from results page)
    shared_id = request.args.get("shared_post_id", type=int)
    if not shared_id:
        shared_id = None

    # Fetch the macro history for each post and attach it
    for post in posts:
        all_history = (MacroPost.query
            .filter(MacroPost.user_id == post.user.id)
            .order_by(MacroPost.timestamp.asc())
            .all())
        idx = next((i for i, m in enumerate(all_history) if m.id == post.macro_post.id), None)
        if idx is not None:
            macro_history = all_history[:idx+1]
        else:
            macro_history = all_history
        post.macro_history = macro_history
    
    return render_template("community.html", posts=posts,shared_post_id=shared_id
)


@login_required
@app.route("/create_feed_post/<int:post_id>", methods=["POST"])
def create_feed_post(post_id):
    post = MacroPost.query.get_or_404(post_id)
    user_who_shared_id = current_user.id
    visibility = request.form.get('visibility', 'public')  # Default to public if not specified

    # Prevent duplicate posts: check if this macro_post has already been shared by this user
    existing_post = FeedPost.query.filter_by(user_id=user_who_shared_id, macro_post_id=post.id).first()
    if existing_post:
        # Update visibility if already shared
        existing_post.visibility = visibility
        db.session.commit()
        # Remove flash message to prevent alerts
        return redirect(url_for("feed"))

    new_post = FeedPost(
        user_id=user_who_shared_id,
        macro_post_id=post.id,
        visibility=visibility
    )
    db.session.add(new_post)
    db.session.commit()
    # Remove flash message to prevent alerts
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
                return redirect(url_for("login"))
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
        calorie_goal=data['calorie_goal'],
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
            
            # Validate file type more thoroughly
            allowed_extensions = ['jpg', 'jpeg', 'png']
            file_ext = os.path.splitext(picture_file.filename)[1].lower().replace('.', '')
            if file_ext not in allowed_extensions:
                flash('Invalid file type. Only jpg, jpeg, and png files are allowed.', 'danger')
                return redirect(url_for('profile'))
                
            # Generate a secure filename
            picture_filename = secrets.token_hex(8) + '.' + file_ext
            picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(picture_path), exist_ok=True)
            
            try:
                # Validate image with PIL
                img = Image.open(picture_file)
                img.verify()  # Verify it's an actual image
                
                # Reopen after verify (verify closes the file)
                picture_file.seek(0)
                img = Image.open(picture_file)
                
                # Resize to reasonable dimensions if needed
                if img.height > 500 or img.width > 500:
                    output_size = (500, 500)
                    img.thumbnail(output_size)
                    
                # Save the optimized image
                img.save(picture_path)
                
                # Update user's profile picture
                # Delete old picture if it exists and isn't the default
                if current_user.profile_picture and current_user.profile_picture != 'placeholder-profile.jpg':
                    old_picture_path = os.path.join(app.root_path, 'static/profile_pics', current_user.profile_picture)
                    if os.path.exists(old_picture_path):
                        os.remove(old_picture_path)
                        
                current_user.profile_picture = picture_filename
                db.session.commit()
                flash('Profile picture updated successfully!', 'success')
            except Exception as e:
                flash(f'Error processing image: {str(e)}', 'danger')
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
@login_required  
def news():
    return redirect(url_for('feed'))

@app.route('/search_users', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('q', '')
    results = []

    if query:
        users = User.query.filter(
            User.name.ilike(f"%{query}%"),
            User.id != current_user.id
        ).all()

        for user in users:
            # Check if already friends
            is_friend = current_user.friends.filter_by(id=user.id).first() is not None
            # Check if request already sent or received
            sent_request = FriendRequest.query.filter_by(requester_id=current_user.id, receiver_id=user.id, status='pending').first()
            received_request = FriendRequest.query.filter_by(requester_id=user.id, receiver_id=current_user.id, status='pending').first()
            
            results.append({
                'id': user.id,
                'name': user.name,
                'is_friend': is_friend,
                'request_pending': bool(sent_request or received_request)
            })

    return jsonify(results)

@app.route('/get_friends', methods=['GET'])
def get_friends():
    friends = current_user.friends.all()
    return jsonify([
        {
            'id': friend.id,
            'name': friend.name,
            'profile_picture': url_for('static', filename='profile_pics/' + friend.profile_picture)
        } for friend in friends
    ])

@app.route('/friends/list', methods=['GET'])
@login_required
def get_friends_list():
    friends = current_user.friends.all()
    return jsonify([
        {
            'id': friend.id,
            'name': friend.name
        } for friend in friends
    ])

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

    if not receiver_name or not post_id:
        return jsonify({"error": "Missing receiver name or post ID"}), 400

    try:
        post_id = int(post_id)
        post = MacroPost.query.get(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        # Strict ownership check
        if post.user_id != current_user.id:
            return jsonify({"error": "You can only share your own posts"}), 403
        
        # Handle both name and ID for receiver
        if receiver_name.isdigit():
            # If it's a numeric ID
            receiver = User.query.get(int(receiver_name))
            if not receiver:
                return jsonify({"error": f"User with ID {receiver_name} not found"}), 404
        else:
            # If it's a username string
            receiver = User.query.filter(User.name == receiver_name).first()
            if not receiver:
                return jsonify({"error": f"User '{receiver_name}' not found"}), 404

        # Check if already shared
        existing_share = SharedPost.query.filter_by(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            post_id=post.id
        ).first()

        if existing_share:
            return jsonify({"message": f"Already shared with {receiver.name}"})

        # Create new shared post
        shared_post = SharedPost(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            post_id=post.id
        )
        db.session.add(shared_post)
        db.session.commit()

        return jsonify({"message": f"Post shared with {receiver.name}!", "success": True})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error sharing post: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

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
            'calorie_goal': sp.post.calorie_goal.capitalize(),
            'timestamp': sp.timestamp.strftime('%Y-%m-%d'),
            'shared_with': sp.receiver.name if sp.sender_id == current_user.id else sp.sender.name
        }

    return jsonify({
        'sent': [format_post(p) for p in sent],
        'received': [format_post(p) for p in received]
    })

@app.route("/friends" ,methods=["GET"])
@login_required
def friends():
    pending_reqs = (FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all())
    friends = []
    
    return render_template("friends.html", friends=friends, pending_requests=pending_reqs)

@app.route('/add_friends/<int:user_id>', methods=['POST'])
@login_required
def add_friend(user_id):
    receiver = User.query.get_or_404(user_id)
    
    # Check if there's an add friend request is already made
    existing_request = FriendRequest.query.filter_by(
        requester_id=current_user.id, 
        receiver_id=receiver.id
    ).first()
    
    # Check if users are already friends
    already_friends = current_user.friends.filter_by(id=user_id).first()
    
    if already_friends:
    # Prevent duplicate add friends request 
        flash(f"You are already friends with {receiver.name}", "info")
        return redirect(url_for('friends'))
    
    if existing_request:
    # If previous request is declined the user can send request again
        if existing_request.status == 'declined':
            existing_request.status = 'pending'
            existing_request.timestamp = datetime.now()
            db.session.commit()
            flash(f"Friend request sent to {receiver.name}", "success")
        else: 
            flash(f"You already have a connection with {receiver.name}", "info")
        
        return redirect(url_for('friends'))
    
    # Create new friend request
    req = FriendRequest(requester=current_user, receiver=receiver, status='pending')
    db.session.add(req)
    db.session.commit()
    
    flash(f"Friend request sent to {receiver.name}", "success")
    return redirect(url_for('friends'))


@app.route('/friend_requests/respond/<int:request_id>', methods=['POST'])
@login_required
def respond_friend_request(request_id):
    decision = request.form.get('decision') 
    request_entry = FriendRequest.query.filter_by(request_id = request_id, receiver_id=current_user.id).first()
    if decision == 'accept':
        request_entry.status = 'accepted'
        # Add the sender as a friend
        sender = request_entry.requester
        receiver = request_entry.receiver
        sender.friends.append(receiver)
        receiver.friends.append(sender)
    elif decision == 'decline':
        # db.session.delete(request_entry)
        request_entry.status ='declined'
    db.session.commit()
    return redirect(url_for('friends'))

@app.route('/profile/<int:user_id>')  #View another user's profile and check if they have accepted the "add friend" request 
@login_required
def view_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return redirect(url_for('profile'))
    
    # Redirect to the username-based URL for better SEO and usability
    return redirect(url_for('view_user_profile_by_name', username=user.name))

@app.route('/profile/u/<username>')  # View another user's profile using their username
@login_required
def view_user_profile_by_name(username):
    user = User.query.filter_by(name=username).first_or_404()
    if user.id == current_user.id:
        return redirect(url_for('profile'))  

    macro_posts = MacroPost.query.filter_by(user_id=user.id).order_by(MacroPost.timestamp.desc()).all()
    form = ProfilePictureForm()

    # Check if a friend request has already been sent
    already_sent = FriendRequest.query.filter_by(requester_id=current_user.id, receiver_id=user.id).first()

    return render_template(
        'profile.html', user=user, macro_posts=macro_posts, form=form, friend_request_sent=bool(already_sent)
    )

def strip_tz(dt):
    return dt.replace(tzinfo=None) if dt and hasattr(dt, 'tzinfo') and dt.tzinfo else dt

if __name__ == "__app__":
    app.run(debug=True)