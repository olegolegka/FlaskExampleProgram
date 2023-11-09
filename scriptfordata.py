"""
Скрипт добавляет 10 телефонов сяоми в таблицу products
"""

from app import app
from models import db, Products

for i in range(1, 10):
    product1 = Products(name=f"телефон Сяоми{i}", price=str(200 + i))
    with app.app_context():
        db.session.add(product1)
        db.session.commit()
