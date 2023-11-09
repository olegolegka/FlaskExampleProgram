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
from api_bp.api import api_bp

app = Flask(__name__)  # инициализируем экземпляр нашего приложения
app.secret_key = "123123412341234asdasd"  # задаем секретный ключ, нужен для сессий, логина и некоторых других модулей

# -----------------Прописываем конфигурацию нашего приложения(лучше это вынести в отдельный файл config) ---------------

# в конфиг приложения прописываем путь до базы данных в формате driver://username:password@adress:port(если нужен)/имяБД
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://alek:123654@localhost/test_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # отключаем автоматическое отслеживание изменений в метаданных

app.config[
    'MAIL_SERVER'] = "smtp.gmail.com"  # указываем адрес smtp сервера(берется из инструкции по настройке smtp например гугла или майла)
app.config['MAIL_PORT'] = 587  # указываем порт для smtp
app.config['MAIL_USE_TLS'] = True  # указываем что будем использовать TLS
app.config['MAIL_USERNAME'] = os.environ.get(
    'mail')  # здесь прописываем логин от почты с которой будем отправлять письма
app.config['MAIL_PASSWORD'] = os.environ.get(
    'password')  # здесь прописываем токен который получаем при регистрации нашего приложения в почтовом клиенте
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('mail')  # устанавливаем отправителя по умолчанию == username

app.config['FLASK_ADMIN_SWATCH'] = 'simplex'  # устанавливаем тему админки(можно выбрать тут https://bootswatch.com/3/)
# ----------------------------------------------------------------------------------------------------------------------

# ---------------------- создаем сущности для работы модулей(лучше вынести в отдельный файл __init__.py) ---------------
db.init_app(app)  # инициализируем приложение в бд

mail = Mail(app)  # создаем сущность для работы с почтой

login_manager = LoginManager()  # сущность для работы flask-login
login_manager.init_app(app)  # инициализируем приложение для flask-login

admin = Admin(app, index_view=MyAdminIndexView(), name='ExampleStore',
              template_mode='bootstrap3')  # сущность для работы админки
admin.add_view(MyModelView(User, db.session))  # добавляем ModelView для вкладки User в админке(Из файла adminview.py)
admin.add_view(ProductsView(Products, db.session))  # ModelView для вкладки Products(Из файла adminview.py)
admin.add_view(OrderView(Order, db.session))  # ModelView для вкладки Order(Из файла adminview.py)

app.register_blueprint(api_bp, url_prefix="/api")


# ----------------------------------------------------------------------------------------------------------------------


@login_manager.user_loader
def load_user(user_id):
    """
    Callback-функция для возврата текущего пользователя
    Вызывается автоматически когда мы обращаемся к текущему пользователю
    Нужна для работа flask-login.

    :param user_id: id пользователя
    :return: Объект пользователя из бд с id == user_id
    """
    return User.query.filter(User.id == user_id).first()


# ----------------------------- Далее идут функции-представления для маршрутов приложения ------------------------------


@app.route('/home')
@app.route("/index/")
@app.route('/')
def index():
    """
    Функция-обработчик адресов домашней страницы

    :return: страницу index.html
    """
    session.clear()  # сессия очищается только для тестов, чтобы не перезагружать сервер, у себя убрать отсюда
    session.modified = True
    session["Cart"] = {"items": {}, "total": 0}  # создаем пустую корзину в сессии
    return render_template('index.html')


@login_required
@app.route('/about')
def about():
    """
    Функция-обработчик адреса страницы about.
    Для демонстрации декоратора @login_required выдается только после авторизации

    :return: страницу about.html
    """
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Функция-обработчик адреса авторизации

    :return: Если обратились по методу GET отдаем страницу sign_in.html, если по методу POST:
    перенаправляет на себя же в случае не успешной авторизации,
    перенаправляет на index в случае успешной авторизации,
    перенаправляет на admin в случае входа под админом
    """
    if request.method == 'POST':  # проверяем метод по которому запрашивается страница
        email = request.form.get('email')  # берем данные из поля email формы
        password = request.form.get('password')  # берем данные из поля password формы
        try:
            # обращаемся в бд, получаем пользователя по id, если к бд не подключает или пользователя с таким email нет, срабатывает except
            user = User.query.filter(User.email == email).one()
        except:
            # если сработал, выдаем flash-сообщение и переадресовываем на себя же
            flash("Пользователь с указанным логин/паролем не найден")
            return redirect("/login")
        if check_password_hash(user.password, password):
            # если пользователя нашли, проверяем совпадают ли хеш пароля из бд с хешом пароля из поля формы
            if user.role == 2:
                # если роль пользователя просто user(id == 2), то авторизовываем во flask-login и переадресовываем на /
                login_user(user)
                return render_template('index.html')
            else:
                # если роль пользователя admin(id == 1), то авторизовываем во flask-login и переадресовываем на /admin
                login_user(user)
                return redirect('/admin')
        else:
            # если хэши паролей не совпали, выдаем flash-сообщение и переадресовываем на себя же
            flash("Пользователь с указанным логин/паролем не найден")
            return redirect('/login')
    return render_template('sign_in.html')  # Если пользователь обратился по методу GET рисуем страницу sign_in


@app.route("/logout")
@login_required
def logout():
    """
    Функция-обработчик адреса logout
    завершает сессию пользователя

    :return:  перенаправляет на index
    """
    logout_user()  # вызываем функцию из flask-login
    return redirect("/index")  # переадресовываем на индекс


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Функция-обработчик адреса регистрации

    :return: signup.html если обратились по методу GET,если обратились по методу POST:
    перенаправляет на login в случае успешной регистрации,
    в случае не успешной регистрации выводит надпись "Добавление не удалось"
    """
    if request.method == 'POST':  # проверяем метод по которому запрашивается страница
        name = request.form.get("name")  # берем данные из поля name формы
        email = request.form.get("email")  # берем данные из поля email формы
        password = request.form.get("password")  # берем данные из поля password формы
        password = generate_password_hash(password)  # генерируем хэш пароля
        new_user = User(name=name, email=email, password=password, role=2)  # создаем новый объект пользователя
        try:
            db.session.add(new_user)  # добавляем пользователя в метаданные
            db.session.commit()  # выполняем коммит в базу
            return redirect("/login")  # если код выше сработал перенаправляем на логин
        except:
            # если сработал выводим надпись что добавление не удалось
            return "Добавление не удалось"
    else:  # если метод GET рисуем страницу signup
        return render_template('signup.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Функция-обработчик адреса contact
    берет данные из формы на сайте и отправляем сообщение на gmail

    :return: если метод POST, переадресовывает на index в случае успешной отправки,
    если метод GET отдает страницу contact.html
    """
    if request.method == 'POST':  # проверяем метод запроса
        email = request.form.get("email")  # берем данные из поля email формы
        phone = request.form.get("phone")  # берем данные из поля phone формы
        message = request.form.get("message")  # берем данные из поля message формы
        # создаем объект сообщения, первый параметр тема письма, второй - получатель
        msg = Message("Клиент оставил обращение на сайте", recipients=[email])
        msg.body = f"Номер телефона клиента: {phone}, сообщение от клиента: {message}"  # добавляем текст в тело сообщения
        mail.send(msg)  # отправляем сообщение
        return redirect('/index')  # переадресовываем на индекс
    return render_template('contact.html')  # если метод GET отдаем страницу contact.html


@app.route('/catalog')
def catalog():
    """
    Функция-обработчик адреса /catalog
    Выводит товары на страницу catalog.html

    :return: страницу catalog.html со списком товаров
    """
    products = Products.query.all()  # Получаем все товары из бд(соответствует select * from products)
    return render_template('catalog.html',
                           products=products)  # отдаем страницу catalog.html, товары лежат в списке products


@app.route('/item/<int:product_id>', methods=['GET', 'POST'])
def show_item(product_id: int):
    """
    Функция-обработчик страницы конкретного товара

    :param product_id: id продукта страницу которого необходимо вывести
    :return: Страницу конкретного товара с темплейтом item.html
    или 404 код в случае если пользователь перешел не с каталога
    """
    if request.method == 'POST':  # если обратились по POST запросу значит запрос шел с кнопки на странице каталога
        item = Products.query.filter(Products.id == product_id).first()  # получаем продукт по id
        return render_template('item.html', item=item)  # отдаем страницу item.html с продуктом в переменной item
    return Response("Данную страницу можно посетить только после посещения каталога",
                    404)  # в случае обращения по методу GET отдаем 404 статус код с сообщением


@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id: int):
    """
    Функция для добавления товара в корзину
    :param product_id: id продукта который необходимо добавить в корзину
    :return: добавляет товар в корзину в сессии и переадресовывает обратно на каталог
    """
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
def cart():
    """
    Функция-обработчик адреса /cart для отображения корзины
    "Пересобирает" корзину заново и считает общую сумму товаров,
    это нужно в случае если мы удалили какой-то товар с корзины или добавили новый.
    """
    if "Cart" in session:  # проверяем есть ли корзина в сессии
        session["Cart"]["total"] = 0  # обнуляем общую стоимость
        for product_id in session["Cart"]["items"]:  # проходимся циклом по всем id товаров в корзине
            product = Products.query.filter(Products.id == product_id).first()  # получаем объект товара из бд по id
            session["Cart"]["items"][product_id] = {"item": product.name,
                                                    "qty": session["Cart"]["items"][product_id]["qty"],
                                                    "price": product.price * session["Cart"]["items"][product_id]
                                                    [
                                                        "qty"]}  # формируем заново корзину считая стоимость каждого товара по количеству
            session.modified = True  # указываем session что мы поменяли значение словаря(сам не обновится)
            session["Cart"]["total"] += session["Cart"]["items"][product_id][
                "price"]  # добавляем к общей стоимости заказа стоимость товара*количество
        return render_template("cart.html", cart=session["Cart"])  # отдаем страницу cart.html с товарами в словаре cart


@app.route("/remove_item/")
def remove_from_cart():
    """
    Функция для удаления товара с корзины
    :return: удаляет товар из сессии и перенаправляет на корзину
    """
    product_id = request.args.get("product_id")  # из аргументов запроса получаем id продукта
    item = session["Cart"]["items"].pop(str(product_id))  # удаляем ключ с id продукта из сессии
    session["Cart"]["total"] -= item[
        "price"]  # отнимаем от общей стоимости(бесполезное действие в данном случае, так как на /cart мы все равно пересчитаем, просто как пример того как можно сделать пересчет)
    session.modified = True  # указываем на то что поменяли словарь в сессии(сам не обновится)
    return redirect("/cart")  # перенаправляем на корзину


@app.route("/make_order")
def make_order():
    """
    Функция для создания заказа в базе данных.
    Перед отправкой заказа пользователю необходимо авторизоваться
    Создает запись в БД в таблице Orders
    :return: Оставляет запись в таблице Orders и переадресовывает на индекс если успешно,
    либо переадресовывает на login если пользователь не авторизовался
    """
    if "Cart" in session and session["Cart"]["total"] != 0:  # проверяем что корзина есть и она не пустая
        if current_user.is_authenticated:  # проверяем авторизовался ли пользователь
            new_order = Order(user_id=current_user.get_id(),
                              date=datetime.now(),
                              total=session["Cart"][
                                  "total"])  # создаем объект заказа с текущей датой и стоимостью из сессии
            for product_id in session["Cart"]["items"]:  # проходимся по id продуктов в сессии
                for i in range(session["Cart"]["items"][product_id][
                                   "qty"]):  # формируем range(количество товара в корзине) чтобы добавить несколько одинаковых товаров в заказ
                    product = Products.query.filter(Products.id == product_id).first()  # получаем объект товара из бд
                    new_order.cart.append(product)  # добавляем в список cart модели Order объект товара
            db.session.add(new_order)  # добавляем заказ в метаданные
            db.session.commit()  # выполняем коммит в базу данных
            return redirect('/')  # переадресовываем на индекс
        else:
            return redirect("/login")  # если пользователь не прошел авторизацию переадресовываем на login


@app.route('/cookies')
def cookies():
    """
    Функция для создания куки
    :return: ответ с кукой
    """
    res = make_response("Посылаю тебе куку храни ее")  # отправляем ответ что создадим тебе куку
    res.set_cookie("Name", "Oleg", max_age=60 * 60 * 24 * 365)  # добавляем куку с временем жизни 1 год
    return res


@app.route('/show_cookies')
def show():
    """
    Функция для отображения куки
    :return:
    """
    if request.cookies.get("Name"):  # проверяем есть ли кука Name
        return "Hello" + request.cookies.get("Name")
    else:
        return "Кук нет"


@app.route('/delete_cookies')
def delete_cookies():
    """
    Функция удаления куки
    :return:
    """
    res = make_response("Мы тебе удаляем куку")
    res.set_cookie("Name", "asdas", max_age=0)  # пересоздаем существующую куку с временем жизни 0
    return res


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)  # Запускаем приложение
