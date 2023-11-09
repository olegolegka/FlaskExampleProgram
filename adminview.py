import flask_admin as fladmin
import flask_login as login
from flask import redirect, url_for
from flask_admin import helpers, expose
from models import User, Order
from flask_admin.contrib.sqla import ModelView


class MyAdminIndexView(fladmin.AdminIndexView):
    """
    Overriding of Admin index view
    """

    @expose('/')
    def index(self):
        """
        Authorization for '/admin' panel
        :return: redirect to '/login' if user not logged in or his role not Admin
        """
        if not login.current_user.is_authenticated:  # если пользователь не авторизован то сразу переадресовываем на логин
            return redirect(url_for('login'))
        else:
            admin = User.query.filter(User.id == login.current_user.get_id()).first()
            if admin.role == 1:  # проверяем роль текущего пользователя, если она админ отдаем страницу
                return super(MyAdminIndexView, self).index()
            return redirect(url_for('login'))


class MyModelView(ModelView):
    """
    Overriding of base ModelView to add authentication for other admin paths
    """
    column_hide_backrefs = False

    def is_accessible(self):
        """
        This method used to check is current user is authenticated and his role is Admin
        :return:
        """
        if not login.current_user.is_authenticated:
            return False
        else:
            admin = User.query.filter(User.id == login.current_user.get_id()).first()
            if admin.role == 1:
                return True
            return False


class OrderView(MyModelView):
    """
    View for '/admin/order'
    """

    column_list = ("id", "user_id", "date", "cart", "total")  # переопределение колонок таблицы
    column_searchable_list = ["date"]  # делаем колонку date доступной для поиска
    column_sortable_list = ["date"]  # делаем колонку date сортируемой


class ProductsView(MyModelView):
    """
    View for '/admin/products'
    """

    column_list = ("id", "name", "price", "orders")  # переопределение колонок таблицы
    column_searchable_list = ["name", "price"]  # делаем колонки name и price доступной для поиска
    column_sortable_list = ["name"]  # делаем колонку name сортируемой
