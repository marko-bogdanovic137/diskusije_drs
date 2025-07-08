from .extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    phone = db.Column(db.String(30))
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)

class Discussion(db.Model):
    __tablename__ = 'discussions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    topic = db.relationship('Topic', backref=db.backref('discussions', lazy=True))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('discussions', lazy=True))



    
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key ka diskusiji
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=False)

    # Foreign key ka korisniku
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Veze
    discussion = db.relationship('Discussion', backref=db.backref('comments', lazy=True, cascade="all, delete"))
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    

class LikeDislike(db.Model):
    __tablename__ = 'likes_dislikes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=False)
    is_like = db.Column(db.Boolean, nullable=False)  # True = Like, False = Dislike

    __table_args__ = (
        db.UniqueConstraint('user_id', 'discussion_id', name='unique_user_discussion_vote'),
    )

class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

