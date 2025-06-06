from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()

def bucharest_time():
    tz = pytz.timezone('Europe/Bucharest')
    return datetime.now(tz)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=bucharest_time)

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(8), nullable=False)
    created_at = db.Column(db.DateTime, default=bucharest_time)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(200), nullable=False)
    client_name = db.Column(db.String(200), nullable=False)
    project_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    folder_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=bucharest_time)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    author_email = db.Column(db.String(120), nullable=False)
    comment_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=bucharest_time)
