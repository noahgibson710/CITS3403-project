from app import db
from datetime import datetime
from flask_login import UserMixin


friend_assoc = db.Table(
    'friend_assoc',
    db.Column('user_id',   db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    profile_picture = db.Column(db.String(255), default='placeholder-profile.jpg')

    requests_sent = db.relationship(
        'FriendRequest',
        foreign_keys='FriendRequest.requester_id',
        back_populates='requester',
        lazy='dynamic'
    )
    # all the requests this user has received:
    requests_received = db.relationship(
        'FriendRequest',
        foreign_keys='FriendRequest.receiver_id',
        back_populates='receiver',
        lazy='dynamic'
    )

    friends = db.relationship(
        'User',
        secondary=friend_assoc,
        primaryjoin=(id == friend_assoc.c.user_id),
        secondaryjoin=(id == friend_assoc.c.friend_id),
        lazy='dynamic'
    )

class MacroPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    bmr = db.Column(db.Float, nullable=False)
    tdee = db.Column(db.Float, nullable=False)
    calorie_goal = db.Column(db.String(10), nullable=False, server_default='maintain')
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('macroposts', lazy=True))



class FeedPost(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    macro_post_id = db.Column(db.Integer, db.ForeignKey('macro_post.id'), nullable=False)
    visibility = db.Column(db.String(20), nullable=False, server_default='public')  # 'public', 'friends', 'private'
    user = db.relationship('User', backref='feed_posts')
    macro_post = db.relationship('MacroPost', backref='feed_entries')

class SharedPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('macro_post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
    post = db.relationship('MacroPost')

class FriendRequest(db.Model):
    __tablename__ = 'friend_request'
    request_id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
    )
    receiver_id  = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
    )
    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending'
    )
    # "Which side is which" helper relationships:
    requester = db.relationship(
        'User',
        foreign_keys=[requester_id],
        back_populates='requests_sent'
    )
    receiver  = db.relationship(
        'User',
        foreign_keys=[receiver_id],
        back_populates='requests_received'
    )