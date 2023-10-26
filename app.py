from flask import Flask,render_template, url_for, request,redirect,flash,get_flashed_messages
from models import db, User
from werkzeug.security import generate_password_hash,check_password_hash
import os
from flask_mail import Mail, Message
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
db.init_app(app)
mail = Mail(app)
@app.route('/home')
@app.route("/index/")
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = User.query.filter(User.email == email).one()
        except:
            flash("Пользователь с указанным логин/паролем не найден")
            return redirect("/login")
        if check_password_hash(user.password,password):
            if user.role == 2:
                return render_template('index.html',username=user.name, email=user.email)
            else:
                return "Admin"
        else:
            flash("Пользователь с указанным логин/паролем не найден")
            return redirect('/login')
    return render_template('sign_in.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=password, role = 2)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
        except:
            return "Добавление не удалось"
    else:
        return render_template('signup.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        msg = Message("Клиент оставил обращение на сайте",recipients=[email])
        msg.body = f"Номер телефона клиента: {phone}, сообщение от клиента: {message}"
        mail.send(msg)
        return redirect('/index')
    return render_template('contact.html')

@app.route('/catalog')
def catalog():
    return "catalog"



@app.route('/item')
def show_item():
    return "item"


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)