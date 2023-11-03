from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()
metadata = db.metadata


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(300), nullable = False)
    role = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    orders = db.relationship("Order",backref="orders",lazy=True,cascade="all,delete-orphan")

class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', backref='user', lazy=True, cascade="all, delete-orphan",)



cart = db.Table('cart',
    db.Column('products', db.Integer, db.ForeignKey('products.id')),
    db.Column('orders', db.Integer, db.ForeignKey('orders.id')),
)

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship("Order",secondary=cart,back_populates="cart")

    def __repr__(self):
        return self.name

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    cart = db.relationship("Products",secondary=cart,back_populates="orders")
    date = db.Column(db.DateTime)
    total = db.Column(db.Float,nullable=False)

    def __repr__(self):
        return str(self.id)
