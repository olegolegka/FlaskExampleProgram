<H2>Пример учебного проекта для студентов</H2>
<p>Написан в рамках семинаров по backend python разработки</p> 
Реализован на:
<ul>
<li> Flask </li>
<li> Flask-SQLAlchemy </li>
<li> Alembic </li>
<li> Flask-Mail </li>
<li> Flask-Admin </li> 
<li> Flask-Admin </li> 
</ul>
<p>Api реализован как отдельный BluePrint</p>
Авторизация с использование JWT

<H3> Запуск:</H3>

1. Клонирование репозитория

```git clone https://github.com/olegolegka/FlaskExampleProgram```

2. Переход в директорию

``` cd FlaskProgram```

3. Создание виртуального окружения

```python3 -m venv venv```

4. Активация виртуального окружения

```source venv/bin/activate```

5. Установка зависимостей

```pip3 install -r requirements.txt```

6. Необходимо создать docker-контейнер с PostgreSQL

Пример тут: https://habr.com/ru/articles/578744/

7. Выполнение миграций

 ``` alembic init migrations ```

В файле ```alembic.ini``` в переменную ```sqlalchemy.url``` указываем адрес базы

Выполняем все миграции из папки ```migrations/versions```

```alembic upgrade head```

8. После запуска необходимо создать роли и пользователя-администратора

``` python3 scriptforadmin.py```

9. Запустить проект
``` python3 app.py```

<H3> Что доступно: </H3>
<ul>
<li> Главная страница </li>
<li> Страница About </li>
<li> Страница каталог с выводом товаров из бд</li>
<li> Роли пользователей</li>
<li> Регистрация пользователя</li>
<li> Авторизация пользователя</li>
<li> Добавление,удаление,просмотр товаров через admin-панель</li>
<li> Корзина </li>
<li> Оформление заказа</li>
<li> Уведомления на почту о заказе</li>
<li> Форма обратной связи </li>
<li> Авторизация пользователя в API через JWT </li>
<li> Получения информации из бд через API</li>
</ul>

Весь фронтенд это просто шаблоны из интернета, над ним не заморачивались))

Передаю привет своим студентам которые читают Readme в моих личных репозиториях :kissing_heart: