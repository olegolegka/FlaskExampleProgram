from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

metadata = db.metadata


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(300), nullable = False)
    role = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', backref='user', lazy=True, cascade="all, delete-orphan")