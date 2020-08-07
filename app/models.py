import time
import jwt
from datetime import datetime
from app import app
from app import db, auth
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
from flask_login import UserMixin
from flask import g
from hashlib import md5

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('Image', backref='upmaster', lazy='dynamic')
    
    followed = db.relationship(
    'User', secondary=followers,
    primaryjoin=(followers.c.follower_id == id),
    secondaryjoin=(followers.c.followed_id == id),
    backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
        
    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])
        
    @auth.verify_password
    def verify_password(username_or_token, password):
        # first try to authenticate by token
        user = User.verify_auth_token(username_or_token)
        if not user:
            # try to authenticate with username/password
            user = User.query.filter_by(username=username_or_token).first()
            if not user or not user.check_password(password):
                return False
        g.user = user
        return True


    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))
        
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
        
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() == 1

    def followed_posts(self):
        followed = Post.query.join(
        followers, (followers.c.followed_id == Post.user_id)).filter(
        followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id == self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
            
        


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
        
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    detected = db.relationship('DetectData', backref='fromwho', lazy='dynamic')
    
class DetectData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_index = db.Column(db.Integer)
    predicted_class = db.Column(db.String(120))
    obj_score = db.Column(db.Float)
    left = db.Column(db.Integer)
    top = db.Column(db.Integer)
    right = db.Column(db.Integer)
    bottom = db.Column(db.Integer)
    all_score = db.Column(db.PickleType())
    multiple_obj = db.Column(db.PickleType())
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))