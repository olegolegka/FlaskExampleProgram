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
    orders = db.relationship("Order",backref="orders",lazy=True,cascade="all,delete-orphan")

class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', backref='user', lazy=True, cascade="all, delete-orphan")

class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    products = db.Column(db.Integer, db.ForeignKey("products.id"),nullable=False)
    orders = db.Column(db.Integer, db.ForeignKey("orders.id"),nullable=False)
    product_quantity = db.Column(db.Integer)
    product_price = db.Column(db.Float)


class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship("Order",secondary=Cart,backref= db.backref('products', lazy='dynamic'))

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    cart = db.relationship("Products",secondary=Cart,backref = db.backref('orders', lazy='dynamic'))
    date = db.Column(db.DateTime)
