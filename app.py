from flask import Flask, render_template, url_for, request, redirect, flash, get_flashed_messages, session, \
    make_response, Response
from models import db, User, Products, cart, Order
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_mail import Mail, Message
from datetime import datetime
from flask_admin import Admin
from adminview import MyAdminIndexView, OrderView, MyModelView, ProductsView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://alek:123654@localhost/test_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "123123412341234asdasd"
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('mail')
app.config['MAIL_PASSWORD'] = os.environ.get('password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('mail')
app.config['FLASK_ADMIN_SWATCH'] = 'simplex'
db.init_app(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)

admin = Admin(app, index_view=MyAdminIndexView(), name='ExampleStore', template_mode='bootstrap3')
admin.add_view(MyModelView(User, db.session))
admin.add_view(ProductsView(Products, db.session))
admin.add_view(OrderView(Order, db.session))


@login_manager.user_loader
def load_user (user_id):
    return User.query.filter(User.id == user_id).first()


@app.route('/home')
@app.route("/index/")
@app.route('/')
def index ():
    session.clear()
    session.modified = True
    session["Cart"] = {"items": {}, "total": 0}
    print(session)
    return render_template('index.html')


@login_required
@app.route('/about')
def about ():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login ():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = User.query.filter(User.email == email).one()
        except:
            flash("Пользователь с указанным логин/паролем не найден")
            return redirect("/login")
        if check_password_hash(user.password, password):
            if user.role == 2:
                login_user(user)
                return render_template('index.html')
            else:
                login_user(user)
                return redirect('/admin')
        else:
            flash("Пользователь с указанным логин/паролем не найден")
            return redirect('/login')
    return render_template('sign_in.html')


@app.route("/logout")
@login_required
def logout ():
    logout_user()
    return redirect("/index")


@app.route('/signup', methods=['GET', 'POST'])
def signup ():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=password, role=2)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
        except:
            return "Добавление не удалось"
    else:
        return render_template('signup.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact ():
    if request.method == 'POST':
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        msg = Message("Клиент оставил обращение на сайте", recipients=[email])
        msg.body = f"Номер телефона клиента: {phone}, сообщение от клиента: {message}"
        mail.send(msg)
        return redirect('/index')
    return render_template('contact.html')


@app.route('/catalog')
def catalog ():
    products = Products.query.all()  # select * from products
    return render_template('catalog.html', products=products)


@app.route('/item/<int:product_id>', methods=['GET', 'POST'])
def show_item (product_id: int):
    if request.method == 'POST':
        item = Products.query.filter(Products.id == product_id).first()
        return render_template('item.html', item=item)
    return Response("Данную страницу можно посетить только после посещения каталога", 404)


@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart (product_id: int):
    if request.method == 'POST':
        if "Cart" in session:  # Проверяем на то есть ли корзина в сессии
            if not str(product_id) in session["Cart"]["items"]:  # проверяем на то есть ли имя в корзине, если нет, то добавляем в корзину словарь с ключом "имя"
                session["Cart"]["items"][str(product_id)] = {"product": product_id, "qty": 1}
                session.modified = True  # Если корзина - это список или словарь, то нужно каждый раз когда мы его обновляем ставить флаг True
            else:  # если имя уже в сессии то увеличиваем количество "товара"
                session["Cart"]["items"][str(product_id)]["qty"] += 1
                session.modified = True
        return redirect("/catalog")


@app.route("/cart")
def cart ():
    """Функция для отображения корзины"""
    if "Cart" in session:
        session["Cart"]["total"] = 0
        for product_id in session["Cart"]["items"]:
            product = Products.query.filter(Products.id == product_id).first()
            session["Cart"]["items"][product_id] = {"item": product.name,
                                                    "qty": session["Cart"]["items"][product_id]["qty"],
                                                    "price": product.price * session["Cart"]["items"][product_id]
                                                    ["qty"]}
            session.modified = True
            session["Cart"]["total"] += session["Cart"]["items"][product_id]["price"]
        return render_template("cart.html", cart=session["Cart"])


@app.route("/remove_item/")
def remove_from_cart ():
    product_id = request.args.get("product_id")
    item = session["Cart"]["items"].pop(str(product_id))
    session["Cart"]["total"] -= item["price"]
    session.modified = True
    return redirect("/cart")


@app.route("/make_order")
def make_order ():
    if "Cart" in session and session["Cart"]["total"] != 0:
        if current_user.is_authenticated:
            new_order = Order(user_id=current_user.get_id(),
                              date=datetime.now(),
                              total=session["Cart"]["total"])
            for product_id in session["Cart"]["items"]:
                for i in range(session["Cart"]["items"][product_id]["qty"]):
                    product = Products.query.filter(Products.id == product_id).first()
                    new_order.cart.append(product)
            db.session.add(new_order)
            db.session.commit()
            return redirect('/')
        else:
            return redirect("/login")


@app.route('/cookies')
def cookies ():
    res = make_response("Посылаю тебе куку храни ее")
    res.set_cookie("Name", "Oleg", max_age=60 * 60 * 24 * 365)
    return res


@app.route('/show_cookies')
def show ():
    if request.cookies.get("Name"):
        return "Hello" + request.cookies.get("Name")
    else:
        return "Кук нет"


@app.route('/delete_cookies')
def delete_cookies ():
    res = make_response("Мы тебе удаляем куку")
    res.set_cookie("Name", "asdas", max_age=0)
    return res


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
