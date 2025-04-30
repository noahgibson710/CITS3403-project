from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # macros = db.relationship('MacroData', backref='user', lazy=True)


# class CurrentMacros(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     calories = db.Column(db.Integer, nullable=False)
#     protein = db.Column(db.Float, nullable=False)  # grams
#     carbs = db.Column(db.Float, nullable=False)    # grams
#     fats = db.Column(db.Float, nullable=False)     # grams
#     goal_type = db.Column(db.String(50))           # e.g., "bulking", "cutting", etc.
#     date_created = db.Column(db.DateTime, server_default=db.func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



